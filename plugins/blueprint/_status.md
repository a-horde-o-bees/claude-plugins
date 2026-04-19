# In-Flight Status: blueprint-plugin

Notes migrated from `purpose-map/state.md` and logs when this plugin was boxed. Accumulates further work as development continues on this branch.

## Open Work

### Blueprint plugin parity

The ocd plugin consolidated into `systems/` with the `bin/ocd-run` wrapper and `ocd-run <name>` auto-promotion pattern during v0.2.0 development. Blueprint hasn't been updated yet. Work:

- [ ] Mirror the `systems/` layout (flatten any remaining `lib/` / `servers/` / `skills/` splits)
- [ ] Add `bin/blueprint-run` wrapper following the `<plugin>-run` convention
- [ ] Update `run.py` auto-promotion (copy from ocd's)
- [ ] Sweep SKILL.md / README invocations to `blueprint-run <name>` form
- [ ] Rename any command-colliding skills (same pattern as `/ocd:plugin` → `/ocd:setup` and `/ocd:commit`+`/ocd:push` → `/ocd:git`)

### Deferred Post-v1

- **blueprint plugin** — substantial MCP-backed research workflow. Not evaluated against current governance; re-enters active development when the prerequisites (audit tooling, doc regen) settle.

## Migrated Log: Blueprint plugin post-v1 improvements

Identified during best-practices research session. Deferred to post-v1.

1. **External research ingestion** — add --source route to /research for parsing existing documents into entity registrations
2. **Conditional measure clearing** — only clear measures when criteria changed, not when entities added
3. **PFN formalization gaps** — missing numbered steps in Phase 1 and Phase 3 workflows
4. **Static content directory recipe** — add GitHub README/curated list recipe to directory-traversal.md
5. **Duplicate resolution timing** — find-duplicates should only run within deep research resolve-duplicates workflow
6. **Phase 1 gate criteria** — surface metrics at Phase 1 gate for data-backed readiness check
