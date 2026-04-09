"""MCP server for stash operations.

Agent-facing tools for capturing ideas, future work, and unaddressed
observations into a markdown holding area. Business logic lives in
``_stash_store``; this server is a thin presentation layer.

Tools follow object_action naming: stash_add, stash_review,
stash_remove, stash_promote. All return structured JSON.

Runs via stdio transport. Project root from CLAUDE_PROJECT_DIR env
var, falling back to the current working directory.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from . import _stash_store as store
from ._helpers import _err, _ok, _project_root

# --- Configuration ---


mcp = FastMCP(
    "ocd-stash",
    instructions="""Markdown holding area for ideas, future work, and unaddressed observations. Reach for these tools when something surfaces mid-work that should be captured for later without breaking flow.

Capture fast — a three-second stash beats a ten-minute detour. Return to the work in progress immediately after adding.

Project vs unattached routing:
- Project-belonging info (ideas tied to the current codebase) → stash_add with default unattached=false; lands in <project>/.claude/stash/stash.md
- Cross-project ideas or observations not tied to any particular codebase → stash_add with unattached=true; lands in ~/.claude/stash/stash.md under ## Unattached

When stash is the right mechanism vs alternatives:
- Problems encountered mid-workflow (rule violations, tool gaps, unexpected state) → friction tools, not stash
- Settled choices with rationale worth preserving → decisions tools, not stash
- Stash is for ideas, future work, and observations not yet acted on — the holding area between noticing and doing

Default to simple entries. Use the detail argument only when substantial context (constraints, approaches explored, blockers) would be lost in a one-line summary — the server writes it to a companion {slug}.md file and links it from the entry.

Lifecycle: stash is a holding area, not a permanent record. Call stash_remove when an entry has been addressed or moved to a tracker. Use stash_promote when an entry captured as unattached turns out to belong to the current project.""",
)


# ============================================================
# stash_* — stash operations
# ============================================================


@mcp.tool()
def stash_add(
    title: str,
    summary: str,
    detail: str | None = None,
    unattached: bool = False,
) -> str:
    """Add an entry to the stash. Capture fast — do not deliberate.

    Use when something surfaces mid-work that should be captured for later without breaking the current flow. Default routing is to the current project's stash.

    Args:
        title: Short title identifying the entry. Must be unique within its target section.
        summary: One-line description suitable for the scannable entry list.
        detail: Optional substantial context — constraints, approaches explored, what blocked progress. When provided, the server writes a companion {slug}.md file next to stash.md and links it from the entry line. Use only when a one-line summary would lose meaningful information.
        unattached: When true, routes the entry to the user-level stash (~/.claude/stash/stash.md) under ## Unattached. Use for cross-project ideas. When false (default), routes to <project>/.claude/stash/stash.md.

    Returns {action, scope, section, stash_file, detail_file, entry} on success.
    """
    try:
        return _ok(
            store.add(
                _project_root(),
                title=title,
                summary=summary,
                detail=detail,
                unattached=unattached,
            )
        )
    except Exception as e:
        return _err(e)


@mcp.tool()
def stash_review(scope: str = "project") -> str:
    """List stash entries grouped by section.

    Use to survey what has been stashed before starting related work, or to flag entries that recent work may have addressed.

    Args:
        scope: "project" (default) reads only the current project's stash. "user" reads only the user-level stash. "all" reads both and returns results for each.

    Returns {scope, results: [{scope, stash_file, exists, sections, total}]}. Each section has a heading (null for the top section of the project file) and an entries array. Entries with companion detail files include detail_content inline so the agent does not need a second read.
    """
    try:
        return _ok(store.review(_project_root(), scope=scope))
    except Exception as e:
        return _err(e)


@mcp.tool()
def stash_remove(title: str, scope: str = "project") -> str:
    """Remove an entry by exact title. Also deletes the companion detail file when present.

    Use when an entry has been addressed, moved to an issue tracker, or superseded. Stash is a queue, not an archive — resolved entries leave the file.

    Args:
        title: Exact title of the entry to remove.
        scope: "project" (default) removes from the current project stash. "user" removes from the user-level stash. "all" searches both and removes the first match.

    Returns {action: "removed"|"not_found", scope, stash_file, detail_deleted, entry}.
    """
    try:
        return _ok(
            store.remove(_project_root(), title=title, scope=scope)
        )
    except Exception as e:
        return _err(e)


@mcp.tool()
def stash_promote(title: str) -> str:
    """Move an entry from the user-level stash into the current project stash.

    Use when an idea captured as unattached is recognized as belonging to the current project. Moves the companion detail file alongside when present.

    Args:
        title: Exact title of the user-level entry to promote.

    Returns {action: "promoted"|"not_found", from_stash_file, to_stash_file, entry} on success, or {error} on conflict with an existing project-side entry.
    """
    try:
        return _ok(store.promote(_project_root(), title=title))
    except Exception as e:
        return _err(e)


if __name__ == "__main__":
    mcp.run()
