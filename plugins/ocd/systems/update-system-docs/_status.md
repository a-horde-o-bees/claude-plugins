# In-Flight Status: update-system-docs

In-flight notes migrated from `purpose-map/state.md` when this system was boxed. Accumulates further work as development continues on this branch.

## Open Work

### update-system-docs (design-only placeholder)

`SKILL.md` is a placeholder flagged `disable-model-invocation: true` + `user-invocable: false`. `_DESIGN.md` is the canonical design — everything needed to implement is documented there. Prior partial-implementation component files were removed during main-branch cleanup.

Implementation work (from _DESIGN.md Residual Work Items):

- [ ] Discovery CLI (`plugins/ocd/systems/update-system-docs/__main__.py` + `_discovery.py`)
- [ ] Fact-bundle builder (ast-based Python module)
- [ ] Navigator schema extension for `doc_verified_at` hash markers (separate sub-task)
- [ ] `ast.parse` reliability probe in a worktree (confirms fact-bundle foundation)
- [ ] Idempotence verification — run twice on unchanged reality; assert zero diff
- [ ] End-to-end on `systems/governance`; calibrate prompts
- [ ] Iterate until stable
- [ ] Normalize argument-hint to post-refactor conventions (`--target project` pre-dates verb-flag pairing + positional preference; revisit when implementation lands)

### Mass documentation audit (depends on update-system-docs)

Once update-system-docs is stable, run it whole-project to regenerate canonical docs and surgical-edit non-obvious surfaces. Tune prompts based on observed gaps. Run until output converges.
