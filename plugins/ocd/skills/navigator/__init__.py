"""Navigator operations.

Facade module — public interface for navigator functionality. Database
infrastructure lives in _db.py, filesystem scanning in _scanner.py.
Business logic lives here. Presentation lives in __main__.py.
"""

import fnmatch
import logging
import os
import sqlite3
from pathlib import Path

from ._db import get_connection, init_db, SCHEMA, MIGRATIONS, SEED_PATH  # noqa: F401
from ._frontmatter import parse_governance, scan_governance_dirs  # noqa: F401
from ._scanner import (  # noqa: F401
    scan_path,
    _walk_filesystem,
    _is_pattern,
    _compute_git_hash,
    _compute_file_metrics,
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
    sizes: bool = False,
) -> str:
    """List non-excluded file paths under target_path.

    Walks filesystem using navigator rules (exclude, traverse). Returns
    files only (not directories), sorted, one per line. If patterns
    provided, keeps only paths where basename matches any pattern via
    fnmatch. If excludes provided, removes paths where any path component
    matches any exclude pattern via fnmatch.

    When sizes=True, appends line_count and char_count columns per line.

    Returns empty string if no files match.
    """
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
            return "\n".join(files)

        # Fetch size data from database for matched files
        lines = []
        for f in files:
            row = conn.execute(
                "SELECT line_count, char_count FROM entries WHERE path = ?",
                (f,),
            ).fetchone()
            if row and row["line_count"] is not None:
                lines.append(f"{f}\t{row['line_count']}\t{row['char_count']}")
            else:
                lines.append(f)
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

        # Compute file metrics for files when setting description
        metrics = {"git_hash": None, "line_count": None, "char_count": None}
        if description is not None and not is_pat and entry_type == "file":
            metrics = _compute_file_metrics(entry_path)

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


# --- Governance ---


def governance_load(db_path: str, project_dir: str) -> str:
    """Load governance entries from frontmatter in rules and conventions.

    Scans .claude/rules/ and .claude/conventions/ for files with governance
    frontmatter (pattern + depends fields). Populates governance table with
    patterns and governs table with dependency relationships.

    Idempotent — safe to rerun. Uses INSERT OR REPLACE for governance and
    INSERT OR IGNORE for governs.
    """
    entries = scan_governance_dirs(Path(project_dir))

    conn = get_connection(db_path)
    try:
        for entry_path, entry in entries.items():
            # Ensure entry exists in entries table
            conn.execute(
                "INSERT OR IGNORE INTO entries (path, entry_type) VALUES (?, 'file')",
                (entry_path,),
            )

            # Rules (in /rules/) are auto-loaded; conventions are not
            auto_loaded = 1 if "/rules/" in entry_path else 0

            conn.execute(
                "INSERT OR REPLACE INTO governance (entry_path, pattern, auto_loaded) "
                "VALUES (?, ?, ?)",
                (entry_path, entry["pattern"], auto_loaded),
            )

        # Populate governs: flip depends to governs direction
        # If B depends on A, then A governs B
        for entry_path, entry in entries.items():
            for dep in entry["depends"]:
                conn.execute(
                    "INSERT OR IGNORE INTO governs (governor_path, governed_path) "
                    "VALUES (?, ?)",
                    (dep, entry_path),
                )

        conn.commit()

        gov_count = conn.execute("SELECT COUNT(*) as c FROM governance").fetchone()["c"]
        rel_count = conn.execute("SELECT COUNT(*) as c FROM governs").fetchone()["c"]
        return f"Loaded {gov_count} governance entries, {rel_count} governs relationships"
    finally:
        conn.close()


def list_governance(db_path: str) -> str:
    """List all governance entries with patterns and loading mode."""
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            "SELECT g.entry_path, g.pattern, g.auto_loaded "
            "FROM governance g ORDER BY g.entry_path"
        ).fetchall()

        if not rows:
            return "No governance entries."

        lines = []
        for row in rows:
            mode = "rule" if row["auto_loaded"] else "convention"
            lines.append(f"{row['entry_path']}  {row['pattern']}  [{mode}]")
        return "\n".join(lines)
    finally:
        conn.close()


def governance_for(db_path: str, file_paths: list[str]) -> str:
    """Find which governance entries govern given files.

    Matches via runtime pattern matching against governance patterns.
    Returns output compatible with conventions list-matching format.
    """
    conn = get_connection(db_path)
    try:
        # Load all governance entries for pattern matching
        gov_rows = conn.execute(
            "SELECT entry_path, pattern FROM governance ORDER BY entry_path"
        ).fetchall()

        # Load settings for line count tags
        warn_threshold = None
        fail_threshold = None
        warn_row = conn.execute(
            "SELECT value FROM config WHERE key = 'lines_warn_threshold'"
        ).fetchone()
        fail_row = conn.execute(
            "SELECT value FROM config WHERE key = 'lines_fail_threshold'"
        ).fetchone()
        if warn_row:
            warn_threshold = int(warn_row["value"])
        if fail_row:
            fail_threshold = int(fail_row["value"])

        # Match each file against governance patterns
        results: dict[str, list[str]] = {}
        for file_path in file_paths:
            basename = Path(file_path).name
            matches = []
            for gov in gov_rows:
                pattern = gov["pattern"]
                if fnmatch.fnmatch(basename, pattern) or fnmatch.fnmatch(file_path, pattern):
                    matches.append(gov["entry_path"])
            if matches:
                results[file_path] = sorted(matches)

        if not results:
            return "No governance matches."

        # Collect all unique criteria
        all_criteria = sorted({c for cs in results.values() for c in cs})

        # Format output
        lines = ["Criteria:"]
        for c in all_criteria:
            lines.append(f"  {c}")
        lines.append("")

        for file_path in file_paths:
            if file_path not in results:
                continue

            # Line count tag
            tag = ""
            if fail_threshold or warn_threshold:
                row = conn.execute(
                    "SELECT line_count FROM entries WHERE path = ?",
                    (file_path,),
                ).fetchone()
                if row and row["line_count"] is not None:
                    lc = row["line_count"]
                    if fail_threshold and lc > fail_threshold:
                        tag = f" [fail: {lc} lines]"
                    elif warn_threshold and lc > warn_threshold:
                        tag = f" [warn: {lc} lines]"

            lines.append(f"{file_path}{tag} follows:")
            for c in results[file_path]:
                lines.append(f"  {c}")

        return "\n".join(lines)
    finally:
        conn.close()


def governance_order(db_path: str) -> str:
    """Topological ordering of governance entries via governs relationships.

    Returns levels where level 0 has no governors, level N is governed
    only by levels 0..N-1. Uses Kahn's algorithm on governance-to-governance
    governs edges.
    """
    conn = get_connection(db_path)
    try:
        gov_paths = [
            row["entry_path"]
            for row in conn.execute("SELECT entry_path FROM governance").fetchall()
        ]

        if not gov_paths:
            return "No governance entries."

        gov_set = set(gov_paths)

        # Load governance-to-governance governs edges
        edges = conn.execute(
            "SELECT governor_path, governed_path FROM governs"
        ).fetchall()

        in_degree: dict[str, int] = {p: 0 for p in gov_paths}
        dependents: dict[str, list[str]] = {p: [] for p in gov_paths}

        for edge in edges:
            gov = edge["governor_path"]
            dep = edge["governed_path"]
            if gov in gov_set and dep in gov_set:
                in_degree[dep] += 1
                dependents[gov].append(dep)

        # Kahn's algorithm with level tracking
        levels: list[list[str]] = []
        current = sorted(p for p in in_degree if in_degree[p] == 0)

        while current:
            levels.append(current)
            next_level = []
            for node in current:
                for dep in dependents[node]:
                    in_degree[dep] -= 1
                    if in_degree[dep] == 0:
                        next_level.append(dep)
            current = sorted(set(next_level))

        remaining = [p for p in in_degree if in_degree[p] > 0]
        if remaining:
            return f"Cycle detected among: {', '.join(sorted(remaining))}"

        lines = []
        for i, level in enumerate(levels):
            lines.append(f"Level {i}:")
            for path in level:
                lines.append(f"  {path}")
        return "\n".join(lines)
    finally:
        conn.close()


def governance_graph(db_path: str) -> str:
    """Show governance-to-governance edges and root entries.

    Displays which governance entries govern which other governance entries,
    and which entries are roots (no governor). Complements governance-order
    which shows levels but not edges.
    """
    conn = get_connection(db_path)
    try:
        gov_paths = {
            row["entry_path"]
            for row in conn.execute("SELECT entry_path FROM governance").fetchall()
        }

        if not gov_paths:
            return "No governance entries."

        edges = conn.execute(
            "SELECT governor_path, governed_path FROM governs"
        ).fetchall()

        # Filter to governance-to-governance edges
        gov_edges: dict[str, list[str]] = {p: [] for p in gov_paths}
        governed_set: set[str] = set()
        for edge in edges:
            gov = edge["governor_path"]
            dep = edge["governed_path"]
            if gov in gov_paths and dep in gov_paths:
                gov_edges[gov].append(dep)
                governed_set.add(dep)

        roots = sorted(gov_paths - governed_set)

        lines = []
        if roots:
            lines.append(f"Roots ({len(roots)}):")
            for r in roots:
                lines.append(f"  {r}")
            lines.append("")

        lines.append(f"Edges ({sum(len(v) for v in gov_edges.values())}):")
        for gov in sorted(gov_edges):
            targets = sorted(gov_edges[gov])
            if targets:
                for t in targets:
                    lines.append(f"  {gov}  -->  {t}")

        # Leaf entries (govern nothing within governance)
        leaves = sorted(p for p in gov_paths if not gov_edges[p])
        if leaves:
            lines.append("")
            lines.append(f"Leaves ({len(leaves)}):")
            for l in leaves:
                lines.append(f"  {l}")

        return "\n".join(lines)
    finally:
        conn.close()


def get_unclassified(db_path: str) -> str:
    """Find file entries with no governance coverage.

    Returns file entries that match no governance pattern. Groups by
    file extension to surface which file types lack conventions.
    """
    conn = get_connection(db_path)
    try:
        gov_rows = conn.execute(
            "SELECT entry_path, pattern FROM governance"
        ).fetchall()

        if not gov_rows:
            return "No governance entries loaded."

        gov_paths = {r["entry_path"] for r in gov_rows}

        # Get all concrete file entries (not patterns, not directories, not governance entries)
        file_rows = conn.execute(
            "SELECT path FROM entries "
            "WHERE entry_type = 'file' AND path NOT LIKE '%*%' AND exclude = 0"
        ).fetchall()

        unclassified: list[str] = []
        for row in file_rows:
            file_path = row["path"]
            if file_path in gov_paths:
                continue
            basename = Path(file_path).name
            matched = False
            for gov in gov_rows:
                pattern = gov["pattern"]
                if fnmatch.fnmatch(basename, pattern) or fnmatch.fnmatch(file_path, pattern):
                    matched = True
                    break
            if not matched:
                unclassified.append(file_path)

        if not unclassified:
            return "All file entries have governance coverage."

        # Group by extension
        by_ext: dict[str, list[str]] = {}
        for path in sorted(unclassified):
            ext = Path(path).suffix or "(no extension)"
            by_ext.setdefault(ext, []).append(path)

        lines = [f"Unclassified: {len(unclassified)} files without governance coverage"]
        lines.append("")
        for ext in sorted(by_ext):
            lines.append(f"{ext} ({len(by_ext[ext])} files):")
            for path in by_ext[ext]:
                lines.append(f"  {path}")
        return "\n".join(lines)
    finally:
        conn.close()
