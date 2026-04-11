"""MCP server for governance operations.

Agent-facing tools for loading, matching, and ordering the rules and
conventions governance chain. Business logic lives in skills.governance;
this server is a thin presentation layer.

Tools follow object_action naming: governance_*. All return structured
JSON.

Runs via stdio transport. Database path from GOVERNANCE_DB env var.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

import skills.governance as gov

from ._helpers import _err, _ok

# --- Configuration ---

DB_PATH = os.environ.get("GOVERNANCE_DB", ".claude/ocd/governance/governance.db")

mcp = FastMCP(
    "ocd-governance",
    instructions="""Governance index. Loads rules and conventions from frontmatter and answers three questions about the governance chain:

- Which governance entries apply to a file → governance_match
- What is the full set of governance entries → governance_list
- How should governance be traversed in dependency order → governance_order

Reach for this server when you need to know what governs a file, what the full governance surface is, or how to walk the chain root-first (e.g. during evaluate-governance). Governance state is self-refreshing — every query reloads changed files from disk before answering.

Governance is independent from navigator. Navigator indexes files and paths; governance indexes the rules and conventions that govern them.""",
)

# --- Helpers ---

_NO_DB_MSG = json.dumps({
    "error": "Governance database not initialized.",
    "action": "Run /ocd-init to create the database first.",
})


def _check_db() -> str | None:
    """Return error JSON if database doesn't exist, None if OK."""
    if not Path(DB_PATH).exists():
        return _NO_DB_MSG
    return None


# ============================================================
# governance_* — rules and conventions discovery
# ============================================================


@mcp.tool()
def governance_match(file_paths: list[str], include_rules: bool = False) -> str:
    """Find which governance entries apply to the given file paths.

    By default returns only conventions (on-demand). Rules are always
    loaded into agent context, so they're excluded unless include_rules
    is set. Set include_rules=true when rules themselves are the
    evaluation target.

    Returns {matches: {file_path: [convention_paths]}, conventions: [all_unique]}.
    """
    if err := _check_db(): return err
    try:
        return _ok(gov.governance_match(DB_PATH, file_paths, include_rules=include_rules))
    except Exception as e:
        return _err(e)


@mcp.tool()
def governance_list() -> str:
    """List all governance entries. Returns array of {path, includes, mode}.

    Mode is 'rule' (auto-loaded) or 'convention' (on-demand).
    """
    if err := _check_db(): return err
    try:
        return _ok(gov.governance_list(DB_PATH))
    except Exception as e:
        return _err(e)


@mcp.tool()
def governance_order() -> str:
    """Topologically order governance entries for root-first traversal.

    Groups rules and conventions into levels via Tarjan's strongly-connected
    components algorithm on the governed_by dependency graph, then emits
    levels foundation-first. Files in the same level are mutually
    independent or mutually dependent (valid siblings).

    Detects dangling references — governed_by targets that are not
    themselves governance entries. When dangling references exist, levels
    is empty and dangling carries the offending edges; the caller must fix
    the frontmatter and re-query before proceeding.

    Returns {levels: [[{path, governors: [str, ...]}, ...], ...], dangling: [{entry_path, missing}, ...]}.
    """
    if err := _check_db(): return err
    try:
        return _ok(gov.governance_order(DB_PATH))
    except Exception as e:
        return _err(e)
