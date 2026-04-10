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

import os
import re
from collections import deque
from pathlib import Path

from ._frontmatter import parse_governance


# --- Parsers ---


def _resolve_plugin_root() -> Path | None:
    """Resolve CLAUDE_PLUGIN_ROOT from environment or persisted file."""
    env = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if env:
        return Path(env)
    plugin_root_file = Path(".claude/ocd/.plugin_root")
    try:
        value = plugin_root_file.read_text().strip()
        if value:
            return Path(value)
    except (FileNotFoundError, PermissionError):
        pass
    return None


# File extensions that indicate a file reference (not a command invocation)
_FILE_EXTENSIONS = re.compile(r'\.(?:md|py|sh|json|csv)$')


def _parse_skill_refs(file_path: str) -> list[str]:
    """Extract file references from a SKILL.md.

    Finds backtick-wrapped paths in workflow steps that look like file
    references. Skips fenced code blocks.

    Resolution rules:
    - Relative paths (no ${}) resolve from SKILL.md's directory only —
      beside or below, never upward
    - ${CLAUDE_PLUGIN_ROOT} paths resolve via env var when the path
      ends in a file extension (file reference, not command invocation)
    """
    try:
        content = Path(file_path).read_text()
    except (FileNotFoundError, PermissionError, OSError):
        return []

    skill_dir = Path(file_path).parent
    refs: list[str] = []
    in_code_block = False

    # Match backtick-wrapped paths containing '/'
    backtick_path = re.compile(r'`([^`]+/[^`]+)`')

    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        for match in backtick_path.finditer(line):
            ref = match.group(1)

            if "${CLAUDE_PLUGIN_ROOT}" in ref:
                # Env var path — resolve only if it's a file reference
                if not _FILE_EXTENSIONS.search(ref):
                    continue
                plugin_root = _resolve_plugin_root()
                if not plugin_root:
                    continue
                resolved = Path(ref.replace("${CLAUDE_PLUGIN_ROOT}", str(plugin_root)))
                if resolved.exists():
                    refs.append(str(resolved.resolve()))
            elif "${" in ref:
                # Other env vars — skip (unknown resolution)
                continue
            else:
                # Relative path — resolve from skill directory only
                if not _FILE_EXTENSIONS.search(ref):
                    continue
                resolved = skill_dir / ref
                if resolved.exists():
                    refs.append(str(resolved.resolve()))

    return refs


def _parse_governance_refs(file_path: str) -> list[str]:
    """Extract governed_by: references from governance frontmatter.

    Returns project-relative paths from the governed_by field. These are
    already project-relative in the frontmatter.
    """
    parsed = parse_governance(Path(file_path))
    if parsed is None:
        return []
    return parsed.get("governed_by", [])


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
