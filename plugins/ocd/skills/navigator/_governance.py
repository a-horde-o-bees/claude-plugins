"""Governance operations.

Governance loading, matching, ordering, and analysis. Operates on the
governance and governs tables in the navigator database.

All functions return structured data (dicts/lists). Formatting for
CLI display belongs in __main__.py.
"""

from __future__ import annotations

from pathlib import Path

from ._db import get_connection
from ._frontmatter import matches_pattern, normalize_patterns, scan_governance_dirs


def governance_load(db_path: str, project_dir: str) -> dict:
    """Load governance entries from frontmatter in rules and conventions.

    Idempotent — safe to rerun.
    """
    entries = scan_governance_dirs(Path(project_dir))

    conn = get_connection(db_path)
    try:
        for entry_path, entry in entries.items():
            conn.execute(
                "INSERT OR IGNORE INTO entries (path, entry_type) VALUES (?, 'file')",
                (entry_path,),
            )
            auto_loaded = 1 if "/rules/" in entry_path else 0
            conn.execute(
                "INSERT OR REPLACE INTO governance (entry_path, matches, excludes, auto_loaded) "
                "VALUES (?, ?, ?, ?)",
                (entry_path, entry["matches"], entry.get("excludes"), auto_loaded),
            )

        for entry_path, entry in entries.items():
            for dep in entry["governed_by"]:
                conn.execute(
                    "INSERT OR IGNORE INTO governs (governor_path, governed_path) "
                    "VALUES (?, ?)",
                    (dep, entry_path),
                )

        conn.commit()

        gov_count = conn.execute("SELECT COUNT(*) as c FROM governance").fetchone()["c"]
        rel_count = conn.execute("SELECT COUNT(*) as c FROM governs").fetchone()["c"]
        return {
            "governance_entries": gov_count,
            "governs_relationships": rel_count,
        }
    finally:
        conn.close()


def governance_list(db_path: str) -> list[dict]:
    """List all governance entries with patterns and loading mode."""
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            "SELECT g.entry_path, g.matches, g.excludes, g.auto_loaded "
            "FROM governance g ORDER BY g.entry_path"
        ).fetchall()

        result = []
        for row in rows:
            entry = {
                "path": row["entry_path"],
                "matches": row["matches"],
                "mode": "rule" if row["auto_loaded"] else "convention",
            }
            if row["excludes"]:
                entry["excludes"] = row["excludes"]
            result.append(entry)
        return result
    finally:
        conn.close()


def governance_match(db_path: str, file_paths: list[str], include_rules: bool = False) -> dict:
    """Match files against governance patterns.

    By default returns only conventions (on-demand) since rules are always
    loaded into agent context. Set include_rules=True for governance
    evaluation where rules themselves are the evaluation target.
    """
    conn = get_connection(db_path)
    try:
        gov_rows = conn.execute(
            "SELECT entry_path, matches, excludes, auto_loaded FROM governance ORDER BY entry_path"
        ).fetchall()

        result_matches: dict[str, list[str]] = {}
        for file_path in file_paths:
            file_matches = []
            for gov in gov_rows:
                if not include_rules and gov["auto_loaded"]:
                    continue
                include_patterns = normalize_patterns(gov["matches"])
                included = any(
                    matches_pattern(file_path, p) for p in include_patterns
                )
                if not included:
                    continue
                if gov["excludes"]:
                    exclude_patterns = normalize_patterns(gov["excludes"])
                    excluded = any(
                        matches_pattern(file_path, p) for p in exclude_patterns
                    )
                    if excluded:
                        continue
                file_matches.append(gov["entry_path"])
            if file_matches:
                result_matches[file_path] = sorted(file_matches)

        conventions = sorted({c for cs in result_matches.values() for c in cs})

        return {
            "matches": result_matches,
            "conventions": conventions,
        }
    finally:
        conn.close()


def governance_order(db_path: str) -> dict:
    """Topological ordering of governance entries via governs relationships.

    Returns levels where level 0 has no governors, level N is governed
    only by levels 0..N-1. Uses Kahn's algorithm.
    """
    conn = get_connection(db_path)
    try:
        gov_paths = [
            row["entry_path"]
            for row in conn.execute("SELECT entry_path FROM governance").fetchall()
        ]

        if not gov_paths:
            return {"levels": [], "cycle": None}

        gov_set = set(gov_paths)

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

        remaining = sorted(p for p in in_degree if in_degree[p] > 0)

        return {
            "levels": [{"level": i, "entries": level} for i, level in enumerate(levels)],
            "cycle": remaining if remaining else None,
        }
    finally:
        conn.close()


def governance_graph(db_path: str) -> dict:
    """Governance dependency edges, roots, and leaves."""
    conn = get_connection(db_path)
    try:
        gov_paths = {
            row["entry_path"]
            for row in conn.execute("SELECT entry_path FROM governance").fetchall()
        }

        if not gov_paths:
            return {"roots": [], "edges": [], "leaves": []}

        edges = conn.execute(
            "SELECT governor_path, governed_path FROM governs"
        ).fetchall()

        gov_edges: dict[str, list[str]] = {p: [] for p in gov_paths}
        governed_set: set[str] = set()
        for edge in edges:
            gov = edge["governor_path"]
            dep = edge["governed_path"]
            if gov in gov_paths and dep in gov_paths:
                gov_edges[gov].append(dep)
                governed_set.add(dep)

        roots = sorted(gov_paths - governed_set)
        leaves = sorted(p for p in gov_paths if not gov_edges[p])

        edge_list = []
        for gov in sorted(gov_edges):
            for target in sorted(gov_edges[gov]):
                edge_list.append({"from": gov, "to": target})

        return {
            "roots": roots,
            "edges": edge_list,
            "leaves": leaves,
        }
    finally:
        conn.close()


def governance_unclassified(db_path: str) -> dict:
    """Find file entries with no governance coverage, grouped by extension."""
    conn = get_connection(db_path)
    try:
        gov_rows = conn.execute(
            "SELECT entry_path, matches, excludes FROM governance"
        ).fetchall()

        if not gov_rows:
            return {"total": 0, "by_extension": {}}

        gov_paths = {r["entry_path"] for r in gov_rows}

        file_rows = conn.execute(
            "SELECT path FROM entries "
            "WHERE entry_type = 'file' AND exclude = 0"
        ).fetchall()

        unclassified: list[str] = []
        for row in file_rows:
            file_path = row["path"]
            if file_path in gov_paths:
                continue
            matched = False
            for gov in gov_rows:
                include_patterns = normalize_patterns(gov["matches"])
                included = any(
                    matches_pattern(file_path, p) for p in include_patterns
                )
                if not included:
                    continue
                if gov["excludes"]:
                    exclude_patterns = normalize_patterns(gov["excludes"])
                    excluded = any(
                        matches_pattern(file_path, p) for p in exclude_patterns
                    )
                    if excluded:
                        continue
                matched = True
                break
            if not matched:
                unclassified.append(file_path)

        by_ext: dict[str, list[str]] = {}
        for path in sorted(unclassified):
            ext = Path(path).suffix or "(no extension)"
            by_ext.setdefault(ext, []).append(path)

        return {
            "total": len(unclassified),
            "by_extension": by_ext,
        }
    finally:
        conn.close()
