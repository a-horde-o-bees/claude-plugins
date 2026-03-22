"""Navigator operations.

SQLite-backed storage for project directory structure and file descriptions.
Functions take explicit parameters and return strings. No argparse, no
print/input, no sys.exit — presentation lives in navigator_cli.py.
"""

import csv
import fnmatch
import hashlib
import logging
import os
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

SCHEMA = """
CREATE TABLE IF NOT EXISTS entries (
    path TEXT PRIMARY KEY,
    parent_path TEXT,
    entry_type TEXT CHECK (entry_type IN ('file', 'directory')),
    exclude INTEGER NOT NULL DEFAULT 0,
    traverse INTEGER NOT NULL DEFAULT 1,
    description TEXT,
    git_hash TEXT,
    stale INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_entries_parent ON entries(parent_path);
"""

MIGRATIONS = [
    "ALTER TABLE entries ADD COLUMN stale INTEGER NOT NULL DEFAULT 0",
]

SEED_PATH = Path(__file__).parent / "navigator_seed.csv"


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


def get_connection(db_path: str) -> sqlite3.Connection:
    """Open database connection with WAL mode for concurrent access."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str) -> str:
    """Create database with schema, upsert seed rules from CSV.

    Idempotent — safe to rerun. Creates schema if missing, then upserts
    seed rules (adds new patterns, updates changed ones). Non-seed
    entries are untouched.
    """
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection(str(path))
    try:
        conn.executescript(SCHEMA)

        for migration in MIGRATIONS:
            try:
                conn.execute(migration)
            except sqlite3.OperationalError:
                pass

        if not SEED_PATH.exists():
            return f"Initialized: {path} (no seed file)"

        added = 0
        updated = 0
        with open(SEED_PATH, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                desc_raw = row.get("description", "")
                description = desc_raw if desc_raw else None
                exclude = int(row.get("exclude", 0))
                traverse = int(row.get("traverse", 1))
                entry_type = row.get("entry_type") or None

                existing = conn.execute(
                    "SELECT exclude, traverse, description, entry_type "
                    "FROM entries WHERE path = ?",
                    (row["path"],),
                ).fetchone()

                if existing is None:
                    conn.execute(
                        "INSERT INTO entries "
                        "(path, parent_path, entry_type, exclude, traverse, description) "
                        "VALUES (?, ?, ?, ?, ?, ?)",
                        (row["path"], None, entry_type, exclude, traverse, description),
                    )
                    added += 1
                elif (
                    existing[0] != exclude
                    or existing[1] != traverse
                    or existing[2] != description
                    or existing[3] != entry_type
                ):
                    conn.execute(
                        "UPDATE entries SET exclude = ?, traverse = ?, "
                        "description = ?, entry_type = ? WHERE path = ?",
                        (exclude, traverse, description, entry_type, row["path"]),
                    )
                    updated += 1

        conn.commit()
        parts = []
        if added:
            parts.append(f"{added} added")
        if updated:
            parts.append(f"{updated} updated")
        if not parts:
            parts.append("all current")
        return f"Initialized: {path} (seed rules: {', '.join(parts)})"
    finally:
        conn.close()


def show_path(db_path: str, target_path: str) -> str:
    """Show entry at path. Files return description. Directories return description and children."""
    target_path = target_path.rstrip("/")
    if target_path == ".":
        target_path = ""

    conn = get_connection(db_path)
    try:
        entry = conn.execute(
            "SELECT * FROM entries WHERE path = ?", (target_path,)
        ).fetchone()

        # File entry — return single entry with description
        if entry and entry["entry_type"] == "file":
            lines = [entry["path"]]
            if entry["description"] is None:
                lines.append("[?]")
            elif entry["stale"]:
                lines.append(f"[~] {entry['description']}")
            elif entry["description"]:
                lines.append(entry["description"])
            return "\n".join(lines)

        # Directory entry — return listing
        lines = []

        display_path = target_path + "/" if target_path else "./"
        lines.append(display_path)

        if entry and entry["description"] is None:
            lines.append("[?]")
        elif entry and entry["stale"] and entry["description"]:
            lines.append(f"[~] {entry['description']}")
        elif entry and entry["description"]:
            lines.append(entry["description"])

        children = conn.execute(
            "SELECT * FROM entries WHERE parent_path = ? "
            "AND exclude = 0 "
            "ORDER BY "
            "CASE entry_type WHEN 'directory' THEN 0 ELSE 1 END, path",
            (target_path,),
        ).fetchall()

        if children:
            if entry and (entry["description"] is not None and entry["description"]):
                lines.append("")
            for child in children:
                child_display = child["path"]
                if child["entry_type"] == "directory":
                    child_display += "/"
                desc = child["description"]
                if desc is None:
                    lines.append(f"- {child_display} [?]")
                elif child["stale"] and desc:
                    lines.append(f"- {child_display} [~] {desc}")
                elif desc:
                    lines.append(f"- {child_display} - {desc}")
                else:
                    lines.append(f"- {child_display}")

        if not entry and not children:
            lines.append("(no entries)")

        return "\n".join(lines)
    finally:
        conn.close()


def scan_path(db_path: str, target_path: str) -> str:
    """Sync filesystem to database. Auto-adds missing, auto-removes stale.
    Reports entries needing descriptions. Returns formatted report."""
    target_path = target_path.rstrip("/")
    if target_path == ".":
        target_path = ""

    conn = get_connection(db_path)
    try:
        # Load pattern-based rules from database
        pattern_rows = conn.execute(
            "SELECT path, exclude, traverse, description FROM entries "
            "WHERE path LIKE '%*%'"
        ).fetchall()

        exclude_rules = [r for r in pattern_rows if r["exclude"]]
        shallow_rules = [r for r in pattern_rows if not r["exclude"] and not r["traverse"]]
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

        # Walk filesystem
        disk_entries = {}
        scan_root = target_path if target_path else "."

        for dirpath, dirnames, filenames in os.walk(scan_root):
            rel_dir = os.path.normpath(dirpath)
            if rel_dir == ".":
                rel_dir = ""

            # Classify directories: excluded, shallow, or normal
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


def get_undescribed(db_path: str) -> str:
    """Return deepest directory with undescribed or stale entries.
    Uses [?] for new entries, [~] for stale. Agent calls repeatedly until no work remaining."""
    conn = get_connection(db_path)
    try:
        # Find all entries needing attention: NULL description or stale
        work_entries = conn.execute(
            "SELECT path, parent_path, entry_type FROM entries "
            "WHERE (description IS NULL OR stale = 1) AND path NOT LIKE '%*%'"
        ).fetchall()

        if not work_entries:
            return "No work remaining."

        # Collect directories that need attention
        work_dirs = set()
        for row in work_entries:
            if row["entry_type"] == "directory":
                work_dirs.add(row["path"] if row["path"] is not None else "")
            else:
                work_dirs.add(row["parent_path"] if row["parent_path"] is not None else "")

        # Pick deepest (longest path = most segments)
        deepest = max(work_dirs, key=lambda p: p.count("/") if p else -1)

        # Render with progress header
        header = f"[{len(work_entries)} remaining across {len(work_dirs)} directories]"
        body = show_path(db_path, deepest)
        return f"{header}\n{body}"
    finally:
        conn.close()


def set_entry(
    db_path: str,
    entry_path: str,
    description: str | None = None,
    exclude: int | None = None,
    traverse: int | None = None,
) -> str:
    """Create or update entry. Returns status message."""
    entry_path = entry_path.rstrip("/")
    if entry_path == ".":
        entry_path = ""

    is_pat = _is_pattern(entry_path)

    if is_pat:
        entry_type = None
        parent_path = None
    else:
        if os.path.isdir(entry_path) if entry_path else True:
            entry_type = "directory"
        elif os.path.isfile(entry_path):
            entry_type = "file"
        else:
            entry_type = "file"

        parent_path = str(Path(entry_path).parent) if entry_path else None
        if parent_path == ".":
            parent_path = ""

    conn = get_connection(db_path)
    try:
        existing = conn.execute(
            "SELECT * FROM entries WHERE path = ?", (entry_path,)
        ).fetchone()

        # Compute git hash for files when setting description
        git_hash = None
        if description is not None and not is_pat and entry_type == "file":
            git_hash = _compute_git_hash(entry_path)

        if existing:
            updates = []
            params = []
            if description is not None:
                updates.append("description = ?")
                params.append(description)
                updates.append("stale = 0")
            if exclude is not None:
                updates.append("exclude = ?")
                params.append(exclude)
            if traverse is not None:
                updates.append("traverse = ?")
                params.append(traverse)
            if git_hash is not None:
                updates.append("git_hash = ?")
                params.append(git_hash)
            if not updates:
                return f"No changes: {entry_path}"
            params.append(entry_path)
            conn.execute(
                f"UPDATE entries SET {', '.join(updates)} WHERE path = ?",
                params,
            )
            conn.commit()
            display = entry_path if entry_path else "."
            return f"Updated: {display}"
        else:
            conn.execute(
                "INSERT INTO entries "
                "(path, parent_path, entry_type, exclude, traverse, description, git_hash) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    entry_path,
                    parent_path,
                    entry_type,
                    exclude if exclude is not None else 0,
                    traverse if traverse is not None else 1,
                    description,
                    git_hash,
                ),
            )
            conn.commit()
            display = entry_path if entry_path else "."
            kind = entry_type or "pattern"
            return f"Added: {display} ({kind})"
    finally:
        conn.close()


def remove_entry(
    db_path: str,
    entry_path: str,
    recursive: bool = False,
    all_entries: bool = False,
) -> str:
    """Remove entries. Returns status message."""
    conn = get_connection(db_path)
    try:
        if all_entries:
            result = conn.execute(
                "DELETE FROM entries WHERE path NOT LIKE '%*%'"
            )
            conn.commit()
            return f"Removed all {result.rowcount} entries (rules preserved)"

        entry_path = entry_path.rstrip("/")

        if recursive:
            existing = conn.execute(
                "SELECT entry_type FROM entries WHERE path = ?", (entry_path,)
            ).fetchone()
            if existing and existing["entry_type"] == "file":
                return f"Error: -r not valid for file entries. Use remove without -r."
            result = conn.execute(
                "DELETE FROM entries WHERE path = ? OR path LIKE ?",
                (entry_path, entry_path + "/%"),
            )
            conn.commit()
            if result.rowcount == 0:
                return f"Not found: {entry_path}"
            return f"Removed {result.rowcount} entries under {entry_path}/"
        else:
            result = conn.execute(
                "DELETE FROM entries WHERE path = ?", (entry_path,)
            )
            conn.commit()
            if result.rowcount == 0:
                return f"Not found: {entry_path}"
            return f"Removed: {entry_path}"
    finally:
        conn.close()


def search_entries(db_path: str, pattern: str) -> str:
    """Search descriptions by pattern. Returns formatted results."""
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            "SELECT path, entry_type, description FROM entries "
            "WHERE description LIKE ? AND path NOT LIKE '%*%' "
            "ORDER BY path",
            (f"%{pattern}%",),
        ).fetchall()

        if not rows:
            return f'No entries matching "{pattern}"'

        lines = [f'Search: "{pattern}" ({len(rows)} results)']
        lines.append("")
        for row in rows:
            display = row["path"] if row["path"] else "."
            if row["entry_type"] == "directory":
                display += "/"
            lines.append(f"- {display} - {row['description']}")

        return "\n".join(lines)
    finally:
        conn.close()
