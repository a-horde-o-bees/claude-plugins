"""Reference mapping.

Builds a dependency DAG from file references. Each file type has a
parser that extracts references to other files. BFS traversal follows
references recursively, deduplicating and detecting cycles.

Parsers:
  - SKILL.md: backtick-wrapped relative paths in workflow steps
  - Governance (.claude/rules/, .claude/conventions/): depends: frontmatter
  - Component _*.md: leaf nodes (no outward references)
"""

from __future__ import annotations

import re
from collections import deque
from pathlib import Path

from ._frontmatter import parse_governance


# --- Parsers ---


def _parse_skill_refs(file_path: str) -> list[str]:
    """Extract file references from a SKILL.md.

    Finds backtick-wrapped paths in workflow steps that look like
    relative file references: contain '/' and end in a known extension.
    Skips fenced code blocks. Resolves relative to the skill directory.
    """
    try:
        content = Path(file_path).read_text()
    except (FileNotFoundError, PermissionError, OSError):
        return []

    skill_dir = Path(file_path).parent
    refs: list[str] = []
    in_code_block = False

    # Match backtick-wrapped paths: `path/to/file.ext`
    backtick_path = re.compile(
        r'`([^`]+/[^`]+\.(?:md|py|sh|json|csv))`'
    )

    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        for match in backtick_path.finditer(line):
            ref = match.group(1)
            # Skip paths with ${} variable substitution — CLI scripts, not file refs
            if "${" in ref:
                continue
            # Resolve relative to skill directory
            resolved = skill_dir / ref
            if resolved.exists():
                refs.append(str(resolved.resolve()))

    return refs


def _parse_governance_refs(file_path: str) -> list[str]:
    """Extract depends: references from governance frontmatter.

    Returns project-relative paths from the depends field. These are
    already project-relative in the frontmatter.
    """
    parsed = parse_governance(Path(file_path))
    if parsed is None:
        return []
    return parsed.get("depends", [])


def _classify_and_parse(file_path: str) -> list[str]:
    """Dispatch to the appropriate parser based on file type.

    Returns list of referenced file paths (resolved or project-relative).
    """
    p = Path(file_path)

    # Component files (_*.md) are leaf nodes
    if p.name.startswith("_") and p.suffix == ".md":
        return []

    # SKILL.md files
    if p.name == "SKILL.md":
        return _parse_skill_refs(file_path)

    # Governance files (rules and conventions)
    if ".claude/rules/" in file_path or ".claude/conventions/" in file_path:
        return _parse_governance_refs(file_path)

    return []


# --- DAG Builder ---


def references_map(paths: list[str], max_depth: int = 20) -> dict:
    """Build reference DAG from starting paths via BFS.

    Follows file references recursively, deduplicating as it goes.
    Returns structured result with files, edges, and metadata.

    Args:
        paths: Starting file paths (project-relative or absolute).
        max_depth: Maximum traversal depth to prevent runaway recursion.

    Returns:
        {
            "files": [{"path": str, "depth": int, "references": [...], "referenced_by": [...]}],
            "roots": [...],
            "total_files": int
        }
    """
    # Normalize starting paths
    roots = []
    for p in paths:
        resolved = str(Path(p).resolve()) if Path(p).is_absolute() else p
        roots.append(resolved)

    # BFS traversal
    visited: dict[str, int] = {}  # path -> depth
    edges: dict[str, list[str]] = {}  # from -> [to]
    reverse_edges: dict[str, list[str]] = {}  # to -> [from]
    queue: deque[tuple[str, int]] = deque()

    for root in roots:
        if root not in visited:
            visited[root] = 0
            edges[root] = []
            reverse_edges.setdefault(root, [])
            queue.append((root, 0))

    while queue:
        current, depth = queue.popleft()
        if depth >= max_depth:
            continue

        refs = _classify_and_parse(current)
        for ref in refs:
            # Normalize reference path
            ref_resolved = str(Path(ref).resolve()) if Path(ref).is_absolute() else ref

            # Record edge
            edges.setdefault(current, []).append(ref_resolved)
            reverse_edges.setdefault(ref_resolved, []).append(current)

            # Visit if new
            if ref_resolved not in visited:
                visited[ref_resolved] = depth + 1
                edges.setdefault(ref_resolved, [])
                queue.append((ref_resolved, depth + 1))

    # Build result
    files = []
    for path, depth in sorted(visited.items(), key=lambda x: (x[1], x[0])):
        files.append({
            "path": path,
            "depth": depth,
            "references": sorted(set(edges.get(path, []))),
            "referenced_by": sorted(set(reverse_edges.get(path, []))),
        })

    return {
        "files": files,
        "roots": roots,
        "total_files": len(files),
    }
