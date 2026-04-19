"""Navigator filesystem scanning.

Walks filesystem with rule-based pruning, computes git-compatible hashes,
detects changes, and syncs database state. Before walking, consolidates
path-pattern rules from every deployed `.claude/*/*/paths.csv` into the
path_patterns table so per-system declarations flow into navigator's
pattern matching.

All walking is anchored on the project root resolved via
framework.get_project_dir(); paths stored in the paths table are always
project-relative.
"""

import csv
import fnmatch
import hashlib
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import framework

from ._db import get_connection


def _matches_pattern_any(path: str, patterns: list[sqlite3.Row]) -> sqlite3.Row | None:
    """Check if path matches any glob pattern. Returns first match."""
    path_parts = Path(path).parts
    for rule in patterns:
        pattern = rule["pattern"]
        pattern_parts = Path(pattern).parts
        if len(pattern_parts) == 0:
            continue
        if pattern_parts[0] == "**":
            target = str(Path(*pattern_parts[1:]))
            for i in range(len(path_parts)):
                candidate = str(Path(*path_parts[i:]))
                if fnmatch.fnmatch(candidate, target):
                    return rule
        else:
            if fnmatch.fnmatch(path, pattern):
                return rule
    return None


def _compute_file_metrics(file_path: Path) -> dict:
    """Compute git hash, line count, and char count from a single file read.

    file_path must be an absolute path (callers that start from project-
    relative data compose with framework.get_project_dir first).

    Returns dict with keys: git_hash, line_count, char_count.
    All values None for directories or on read error.
    """
    try:
        data = file_path.read_bytes()
    except (OSError, IsADirectoryError):
        return {"git_hash": None, "line_count": None, "char_count": None}
    header = f"blob {len(data)}\0".encode()
    git_hash = hashlib.sha1(header + data).hexdigest()
    line_count = data.count(b"\n") + (1 if data and not data.endswith(b"\n") else 0)
    char_count = len(data)
    return {"git_hash": git_hash, "line_count": line_count, "char_count": char_count}


def _compute_git_hash(file_path: Path) -> str | None:
    """Compute git-compatible blob hash for a file. Returns hex digest or None for directories."""
    return _compute_file_metrics(file_path)["git_hash"]


def _mark_parents_stale(conn: sqlite3.Connection, entry_path: str) -> list[str]:
    """Mark all non-rule-matched parent directories as stale up the path.

    `stale` is the single signal that a path needs purpose description —
    set to 1 on both user-described parents (purpose may be wrong) and
    undescribed parents (purpose never written). Rule-matched parents
    skip cascade because their purpose is deterministic and they're
    maintained stale=0 in the main scan loop.

    Returns staled paths.
    """
    staled = []
    current = entry_path
    while True:
        parent = str(Path(current).parent) if current else None
        if parent == "." or parent is None:
            parent = ""
        if parent == current:
            break
        current = parent
        row = conn.execute(
            "SELECT stale FROM paths WHERE path = ?", (current,)
        ).fetchone()
        if row and not row["stale"]:
            conn.execute(
                "UPDATE paths SET stale = 1 WHERE path = ?",
                (current,),
            )
            staled.append(current)
        if not current:
            break
    return staled


def _discover_deployed_paths_csv() -> list[Path]:
    """Return absolute paths of every deployed paths.csv under .claude/*/*/."""
    project_dir = framework.get_project_dir()
    claude_dir = project_dir / ".claude"
    deployed = []
    if not claude_dir.is_dir():
        return deployed
    for plugin_dir in sorted(claude_dir.iterdir()):
        if not plugin_dir.is_dir():
            continue
        for system_dir in sorted(plugin_dir.iterdir()):
            if not system_dir.is_dir():
                continue
            paths_csv = system_dir / "paths.csv"
            if paths_csv.is_file():
                deployed.append(paths_csv)
    return deployed


def _consolidate_path_patterns(conn: sqlite3.Connection) -> None:
    """Refresh path_patterns from deployed paths.csv files when any changed.

    Walks `.claude/*/*/paths.csv`, hashes each, compares to the
    path_pattern_sources table. If the set of sources or any content
    hash differs, rebuilds path_patterns from scratch and updates
    path_pattern_sources. No-op when sources are current.
    """
    project_dir = framework.get_project_dir()
    deployed = _discover_deployed_paths_csv()

    current_sources: dict[str, str] = {}
    for f in deployed:
        source_path = str(f.relative_to(project_dir))
        content_hash = hashlib.sha1(f.read_bytes()).hexdigest()
        current_sources[source_path] = content_hash

    known = {
        row["source_path"]: row["content_hash"]
        for row in conn.execute(
            "SELECT source_path, content_hash FROM path_pattern_sources"
        ).fetchall()
    }

    if current_sources == known:
        return

    conn.execute("DELETE FROM path_patterns")
    conn.execute("DELETE FROM path_pattern_sources")

    now = datetime.now(timezone.utc).isoformat()
    for source_path, content_hash in current_sources.items():
        abs_source = project_dir / source_path
        with open(abs_source, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                pattern = row["path"]
                purpose_raw = row.get("purpose", "") or ""
                purpose = purpose_raw if purpose_raw else None
                exclude = int(row.get("exclude", 0))
                traverse = int(row.get("traverse", 1))
                entry_type = row.get("entry_type") or None
                conn.execute(
                    "INSERT OR REPLACE INTO path_patterns "
                    "(pattern, entry_type, exclude, traverse, purpose) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (pattern, entry_type, exclude, traverse, purpose),
                )
        conn.execute(
            "INSERT INTO path_pattern_sources (source_path, content_hash, loaded_at) "
            "VALUES (?, ?, ?)",
            (source_path, content_hash, now),
        )


def _walk_filesystem(
    conn: sqlite3.Connection, target_subpath: str
) -> dict[str, str]:
    """Walk filesystem with pattern-based pruning.

    Walks `framework.get_project_dir() / target_subpath` (empty subpath
    means the whole project). All paths in the returned dict are
    project-relative strings, independent of working directory.

    Loads exclude and shallow patterns from database. Excluded paths
    are omitted entirely; shallow directories are listed but not
    descended into.

    Returns dict mapping path to entry type ("file" or "directory").
    """
    pattern_rows = conn.execute(
        "SELECT pattern, exclude, traverse, purpose FROM path_patterns"
    ).fetchall()

    exclude_patterns = [r for r in pattern_rows if r["exclude"]]
    shallow_patterns = [r for r in pattern_rows if not r["exclude"] and not r["traverse"]]

    project_dir = framework.get_project_dir()
    scan_root = project_dir / target_subpath if target_subpath else project_dir

    disk_paths: dict[str, str] = {}

    for dirpath, dirnames, filenames in os.walk(scan_root):
        abs_dir = Path(dirpath)
        if abs_dir == project_dir:
            rel_dir = ""
        else:
            rel_dir = str(abs_dir.relative_to(project_dir))

        shallow_dirs = []
        remaining_dirs = []
        for d in dirnames:
            d_path = f"{rel_dir}/{d}" if rel_dir else d
            if _matches_pattern_any(d_path, exclude_patterns):
                continue
            concrete = conn.execute(
                "SELECT traverse FROM paths "
                "WHERE path = ? AND traverse = 0",
                (d_path,),
            ).fetchone()
            if concrete or _matches_pattern_any(d_path, shallow_patterns):
                shallow_dirs.append(d)
            else:
                remaining_dirs.append(d)

        dirnames[:] = remaining_dirs

        for d in shallow_dirs:
            d_path = f"{rel_dir}/{d}" if rel_dir else d
            disk_paths[d_path] = "directory"

        if rel_dir and rel_dir != target_subpath:
            disk_paths[rel_dir] = "directory"

        for filename in filenames:
            file_path = f"{rel_dir}/{filename}" if rel_dir else filename
            if not _matches_pattern_any(file_path, exclude_patterns):
                disk_paths[file_path] = "file"

        for dirname in dirnames:
            dir_path = f"{rel_dir}/{dirname}" if rel_dir else dirname
            disk_paths[dir_path] = "directory"

    return disk_paths


def scan_path(db_path: str, target_subpath: str = "") -> str:
    """Sync filesystem to database. Auto-adds missing, auto-removes stale.

    target_subpath is relative to the project root (empty means whole
    project). Walking is always anchored on framework.get_project_dir(),
    independent of working directory. Paths stored in the paths table
    are project-relative.

    Returns formatted report.
    """
    target_subpath = target_subpath.rstrip("/")
    if target_subpath == ".":
        target_subpath = ""

    project_dir = framework.get_project_dir()

    conn = get_connection(db_path)
    try:
        _consolidate_path_patterns(conn)

        disk_paths = _walk_filesystem(conn, target_subpath)

        pattern_rows = conn.execute(
            "SELECT pattern, exclude, traverse, purpose FROM path_patterns"
        ).fetchall()
        prescribed_patterns = [r for r in pattern_rows if not r["exclude"] and r["purpose"]]

        db_paths = {}
        if target_subpath:
            rows = conn.execute(
                "SELECT path, git_hash FROM paths "
                "WHERE path = ? OR path LIKE ?",
                (target_subpath, target_subpath + "/%"),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT path, git_hash FROM paths"
            ).fetchall()

        for row in rows:
            db_paths[row["path"]] = row["git_hash"]

        added = []
        changed = []
        staled_parents = set()

        for path in sorted(disk_paths):
            entry_type = disk_paths[path]
            rule = _matches_pattern_any(path, prescribed_patterns)

            if path not in db_paths:
                # New path — insert with rule purpose if matched, otherwise
                # mark stale since it needs a user-authored purpose. Rule-
                # matched new paths are immediately complete (stale=0) and
                # do not cascade to parents.
                parent_path = str(Path(path).parent) if path else None
                if parent_path == ".":
                    parent_path = ""

                purpose = rule["purpose"] if rule else None
                stale = 0 if rule else 1
                if entry_type == "file":
                    metrics = _compute_file_metrics(project_dir / path)
                else:
                    metrics = {"git_hash": None, "line_count": None, "char_count": None}

                conn.execute(
                    "INSERT OR IGNORE INTO paths "
                    "(path, parent_path, entry_type, purpose, stale, git_hash, line_count, char_count) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (path, parent_path, entry_type, purpose, stale,
                     metrics["git_hash"], metrics["line_count"], metrics["char_count"]),
                )
                display = path + "/" if entry_type == "directory" else path
                added.append(f"- {display}")
                if not rule:
                    for p in _mark_parents_stale(conn, path):
                        staled_parents.add(p)

            elif rule and entry_type == "directory":
                # Rule-matched directory: re-apply purpose, ensure stale=0.
                # No hash to track on directories. No cascade — rule-derived
                # purposes are deterministic and don't invalidate parents.
                existing = conn.execute(
                    "SELECT purpose, stale FROM paths WHERE path = ?", (path,)
                ).fetchone()
                if existing["purpose"] != rule["purpose"] or existing["stale"]:
                    conn.execute(
                        "UPDATE paths SET purpose = ?, stale = 0 WHERE path = ?",
                        (rule["purpose"], path),
                    )

            elif entry_type == "file":
                metrics = _compute_file_metrics(project_dir / path)
                current_hash = metrics["git_hash"]
                stored_hash = db_paths[path]

                if rule:
                    # Rule-matched: always re-apply purpose + ensure stale=0.
                    # Handles both content changes and newly-added rules that
                    # match previously unmatched (or stale) paths. No cascade
                    # — rule-derived purposes are deterministic and don't
                    # invalidate parent summaries.
                    existing = conn.execute(
                        "SELECT purpose, stale FROM paths WHERE path = ?", (path,)
                    ).fetchone()
                    if (existing["purpose"] != rule["purpose"]
                            or existing["stale"]
                            or current_hash != stored_hash):
                        conn.execute(
                            "UPDATE paths SET purpose = ?, stale = 0, "
                            "git_hash = ?, line_count = ?, char_count = ? "
                            "WHERE path = ?",
                            (rule["purpose"], current_hash, metrics["line_count"], metrics["char_count"], path),
                        )
                elif stored_hash is not None and current_hash != stored_hash:
                    # Non-rule-matched content change — mark stale unconditionally
                    # and cascade. stale is the single signal for "needs purpose
                    # description"; whether the path already had a user-authored
                    # purpose or never had one, it now needs review.
                    conn.execute(
                        "UPDATE paths SET stale = 1, "
                        "git_hash = ?, line_count = ?, char_count = ? "
                        "WHERE path = ?",
                        (current_hash, metrics["line_count"], metrics["char_count"], path),
                    )
                    changed.append(f"- {path}")
                    for p in _mark_parents_stale(conn, path):
                        staled_parents.add(p)
                elif stored_hash is None and current_hash is not None:
                    conn.execute(
                        "UPDATE paths SET git_hash = ?, line_count = ?, char_count = ? WHERE path = ?",
                        (current_hash, metrics["line_count"], metrics["char_count"], path),
                    )

        # Auto-remove entries that no longer exist on disk
        removed = []
        for path in sorted(db_paths):
            if path not in disk_paths and path != target_subpath:
                conn.execute("DELETE FROM paths WHERE path = ?", (path,))
                removed.append(f"- {path}")
                for p in _mark_parents_stale(conn, path):
                    staled_parents.add(p)

        conn.commit()

        display_target = target_subpath + "/" if target_subpath else "./"
        lines = [f"Scan: {display_target}"]
        summary_parts = [f"Added {len(added)}", f"removed {len(removed)}"]
        if changed:
            summary_parts.append(f"changed {len(changed)}")
        if staled_parents:
            summary_parts.append(f"staled {len(staled_parents)} parent(s)")
        lines.append(", ".join(summary_parts))

        return "\n".join(lines)
    finally:
        conn.close()
