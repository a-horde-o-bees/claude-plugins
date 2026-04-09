"""MCP server for the decisions discipline.

Agent-facing tools for recording and maintaining non-obvious project
decisions in the project-root `decisions.md` index and `decisions/*.md`
detail files. Business logic lives in `_decisions_store`; this server is
a thin presentation layer.

Tools follow object_action naming: decisions_record, decisions_list,
decisions_get, decisions_update, decisions_remove. All return structured
JSON.

Runs via stdio transport. Project root from CLAUDE_PROJECT_DIR env var,
falling back to the current working directory.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from . import _decisions_store as store
from ._helpers import _err, _ok, _project_root

# --- Configuration ---


mcp = FastMCP(
    "ocd-decisions",
    instructions="""Project decisions index. Records non-obvious choices so future sessions do not re-litigate settled questions.

Reach for these tools when a choice is being made or revisited:
- A new choice with alternatives considered and rejected → decisions_record
- Revisiting a prior decision or surveying what has been decided → decisions_list then decisions_get
- Direction changed on a recorded decision → decisions_update
- Decision is no longer relevant to current project state → decisions_remove

What qualifies: non-obvious choices where alternatives were considered and rejected, or where the reasoning is not derivable from code or conventions. The goal is preventative — keep future work from re-exploring rejected alternatives.

What does NOT qualify: implementation details visible in the code, choices dictated by convention, standard patterns obvious from reading the source. If a fresh agent can derive the answer from the code, it is not a decision.

Capture Rationale: the summary alone is rarely enough. When the reasoning is worth preserving, record context (what prompted it), options (alternatives considered with trade-offs), decision (what was chosen and why), and consequences (what this enables, constrains, and how risks are mitigated). A decision without rationale devolves into a setting — future agents cannot tell whether the conditions still hold.

Lifecycle: kept current with project state, not preserved as a historical archive. Update entries when direction changes; remove entries and their detail files when the decision is no longer relevant. No change logs, no superseded-by chains — the index reflects current reality.""",
)

# ============================================================
# decisions_* — decisions index and detail file management
# ============================================================


@mcp.tool()
def decisions_record(
    title: str,
    summary: str,
    context: str | None = None,
    options: str | None = None,
    decision: str | None = None,
    consequences: str | None = None,
) -> str:
    """Record a new decision in the project-root decisions.md index.

    Use when a non-obvious choice is being made and alternatives were considered and rejected. Do not use for implementation details visible in the code or choices dictated by convention.

    Args:
        title: Short, stable name for the decision (used in the index and as the detail filename slug).
        summary: One-line summary suitable for the scannable index.
        context: What prompted the decision — the problem or question being resolved.
        options: Alternatives evaluated with trade-offs. Explain what was rejected and why.
        decision: What was chosen and the reasoning behind it.
        consequences: What this enables, constrains, and how risks are mitigated.

    When any of context/options/decision/consequences is supplied, a detail file is created at decisions/<slug>.md and linked from the index entry. Capture all four whenever the rationale is worth preserving — a summary alone is rarely enough for future agents to tell whether the conditions still hold.

    Returns {action: "recorded", index, title, summary, detail_path}.
    """
    try:
        return _ok(
            store.record(
                _project_root(),
                title=title,
                summary=summary,
                context=context,
                options=options,
                decision=decision,
                consequences=consequences,
            )
        )
    except Exception as e:
        return _err(e)


@mcp.tool()
def decisions_list() -> str:
    """List all decisions in insertion order with their summaries.

    Use to survey what has been decided before making a new choice, or to locate the identifier needed by decisions_get / decisions_update / decisions_remove.

    Returns {count, decisions: [{index, title, summary, detail_path}]}. The index field is 1-based and may be used as the identifier in other tools.
    """
    try:
        return _ok(store.list_decisions(_project_root()))
    except Exception as e:
        return _err(e)


@mcp.tool()
def decisions_get(identifier: str) -> str:
    """Return full content for one decision, including the detail file if one exists.

    Use when revisiting a recorded decision to understand its full rationale before deciding whether to proceed, update, or remove it.

    Args:
        identifier: Either the 1-based index (as a string, e.g. "3") or the exact title of the decision. Title matching is case-insensitive.

    Returns {index, title, summary, detail_path, detail} where detail is {context, options, decision, consequences, raw} when a detail file exists, or null when the entry is index-only. Returns an error when no entry matches the identifier.
    """
    try:
        return _ok(store.get(_project_root(), identifier))
    except Exception as e:
        return _err(e)


@mcp.tool()
def decisions_update(
    identifier: str,
    title: str | None = None,
    summary: str | None = None,
    context: str | None = None,
    options: str | None = None,
    decision: str | None = None,
    consequences: str | None = None,
) -> str:
    """Update an existing decision when direction changes.

    Use when a recorded decision is still relevant but one or more fields need to change — revised summary, corrected rationale, updated consequences as the project learns what the decision enables or constrains.

    Args:
        identifier: 1-based index (as a string) or exact title of the decision to update.
        title: New title. Detail file is renamed if its slug was derived from the old title.
        summary: New one-line summary.
        context/options/decision/consequences: New detail sections. Supplied fields replace prior values; unspecified fields are left unchanged. If any detail is supplied and no detail file exists yet, one is created.

    Do not use to record a wholly different decision — remove the stale entry and record a new one instead. Returns {action: "updated", index, title, summary, detail_path}.
    """
    try:
        return _ok(
            store.update(
                _project_root(),
                identifier=identifier,
                title=title,
                summary=summary,
                context=context,
                options=options,
                decision=decision,
                consequences=consequences,
            )
        )
    except Exception as e:
        return _err(e)


@mcp.tool()
def decisions_remove(identifier: str) -> str:
    """Remove a decision entry and its detail file when the decision is no longer relevant.

    Use when the project state has changed such that the decision no longer applies — the constraint is gone, the alternative chosen was itself later replaced, or the concern has become irrelevant. decisions.md is kept current with project state, not preserved as a historical archive.

    Args:
        identifier: 1-based index (as a string) or exact title of the decision to remove.

    Returns {action: "removed", title, detail_removed}.
    """
    try:
        return _ok(store.remove(_project_root(), identifier))
    except Exception as e:
        return _err(e)


if __name__ == "__main__":
    mcp.run()
