"""Navigator operations.

Facade module — public interface for navigator functionality. Database
infrastructure lives in _db.py, filesystem scanning in _scanner.py.
Business logic lives here. Presentation lives in navigator_cli.py.
"""

import fnmatch
import logging
import os
import sqlite3
from pathlib import Path

try:
    from ._db import get_connection, init_db, SCHEMA, MIGRATIONS, SEED_PATH  # noqa: F401
    from ._scanner import (  # noqa: F401
        scan_path,
        _walk_filesystem,
        _is_pattern,
        _compute_git_hash,
        _matches_any_rule,
        _mark_parents_stale,
    )
except ImportError:
    from _db import get_connection, init_db, SCHEMA, MIGRATIONS, SEED_PATH  # type: ignore[import-not-found] # noqa: F401
    from _scanner import (  # type: ignore[import-not-found] # noqa: F401
        scan_path,
        _walk_filesystem,
        _is_pattern,
        _compute_git_hash,
        _matches_any_rule,
        _mark_parents_stale,
    )

logger = logging.getLogger(__name__)


def describe_path(db_path: str, target_path: str) -> str:
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


def list_files(
    db_path: str,
    target_path: str,
    patterns: list[str] | None = None,
    excludes: list[str] | None = None,
) -> str:
    """List non-excluded file paths under target_path.

    Walks filesystem using navigator rules (exclude, traverse). Returns
    files only (not directories), sorted, one per line. If patterns
    provided, keeps only paths where basename matches any pattern via
    fnmatch. If excludes provided, removes paths where any path component
    matches any exclude pattern via fnmatch.

    Returns empty string if no files match.
    """
    target_path = target_path.rstrip("/")
    if target_path == ".":
        target_path = ""

    conn = get_connection(db_path)
    try:
        disk_entries = _walk_filesystem(conn, target_path)
    finally:
        conn.close()

    files = sorted(p for p, t in disk_entries.items() if t == "file")

    if patterns:
        files = [
            f for f in files
            if any(fnmatch.fnmatch(Path(f).name, pat) for pat in patterns)
        ]

    if excludes:
        files = [
            f for f in files
            if not any(fnmatch.fnmatch(f, pat) for pat in excludes)
        ]

    return "\n".join(files)


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
        body = describe_path(db_path, deepest)
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
            params: list = []
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
                return f"Error: --recursive not valid for file entries. Use remove without --recursive."
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
