---
log-role: reference
---

# MCP

Decisions governing MCP server design — subprocess bootstrap, tool shape, and the division between domain operations and generic data access.

## MCP subprocess bootstraps project dir from cwd

### Context

The path resolution refactor made `plugin.get_project_dir()` raise when `CLAUDE_PROJECT_DIR` is unset, on the principle that silent cwd fallback corrupts state when code runs from the wrong directory (see also: decision/framework.md ## Plugin env vars raise vs fallback). This broke all MCP servers that migrated to `plugin.get_project_dir()` because Claude Code does not propagate `CLAUDE_PROJECT_DIR` to MCP subprocesses automatically.

### Options Considered

**Expand `${CLAUDE_PROJECT_DIR}` in `.mcp.json` env block values.** Claude Code expands `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_PLUGIN_DATA}` in `command` and `args` fields, so the reasonable assumption was that env block values support the same expansion. Attempted as a one-line addition to each server's env block.

**Revert `get_project_dir()` to cwd fallback universally.** Simple, restores the old behavior, gives up the safety gained from raising.

**Bootstrap `CLAUDE_PROJECT_DIR` from `Path.cwd().resolve()` at MCP server import time, scoped to `servers/_helpers.py`.** Preserves the raising behavior for all non-MCP contexts; MCP servers have a Claude Code contract that their cwd is the project root, so the bootstrap is safe specifically for that context.

### Decision

Bootstrap `CLAUDE_PROJECT_DIR` from cwd in `servers/_helpers.py` at import time, scoped to the MCP context only.

Option 1 was tried first and did not work. Claude Code's variable expansion is scoped to `command` and `args` fields only. Inside `env` block values, `${CLAUDE_PROJECT_DIR}` passes through as a literal string. In the MCP subprocess, `os.environ["CLAUDE_PROJECT_DIR"]` then contained the literal `${CLAUDE_PROJECT_DIR}`. Downstream, `plugin.get_project_dir()` returned `Path("${CLAUDE_PROJECT_DIR}").resolve()`, which is `cwd / ${CLAUDE_PROJECT_DIR}` — a path under the real project root with a directory name literally equal to `${CLAUDE_PROJECT_DIR}`.

The `decisions` and `stash` MCP servers "succeeded" at writes during in-session verification — but the writes landed at `${project_root}/${CLAUDE_PROJECT_DIR}/.claude/ocd/decisions/decisions.db` and `${project_root}/${CLAUDE_PROJECT_DIR}/.claude/ocd/stash/stash.db`. Real decisions saved via MCP in that state were lost when the garbage directory was removed; they had to be re-added via direct Python skill calls. The failure mode was silent.

The `navigator` MCP server returned mostly-empty data because its scanner walked the garbage directory, finding only the stash/decisions databases that `decisions`/`stash` had just created there. This is what made the failure visible.

Option 3 is verified working after restart: all four MCP servers resolve project paths correctly via the cwd-derived `CLAUDE_PROJECT_DIR`, and no new garbage directory is created.

### Consequences

- **Enables:** MCP servers work correctly without requiring Claude Code platform changes
- **Enables:** `plugin.get_project_dir()` continues to raise in CLI, hook, and test contexts, preserving the silent-wrong-cwd protection for those call sites
- **Constrains:** the exception is narrow but real — someone reading framework-level rules sees "never use cwd fallback" followed by a pointer to one documented exception scoped to MCP servers. Keeping these cross-references in sync matters
- **Constrains:** if Claude Code ever starts propagating `CLAUDE_PROJECT_DIR` to MCP subprocesses automatically, the bootstrap becomes redundant but harmless (the guard `if "CLAUDE_PROJECT_DIR" not in os.environ` becomes a no-op)
- **Constrains:** if a new MCP server is added without importing `servers/_helpers.py`, the bootstrap will not fire and the server will raise. The convention states that all ocd servers must import `_helpers` for this reason (in addition to `_ok`/`_err`)

## Domain tools over generic CRUD

### Context

Blueprint research MCP server initially exposed generic CRUD tools (`create_records`, `read_records`, `update_records`, `delete_records`) with a raw SQL escape hatch (`query`). This led to progressive scope creep toward reimplementing a SQL query builder in JSON — adding operators, conditions, joins, then considering aggregation, ordering, grouping, and subquery composition. Each addition moved further from the server's purpose without matching SQL's expressiveness.

The core problem: generic CRUD tools map to database operations, not domain operations. Agents end up constructing queries instead of expressing intent. The server routes by table name and parses operator syntax instead of encoding business rules.

### Options Considered

**Query builder** — extend `read_records` with `select`, `group_by`, `having`, `order_by`, subquery support. Approaches SQL expressiveness through JSON parameters. Rejected: produces JSON-flavored SQL that is harder to read than actual SQL, adds no business logic interception, and requires ongoing feature additions to match SQL capabilities.

**Domain tools** — replace generic CRUD with purpose-built tools named for what they do. Each tool encodes one operation on one property. Business logic (validation, normalization, dedup) lives in the tool implementation. Agents express intent (`reject_entity`, `add_notes`) rather than constructing queries.

**Raw SQL only** — expose only a query executor. Agents write SQL directly. Rejected: loses all business logic interception (dedup, stage validation, URL normalization, provenance tracking) that makes write operations deterministic.

### Decision

Domain tools. Four consistent verbs operating on entity properties:

- `set` — replace a value (scalar or entire collection)
- `add` — append to a collection
- `remove` — remove specific items from a collection
- `clear` — reset to null or empty

Each tool is named `{verb}_{property}` and takes the entity ID plus only what's changing. `register_entity` is the sole tool without an entity ID (it creates one). Query tools are named `get_*` / `list_*` / `find_*` for domain-specific reads.

No generic table parameter. No operator parsing. No query building. Missing read capability = new domain query tool.

The MCP server provides deterministic operations for agent-facing instructions where supporting data is relational. It is not a general-purpose database interface. Business logic lives in tools so agent instructions stay focused on domain decisions rather than data manipulation.

### Consequences

- **Enables:** agent instructions reference domain operations by name; business logic centralized in tool implementations; no drift toward query builder
- **Constrains:** new read patterns require new tools rather than flexible query construction
- **Mitigation:** purpose-built query tools cover all current phase workflows; `describe_schema` provides orientation; new tools are additive (no breaking changes to existing tools)
