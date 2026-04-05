"""Governance operations.

Governance loading, matching, ordering, and analysis. Operates on the
governance and governs tables in the navigator database.
"""

from __future__ import annotations

import fnmatch
from pathlib import Path

from ._db import get_connection
from ._frontmatter import normalize_patterns, scan_governance_dirs


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


def match_governance(db_path: str, file_paths: list[str]) -> dict[str, list[str]]:
    """Match files against governance patterns. Returns raw mapping.

    Returns dict mapping file_path -> [governance_entry_path, ...] for
    files that have at least one match. Files with no matches are omitted.
    """
    conn = get_connection(db_path)
    try:
        gov_rows = conn.execute(
            "SELECT entry_path, pattern FROM governance ORDER BY entry_path"
        ).fetchall()

        results: dict[str, list[str]] = {}
        for file_path in file_paths:
            basename = Path(file_path).name
            matches = []
            for gov in gov_rows:
                patterns = normalize_patterns(gov["pattern"])
                if any(
                    fnmatch.fnmatch(basename, p) or fnmatch.fnmatch(file_path, p)
                    for p in patterns
                ):
                    matches.append(gov["entry_path"])
            if matches:
                results[file_path] = sorted(matches)

        return results
    finally:
        conn.close()


def governance_for(db_path: str, file_paths: list[str]) -> str:
    """Find which governance entries govern given files.

    Matches via runtime pattern matching against governance patterns.
    Returns output compatible with conventions list-matching format.
    """
    results = match_governance(db_path, file_paths)

    if not results:
        return "No governance matches."

    conn = get_connection(db_path)
    try:
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
                patterns = normalize_patterns(gov["pattern"])
                if any(
                    fnmatch.fnmatch(basename, p) or fnmatch.fnmatch(file_path, p)
                    for p in patterns
                ):
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
