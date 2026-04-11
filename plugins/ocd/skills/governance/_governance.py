"""Governance operations.

Governance loading, matching, and analysis. Owns the conventions and
rules tables, the convention include/exclude junctions, and the
governance_depends_on dependency graph. Independent of navigator —
governance has its own database and its own lifecycle.

Governance data self-refreshes: query functions check staleness via
git_hash comparison and reload from disk when stale. Each governance
file owns only the relationships for which it is the source; removal
of a file cleans up its outgoing edges but leaves incoming references
in place so they surface as dangling references in governance_order.

All functions return structured data (dicts/lists). Formatting for
CLI display belongs in __main__.py.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import plugin

from ._db import get_connection
from ._frontmatter import normalize_patterns, parse_governance


def _git_hash(file_path: Path) -> str | None:
    """Compute git-compatible blob hash for a file."""
    try:
        data = file_path.read_bytes()
    except (OSError, IsADirectoryError):
        return None
    header = f"blob {len(data)}\0".encode()
    return hashlib.sha1(header + data).hexdigest()


def _scan_disk_paths() -> tuple[set[str], set[str]]:
    """Scan governance directories and return (rule_paths, convention_paths).

    Paths are project-relative strings, anchored on plugin.get_project_dir().
    """
    project_dir = plugin.get_project_dir()
    rules_dir = project_dir / ".claude" / "rules"
    conv_dir = project_dir / ".claude" / "conventions"

    rule_paths: set[str] = set()
    conv_paths: set[str] = set()
    for scan_dir, target_set in ((rules_dir, rule_paths), (conv_dir, conv_paths)):
        if scan_dir.is_dir():
            for md_file in scan_dir.glob("*.md"):
                if md_file.is_file():
                    target_set.add(str(md_file.relative_to(project_dir)))

    return rule_paths, conv_paths


def _ensure_current(db_path: str) -> None:
    """Refresh governance from disk before queries."""
    governance_load(db_path)


def _delete_governance_for_file(conn, path: str) -> None:
    """Remove all governance state owned by a single file.

    Removes the entry from rules and conventions and deletes its outgoing
    dependency edges. Does NOT delete incoming edges — those represent
    other files claiming this file as a governor. If those other files
    haven't been updated, their stale claims remain in the junction
    table and surface as dangling references in governance_order.
    """
    conn.execute("DELETE FROM rules WHERE entry_path = ?", (path,))
    conn.execute("DELETE FROM conventions WHERE entry_path = ?", (path,))
    # CASCADE on convention_includes/convention_excludes clears pattern rows
    conn.execute(
        "DELETE FROM governance_depends_on WHERE entry_path = ?", (path,)
    )


def _load_governance_for_file(
    conn, path: str, current_hash: str, is_rule: bool
) -> None:
    """Rebuild all governance state owned by a single file.

    Idempotent. Clears the file's existing rows in rules/conventions,
    convention_includes/convention_excludes, and outgoing edges, then
    inserts fresh state from the file's current frontmatter. Caller has
    determined this file needs to be loaded — either it's new or its
    hash differs from what's stored.

    Each governance file owns only its own outgoing edges. Incoming
    edges (Z → this file) are not touched here; they belong to Z and
    are managed when Z is loaded.
    """
    project_dir = plugin.get_project_dir()
    entry = parse_governance(project_dir / path)

    _delete_governance_for_file(conn, path)

    if entry is None:
        return

    if is_rule:
        conn.execute(
            "INSERT INTO rules (entry_path, git_hash) VALUES (?, ?)",
            (path, current_hash),
        )
    else:
        conn.execute(
            "INSERT INTO conventions (entry_path, includes, excludes, git_hash) "
            "VALUES (?, ?, ?, ?)",
            (path, entry["includes"], entry.get("excludes"), current_hash),
        )
        for pattern in normalize_patterns(entry["includes"]):
            conn.execute(
                "INSERT INTO convention_includes (entry_path, pattern) "
                "VALUES (?, ?)",
                (path, pattern),
            )
        if entry.get("excludes"):
            for pattern in normalize_patterns(entry["excludes"]):
                conn.execute(
                    "INSERT INTO convention_excludes (entry_path, pattern) "
                    "VALUES (?, ?)",
                    (path, pattern),
                )

    for target in entry.get("governed_by", []):
        conn.execute(
            "INSERT INTO governance_depends_on (entry_path, depends_on_path) "
            "VALUES (?, ?)",
            (path, target),
        )


def governance_load(db_path: str) -> dict:
    """Incrementally reconcile governance state against disk.

    Hash-driven: each file's database state is rebuilt only when the file
    is new or its content has changed. Files removed from disk are deleted
    along with their outgoing dependency edges. Incoming edges from other
    files that still claim a deleted file as a governor are preserved as
    stale references — governance_order surfaces them as dangling.

    Safe to call before every query.
    """
    project_dir = plugin.get_project_dir()
    rule_paths, conv_paths = _scan_disk_paths()
    is_rule_map = {p: True for p in rule_paths} | {p: False for p in conv_paths}
    all_disk_paths = rule_paths | conv_paths

    conn = get_connection(db_path)
    try:
        db_hashes: dict[str, str | None] = {}
        for row in conn.execute(
            "SELECT entry_path, git_hash FROM rules"
        ).fetchall():
            db_hashes[row["entry_path"]] = row["git_hash"]
        for row in conn.execute(
            "SELECT entry_path, git_hash FROM conventions"
        ).fetchall():
            db_hashes[row["entry_path"]] = row["git_hash"]

        for path in sorted(all_disk_paths):
            current_hash = _git_hash(project_dir / path)
            if current_hash is None:
                continue
            if db_hashes.get(path) == current_hash:
                continue
            _load_governance_for_file(
                conn, path, current_hash, is_rule_map[path]
            )

        for removed in db_hashes.keys() - all_disk_paths:
            _delete_governance_for_file(conn, removed)

        conn.commit()

        rule_count = conn.execute(
            "SELECT COUNT(*) as c FROM rules"
        ).fetchone()["c"]
        conv_count = conn.execute(
            "SELECT COUNT(*) as c FROM conventions"
        ).fetchone()["c"]
        return {"governance_entries": rule_count + conv_count}
    finally:
        conn.close()


def governance_list(db_path: str) -> list[dict]:
    """List all governance entries with patterns and loading mode."""
    _ensure_current(db_path)
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            "SELECT entry_path, includes, excludes, 'convention' as mode "
            "FROM conventions "
            "UNION ALL "
            "SELECT entry_path, '*' as includes, NULL as excludes, 'rule' as mode "
            "FROM rules "
            "ORDER BY entry_path"
        ).fetchall()

        result = []
        for row in rows:
            entry = {
                "path": row["entry_path"],
                "includes": row["includes"],
                "mode": row["mode"],
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

    Uses path_match() custom SQL function for matching — same semantics
    as matches_pattern (basename, ** prefix, full-path modes).
    """
    _ensure_current(db_path)
    conn = get_connection(db_path)
    try:
        placeholders = ", ".join("(?)" for _ in file_paths)
        params: list[str] = list(file_paths)

        query = f"""
            WITH files(path) AS (VALUES {placeholders})
            SELECT DISTINCT f.path AS file_path, ci.entry_path
            FROM files f
            JOIN convention_includes ci ON path_match(f.path, ci.pattern)
            LEFT JOIN convention_excludes ce
                ON ci.entry_path = ce.entry_path AND path_match(f.path, ce.pattern)
            WHERE ce.entry_path IS NULL
            ORDER BY f.path, ci.entry_path
        """

        rows = conn.execute(query, params).fetchall()

        result_matches: dict[str, list[str]] = {}
        for row in rows:
            result_matches.setdefault(row["file_path"], []).append(row["entry_path"])

        if include_rules:
            rule_rows = conn.execute("SELECT entry_path FROM rules").fetchall()
            rule_paths = [r["entry_path"] for r in rule_rows]
            for fp in file_paths:
                for rp in rule_paths:
                    result_matches.setdefault(fp, []).append(rp)

        conventions = sorted({c for cs in result_matches.values() for c in cs})

        return {
            "matches": result_matches,
            "conventions": conventions,
        }
    finally:
        conn.close()


def _tarjan_scc(nodes: list[str], edges: dict[str, list[str]]) -> list[list[str]]:
    """Tarjan's strongly-connected components algorithm.

    Returns SCCs in reverse topological order: components with no outgoing
    edges to other components come first. For governance dependencies where
    A depends on B (A → B), this yields foundation-first ordering suitable
    for root-first traversal.

    Reference: Tarjan, R. (1972). "Depth-first search and linear graph
    algorithms." SIAM Journal on Computing 1(2), 146–160.
    """
    index_counter = [0]
    stack: list[str] = []
    lowlinks: dict[str, int] = {}
    index: dict[str, int] = {}
    on_stack: set[str] = set()
    sccs: list[list[str]] = []

    def strongconnect(node: str) -> None:
        index[node] = index_counter[0]
        lowlinks[node] = index_counter[0]
        index_counter[0] += 1
        stack.append(node)
        on_stack.add(node)

        for successor in edges.get(node, []):
            if successor not in index:
                strongconnect(successor)
                lowlinks[node] = min(lowlinks[node], lowlinks[successor])
            elif successor in on_stack:
                lowlinks[node] = min(lowlinks[node], index[successor])

        if lowlinks[node] == index[node]:
            component: list[str] = []
            while True:
                w = stack.pop()
                on_stack.remove(w)
                component.append(w)
                if w == node:
                    break
            sccs.append(sorted(component))

    for node in sorted(nodes):
        if node not in index:
            strongconnect(node)

    return sccs


def governance_order(db_path: str) -> dict:
    """Compute level-grouped governance ordering for root-first traversal.

    Loads all governance entries and their declared dependencies,
    detects dangling references, then groups entries into levels:

    1. Tarjan's SCC algorithm collapses cycles (mutual or larger) into
       single components.
    2. The SCC DAG is layered by longest dependency depth — every
       component is placed in level max(level of its dependency
       components) + 1, or level 0 if it has no dependencies.

    Independent foundations occupy the same level. Components in a
    cycle occupy the same level. Each level is fully resolvable
    against everything in earlier levels.

    When dangling references exist (governed_by targets that are not
    themselves governance entries), levels is empty and dangling
    carries the offending edges. Otherwise dangling is empty and
    levels contains every governance entry.

    Returns {levels: [[{path, governors}, ...], ...], dangling: [...]}.
    """
    _ensure_current(db_path)
    conn = get_connection(db_path)
    try:
        entry_rows = conn.execute(
            "SELECT entry_path FROM conventions "
            "UNION ALL "
            "SELECT entry_path FROM rules"
        ).fetchall()
        entries = {row["entry_path"] for row in entry_rows}

        edge_rows = conn.execute(
            "SELECT entry_path, depends_on_path FROM governance_depends_on"
        ).fetchall()

        edges: dict[str, list[str]] = {}
        governors: dict[str, list[str]] = {}
        dangling: list[dict] = []
        for row in edge_rows:
            src = row["entry_path"]
            dst = row["depends_on_path"]
            if dst not in entries:
                dangling.append({"entry_path": src, "missing": dst})
                continue
            edges.setdefault(src, []).append(dst)
            governors.setdefault(src, []).append(dst)

        if dangling:
            return {"levels": [], "dangling": dangling}

        sccs = _tarjan_scc(sorted(entries), edges)
        scc_index = {node: i for i, scc in enumerate(sccs) for node in scc}

        # SCC DAG: scc_deps[i] = set of SCCs that SCC i depends on
        scc_deps: list[set[int]] = [set() for _ in sccs]
        for src, dsts in edges.items():
            src_scc = scc_index[src]
            for dst in dsts:
                dst_scc = scc_index[dst]
                if src_scc != dst_scc:
                    scc_deps[src_scc].add(dst_scc)

        # Tarjan emits SCCs in reverse topological order: dependencies
        # before dependents. Walking in that order lets each SCC's level
        # resolve from already-computed dependency levels.
        scc_level = [0] * len(sccs)
        for i in range(len(sccs)):
            if scc_deps[i]:
                scc_level[i] = max(scc_level[d] for d in scc_deps[i]) + 1

        levels_map: dict[int, list[int]] = {}
        for i, lvl in enumerate(scc_level):
            levels_map.setdefault(lvl, []).append(i)

        levels = []
        for lvl in sorted(levels_map.keys()):
            level_entries = []
            for scc_i in sorted(levels_map[lvl]):
                for path in sccs[scc_i]:
                    level_entries.append(
                        {
                            "path": path,
                            "governors": sorted(governors.get(path, [])),
                        }
                    )
            levels.append(level_entries)

        return {"levels": levels, "dangling": []}
    finally:
        conn.close()


