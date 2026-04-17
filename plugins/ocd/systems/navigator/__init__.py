"""Navigator operations.

Facade module — public interface for navigator functionality. Domain
modules: _db (database), _scanner (filesystem), _references (file
reference mapping), _skills (skill resolution).

All functions return structured data (dicts/lists). Formatting for
CLI display belongs in __main__.py. Presentation lives in __main__.py.
"""

import fnmatch
from pathlib import Path

import plugin

from ._db import *  # noqa: F401,F403
from ._scanner import *  # noqa: F401,F403
from ._scanner import _walk_filesystem, _compute_file_metrics  # used by facade
from ._references import *  # noqa: F401,F403
from ._skills import *  # noqa: F401,F403

# Cross-package: scope_analyze composites governance matching into its result,
# so the facade imports governance_match from the governance library.
from systems.governance import governance_match


def _ensure_scanned(db_path: str) -> None:
    """Populate the paths table from disk before a read or write.

    Every facade function that touches the paths table calls this first —
    navigator owns its own population, callers never have to scan before
    invoking a navigator function.
    """
    scan_path(db_path)


def paths_get(db_path: str, paths: str | list[str]) -> dict:
    """Retrieve path details for one or more paths.

    Files return type, purpose, stale flag. Directories return entry
    info plus children. Single path returns one dict; multiple paths
    return {"paths": [dict, ...]}.
    """
    _ensure_scanned(db_path)
    if isinstance(paths, str):
        return _paths_get_single(db_path, paths)

    return {"paths": [_paths_get_single(db_path, p) for p in paths]}


def _paths_get_single(db_path: str, target_path: str) -> dict:
    """Retrieve path details for a single path."""
    target_path = target_path.rstrip("/")
    if target_path == ".":
        target_path = ""

    conn = get_connection(db_path)
    try:
        row = conn.execute(
            "SELECT * FROM paths WHERE path = ?", (target_path,)
        ).fetchone()

        def _row_dict(r) -> dict:
            return {
                "path": r["path"] or ".",
                "type": r["entry_type"],
                "purpose": r["purpose"],
                "stale": bool(r["stale"]),
            }

        if row and row["entry_type"] == "file":
            return _row_dict(row)

        result = {
            "path": (target_path + "/") if target_path else "./",
            "type": "directory",
            "purpose": row["purpose"] if row else None,
            "stale": bool(row["stale"]) if row else False,
            "children": [],
        }

        children = conn.execute(
            "SELECT * FROM paths WHERE parent_path = ? "
            "AND exclude = 0 "
            "ORDER BY "
            "CASE entry_type WHEN 'directory' THEN 0 ELSE 1 END, path",
            (target_path,),
        ).fetchall()

        for child in children:
            result["children"].append(_row_dict(child))

        if not row and not children:
            result["children"] = None  # signals "no paths"

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
        disk_paths = _walk_filesystem(conn, target_path)

        files = sorted(p for p, t in disk_paths.items() if t == "file")

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
                "SELECT line_count, char_count FROM paths WHERE path = ?",
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
    """Return deepest directory with paths needing purpose description.

    Returns progress info and directory listing. When no work remains,
    returns {"done": True}.
    """
    _ensure_scanned(db_path)
    conn = get_connection(db_path)
    try:
        work_rows = conn.execute(
            "SELECT path, parent_path, entry_type FROM paths "
            "WHERE purpose IS NULL OR stale = 1"
        ).fetchall()

        if not work_rows:
            return {"done": True}

        work_dirs = set()
        for row in work_rows:
            if row["entry_type"] == "directory":
                work_dirs.add(row["path"] if row["path"] is not None else "")
            else:
                work_dirs.add(row["parent_path"] if row["parent_path"] is not None else "")

        deepest = max(work_dirs, key=lambda p: p.count("/") if p else -1)

        return {
            "done": False,
            "remaining": len(work_rows),
            "directories": len(work_dirs),
            "target": deepest,
            "listing": paths_get(db_path, deepest),
        }
    finally:
        conn.close()


def paths_upsert(
    db_path: str,
    entry_path: str,
    purpose: str | None = None,
    exclude: int | None = None,
    traverse: int | None = None,
) -> dict:
    """Create or update a path. Returns status dict.

    Only accepts concrete paths (files and directories), not glob
    patterns. Patterns are declared in per-system paths.csv files and
    aggregated into path_patterns by navigator on scan.
    """
    _ensure_scanned(db_path)
    entry_path = entry_path.rstrip("/")
    if entry_path == ".":
        entry_path = ""

    if "*" in entry_path:
        raise ValueError(
            f"paths_upsert does not accept glob patterns: {entry_path!r}. "
            "Patterns are declared in per-system paths.csv files."
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
            "SELECT * FROM paths WHERE path = ?", (entry_path,)
        ).fetchone()

        metrics = {"git_hash": None, "line_count": None, "char_count": None}
        if purpose is not None and entry_type == "file":
            metrics = _compute_file_metrics(plugin.get_project_dir() / entry_path)

        display = entry_path if entry_path else "."

        if existing:
            updates = []
            params: list = []
            if purpose is not None:
                updates.append("purpose = ?")
                params.append(purpose)
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
                f"UPDATE paths SET {', '.join(updates)} WHERE path = ?",
                params,
            )
            conn.commit()
            return {"action": "updated", "path": display}
        else:
            conn.execute(
                "INSERT INTO paths "
                "(path, parent_path, entry_type, exclude, traverse, purpose, git_hash, line_count, char_count) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    entry_path,
                    parent_path,
                    entry_type,
                    exclude if exclude is not None else 0,
                    traverse if traverse is not None else 1,
                    purpose,
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
    mode: str = "single",
) -> dict:
    """Remove paths. Returns status dict.

    Modes:
        single    — remove one path by path (default)
        recursive — remove directory and all children
        all       — remove every concrete path (path_patterns table untouched)
    """
    if mode not in ("single", "recursive", "all"):
        raise ValueError(
            f"paths_remove: mode must be one of 'single', 'recursive', 'all'; got {mode!r}"
        )

    _ensure_scanned(db_path)
    conn = get_connection(db_path)
    try:
        if mode == "all":
            result = conn.execute("DELETE FROM paths")
            conn.commit()
            return {"action": "removed_all", "count": result.rowcount}

        entry_path = entry_path.rstrip("/")

        if mode == "recursive":
            existing = conn.execute(
                "SELECT entry_type FROM paths WHERE path = ?", (entry_path,)
            ).fetchone()
            if existing and existing["entry_type"] == "file":
                return {"action": "error", "message": "recursive mode not valid for file paths"}
            result = conn.execute(
                "DELETE FROM paths WHERE path = ? OR path LIKE ?",
                (entry_path, entry_path + "/%"),
            )
            conn.commit()
            if result.rowcount == 0:
                return {"action": "not_found", "path": entry_path}
            return {"action": "removed_recursive", "path": entry_path, "count": result.rowcount}

        # mode == "single"
        result = conn.execute(
            "DELETE FROM paths WHERE path = ?", (entry_path,)
        )
        conn.commit()
        if result.rowcount == 0:
            return {"action": "not_found", "path": entry_path}
        return {"action": "removed", "path": entry_path}
    finally:
        conn.close()


def paths_search(db_path: str, pattern: str) -> dict:
    """Search path purposes by pattern."""
    _ensure_scanned(db_path)
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            "SELECT path, entry_type, purpose FROM paths "
            "WHERE purpose LIKE ? "
            "ORDER BY path",
            (f"%{pattern}%",),
        ).fetchall()

        return {
            "pattern": pattern,
            "results": [
                {
                    "path": row["path"] if row["path"] else ".",
                    "type": row["entry_type"],
                    "purpose": row["purpose"],
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
                "SELECT line_count, char_count FROM paths WHERE path = ?",
                (file_path,),
            ).fetchone()
            if row:
                size_map[file_path] = {
                    "line_count": row["line_count"],
                    "char_count": row["char_count"],
                }
    finally:
        conn.close()

    gov_result = governance_match(all_paths)
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
