"""Governance operations.

Governance matching, listing, and dependency ordering. Reads rules and
conventions directly from disk — no database, no caching. Convention
files in .claude/conventions/ carry frontmatter with include/exclude
patterns and governed_by dependencies; rule files in .claude/rules/
are always-on context with no pattern matching.

All functions resolve project directory internally via plugin framework.
All functions return structured data (dicts/lists). Formatting for
CLI display belongs in cli.py.
"""

from __future__ import annotations

from pathlib import Path

import plugin

from ._frontmatter import matches_pattern, normalize_patterns, parse_governance


def _scan_governance_files() -> tuple[list[Path], list[Path]]:
    """Scan governance directories and return (rule_files, convention_files)."""
    project_dir = plugin.get_project_dir()
    rules_dir = project_dir / ".claude" / "rules"
    conv_dir = project_dir / ".claude" / "conventions"

    rule_files = sorted(rules_dir.rglob("*.md")) if rules_dir.is_dir() else []
    conv_files = sorted(conv_dir.rglob("*.md")) if conv_dir.is_dir() else []

    return (
        [f for f in rule_files if f.is_file()],
        [f for f in conv_files if f.is_file()],
    )


def governance_match(file_paths: list[str], include_rules: bool = False) -> dict:
    """Match files against governance patterns.

    By default returns only conventions (on-demand) since rules are always
    loaded into agent context. Set include_rules=True for governance
    evaluation where rules themselves are the evaluation target.

    Scans convention files from disk on every call — no caching.
    """
    project_dir = plugin.get_project_dir()
    rule_files, conv_files = _scan_governance_files()

    result_matches: dict[str, list[str]] = {}

    for conv_path in conv_files:
        entry = parse_governance(conv_path)
        if not entry:
            continue
        entry_rel = str(conv_path.relative_to(project_dir))
        includes = normalize_patterns(entry["includes"])
        excludes = (
            normalize_patterns(entry["excludes"]) if entry.get("excludes") else []
        )

        for fp in file_paths:
            matched = any(matches_pattern(fp, p) for p in includes)
            excluded = any(matches_pattern(fp, p) for p in excludes)
            if matched and not excluded:
                result_matches.setdefault(fp, []).append(entry_rel)

    if include_rules:
        rule_paths = [str(f.relative_to(project_dir)) for f in rule_files]
        for fp in file_paths:
            for rp in rule_paths:
                result_matches.setdefault(fp, []).append(rp)

    conventions = sorted({c for cs in result_matches.values() for c in cs})

    return {
        "matches": result_matches,
        "conventions": conventions,
    }


def governance_list() -> list[dict]:
    """List all governance entries with patterns and loading mode."""
    project_dir = plugin.get_project_dir()
    rule_files, conv_files = _scan_governance_files()

    result = []

    for rule_path in rule_files:
        result.append({
            "path": str(rule_path.relative_to(project_dir)),
            "includes": "*",
            "mode": "rule",
        })

    for conv_path in conv_files:
        entry = parse_governance(conv_path)
        if not entry:
            continue
        item: dict = {
            "path": str(conv_path.relative_to(project_dir)),
            "includes": entry["includes"],
            "mode": "convention",
        }
        if entry.get("excludes"):
            item["excludes"] = entry["excludes"]
        result.append(item)

    return sorted(result, key=lambda e: e["path"])


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


def governance_order() -> dict:
    """Compute level-grouped governance ordering for root-first traversal.

    Scans all governance files and their declared dependencies,
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
    project_dir = plugin.get_project_dir()
    rule_files, conv_files = _scan_governance_files()

    entries: set[str] = set()
    edges: dict[str, list[str]] = {}
    governors: dict[str, list[str]] = {}

    for file_path in rule_files + conv_files:
        entry_path = str(file_path.relative_to(project_dir))
        entries.add(entry_path)

        entry = parse_governance(file_path)
        if entry and entry.get("governed_by"):
            for target in entry["governed_by"]:
                edges.setdefault(entry_path, []).append(target)
                governors.setdefault(entry_path, []).append(target)

    dangling: list[dict] = []
    for src, dsts in edges.items():
        for dst in dsts:
            if dst not in entries:
                dangling.append({"entry_path": src, "missing": dst})

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
