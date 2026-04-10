"""MCP server for stash operations.

Agent-facing tools for capturing ideas, future work, and unaddressed
observations into a SQLite database. Business logic lives in
skills.stash; this server is a thin presentation layer that handles
scope-to-database resolution.

Two scopes:
- project — entries belonging to the current project, stored at
  <project>/.claude/ocd/stash/stash.db
- user — cross-project entries, stored at ~/.claude/ocd/stash/stash.db

Tools follow object_action naming: stash_add, stash_list, stash_search,
stash_get, stash_update, stash_remove. All return structured JSON.

Runs via stdio transport. Project root from CLAUDE_PROJECT_DIR env var,
falling back to the current working directory.
"""

from __future__ import annotations

import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

import skills.stash as stash_skill

from ._helpers import _err, _ok, _project_root

# --- Configuration ---

STASH_DB_REL = os.environ.get("STASH_DB", ".claude/ocd/stash/stash.db")


def _project_db() -> str:
    return os.path.join(str(_project_root()), STASH_DB_REL)


def _user_db() -> str:
    override = os.environ.get("STASH_USER_DB")
    if override:
        return str(Path(override).expanduser())
    return str(Path.home() / ".claude" / "ocd" / "stash" / "stash.db")


def _resolve_db(scope: str) -> str:
    if scope == "user":
        return _user_db()
    return _project_db()


mcp = FastMCP(
    "ocd-stash",
    instructions="""SQLite holding area for ideas, future work, and unaddressed observations. Reach for these tools when something surfaces mid-work that should be captured for later without breaking flow.

Capture fast — a three-second stash beats a ten-minute detour. Return to the work in progress immediately after adding.

Project vs user routing:
- Project-belonging info (ideas tied to the current codebase) → stash_add with default scope="project"
- Cross-project ideas or observations not tied to any particular codebase → stash_add with scope="user"

When stash is the right mechanism vs alternatives:
- Problems encountered mid-workflow (rule violations, tool gaps, unexpected state) → friction tools, not stash
- Settled choices with rationale worth preserving → decisions tools, not stash
- Stash is for ideas, future work, and observations not yet acted on — the holding area between noticing and doing

Default to simple entries. Use detail_md only when substantial context (constraints, approaches explored, blockers) would be lost in a one-line summary.

Lifecycle: stash is a holding area, not a permanent record. Call stash_remove when an entry has been addressed or moved to a tracker. Use stash_update with a different scope to promote an entry from user to project when it turns out to belong to the current codebase.""",
)


# ============================================================
# stash_* — stash operations
# ============================================================


@mcp.tool()
def stash_add(
    summary: str,
    detail_md: str | None = None,
    scope: str = "project",
) -> str:
    """Add an entry to the stash. Capture fast — do not deliberate.

    Use when something surfaces mid-work that should be captured for later without breaking the current flow.

    Args:
        summary: One-line description suitable for scanning.
        detail_md: Optional substantial context — constraints, approaches explored, what blocked progress.
        scope: "project" (default) or "user". Project entries belong to the current codebase; user entries are cross-project.

    Returns {id, summary, has_detail, created_at, updated_at}.
    """
    try:
        return _ok(stash_skill.stash_add(
            _resolve_db(scope), summary=summary, detail_md=detail_md,
        ))
    except Exception as e:
        return _err(e)


@mcp.tool()
def stash_list(
    ids: list[int] | None = None,
    scope: str = "project",
    limit: int | None = None,
) -> str:
    """List stash entries metadata in insertion order.

    Use to survey what has been stashed before starting related work, or to find ids for stash_get / stash_update / stash_remove.

    Args:
        ids: Optional list of specific ids to retrieve.
        scope: "project" (default) or "user".
        limit: Optional cap on entries returned.

    Returns {total, entries: [{id, summary, has_detail, created_at, updated_at}]}.
    """
    try:
        return _ok(stash_skill.stash_list(
            _resolve_db(scope), ids=ids, limit=limit,
        ))
    except Exception as e:
        return _err(e)


@mcp.tool()
def stash_search(pattern: str, scope: str = "project") -> str:
    """Regex search across summary and detail_md fields.

    Use to find stash entries by keyword or pattern without scanning the full list.

    Args:
        pattern: Regular expression to match against summary and detail_md.
        scope: "project" (default) or "user".

    Returns {total, entries: [{id, summary, has_detail, created_at, updated_at}]}.
    """
    try:
        return _ok(stash_skill.stash_search(
            _resolve_db(scope), pattern=pattern,
        ))
    except Exception as e:
        return _err(e)


@mcp.tool()
def stash_get(ids: list[int], scope: str = "project") -> str:
    """Return full stash entry content including detail_md.

    Use when reviewing a stashed idea to understand its full context.

    Args:
        ids: List of entry ids to retrieve with full content.
        scope: "project" (default) or "user".

    Returns {entries: [{id, summary, detail_md, created_at, updated_at}]}.
    """
    try:
        return _ok(stash_skill.stash_get(
            _resolve_db(scope), ids=ids,
        ))
    except Exception as e:
        return _err(e)


@mcp.tool()
def stash_update(
    id: int,
    summary: str | None = None,
    detail_md: str | None = None,
    scope: str = "project",
) -> str:
    """Update an existing stash entry, or promote it across scopes.

    Normal update: modifies fields in the specified scope's database.
    Cross-scope promotion: if the entry is not found in the specified scope
    but exists in the other scope, moves it to the specified scope.

    Args:
        id: The entry id to update.
        summary: New summary. None leaves unchanged.
        detail_md: New detail markdown. None leaves unchanged; empty string "" clears to null.
        scope: Target scope — "project" (default) or "user". If the entry lives in the other scope, it is moved here.

    Returns {id, summary, has_detail, created_at, updated_at} on normal update.
    Returns {action: "promoted", from_scope, to_scope, entry} on cross-scope move.
    """
    try:
        target_db = _resolve_db(scope)
        other_scope = "user" if scope == "project" else "project"
        other_db = _resolve_db(other_scope)

        # Try normal update in target scope first
        try:
            result = stash_skill.stash_update(
                target_db, id=id, summary=summary, detail_md=detail_md,
            )
            return _ok(result)
        except ValueError:
            pass

        # Not found in target scope — check the other scope for promotion
        try:
            full = stash_skill.stash_get(other_db, ids=id)
        except Exception:
            full = {"entries": []}

        if not full["entries"]:
            raise ValueError(
                f"No stash entry with id {id} in either scope; "
                "call stash_list to see available entries"
            )

        # Cross-scope promotion: add to target, remove from source
        entry = full["entries"][0]
        new_summary = summary if summary is not None else entry["summary"]
        if detail_md is not None:
            new_detail = None if detail_md == "" else detail_md
        else:
            new_detail = entry["detail_md"]

        new_entry = stash_skill.stash_add(
            target_db, summary=new_summary, detail_md=new_detail,
        )
        stash_skill.stash_remove(other_db, id=id)

        return _ok({
            "action": "promoted",
            "from_scope": other_scope,
            "to_scope": scope,
            "entry": new_entry,
        })

    except Exception as e:
        return _err(e)


@mcp.tool()
def stash_remove(id: int, scope: str = "project") -> str:
    """Remove a stash entry when it has been addressed or moved to a tracker.

    Args:
        id: The entry id to remove.
        scope: "project" (default) or "user".

    Returns {removed: {entry metadata}, remaining: N}.
    """
    try:
        return _ok(stash_skill.stash_remove(
            _resolve_db(scope), id=id,
        ))
    except Exception as e:
        return _err(e)


if __name__ == "__main__":
    mcp.run()
