"""MCP server for navigator operations.

Agent-facing tools for project structure navigation, governance discovery,
reference mapping, and scope analysis. Business logic lives in
skills.navigator; this server is a thin presentation layer.

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
    """Wrap result as JSON response."""
    if isinstance(result, str):
        return json.dumps({"result": result})
    if isinstance(result, list):
        return json.dumps({"result": result}, default=str)
    if isinstance(result, dict):
        return json.dumps(result, default=str)
    return json.dumps({"result": str(result)})


def _err(e: Exception) -> str:
    """Wrap exception as JSON error."""
    return json.dumps({"error": str(e)})


# ============================================================
# Structure Navigation
# ============================================================


@mcp.tool()
def describe_path(target_path: str) -> str:
    """Navigate project structure by path. Directories list children with descriptions; files show description. Start with '.' for top-level overview.

    Markers: [?] = needs description, [~] = stale (file changed since described).
    """
    if err := _check_db(): return err
    _auto_scan(target_path)
    try:
        return _ok(nav.describe_path(DB_PATH, target_path))
    except Exception as e:
        return _err(e)


@mcp.tool()
def list_files(
    target_path: str = ".",
    patterns: list[str] | None = None,
    excludes: list[str] | None = None,
    sizes: bool = False,
) -> str:
    """List non-excluded file paths under target_path. One per line, sorted.

    Args:
        target_path: Directory to list. Defaults to project root.
        patterns: Basename glob filters (e.g. ["*.md"]). Only matching files returned.
        excludes: Path glob filters. Matching files removed from results.
        sizes: If true, append line_count and char_count columns per file.
    """
    if err := _check_db(): return err
    _auto_scan(target_path)
    try:
        return _ok(nav.list_files(DB_PATH, target_path, patterns=patterns,
                                  excludes=excludes, sizes=sizes))
    except Exception as e:
        return _err(e)


@mcp.tool()
def search_entries(pattern: str) -> str:
    """Search file descriptions by keyword. Find files by what they do, not their name.

    Args:
        pattern: Substring to match against entry descriptions.
    """
    if err := _check_db(): return err
    _auto_scan()
    try:
        return _ok(nav.search_entries(DB_PATH, pattern))
    except Exception as e:
        return _err(e)


# ============================================================
# Governance
# ============================================================


@mcp.tool()
def governance_for(file_paths: list[str]) -> str:
    """Find which rules and conventions govern given files. Pass all target paths in one call.

    Returns criteria list and per-file governance matches. Use before creating or modifying files
    to discover applicable conventions.

    Args:
        file_paths: Array of project-relative file paths to check.
    """
    if err := _check_db(): return err
    _auto_scan()
    try:
        return _ok(nav.governance_for(DB_PATH, file_paths))
    except Exception as e:
        return _err(e)


@mcp.tool()
def governance_order() -> str:
    """Topological ordering of governance entries for evaluation sequence.

    Returns levels where level 0 has no governors, level N is governed only by levels 0..N-1.
    Use to determine evaluation order in governance chain traversals.
    """
    if err := _check_db(): return err
    _auto_scan()
    try:
        return _ok(nav.governance_order(DB_PATH))
    except Exception as e:
        return _err(e)


@mcp.tool()
def list_governance() -> str:
    """List all governance entries with patterns and loading mode (rule or convention)."""
    if err := _check_db(): return err
    _auto_scan()
    try:
        return _ok(nav.list_governance(DB_PATH))
    except Exception as e:
        return _err(e)


@mcp.tool()
def governance_graph() -> str:
    """Show governance dependency edges, roots (no governor), and leaves (govern nothing).

    Complements governance_order which shows levels but not edges.
    """
    if err := _check_db(): return err
    _auto_scan()
    try:
        return _ok(nav.governance_graph(DB_PATH))
    except Exception as e:
        return _err(e)


@mcp.tool()
def get_unclassified() -> str:
    """Find file entries with no governance coverage, grouped by extension.

    Use to identify file types that lack conventions.
    """
    if err := _check_db(): return err
    _auto_scan()
    try:
        return _ok(nav.get_unclassified(DB_PATH))
    except Exception as e:
        return _err(e)


# ============================================================
# Navigator Skill Support
# ============================================================


@mcp.tool()
def get_undescribed() -> str:
    """Return deepest directory with undescribed or stale entries.

    Call repeatedly during /ocd-navigator workflow until response contains 'No work remaining.'
    """
    if err := _check_db(): return err
    _auto_scan()
    try:
        return _ok(nav.get_undescribed(DB_PATH))
    except Exception as e:
        return _err(e)


@mcp.tool()
def set_entry(
    entry_path: str,
    description: str | None = None,
    exclude: int | None = None,
    traverse: int | None = None,
) -> str:
    """Create or update entry description, exclusion, or traversal flags.

    Args:
        entry_path: Project-relative path of the entry.
        description: New description text. Pass to set or update.
        exclude: 1 to exclude from scans/listings, 0 to include.
        traverse: 1 to allow traversal into directory, 0 to block.
    """
    if err := _check_db(): return err
    _auto_scan()
    try:
        return _ok(nav.set_entry(DB_PATH, entry_path, description=description,
                                 exclude=exclude, traverse=traverse))
    except Exception as e:
        return _err(e)


# ============================================================
# Skill Resolution
# ============================================================


@mcp.tool()
def resolve_skill(name: str) -> str:
    """Resolve skill name to SKILL.md file path. Searches personal, project, plugin-dir, and marketplace locations.

    Args:
        name: Skill name as it appears in frontmatter (e.g. 'ocd-navigator').

    Returns path on success, error if not found.
    """
    try:
        result = nav.resolve_skill(name)
        if result:
            return _ok(str(result))
        return json.dumps({"error": f"Skill not found: {name}"})
    except Exception as e:
        return _err(e)


@mcp.tool()
def list_skills() -> str:
    """List all discoverable skills with source and path.

    Returns array of {name, source, path} entries in priority order.
    Sources: personal, project, plugin-dir, marketplace.
    """
    try:
        return _ok(nav.list_skills())
    except Exception as e:
        return _err(e)


# ============================================================
# Reference Mapping
# ============================================================


@mcp.tool()
def scope_analysis(paths: list[str]) -> str:
    """Analyze scope: follow references, collect sizes, map governance.

    Composite tool that combines map_references + file sizes + governance matching.
    Returns structured matrix of files with line counts, governance coverage, and
    reference relationships. Includes governance_index for grouping files by convention.

    Args:
        paths: Starting file paths to analyze scope from.
    """
    if err := _check_db(): return err
    _auto_scan()
    try:
        return _ok(nav.scope_analysis(DB_PATH, paths))
    except Exception as e:
        return _err(e)


@mcp.tool()
def map_references(paths: list[str], max_depth: int = 20) -> str:
    """Follow file references recursively to build a dependency DAG.

    Works with SKILL.md backtick paths, governance depends: fields, and component
    _*.md files (leaf nodes). Returns file list with depth, references, and
    referenced_by for each file.

    Args:
        paths: Starting file paths (project-relative or absolute).
        max_depth: Maximum traversal depth. Default 20.
    """
    try:
        return _ok(nav.map_references(paths, max_depth=max_depth))
    except Exception as e:
        return _err(e)


if __name__ == "__main__":
    mcp.run()
