"""MCP server for the project log.

Agent-facing tools for recording project context across multiple log types
(decision, friction, problem, idea, and any type the user registers) in a
single SQLite database. Business logic lives in servers.log; this server is
a thin presentation layer.

Tools follow object_action naming: record CRUD under log_*, type and tag
management under type_* and tag_*. All return structured JSON.

Runs via stdio transport. Database path from LOG_DB env var (relative to
project root), defaulting to .claude/ocd/log/log.db.
"""

from __future__ import annotations

import os

from mcp.server.fastmcp import FastMCP

import plugin
import servers.log as _log

from .._helpers import _err, _ok


def _db_path() -> str:
    """Resolve log database path relative to project root."""
    rel = os.environ.get("LOG_DB", ".claude/ocd/log/log.db")
    return str(plugin.get_project_dir() / rel)


mcp = FastMCP(
    "log",
    instructions="""Project log — SQLite-backed records across multiple log types with per-type tag management.

Reach for these tools when capturing context a future session will need: non-obvious choices, process gaps, observed defects, exploratory ideas. Each log_type has its own routing guidance (call type_list to see the full text). Summary below.

Types and when to use each:

- decision — non-obvious choices where alternatives were considered and rejected. Does NOT include implementation details visible in code or choices dictated by convention. Capture detail_md with context, options, the decision, and consequences.

- friction — process gaps encountered during work: rules the system forced you to violate, missing capabilities, broken process steps. Every friction encounter is a Fix-or-Log decision — never default to logging. Log when the fix would derail current work. When logging, add a system:<name> tag naming the system the friction is about, not the workflow that surfaced it.

- problem — observed defects or issues needing investigation later. Concrete, unexpected, wrong. Not rule violations (that's friction). Not ideas (that's idea).

- idea — exploratory ideas, future work, improvement suggestions tied to this project. Cross-project or personal context belongs in Claude memory, not here.

Routing vs alternatives:
- Settled choice with rationale → decision, not friction or idea
- Mid-workflow gap → friction or problem, not idea
- User preferences or personal context → Claude memory, not log
- Project knowledge any user would benefit from → log, not memory

Lifecycle: logs are a queue, not an archive. Call log_remove when an entry is resolved or moved to a tracker.

Use log_list or log_search to review. Use log_get for full detail. Use log_add immediately at the moment of encounter — context degrades if deferred. Use type_list to read full routing instructions per type.""",
)


# ============================================================
# log_* — record CRUD
# ============================================================


@mcp.tool()
def log_add(
    log_type: str,
    summary: str,
    detail_md: str | None = None,
    tags: list[str] | None = None,
) -> str:
    """Add a new record under log_type with optional detail and tags.

    Use immediately at the moment of encounter — context degrades if deferred.
    Tags are upserted implicitly under the record's log_type; misspellings
    create singleton tags that stand out in tag_list alongside canonical
    high-count tags.

    Args:
        log_type: Registered type name. Call type_list to see available types.
        summary: One-line description for scanning.
        detail_md: Optional markdown with extended context. Omit when the
            summary alone preserves meaning; include when rich rationale,
            reproduction steps, or nuanced trade-offs would otherwise be lost.
        tags: Optional list of free-form tag strings scoped under log_type.
            Conventions like "system:navigator" or "severity:high" are plain
            strings; the schema treats them uniformly.

    Returns {id, log_type, summary, has_detail, tags, created_at, updated_at}.
    """
    try:
        return _ok(
            _log.log_add(
                _db_path(),
                log_type=log_type,
                summary=summary,
                detail_md=detail_md,
                tags=tags,
            )
        )
    except Exception as e:
        return _err(e)


@mcp.tool()
def log_list(
    log_type: str | None = None,
    tags: list[str] | None = None,
    ids: list[int] | None = None,
    limit: int | None = None,
) -> str:
    """List records as metadata (no detail_md).

    Use to browse the queue or scope to a single type. Returns metadata only —
    call log_get to read detail_md content.

    Args:
        log_type: Filter to one type if provided.
        tags: Require every tag in the list to be present on the record.
        ids: Return metadata for these specific ids (ignores other filters).
        limit: Cap on total entries returned.

    Returns {total, entries: [{id, log_type, summary, has_detail, tags, ...}]}.
    """
    try:
        return _ok(
            _log.log_list(
                _db_path(), log_type=log_type, tags=tags, ids=ids, limit=limit,
            )
        )
    except Exception as e:
        return _err(e)


@mcp.tool()
def log_search(
    pattern: str,
    log_type: str | None = None,
    tags: list[str] | None = None,
) -> str:
    """Regex search across summary and detail_md.

    Use when the target entries are known by keyword but not by id. Scope
    with log_type or tags to narrow results.

    Args:
        pattern: Regex pattern matched against summary and detail_md.
        log_type: Restrict search to one type.
        tags: Require every tag in the list to be present on the record.

    Returns {total, entries: [{id, log_type, summary, has_detail, tags, ...}]}.
    """
    try:
        return _ok(
            _log.log_search(
                _db_path(), pattern=pattern, log_type=log_type, tags=tags,
            )
        )
    except Exception as e:
        return _err(e)


@mcp.tool()
def log_get(ids: list[int]) -> str:
    """Get full records including detail_md content.

    Use after log_list or log_search to read the full detail of specific
    entries.

    Args:
        ids: List of record ids to retrieve.

    Returns {entries: [{id, log_type, summary, detail_md, tags, ...}]}.
    """
    try:
        return _ok(_log.log_get(_db_path(), ids=ids))
    except Exception as e:
        return _err(e)


@mcp.tool()
def log_update(
    id: int,
    summary: str | None = None,
    detail_md: str | None = None,
    tags: list[str] | None = None,
) -> str:
    """Update fields on an existing record.

    None on any field leaves it unchanged. Empty string on detail_md clears
    it to null. A list on tags (even empty) replaces the full tag set.

    Args:
        id: Record id to update.
        summary: New summary text.
        detail_md: New detail markdown. Pass "" to clear.
        tags: Full replacement tag set. Omit to leave tags unchanged.

    Returns updated record metadata.
    """
    try:
        return _ok(
            _log.log_update(
                _db_path(), id=id, summary=summary, detail_md=detail_md, tags=tags,
            )
        )
    except Exception as e:
        return _err(e)


@mcp.tool()
def log_remove(id: int) -> str:
    """Remove a record by id. Cascades to tag attachments.

    Call after the underlying entry is addressed. Logs are a queue, not an
    archive — resolved entries are deleted.

    Args:
        id: Record id to remove.

    Returns {removed: {metadata}, remaining: N}.
    """
    try:
        return _ok(_log.log_remove(_db_path(), id=id))
    except Exception as e:
        return _err(e)


# ============================================================
# type_* — log type management
# ============================================================


@mcp.tool()
def type_add(name: str, instructions: str) -> str:
    """Register a new log type with routing instructions.

    Use when the existing types don't fit the content being captured. The
    instructions text is agent-facing guidance explaining when to reach for
    this type — write it like a server-instructions fragment.

    Args:
        name: Short type name (alphanumeric + dash/underscore suggested).
        instructions: Full routing guidance explaining when the type applies.

    Returns {name, instructions, created_at, updated_at}.
    """
    try:
        return _ok(_log.type_add(_db_path(), name=name, instructions=instructions))
    except Exception as e:
        return _err(e)


@mcp.tool()
def type_list() -> str:
    """List all registered log types with routing instructions and counts.

    Returns full instructions text for every type alongside record and tag
    counts — useful for reading per-type routing guidance, seeing which types
    are populated, and surfacing unused types.

    Returns {types: [{name, instructions, record_count, tag_count, ...}]}.
    """
    try:
        return _ok(_log.type_list(_db_path()))
    except Exception as e:
        return _err(e)


@mcp.tool()
def type_update(
    name: str,
    instructions: str | None = None,
    rename: str | None = None,
) -> str:
    """Update instructions and/or rename a type.

    None on either field leaves it unchanged. Rename cascades through
    records, tags, and record_tags.

    Args:
        name: Current type name.
        instructions: New routing guidance text.
        rename: New type name (rename target must not already exist).

    Returns updated type dict.
    """
    try:
        return _ok(
            _log.type_update(
                _db_path(), name=name, instructions=instructions, rename=rename,
            )
        )
    except Exception as e:
        return _err(e)


@mcp.tool()
def type_remove(name: str, force: bool = False) -> str:
    """Remove a log type. Refuses if records exist and force is False.

    With force=True, cascade-deletes all records under the type (which also
    deletes their tag attachments), then deletes the type's tags and the
    type itself.

    Args:
        name: Type to remove.
        force: Required to cascade-delete records.

    Returns {removed, records_deleted, tags_deleted, remaining_types}.
    """
    try:
        return _ok(_log.type_remove(_db_path(), name=name, force=force))
    except Exception as e:
        return _err(e)


# ============================================================
# tag_* — tag management (scoped per type)
# ============================================================


@mcp.tool()
def tag_add(log_type: str, name: str) -> str:
    """Pre-declare a tag under a log_type without attaching it to a record.

    Idempotent: adding an existing tag is a no-op. Most tags are created
    implicitly on log_add; use this when pre-declaring a canonical name to
    prevent misspellings.

    Args:
        log_type: Type the tag belongs to.
        name: Tag string.

    Returns {log_type, name, record_count}.
    """
    try:
        return _ok(_log.tag_add(_db_path(), log_type=log_type, name=name))
    except Exception as e:
        return _err(e)


@mcp.tool()
def tag_list(log_type: str | None = None) -> str:
    """List tags with record counts.

    With log_type: returns one type's tags sorted by count DESC then name.
    Without log_type: returns every registered type grouped with its tags.
    Counts make misspellings stand out as singletons next to canonical
    high-count entries.

    Args:
        log_type: Scope to one type. Omit to see all types grouped.

    Returns {log_type, tags: [...]} with a type, or {by_type: {...}} without.
    """
    try:
        return _ok(_log.tag_list(_db_path(), log_type=log_type))
    except Exception as e:
        return _err(e)


@mcp.tool()
def tag_update(log_type: str, old: str, new: str) -> str:
    """Rename or merge a tag under a log_type.

    If new does not exist, pure rename. If new exists, merge: all records
    carrying old get new instead (deduplicated), then old is deleted. Use to
    clean up misspellings and consolidate parallel spellings.

    Args:
        log_type: Type the tag belongs to.
        old: Current tag name.
        new: Target tag name.

    Returns {log_type, old, new, records_affected}.
    """
    try:
        return _ok(
            _log.tag_update(_db_path(), log_type=log_type, old=old, new=new)
        )
    except Exception as e:
        return _err(e)


@mcp.tool()
def tag_remove(log_type: str, name: str) -> str:
    """Strip a tag from all records under a log_type. Records survive.

    Use to remove a tag that is no longer meaningful without deleting the
    records it was attached to.

    Args:
        log_type: Type the tag belongs to.
        name: Tag to remove.

    Returns {log_type, name, records_affected}.
    """
    try:
        return _ok(_log.tag_remove(_db_path(), log_type=log_type, name=name))
    except Exception as e:
        return _err(e)


if __name__ == "__main__":
    mcp.run()
