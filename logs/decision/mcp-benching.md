---
log-role: reference
---

# MCP Benching

Decision to bench existing MCP servers (transcripts, navigator) and route their functionality through bash CLIs (`ocd-run <system> <verb>`) instead. Reactivate MCPs only when a context-cost case justifies their always-on overhead.

## Context

Existing ocd plugin systems with MCP servers:

- **transcripts** — MCP server exposes ~10 tools (sessions_query, exchanges_query, purposes_set/clear, schema_describe, sql_query, etc.)
- **navigator** — MCP server exposes ~10 tools (paths_get, paths_search, paths_list, paths_upsert, paths_remove, paths_undescribed, references_map, scope_analyze, skills_resolve, skills_list)

MCP servers cost always-on context for tool registration — every tool's name, description, and schema lives in the agent's context whether or not the tool is used. For systems used intermittently (the user noted navigator has been "too context-heavy as an MCP"), the always-on cost outweighs the per-use parse-savings benefit.

Both systems already expose bash CLIs via `ocd-run <system> <verb>`. The MCP layer is supplementary — it adds native tool integration and avoids parsing bash output, but the underlying functionality is reachable via Bash tool.

## Options Considered

**Keep MCPs as the primary interface; tolerate always-on cost.** Rejected: context floor is the dominant cost in the architecture refactor's motivation. Tool registrations for systems used a few times per session don't earn their always-on weight.

**Make MCPs optional via per-system enable flag.** Rejected: adds configuration burden; users have to reason about which MCPs to enable; defeats the simplicity of the new architecture. Easier to just bench all MCPs and add them back when a case is made.

**Bench all MCPs; route through bash CLIs by default.** Adopted. Zero always-on cost when not invoked. Native MCP integration returns when intermittent-use systems prove they need it.

## Decision

MCP server registrations are removed from `plugin.json` for transcripts and navigator. Skills authored for both systems invoke functionality via `uv run -m scripts.<verb>` per the skill-authoring decision; the migrated Python lives under each skill's `scripts/` package.

The MCP server *code* stays in the source tree (benched, not deleted). Reactivation is a `plugin.json` edit away if a future context-cost case justifies it. The criteria for reactivation:

- The system is used in most sessions (always-on overhead amortizes across high engagement)
- Bash output parsing introduces friction (e.g., the agent needs to call multiple tools and reason across them, where MCP tool semantics would be sharper)
- The context cost of tool registration is small relative to the per-session benefit

Until those criteria hit for a specific system, default is bash-CLI-only.

## Consequences

- **Enables:** measurable always-on token reduction once both systems migrate; aligns with skills-as-atomic-unit (skills are the discovery surface, not MCP tools); simpler authoring (one mechanism per system instead of two parallel surfaces)
- **Constrains:** bash output parsing burden lands on the agent for benched systems; per-call subprocess startup cost (vs persistent MCP connection); structured-output discipline matters more (agents parse mechanically — see `agent-first-interfaces` rule)
- **Migration path:** Phase D of `plans/architecture-refactor.md` handles the actual unwiring — remove MCP registrations, author SKILL.md bodies that bridge to bash, verify functional parity, measure context savings
- **Documentation:** MCP server docs (per-system ARCHITECTURE.md describing MCP tools) can stay during the bench — they remain accurate for the code that's preserved; rewrite when reactivation criteria hit
