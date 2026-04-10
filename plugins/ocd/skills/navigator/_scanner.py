"""Navigator filesystem scanning.

Walks filesystem with rule-based pruning, computes git-compatible hashes,
detects changes, and syncs database state.
"""

import fnmatch
import hashlib
import logging
import os
import sqlite3
from pathlib import Path

from ._db import get_connection
from ._frontmatter import normalize_patterns

logger = logging.getLogger(__name__)


def _matches_any_pattern(path: str, patterns: list[sqlite3.Row]) -> sqlite3.Row | None:
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


def _compute_file_metrics(file_path: str) -> dict:
    """Compute git hash, line count, and char count from a single file read.

    Returns dict with keys: git_hash, line_count, char_count.
    All values None for directories or on read error.
    """
    try:
        data = Path(file_path).read_bytes()
    except (OSError, IsADirectoryError):
        return {"git_hash": None, "line_count": None, "char_count": None}
    header = f"blob {len(data)}\0".encode()
    git_hash = hashlib.sha1(header + data).hexdigest()
    line_count = data.count(b"\n") + (1 if data and not data.endswith(b"\n") else 0)
    char_count = len(data)
    return {"git_hash": git_hash, "line_count": line_count, "char_count": char_count}


def _compute_git_hash(file_path: str) -> str | None:
    """Compute git-compatible blob hash for a file. Returns hex digest or None for directories."""
    return _compute_file_metrics(file_path)["git_hash"]


def _mark_parents_stale(conn: sqlite3.Connection, entry_path: str) -> list[str]:
    """Mark all parent directories as stale up the path. Returns staled paths."""
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
            "SELECT description, stale FROM entries WHERE path = ?", (current,)
        ).fetchone()
        if row and row["description"] is not None and not row["stale"]:
            conn.execute(
                "UPDATE entries SET stale = 1 WHERE path = ?",
                (current,),
            )
            staled.append(current)
        if not current:
            break
    return staled


def _walk_filesystem(
    conn: sqlite3.Connection, target_path: str
) -> dict[str, str]:
    """Walk filesystem with pattern-based pruning.

    Loads exclude and shallow patterns from database, walks target_path,
    and returns filtered entries. Excluded paths are omitted entirely.
    Shallow directories are listed but not descended into.

    Returns dict mapping path to entry type ("file" or "directory").
    """
    pattern_rows = conn.execute(
        "SELECT pattern, exclude, traverse, description FROM patterns"
    ).fetchall()

    exclude_patterns = [r for r in pattern_rows if r["exclude"]]
    shallow_patterns = [r for r in pattern_rows if not r["exclude"] and not r["traverse"]]

    disk_entries: dict[str, str] = {}
    scan_root = target_path if target_path else "."

    for dirpath, dirnames, filenames in os.walk(scan_root):
        rel_dir = os.path.normpath(dirpath)
        if rel_dir == ".":
            rel_dir = ""

        shallow_dirs = []
        remaining_dirs = []
        for d in dirnames:
            d_path = os.path.join(rel_dir, d) if rel_dir else d
            if _matches_any_pattern(d_path, exclude_patterns):
                continue
            concrete = conn.execute(
                "SELECT traverse FROM entries "
                "WHERE path = ? AND traverse = 0",
                (d_path,),
            ).fetchone()
            if concrete or _matches_any_pattern(d_path, shallow_patterns):
                shallow_dirs.append(d)
            else:
                remaining_dirs.append(d)

        dirnames[:] = remaining_dirs

        for d in shallow_dirs:
            d_path = os.path.join(rel_dir, d) if rel_dir else d
            disk_entries[d_path] = "directory"

        if rel_dir and rel_dir != target_path:
            disk_entries[rel_dir] = "directory"

        for filename in filenames:
            file_path = os.path.join(rel_dir, filename) if rel_dir else filename
            if not _matches_any_pattern(file_path, exclude_patterns):
                disk_entries[file_path] = "file"

        for dirname in dirnames:
            dir_path = os.path.join(rel_dir, dirname) if rel_dir else dirname
            disk_entries[dir_path] = "directory"

    return disk_entries


def scan_path(db_path: str, target_path: str) -> str:
    """Sync filesystem to database. Auto-adds missing, auto-removes stale.
    Reports entries needing descriptions. Returns formatted report."""
    target_path = target_path.rstrip("/")
    if target_path == ".":
        target_path = ""

    conn = get_connection(db_path)
    try:
        disk_entries = _walk_filesystem(conn, target_path)

        # Load prescribed patterns for auto-descriptions
        pattern_rows = conn.execute(
            "SELECT pattern, exclude, traverse, description FROM patterns"
        ).fetchall()
        prescribed_patterns = [r for r in pattern_rows if not r["exclude"] and r["description"]]

        # Load concrete entries from database
        db_entries = {}
        if target_path:
            rows = conn.execute(
                "SELECT path, git_hash FROM entries "
                "WHERE path = ? OR path LIKE ?",
                (target_path, target_path + "/%"),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT path, git_hash FROM entries"
            ).fetchall()

        for row in rows:
            db_entries[row["path"]] = row["git_hash"]

        # Auto-add missing entries
        added = []
        staled_parents = set()
        for path in sorted(disk_entries):
            if path not in db_entries:
                entry_type = disk_entries[path]
                parent_path = str(Path(path).parent) if path else None
                if parent_path == ".":
                    parent_path = ""

                rule = _matches_any_pattern(path, prescribed_patterns)
                description = rule["description"] if rule else None
                metrics = _compute_file_metrics(path) if entry_type == "file" else {"git_hash": None, "line_count": None, "char_count": None}

                conn.execute(
                    "INSERT OR IGNORE INTO entries "
                    "(path, parent_path, entry_type, description, git_hash, line_count, char_count) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (path, parent_path, entry_type, description, metrics["git_hash"], metrics["line_count"], metrics["char_count"]),
                )
                display = path + "/" if entry_type == "directory" else path
                added.append(f"- {display}")
                for p in _mark_parents_stale(conn, path):
                    staled_parents.add(p)

        # Detect changed files — hash differs from stored, mark stale + parents
        changed = []
        for path in sorted(disk_entries):
            if path in db_entries and disk_entries[path] == "file":
                metrics = _compute_file_metrics(path)
                current_hash = metrics["git_hash"]
                stored_hash = db_entries[path]
                if stored_hash is not None and current_hash != stored_hash:
                    rule = _matches_any_pattern(path, prescribed_patterns)
                    if rule:
                        conn.execute(
                            "UPDATE entries SET description = ?, stale = 0, git_hash = ?, line_count = ?, char_count = ? "
                            "WHERE path = ?",
                            (rule["description"], current_hash, metrics["line_count"], metrics["char_count"], path),
                        )
                    else:
                        conn.execute(
                            "UPDATE entries SET stale = CASE WHEN description IS NOT NULL THEN 1 ELSE 0 END, "
                            "git_hash = ?, line_count = ?, char_count = ? "
                            "WHERE path = ?",
                            (current_hash, metrics["line_count"], metrics["char_count"], path),
                        )
                    changed.append(f"- {path}")
                    for p in _mark_parents_stale(conn, path):
                        staled_parents.add(p)
                elif stored_hash is None and current_hash is not None:
                    conn.execute(
                        "UPDATE entries SET git_hash = ?, line_count = ?, char_count = ? WHERE path = ?",
                        (current_hash, metrics["line_count"], metrics["char_count"], path),
                    )

        # Auto-remove stale entries
        removed = []
        for path in sorted(db_entries):
            if path not in disk_entries and path != target_path:
                conn.execute("DELETE FROM entries WHERE path = ?", (path,))
                removed.append(f"- {path}")
                for p in _mark_parents_stale(conn, path):
                    staled_parents.add(p)

        # Governance pattern matching — populate governs from governance patterns
        gov_rows = conn.execute(
            "SELECT entry_path, matches, excludes FROM governance"
        ).fetchall()
        if gov_rows:
            gov_paths = {r["entry_path"] for r in gov_rows}
            # Get all non-governance file entries in scope
            file_entries = [
                path for path, etype in disk_entries.items()
                if etype == "file" and path not in gov_paths
            ]
            for gov in gov_rows:
                include_patterns = normalize_patterns(gov["matches"])
                exclude_patterns = normalize_patterns(gov["excludes"]) if gov["excludes"] else []
                gov_path = gov["entry_path"]
                for file_path in file_entries:
                    basename = Path(file_path).name
                    included = any(
                        fnmatch.fnmatch(basename, p) or fnmatch.fnmatch(file_path, p)
                        for p in include_patterns
                    )
                    if not included:
                        continue
                    if exclude_patterns and any(
                        fnmatch.fnmatch(basename, p) or fnmatch.fnmatch(file_path, p)
                        for p in exclude_patterns
                    ):
                        continue
                    conn.execute(
                        "INSERT OR IGNORE INTO governs (governor_path, governed_path) "
                        "VALUES (?, ?)",
                        (gov_path, file_path),
                    )
            # Remove stale governs for files no longer on disk
            conn.execute(
                "DELETE FROM governs WHERE governed_path NOT IN "
                "(SELECT path FROM entries)"
            )

        conn.commit()

        # Format report
        display_target = target_path + "/" if target_path else "./"
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
