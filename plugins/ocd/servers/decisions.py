"""MCP server for the decisions discipline.

Agent-facing tools for recording and maintaining non-obvious project
decisions in a SQLite database. Business logic lives in
skills.decisions; this server is a thin presentation layer.

Tools follow object_action naming: decisions_add, decisions_list,
decisions_search, decisions_get, decisions_update, decisions_remove.
All return structured JSON.

Runs via stdio transport. Database path from DECISIONS_DB env var
(relative to project root), defaulting to .claude/ocd/decisions/decisions.db.
"""

from __future__ import annotations

import os

from mcp.server.fastmcp import FastMCP

import plugin
import skills.decisions as decisions_skill

from ._helpers import _err, _ok

# --- Configuration ---


def _db_path() -> str:
    """Resolve decisions database path relative to project root."""
    rel = os.environ.get("DECISIONS_DB", ".claude/ocd/decisions/decisions.db")
    return str(plugin.get_project_dir() / rel)


mcp = FastMCP(
    "ocd-decisions",
    instructions="""Project decisions index. Records non-obvious choices so future sessions do not re-litigate settled questions.

Reach for these tools when a choice is being made or revisited:
- A new choice with alternatives considered and rejected → decisions_add
- Revisiting a prior decision or surveying what has been decided → decisions_list then decisions_get
- Searching for a decision by keyword or pattern → decisions_search
- Direction changed on a recorded decision → decisions_update
- Decision is no longer relevant to current project state → decisions_remove

What qualifies: non-obvious choices where alternatives were considered and rejected, or where the reasoning is not derivable from code or conventions. The goal is preventative — keep future work from re-exploring rejected alternatives.

What does NOT qualify: implementation details visible in the code, choices dictated by convention, standard patterns obvious from reading the source. If a fresh agent can derive the answer from the code, it is not a decision.

Capture Rationale: the summary alone is rarely enough. When the reasoning is worth preserving, include detail_md with context (what prompted it), options (alternatives with trade-offs), the decision (what was chosen and why), and consequences (what this enables and constrains). A decision without rationale devolves into a setting — future agents cannot tell whether the conditions still hold.

Lifecycle: kept current with project state, not preserved as a historical archive. Update entries when direction changes; remove entries when the decision is no longer relevant.""",
)

# ============================================================
# decisions_* — decisions database operations
# ============================================================


@mcp.tool()
def decisions_add(summary: str, detail_md: str | None = None) -> str:
    """Record a new decision.

    Use when a non-obvious choice is being made and alternatives were considered and rejected.

    Args:
        summary: One-line description suitable for scanning.
        detail_md: Optional rich markdown with context, options considered, the decision, and consequences.

    Returns {id, summary, has_detail, created_at, updated_at}.
    """
    try:
        return _ok(decisions_skill.decisions_add(_db_path(), summary=summary, detail_md=detail_md))
    except Exception as e:
        return _err(e)


@mcp.tool()
def decisions_list(ids: list[int] | None = None, limit: int | None = None) -> str:
    """List decisions metadata in insertion order.

    Use to survey what has been decided before making a new choice, or to locate the id needed by decisions_get / decisions_update / decisions_remove.

    Args:
        ids: Optional list of specific ids to retrieve.
        limit: Optional cap on entries returned.

    Returns {total, entries: [{id, summary, has_detail, created_at, updated_at}]}.
    """
    try:
        return _ok(decisions_skill.decisions_list(_db_path(), ids=ids, limit=limit))
    except Exception as e:
        return _err(e)


@mcp.tool()
def decisions_search(pattern: str) -> str:
    """Regex search across summary and detail_md fields.

    Use to find decisions by keyword or pattern without scanning the full list.

    Args:
        pattern: Regular expression to match against summary and detail_md.

    Returns {total, entries: [{id, summary, has_detail, created_at, updated_at}]}.
    """
    try:
        return _ok(decisions_skill.decisions_search(_db_path(), pattern=pattern))
    except Exception as e:
        return _err(e)


@mcp.tool()
def decisions_get(ids: list[int]) -> str:
    """Return full decision content including detail_md.

    Use when revisiting a recorded decision to understand its full rationale.

    Args:
        ids: List of decision ids to retrieve with full content.

    Returns {entries: [{id, summary, detail_md, created_at, updated_at}]}.
    """
    try:
        return _ok(decisions_skill.decisions_get(_db_path(), ids=ids))
    except Exception as e:
        return _err(e)


@mcp.tool()
def decisions_update(
    id: int,
    summary: str | None = None,
    detail_md: str | None = None,
) -> str:
    """Update an existing decision when direction changes.

    Args:
        id: The decision id to update.
        summary: New summary. None leaves unchanged.
        detail_md: New detail markdown. None leaves unchanged; empty string "" clears to null.

    Returns {id, summary, has_detail, created_at, updated_at}.
    """
    try:
        return _ok(decisions_skill.decisions_update(_db_path(), id=id, summary=summary, detail_md=detail_md))
    except Exception as e:
        return _err(e)


@mcp.tool()
def decisions_remove(id: int) -> str:
    """Remove a decision when it is no longer relevant.

    Args:
        id: The decision id to remove.

    Returns {removed: {entry metadata}, remaining: N}.
    """
    try:
        return _ok(decisions_skill.decisions_remove(_db_path(), id=id))
    except Exception as e:
        return _err(e)


if __name__ == "__main__":
    mcp.run()
