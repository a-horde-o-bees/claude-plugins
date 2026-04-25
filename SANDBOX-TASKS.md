# Sandbox: ocd/update-system-docs

Implement the `/ocd:update-system-docs` skill from `_DESIGN.md` (currently a placeholder flagged `disable-model-invocation: true` + `user-invocable: false`); once stable, run it whole-project for the mass documentation audit.

## Pointers

- `plugins/ocd/systems/update-system-docs/_DESIGN.md` — canonical design; everything needed to implement is documented there
- (others as relevant)

## Tasks

- [ ] Discovery CLI (`plugins/ocd/systems/update-system-docs/__main__.py` + `_discovery.py`)
- [ ] Fact-bundle builder (ast-based Python module)
- [ ] Navigator schema extension for `doc_verified_at` hash markers (separate sub-task)
- [ ] `ast.parse` reliability probe in a worktree (confirms fact-bundle foundation)
- [ ] Idempotence verification — run twice on unchanged reality; assert zero diff
- [ ] End-to-end on `systems/governance`; calibrate prompts
- [ ] Iterate until stable
- [ ] Normalize argument-hint to post-refactor conventions (`--target project` pre-dates verb-flag pairing + positional preference; revisit when implementation lands)
- [ ] Mass documentation audit: once update-system-docs is stable, run it whole-project to regenerate canonical docs and surgical-edit non-obvious surfaces; tune prompts based on observed gaps; run until output converges

## Open Questions

- (none yet)
