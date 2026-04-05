"""MCP server for navigator operations.

Agent-facing tools for project structure navigation, governance discovery,
reference mapping, and scope analysis. Business logic lives in
skills.navigator; this server is a thin presentation layer.

Tools follow object_action naming: paths_*, governance_*, skills_*,
references_*, scope_*. All return structured JSON.

Runs via stdio transport. Database path from DB_PATH env var.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# Add the plugin root to sys.path so we can import the navigator package
_plugin_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_plugin_root))

import skills.navigator as nav  # noqa: E402
from skills.navigator import scan_path  # noqa: E402

# --- Configuration ---

DB_PATH = os.environ.get("DB_PATH", ".claude/ocd/navigator/navigator.db")

mcp = FastMCP("ocd-navigator")

# --- Helpers ---

_NO_DB_MSG = json.dumps({
    "error": "Navigator database not initialized.",
    "action": "Run /ocd-init or /ocd-navigator to create the database first.",
})


def _check_db() -> str | None:
    """Return error JSON if database doesn't exist, None if OK."""
    if not Path(DB_PATH).exists():
        return _NO_DB_MSG
    return None


def _auto_scan(target_path: str = ".") -> None:
    """Run filesystem scan before query. Silent — discards output."""
    try:
        scan_path(DB_PATH, target_path)
    except Exception:
        pass


def _ok(result) -> str:
    """Serialize result as JSON string."""
    return json.dumps(result, default=str)


def _err(e: Exception) -> str:
    """Wrap exception as JSON error."""
    return json.dumps({"error": str(e)})


# ============================================================
# paths_* — project structure navigation
# ============================================================


@mcp.tool()
def paths_describe(target_path: str) -> str:
    """Describe entry at path. Files return type, description, stale flag. Directories return entry info plus children array.

    Start with '.' for top-level overview. Children with description=null need descriptions.
    """
    if err := _check_db(): return err
    _auto_scan(target_path)
    try:
        return _ok(nav.paths_describe(DB_PATH, target_path))
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
    _auto_scan(target_path)
    try:
        return _ok(nav.paths_list(DB_PATH, target_path, patterns=patterns,
                                  excludes=excludes, sizes=sizes))
    except Exception as e:
        return _err(e)


@mcp.tool()
def paths_search(pattern: str) -> str:
    """Search file descriptions by keyword. Find files by what they do, not their name.

    Returns {pattern, results: [{path, type, description}]}.
    """
    if err := _check_db(): return err
    _auto_scan()
    try:
        return _ok(nav.paths_search(DB_PATH, pattern))
    except Exception as e:
        return _err(e)


@mcp.tool()
def paths_set(
    entry_path: str,
    description: str | None = None,
    exclude: int | None = None,
    traverse: int | None = None,
) -> str:
    """Create or update entry description, exclusion, or traversal flags.

    Returns {action: "added"|"updated"|"none", path, ...}.
    """
    if err := _check_db(): return err
    _auto_scan()
    try:
        return _ok(nav.paths_set(DB_PATH, entry_path, description=description,
                                 exclude=exclude, traverse=traverse))
    except Exception as e:
        return _err(e)


@mcp.tool()
def paths_undescribed() -> str:
    """Return deepest directory with undescribed or stale entries.

    Returns {done: true} when no work remains. Otherwise returns
    {done: false, remaining, directories, target, listing}.
    Call repeatedly during /ocd-navigator workflow until done is true.
    """
    if err := _check_db(): return err
    _auto_scan()
    try:
        return _ok(nav.paths_undescribed(DB_PATH))
    except Exception as e:
        return _err(e)


@mcp.tool()
def paths_remove(
    entry_path: str,
    recursive: bool = False,
    all_entries: bool = False,
) -> str:
    """Remove entries from database. Rarely needed — scan handles cleanup automatically.

    Returns {action: "removed"|"removed_recursive"|"removed_all"|"not_found"|"error", ...}.
    """
    if err := _check_db(): return err
    _auto_scan()
    try:
        return _ok(nav.paths_remove(DB_PATH, entry_path, recursive=recursive,
                                    all_entries=all_entries))
    except Exception as e:
        return _err(e)


# ============================================================
# governance_* — rules and conventions discovery
# ============================================================


@mcp.tool()
def governance_match(file_paths: list[str], include_rules: bool = False) -> str:
    """Find which conventions apply to files. Call before creating or modifying files.

    Returns only conventions (on-demand) by default. Rules are excluded — they are
    always loaded into agent context. Read each returned convention you haven't already
    read, then follow its requirements.

    Set include_rules=true only for governance evaluation where rules themselves
    are the evaluation target.

    Returns {matches: {file: [convention_paths]}, conventions: [all_unique]}.
    """
    if err := _check_db(): return err
    _auto_scan()
    try:
        return _ok(nav.governance_match(DB_PATH, file_paths, include_rules=include_rules))
    except Exception as e:
        return _err(e)


@mcp.tool()
def governance_list() -> str:
    """List all governance entries. Returns array of {path, pattern, mode}.

    Mode is 'rule' (auto-loaded) or 'convention' (on-demand).
    """
    if err := _check_db(): return err
    _auto_scan()
    try:
        return _ok(nav.governance_list(DB_PATH))
    except Exception as e:
        return _err(e)


@mcp.tool()
def governance_order() -> str:
    """Topological ordering for evaluation sequence.

    Returns {levels: [{level, entries}], cycle: null|[paths]}.
    Level 0 has no governors. Use to determine dependency-safe evaluation order.
    """
    if err := _check_db(): return err
    _auto_scan()
    try:
        return _ok(nav.governance_order(DB_PATH))
    except Exception as e:
        return _err(e)


@mcp.tool()
def governance_graph() -> str:
    """Governance dependency edges, roots, and leaves.

    Returns {roots: [...], edges: [{from, to}], leaves: [...]}.
    """
    if err := _check_db(): return err
    _auto_scan()
    try:
        return _ok(nav.governance_graph(DB_PATH))
    except Exception as e:
        return _err(e)


@mcp.tool()
def governance_unclassified() -> str:
    """Find files with no governance coverage, grouped by extension.

    Returns {total, by_extension: {ext: [paths]}}.
    """
    if err := _check_db(): return err
    _auto_scan()
    try:
        return _ok(nav.governance_unclassified(DB_PATH))
    except Exception as e:
        return _err(e)


# ============================================================
# skills_* — skill resolution
# ============================================================


@mcp.tool()
def skills_resolve(name: str) -> str:
    """Resolve skill name to SKILL.md path. Searches personal, project, plugin-dir, marketplace.

    Returns {path} on success, {error} if not found.
    """
    try:
        result = nav.skills_resolve(name)
        if result:
            return _ok({"path": str(result)})
        return json.dumps({"error": f"Skill not found: {name}"})
    except Exception as e:
        return _err(e)


@mcp.tool()
def skills_list() -> str:
    """List all discoverable skills. Returns array of {name, source, path}.

    Sources: personal, project, plugin-dir, marketplace.
    """
    try:
        return _ok(nav.skills_list())
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
        return _ok(nav.references_map(paths, max_depth=max_depth))
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
    _auto_scan()
    try:
        return _ok(nav.scope_analyze(DB_PATH, paths))
    except Exception as e:
        return _err(e)


if __name__ == "__main__":
    mcp.run()
