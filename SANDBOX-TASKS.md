# Sandbox: blueprint-plugin

Bring the blueprint plugin to parity with ocd's `systems/` layout (`bin/blueprint-run` wrapper, auto-promotion via `run.py`, sweep SKILL.md / README invocations to the new convention) and queue the post-v1 improvements identified during best-practices research.

## Pointers

- (none captured during migration)

## Tasks

### Blueprint plugin parity (v1)

- [ ] Mirror the `systems/` layout (flatten any remaining `lib/` / `servers/` / `skills/` splits)
- [ ] Add `bin/blueprint-run` wrapper following the `<plugin>-run` convention
- [ ] Update `run.py` auto-promotion (copy from ocd's)
- [ ] Sweep SKILL.md / README invocations to `blueprint-run <name>` form
- [ ] Rename any command-colliding skills (same pattern as `/ocd:plugin` → `/ocd:setup` and `/ocd:commit`+`/ocd:push` → `/ocd:git`)

### Post-v1 improvements (from best-practices research)

- [ ] External research ingestion — add `--source` route to `/research` for parsing existing documents into entity registrations
- [ ] Conditional measure clearing — only clear measures when criteria changed, not when entities added
- [ ] PFN formalization gaps — fill in numbered steps in Phase 1 and Phase 3 workflows
- [ ] Static content directory recipe — add GitHub README / curated-list recipe to `directory-traversal.md`
- [ ] Duplicate resolution timing — `find-duplicates` should only run within deep-research `resolve-duplicates` workflow
- [ ] Phase 1 gate criteria — surface metrics at Phase 1 gate for data-backed readiness check

### Re-engagement note

Blueprint is a substantial MCP-backed research workflow. It hasn't been evaluated against current governance; re-enters active development once prerequisites (audit tooling, doc regen) settle.

## Open Questions

- (none yet)
