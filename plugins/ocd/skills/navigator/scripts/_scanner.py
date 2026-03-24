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

try:
    from ._db import get_connection
except ImportError:
    from _db import get_connection  # type: ignore[import-not-found]

logger = logging.getLogger(__name__)


def _is_pattern(path: str) -> bool:
    """Check if path is a glob pattern."""
    return "*" in path


def _matches_any_rule(path: str, rules: list[sqlite3.Row]) -> sqlite3.Row | None:
    """Check if path matches any pattern-based rule. Returns first match."""
    path_parts = Path(path).parts
    for rule in rules:
        pattern = rule["path"]
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


def _compute_git_hash(file_path: str) -> str | None:
    """Compute git-compatible blob hash for a file. Returns hex digest or None for directories."""
    try:
        data = Path(file_path).read_bytes()
    except (OSError, IsADirectoryError):
        return None
    header = f"blob {len(data)}\0".encode()
    return hashlib.sha1(header + data).hexdigest()


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
    """Walk filesystem with rule-based pruning.

    Loads exclude and shallow rules from database, walks target_path,
    and returns filtered entries. Excluded paths are omitted entirely.
    Shallow directories are listed but not descended into.

    Returns dict mapping path to entry type ("file" or "directory").
    """
    pattern_rows = conn.execute(
        "SELECT path, exclude, traverse, description FROM entries "
        "WHERE path LIKE '%*%'"
    ).fetchall()

    exclude_rules = [r for r in pattern_rows if r["exclude"]]
    shallow_rules = [r for r in pattern_rows if not r["exclude"] and not r["traverse"]]

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
            if _matches_any_rule(d_path, exclude_rules):
                continue
            concrete = conn.execute(
                "SELECT traverse FROM entries "
                "WHERE path = ? AND traverse = 0",
                (d_path,),
            ).fetchone()
            if concrete or _matches_any_rule(d_path, shallow_rules):
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
            if not _matches_any_rule(file_path, exclude_rules):
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

        # Load prescribed rules for auto-descriptions
        pattern_rows = conn.execute(
            "SELECT path, exclude, traverse, description FROM entries "
            "WHERE path LIKE '%*%'"
        ).fetchall()
        prescribed_rules = [r for r in pattern_rows if not r["exclude"] and r["description"]]

        # Load concrete entries from database
        db_entries = {}
        if target_path:
            rows = conn.execute(
                "SELECT path, git_hash FROM entries "
                "WHERE (path = ? OR path LIKE ?) AND path NOT LIKE '%*%'",
                (target_path, target_path + "/%"),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT path, git_hash FROM entries WHERE path NOT LIKE '%*%'"
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

                rule = _matches_any_rule(path, prescribed_rules)
                description = rule["description"] if rule else None
                git_hash = _compute_git_hash(path) if entry_type == "file" else None

                conn.execute(
                    "INSERT OR IGNORE INTO entries "
                    "(path, parent_path, entry_type, description, git_hash) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (path, parent_path, entry_type, description, git_hash),
                )
                display = path + "/" if entry_type == "directory" else path
                added.append(f"- {display}")
                for p in _mark_parents_stale(conn, path):
                    staled_parents.add(p)

        # Detect changed files — hash differs from stored, mark stale + parents
        changed = []
        for path in sorted(disk_entries):
            if path in db_entries and disk_entries[path] == "file":
                current_hash = _compute_git_hash(path)
                stored_hash = db_entries[path]
                if stored_hash is not None and current_hash != stored_hash:
                    rule = _matches_any_rule(path, prescribed_rules)
                    if rule:
                        conn.execute(
                            "UPDATE entries SET description = ?, stale = 0, git_hash = ? "
                            "WHERE path = ?",
                            (rule["description"], current_hash, path),
                        )
                    else:
                        conn.execute(
                            "UPDATE entries SET stale = 1, git_hash = ? "
                            "WHERE path = ?",
                            (current_hash, path),
                        )
                    changed.append(f"- {path}")
                    for p in _mark_parents_stale(conn, path):
                        staled_parents.add(p)
                elif stored_hash is None and current_hash is not None:
                    conn.execute(
                        "UPDATE entries SET git_hash = ? WHERE path = ?",
                        (current_hash, path),
                    )

        # Auto-remove stale entries
        removed = []
        for path in sorted(db_entries):
            if path not in disk_entries and path != target_path:
                conn.execute("DELETE FROM entries WHERE path = ?", (path,))
                removed.append(f"- {path}")
                for p in _mark_parents_stale(conn, path):
                    staled_parents.add(p)

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
