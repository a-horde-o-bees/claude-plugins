"""Navigator operations.

Facade module — public interface for navigator functionality. Domain
modules: _db (database), _scanner (filesystem), _frontmatter (parsing),
_governance (governance operations), _skills (skill resolution),
_references (file reference mapping).

All functions return structured data (dicts/lists). Formatting for
CLI display belongs in __main__.py. Presentation lives in __main__.py.
"""

import fnmatch
import logging
from pathlib import Path

import plugin

# Local imports — used by functions in this module
from ._db import get_connection
from ._scanner import scan_path, _walk_filesystem, _compute_file_metrics

# Re-exports — public interface consumed by MCP server and CLI
from ._references import references_map
from ._skills import skills_resolve, skills_list

# Cross-skill: scope_analyze composites governance matching into its result,
# so the facade imports governance_match from the governance skill.
from servers.governance import governance_match

logger = logging.getLogger(__name__)


def _ensure_scanned(db_path: str) -> None:
    """Populate the entries table from disk before a read or write.

    Every facade function that touches the entries table calls this
    first — navigator owns its own population, callers never have to
    scan before invoking a navigator function.
    """
    scan_path(db_path)


def paths_get(db_path: str, paths: str | list[str]) -> dict:
    """Retrieve entry details for one or more paths.

    Files return type, description, stale flag. Directories return entry
    info plus children. Single path returns one dict; multiple paths
    return {"entries": [dict, ...]}.
    """
    _ensure_scanned(db_path)
    if isinstance(paths, str):
        return _paths_get_single(db_path, paths)

    entries = [_paths_get_single(db_path, p) for p in paths]
    return {"entries": entries}


def _paths_get_single(db_path: str, target_path: str) -> dict:
    """Retrieve entry details for a single path."""
    target_path = target_path.rstrip("/")
    if target_path == ".":
        target_path = ""

    conn = get_connection(db_path)
    try:
        entry = conn.execute(
            "SELECT * FROM entries WHERE path = ?", (target_path,)
        ).fetchone()

        def _entry_dict(row) -> dict:
            return {
                "path": row["path"] or ".",
                "type": row["entry_type"],
                "description": row["description"],
                "stale": bool(row["stale"]),
            }

        # File entry
        if entry and entry["entry_type"] == "file":
            return _entry_dict(entry)

        # Directory entry
        result = {
            "path": (target_path + "/") if target_path else "./",
            "type": "directory",
            "description": entry["description"] if entry else None,
            "stale": bool(entry["stale"]) if entry else False,
            "children": [],
        }

        children = conn.execute(
            "SELECT * FROM entries WHERE parent_path = ? "
            "AND exclude = 0 "
            "ORDER BY "
            "CASE entry_type WHEN 'directory' THEN 0 ELSE 1 END, path",
            (target_path,),
        ).fetchall()

        for child in children:
            result["children"].append(_entry_dict(child))

        if not entry and not children:
            result["children"] = None  # signals "no entries"

        return result
    finally:
        conn.close()


def paths_list(
    db_path: str,
    target_path: str,
    patterns: list[str] | None = None,
    excludes: list[str] | None = None,
    sizes: bool = False,
) -> list[dict]:
    """List non-excluded files under target_path.

    Returns list of file dicts. Each dict has 'path' and optionally
    'line_count' and 'char_count' when sizes=True.
    """
    _ensure_scanned(db_path)
    target_path = target_path.rstrip("/")
    if target_path == ".":
        target_path = ""

    conn = get_connection(db_path)
    try:
        disk_entries = _walk_filesystem(conn, target_path)

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

        if not sizes:
            return [{"path": f} for f in files]

        result = []
        for f in files:
            row = conn.execute(
                "SELECT line_count, char_count FROM entries WHERE path = ?",
                (f,),
            ).fetchone()
            entry = {"path": f}
            if row and row["line_count"] is not None:
                entry["line_count"] = row["line_count"]
                entry["char_count"] = row["char_count"]
            result.append(entry)
        return result
    finally:
        conn.close()


def paths_undescribed(db_path: str) -> dict:
    """Return deepest directory with undescribed or stale entries.

    Returns progress info and directory listing. When no work remains,
    returns {"done": True}.
    """
    _ensure_scanned(db_path)
    conn = get_connection(db_path)
    try:
        work_entries = conn.execute(
            "SELECT path, parent_path, entry_type FROM entries "
            "WHERE description IS NULL OR stale = 1"
        ).fetchall()

        if not work_entries:
            return {"done": True}

        work_dirs = set()
        for row in work_entries:
            if row["entry_type"] == "directory":
                work_dirs.add(row["path"] if row["path"] is not None else "")
            else:
                work_dirs.add(row["parent_path"] if row["parent_path"] is not None else "")

        deepest = max(work_dirs, key=lambda p: p.count("/") if p else -1)

        return {
            "done": False,
            "remaining": len(work_entries),
            "directories": len(work_dirs),
            "target": deepest,
            "listing": paths_get(db_path, deepest),
        }
    finally:
        conn.close()


def paths_upsert(
    db_path: str,
    entry_path: str,
    description: str | None = None,
    exclude: int | None = None,
    traverse: int | None = None,
) -> dict:
    """Create or update entry. Returns status dict.

    Only accepts concrete paths (files and directories), not glob patterns.
    Patterns belong in the patterns table and are managed via seed CSV.
    """
    _ensure_scanned(db_path)
    entry_path = entry_path.rstrip("/")
    if entry_path == ".":
        entry_path = ""

    if "*" in entry_path:
        raise ValueError(
            f"paths_upsert does not accept glob patterns: {entry_path!r}. "
            "Patterns are managed via navigator_seed.csv."
        )

    absolute_entry = plugin.get_project_dir() / entry_path if entry_path else plugin.get_project_dir()
    if absolute_entry.is_dir() if entry_path else True:
        entry_type = "directory"
    elif absolute_entry.is_file():
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

        metrics = {"git_hash": None, "line_count": None, "char_count": None}
        if description is not None and entry_type == "file":
            metrics = _compute_file_metrics(plugin.get_project_dir() / entry_path)

        display = entry_path if entry_path else "."

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
            if metrics["git_hash"] is not None:
                updates.append("git_hash = ?")
                params.append(metrics["git_hash"])
                updates.append("line_count = ?")
                params.append(metrics["line_count"])
                updates.append("char_count = ?")
                params.append(metrics["char_count"])
            if not updates:
                return {"action": "none", "path": display}
            params.append(entry_path)
            conn.execute(
                f"UPDATE entries SET {', '.join(updates)} WHERE path = ?",
                params,
            )
            conn.commit()
            return {"action": "updated", "path": display}
        else:
            conn.execute(
                "INSERT INTO entries "
                "(path, parent_path, entry_type, exclude, traverse, description, git_hash, line_count, char_count) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    entry_path,
                    parent_path,
                    entry_type,
                    exclude if exclude is not None else 0,
                    traverse if traverse is not None else 1,
                    description,
                    metrics["git_hash"],
                    metrics["line_count"],
                    metrics["char_count"],
                ),
            )
            conn.commit()
            return {"action": "added", "path": display, "type": entry_type}
    finally:
        conn.close()


def paths_remove(
    db_path: str,
    entry_path: str,
    recursive: bool = False,
    all_entries: bool = False,
) -> dict:
    """Remove entries. Returns status dict."""
    _ensure_scanned(db_path)
    conn = get_connection(db_path)
    try:
        if all_entries:
            result = conn.execute(
                "DELETE FROM entries"
            )
            conn.commit()
            return {"action": "removed_all", "count": result.rowcount}

        entry_path = entry_path.rstrip("/")

        if recursive:
            existing = conn.execute(
                "SELECT entry_type FROM entries WHERE path = ?", (entry_path,)
            ).fetchone()
            if existing and existing["entry_type"] == "file":
                return {"action": "error", "message": "--recursive not valid for file entries"}
            result = conn.execute(
                "DELETE FROM entries WHERE path = ? OR path LIKE ?",
                (entry_path, entry_path + "/%"),
            )
            conn.commit()
            if result.rowcount == 0:
                return {"action": "not_found", "path": entry_path}
            return {"action": "removed_recursive", "path": entry_path, "count": result.rowcount}
        else:
            result = conn.execute(
                "DELETE FROM entries WHERE path = ?", (entry_path,)
            )
            conn.commit()
            if result.rowcount == 0:
                return {"action": "not_found", "path": entry_path}
            return {"action": "removed", "path": entry_path}
    finally:
        conn.close()


def paths_search(db_path: str, pattern: str) -> dict:
    """Search descriptions by pattern."""
    _ensure_scanned(db_path)
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            "SELECT path, entry_type, description FROM entries "
            "WHERE description LIKE ? "
            "ORDER BY path",
            (f"%{pattern}%",),
        ).fetchall()

        return {
            "pattern": pattern,
            "results": [
                {
                    "path": row["path"] if row["path"] else ".",
                    "type": row["entry_type"],
                    "description": row["description"],
                }
                for row in rows
            ],
        }
    finally:
        conn.close()


def scope_analyze(db_path: str, paths: list[str]) -> dict:
    """Build scope matrix combining references, sizes, and governance.

    Follows references from starting paths, collects file sizes from the
    database, and maps governance for all files. Returns a structured
    matrix for intelligent agent partitioning.
    """
    _ensure_scanned(db_path)
    ref_result = references_map(paths)
    all_paths = [f["path"] for f in ref_result["files"]]

    size_map: dict[str, dict[str, int | None]] = {}
    conn = get_connection(db_path)
    try:
        for file_path in all_paths:
            row = conn.execute(
                "SELECT line_count, char_count FROM entries WHERE path = ?",
                (file_path,),
            ).fetchone()
            if row:
                size_map[file_path] = {
                    "line_count": row["line_count"],
                    "char_count": row["char_count"],
                }
    finally:
        conn.close()

    gov_result = governance_match(db_path, all_paths)
    gov_matches = gov_result["matches"]

    files = []
    total_lines = 0
    for f in ref_result["files"]:
        path = f["path"]
        sizes = size_map.get(path, {})
        lc = sizes.get("line_count")
        if lc:
            total_lines += lc
        files.append({
            "path": path,
            "line_count": lc,
            "char_count": sizes.get("char_count"),
            "governance": gov_matches.get(path, []),
            "references": f["references"],
            "referenced_by": f["referenced_by"],
        })

    governance_index: dict[str, list[str]] = {}
    for path, govs in gov_matches.items():
        for gov in govs:
            governance_index.setdefault(gov, []).append(path)

    return {
        "files": files,
        "governance_index": governance_index,
        "total_lines": total_lines,
        "total_files": len(files),
    }
