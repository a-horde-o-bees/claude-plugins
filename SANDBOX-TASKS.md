# Sandbox: verb-naming-rectification

Bring four agent-facing surfaces (MCP tools, CLI verbs, library functions, supporting docs) into a single coherent shape — one concept, one `_query` tool, one `_update` tool, one `_remove` tool, with `<noun>_<verb>` naming. Convention-first; full-project scope; no transitional shims.

## Pointers

- `logs/idea/verb-naming-rectification.md` — canonical plan (Driving Goals, Resolutions captured, Per-target check pattern, all phases). Read this entire file before starting any phase; treat resolutions as load-bearing.
- `logs/problem/Verb naming convention not formally captured.md` — originating problem log; resolved at end of rectification.
- `logs/decision/mcp.md` — decide disposition before Phase 3 starts (supersede with pointer or delete).
- `logs/idea/Move check to project root tooling.md` — drives the `check` → `lint` rename in Phase 2.
- `plugins/ocd/systems/conventions/templates/mcp-server.md` — convention to revise in Phase 1.4.
- `plugins/ocd/systems/conventions/templates/cli.md` — sister convention; keep aligned.

## Tasks

### Phase 1 — Conventions

- [ ] Revise `plugins/ocd/systems/conventions/templates/mcp-server.md` — collapse write verbs to `_update` + `_remove` only; drop `set`/`clear`/`upsert` from the standard verb table; document `_update` as absorbing all field modifications with upsert-by-default semantics
- [ ] Update `plugins/ocd/systems/conventions/templates/cli.md` Verb Names table to match the collapsed write surface
- [ ] Settle disposition of `logs/decision/mcp.md` — supersede with one-line pointer to `mcp-server.md`, or delete

### Phase 2 — System renames

- [ ] Rename system `check` → `lint`

### Phase 3 — Per-target rectification (one commit per target; smallest first)

- [ ] 3.1 `settings_query` + `settings_update` (was `settings_get` + `settings_set`)
- [ ] 3.2 `projects_query` (was `projects_list`)
- [ ] 3.3 `purposes_update` (was `purposes_set` + `purposes_clear`)
- [ ] 3.4 `skills_query` (was `skills_list` + `skills_resolve`)
- [ ] 3.5 `paths_query` + `paths_update` + `paths_remove` (was `paths_get` + `paths_list` + `paths_search` + `paths_undescribed` + `paths_upsert`)

### Phase 4 — Surface sweeps

- [ ] CLI noun-verb migration per system — governance, log, navigator residuals, needs_map, pdf, refactor, sandbox, setup, check/lint
- [ ] Sweep all `SKILL.md` argument-hint frontmatter + Workflow PFN `bash:` invocations
- [ ] Sweep all MCP server `instructions` strings and tool descriptions
- [ ] Sweep all `README.md` / `CLAUDE.md` / `ARCHITECTURE.md` files across systems
- [ ] Sweep all test files for renamed library functions, MCP tool names, CLI verbs
- [ ] Sweep cross-plugin docs for navigator/transcripts tool references

### Phase 5 — Convergence

- [ ] Re-grep loop until an iteration produces zero new findings AND zero convention updates — legacy read verbs (`_get` / `_list` / `_search` / `_find`), legacy write verbs (`_set` / `_add` / `_clear` / `_upsert`), verb-first MCP tool names, flat CLI verbs that should be nested, old system name `check`
- [ ] Mark `logs/problem/Verb naming convention not formally captured.md` resolved
- [ ] Delete `logs/idea/verb-naming-rectification.md`

## Open Questions

- Allowed exceptions for legacy verbs `_get` / `_list` (public API contracts that can't break)? Default per idea file: no, full conformance — document any exception with rationale.
- CLI verb structure for categorical commands (`check dormancy` / `check markdown` / `check python` / `check all`) — keep flat as `lint <dimension>`, or restructure as `lint run --dimension X`? Decide during the `check` → `lint` rename target.
