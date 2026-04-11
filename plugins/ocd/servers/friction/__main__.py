"""MCP server for friction discipline.

Agent-facing tools for logging, querying, searching, updating, and
removing process friction. Friction is the signal that a system, tool,
or process has a gap. Every encounter is a Fix or Log decision — this
server owns the Log path. Business logic lives in servers.friction;
this server is a thin presentation layer.

Tools follow object_action naming: friction_add, friction_list,
friction_search, friction_get, friction_update, friction_remove,
friction_systems_list. All return structured JSON.

Runs via stdio transport. Database path from FRICTION_DB env var.
"""

from __future__ import annotations

import os

from mcp.server.fastmcp import FastMCP

import servers.friction as friction_skill

from .._helpers import _err, _ok

# --- Configuration ---

FRICTION_DB = os.environ.get("FRICTION_DB", ".claude/ocd/friction/friction.db")

mcp = FastMCP(
    "friction",
    instructions="""Process friction queue. Reach for these tools when encountering a gap — a rule the system forced you to violate, a missing capability, a broken process step, unexpected state, or a runtime issue where investigating inline would derail the current task.

Every friction encounter is a Fix or Log decision. Make the choice actively — never default to logging.

Fix now when the current context is better equipped than a future session would be:
- The fix is clear from the current context and reconstructing that context later would be expensive
- The spider-web of related information informing the discovery would be lost to deferral
- The fix is simple enough that doing it now won't derail the current task

Log and continue when:
- The fix would derail current work — requires investigation, touches unrelated systems, or demands design decisions beyond current scope
- The friction is simple enough to describe and act on later without needing current context
- The fix depends on work outside the current task

Deciding question: is the current context better equipped than a future session would be? Complex friction rooted in a rich context web is worth fixing now — context won't regenerate cheaply. Simple friction with standalone context is fine to queue.

When logging: use friction_add immediately at the moment of encounter — do not wait until the task completes, context degrades. The `system` argument names the system the friction is *about*, not the workflow that surfaced it. Friction with navigator discovered during evaluate-governance goes to system='navigator', not 'evaluate-governance'.

When friction is fixed: use friction_remove to clear the entry. Logs are a queue, not an archive — only unresolved friction remains.

Use friction_list to review the queue before starting related work. Use friction_systems_list for an overview of where friction has accumulated. Use friction_search to find entries matching a pattern. Use friction_get to read full detail on specific entries.""",
)


# ============================================================
# friction_* — friction queue operations
# ============================================================


@mcp.tool()
def friction_add(
    system: str,
    summary: str,
    detail_md: str | None = None,
) -> str:
    """Add a friction entry for a system.

    Call immediately at the moment of friction — do not wait until the task
    completes. Context degrades; capture while it's rich.

    Args:
        system: The system the friction is *about*, not the workflow that surfaced it.
            Alphanumerics, underscore, dash — no path separators.
        summary: Concise description of the gap, rule violation, tool miss, or breakdown.
        detail_md: Optional markdown with extended context — what happened, expected
            behavior, workaround used. Use when the summary alone would lose important
            context for a future session.

    Returns {id, system, summary, has_detail, created_at, updated_at}.
    """
    try:
        return _ok(friction_skill.friction_add(FRICTION_DB, system, summary, detail_md=detail_md))
    except Exception as e:
        return _err(e)


@mcp.tool()
def friction_list(
    system: str | None = None,
    ids: list[int] | None = None,
    limit: int | None = None,
) -> str:
    """List friction entries as metadata (no detail content).

    Use before starting related work to surface known gaps. Returns metadata
    only — use friction_get for full detail_md content.

    Args:
        system: If provided, return entries only from this system.
        ids: If provided, return metadata for these specific entry ids (ignores other filters).
        limit: Optional cap on total entries returned.

    Returns {total, entries: [{id, system, summary, has_detail, created_at, updated_at}]}.
    """
    try:
        return _ok(friction_skill.friction_list(FRICTION_DB, system=system, ids=ids, limit=limit))
    except Exception as e:
        return _err(e)


@mcp.tool()
def friction_search(pattern: str, system: str | None = None) -> str:
    """Regex search across summary and detail content.

    Use to find friction entries matching a pattern when you don't know
    which system they belong to.

    Args:
        pattern: Regex pattern to match against summary and detail_md.
        system: If provided, restrict search to this system.

    Returns {total, entries: [{id, system, summary, has_detail, created_at, updated_at}]}.
    """
    try:
        return _ok(friction_skill.friction_search(FRICTION_DB, pattern, system=system))
    except Exception as e:
        return _err(e)


@mcp.tool()
def friction_get(ids: list[int]) -> str:
    """Get full friction entries including detail_md content.

    Use after friction_list or friction_search to read the full detail
    of specific entries.

    Args:
        ids: List of entry ids to retrieve.

    Returns {entries: [{id, system, summary, detail_md, created_at, updated_at}]}.
    """
    try:
        return _ok(friction_skill.friction_get(FRICTION_DB, ids))
    except Exception as e:
        return _err(e)


@mcp.tool()
def friction_update(
    id: int,
    summary: str | None = None,
    detail_md: str | None = None,
    system: str | None = None,
) -> str:
    """Update fields on an existing friction entry.

    None = don't touch the field. Empty string "" clears detail_md.

    Args:
        id: Entry id to update.
        summary: New summary text.
        detail_md: New detail markdown. Pass "" to clear.
        system: New system name.

    Returns updated entry metadata.
    """
    try:
        return _ok(friction_skill.friction_update(FRICTION_DB, id, summary=summary, detail_md=detail_md, system=system))
    except Exception as e:
        return _err(e)


@mcp.tool()
def friction_remove(id: int) -> str:
    """Remove a resolved friction entry by id.

    Call after the underlying cause is fixed and verified. Friction logs
    are a queue, not an archive — resolved entries are deleted.

    Args:
        id: Entry id to remove.

    Returns {removed: {entry metadata}, remaining: N}.
    """
    try:
        return _ok(friction_skill.friction_remove(FRICTION_DB, id))
    except Exception as e:
        return _err(e)


@mcp.tool()
def friction_systems_list() -> str:
    """List all systems with friction entries, with counts.

    Use for an overview of where friction has accumulated across the project.

    Returns {total_systems, total_entries, systems: [{name, count}]}.
    """
    try:
        return _ok(friction_skill.friction_systems_list(FRICTION_DB))
    except Exception as e:
        return _err(e)


if __name__ == "__main__":
    mcp.run()
