"""MCP server for navigator operations.

Agent-facing tools for project structure navigation, governance discovery,
reference mapping, and scope analysis. Business logic lives in
subsystems.navigator; this module is a thin presentation layer.

Tools follow object_action naming: paths_*, governance_*, skills_*,
references_*, scope_*. All return structured JSON.

Runs via stdio transport. Database path from DB_PATH env var.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

import subsystems.navigator as _nav

from ._server_helpers import _err, _ok

# --- Configuration ---

DB_PATH = os.environ.get("DB_PATH", ".claude/ocd/navigator/navigator.db")

mcp = FastMCP(
    "navigator",
    instructions="""Project structure index. Use Navigator first when orienting in unfamiliar areas — it indexes file purposes, structure, and metrics so the agent doesn't have to read every file to find what it needs.

Prefer Navigator for purpose-based queries:
- Find files by what they do → paths_search (vs Grep, which searches content)
- Browse structure with descriptions → paths_get (start with '.' for top-level overview)
- Locate skills across discovery locations → skills_resolve

Prefer Grep for content patterns (function names, string literals, regex matching) and Glob for file name patterns (extensions, naming conventions).

For rules and conventions that govern files (which conventions apply, the governance chain, dependency ordering), reach for the governance server instead.

Use Navigator first for orientation, then Grep/Glob for specific code searches once you know where to look.""",
)

# --- Helpers ---

_NO_DB_MSG = json.dumps({
    "error": "Navigator database not initialized.",
    "action": "Database not initialized. Run /ocd:setup init to deploy infrastructure.",
})


def _check_db() -> str | None:
    """Return error JSON if database doesn't exist, None if OK."""
    if not Path(DB_PATH).exists():
        return _NO_DB_MSG
    return None


# ============================================================
# paths_* — project structure navigation
# ============================================================


@mcp.tool()
def paths_get(paths: str | list[str]) -> str:
    """Retrieve entry details for one or more paths. Files return type, description, stale flag. Directories return entry info plus children.

    Single path returns one entry dict. Multiple paths return {entries: [dict, ...]}.
    Start with '.' for top-level overview. Children with description=null need descriptions.
    """
    if err := _check_db(): return err
    try:
        return _ok(_nav.paths_get(DB_PATH, paths))
    except Exception as e:
        return _err(e)


@mcp.tool()
def paths_list(
    target_path: str = ".",
    patterns: list[str] | None = None,
    excludes: list[str] | None = None,
    sizes: bool = False,
) -> str:
    """List non-excluded files under target_path. Returns array of {path} dicts.

    Args:
        target_path: Directory to list. Defaults to project root.
        patterns: Basename glob filters (e.g. ["*.md"]). Only matching files returned.
        excludes: Path glob filters. Matching files removed from results.
        sizes: If true, include line_count and char_count per file.
    """
    if err := _check_db(): return err
    try:
        return _ok(_nav.paths_list(DB_PATH, target_path, patterns=patterns,
                                  excludes=excludes, sizes=sizes))
    except Exception as e:
        return _err(e)


@mcp.tool()
def paths_search(pattern: str) -> str:
    """Search file descriptions by keyword. Find files by what they do, not by what they contain or how they're named.

    Use this when you know what a file does but not where it lives — Grep searches content (slower for purpose queries), paths_search searches indexed descriptions.

    Returns {pattern, results: [{path, type, description}]}.
    """
    if err := _check_db(): return err
    try:
        return _ok(_nav.paths_search(DB_PATH, pattern))
    except Exception as e:
        return _err(e)


@mcp.tool()
def paths_upsert(
    entry_path: str,
    description: str | None = None,
    exclude: int | None = None,
    traverse: int | None = None,
) -> str:
    """Create or update entry description, exclusion, or traversal flags.

    Returns {action: "added"|"updated"|"none", path, ...}.
    """
    if err := _check_db(): return err
    try:
        return _ok(_nav.paths_upsert(DB_PATH, entry_path, description=description,
                                    exclude=exclude, traverse=traverse))
    except Exception as e:
        return _err(e)


@mcp.tool()
def paths_undescribed() -> str:
    """Return deepest directory with undescribed or stale entries.

    Returns {done: true} when no work remains. Otherwise returns
    {done: false, remaining, directories, target, listing}.
    Call repeatedly during /ocd:navigator workflow until done is true.
    """
    if err := _check_db(): return err
    try:
        return _ok(_nav.paths_undescribed(DB_PATH))
    except Exception as e:
        return _err(e)


@mcp.tool()
def paths_remove(
    entry_path: str,
    mode: str = "single",
) -> str:
    """Remove entries from database. Rarely needed — scan handles cleanup automatically.

    Args:
        entry_path: File or directory path. Ignored when mode="all".
        mode: "single" (default) removes one entry; "recursive" removes a directory and all children; "all" removes every concrete entry (patterns table unaffected).

    Returns {action: "removed"|"removed_recursive"|"removed_all"|"not_found"|"error", ...}.
    """
    if err := _check_db(): return err
    try:
        return _ok(_nav.paths_remove(DB_PATH, entry_path, mode=mode))
    except Exception as e:
        return _err(e)


# ============================================================
# skills_* — skill resolution
# ============================================================


@mcp.tool()
def skills_resolve(name: str) -> str:
    """Resolve skill name to SKILL.md path. Searches personal, project, plugin-dir, marketplace.

    Returns {path} on success, {error, action} if not found.
    """
    try:
        result = _nav.skills_resolve(name)
        if result:
            return _ok({"path": str(result)})
        return json.dumps({
            "error": f"Skill not found: {name}",
            "action": "Call skills_list to see all discoverable skills, or verify the skill name spelling.",
        })
    except Exception as e:
        return _err(e)


@mcp.tool()
def skills_list() -> str:
    """List all discoverable skills. Returns array of {name, source, path}.

    Sources: personal, project, plugin-dir, marketplace.
    """
    try:
        return _ok(_nav.skills_list())
    except Exception as e:
        return _err(e)


# ============================================================
# references_* — file reference traversal
# ============================================================


@mcp.tool()
def references_map(paths: list[str], max_depth: int = 20) -> str:
    """Follow file references recursively to build a dependency DAG.

    Works with SKILL.md backtick paths, governance depends: fields, and component
    _*.md files (leaf nodes).

    Returns {files: [{path, depth, references, referenced_by}], roots, total_files}.
    """
    try:
        return _ok(_nav.references_map(paths, max_depth=max_depth))
    except Exception as e:
        return _err(e)


# ============================================================
# scope_* — composite analysis
# ============================================================


@mcp.tool()
def scope_analyze(paths: list[str]) -> str:
    """Analyze scope: follow references, collect sizes, map governance.

    Composite tool combining references_map + file sizes + governance_match.
    Returns {files: [{path, line_count, char_count, governance, references, referenced_by}],
    governance_index: {convention: [files]}, total_lines, total_files}.
    """
    if err := _check_db(): return err
    try:
        return _ok(_nav.scope_analyze(DB_PATH, paths))
    except Exception as e:
        return _err(e)


if __name__ == "__main__":
    mcp.run()
