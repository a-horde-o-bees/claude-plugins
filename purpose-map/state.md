# Evaluation State

For the data model, CLI, and operational protocol, see `CLAUDE.md` in this folder. This file holds only what's needed to resume work from where it was last left.

## Current Position

**v0.1.0 of the ocd plugin is released.** Branch and tag at `v0.1.0`. Release contains:

- Locked-down skills: init, status, navigator, commit, push, log, md-to-pdf
- Rules and conventions (design-principles, workflow, system-documentation, process-flow-notation, log-routing, markdown — and the matching convention templates)
- Libraries: governance (disk-only), navigator (SQLite-backed), each with its own README + architecture
- Navigator MCP server (thin adapter over `lib/navigator/`)
- Plugin infrastructure (hooks, framework, install_deps, run.py)

Main branch is active dev. Versioning rule (documented in `CLAUDE.md`): main tracks `0.0.z` permanently as a dev build counter; release branches own real semver with disjoint version spaces.

## Remaining Work on Main

Ordered by dependency, not priority. None of this blocks the existing v0.1.0 — all of it is candidate content for v0.2.0.

### audit-static and audit-governance (in development)

Both skills exist on main but aren't locked down. Manual convention audit during v0.1.0 prep surfaced residual issues. To finish:

- [ ] audit-static: verify --target resolution for every input form (slash-qualified, filesystem path, skill path); exercise on representative targets and triage observations
- [ ] audit-governance: exercise on the full governance chain end-to-end; triage observations; decide whether the `_audit-workflow-A.md` vs `_audit-workflow-B.md` A/B is still live or can collapse to one
- [ ] Self-audit both skills via audit-static once they're stable

### update-system-docs (design-only placeholder)

`SKILL.md` is a placeholder flagged `disable-model-invocation: true` + `user-invocable: false`. `_DESIGN.md` is the canonical design — everything needed to implement is documented there. Prior partial-implementation component files were removed during main-branch cleanup.

Implementation work (from _DESIGN.md Residual Work Items):

- [ ] Discovery CLI (`plugins/ocd/skills/update-system-docs/__main__.py` + `_discovery.py`)
- [ ] Fact-bundle builder (ast-based Python module)
- [ ] Navigator schema extension for `doc_verified_at` hash markers (separate sub-task)
- [ ] `ast.parse` reliability probe in a worktree (confirms fact-bundle foundation)
- [ ] Idempotence verification — run twice on unchanged reality; assert zero diff
- [ ] End-to-end on `lib/governance`; calibrate prompts
- [ ] Iterate until stable

### Mass documentation audit (depends on update-system-docs)

Once update-system-docs is stable, run it whole-project to regenerate canonical docs and surgical-edit non-obvious surfaces. Tune prompts based on observed gaps. Run until output converges.

### Cut v0.2.0

Once audit-* skills are locked down (and optionally update-system-docs has landed), branch v0.2.0 from main using the same release-branch process: strip dev-only content, regenerate consumer-facing docs for release scope, tag.

## Deferred Post-v1

- **blueprint plugin** — substantial MCP-backed research workflow. Not evaluated against current governance; re-enters active development when the prerequisites (audit tooling, doc regen) settle.
- **adhd plugin** — not yet created; noted only so the name doesn't get taken.

## Purpose-Map Methodology Status

`purpose-map/` tooling exists but is not actively applied in the current workflow. When to reach for it:

- **Before adding a substantial component** — run the unmet test (`addresses`, `how`, `needs --gaps`) to justify against a specific refined need
- **Pruning** — `addresses --orphans` and `uncovered` surface vestigial content

Outstanding methodology items:

- **Stale components carry over** — c41 (friction server), c42 (decisions server), c43 (stash server) were removed earlier in the v2 build-up; needs n59 (friction signals) and n68 (ideas/observations) are now gaps. Rewire these to the current file-based log system (no MCP server) when those components are formally evaluated.
- **`purpose-map/skill-migration.md`** — archival planning doc referencing a now-removed Pit of Success principle. Decide: action the migration, or delete as abandoned planning.

## Non-Blocking Concerns

- **Convention loading on read** — conventions currently surface on Read/Edit/Write via the convention_gate hook. Governance reads from disk on every call, so behavior is already correct; the note is kept in case future cache introduction reopens the question.
- **Print() usage review** — deferred during the earlier logging convention drop. Pick up next time CLI output surface gets substantial edits.
- **Logged problems awaiting action** — see `.claude/logs/problem/` for currently open items (governance test coverage thin vs navigator, convention-agent test missing worktree isolation, principle-proposal entries for autonomous execution and capability-gap flagging, worktree isolation leak, plugin name resolution repeat-path risk).

## v1 Reference Database

The v1 purpose-map database is preserved at `purpose-map-v1.db` (read-only). Useful when re-adding a component — rationale text is often portable with sharpening for the more-specific sub-need. v1 had 43 components, 97 addressing edges, 19 roots. Ids are not preserved across v1→v2.

```bash
python3 -c "import sqlite3; db = sqlite3.connect('purpose-map/purpose-map-v1.db'); [print(r) for r in db.execute('SELECT * FROM components ORDER BY CAST(SUBSTR(id, 2) AS INTEGER)')]"
```

## Key Files

- `purpose-map/CLAUDE.md` — methodology operational reference; read first on entry
- `purpose-map/purpose_map.py` — tool implementation
- `purpose-map/purpose-map.db` — live v2 database
- `plugins/ocd/templates/{rules,conventions,patterns,logs}/*` — governance templates
- `plugins/ocd/skills/*/SKILL.md` — skills (released set on v0.1.0 branch; full set on main)
- `plugins/ocd/lib/navigator/` — navigator library (own README + architecture)
- `plugins/ocd/lib/governance/` — governance library (own README + architecture)
- `plugins/ocd/servers/navigator.py` — navigator MCP server (thin adapter)
- `plugins/ocd/plugin/` — plugin framework (generic, shared across plugins)
- `plugins/ocd/hooks/` — auto-approval and convention_gate hooks
- `scripts/sync-templates.py` — template → deployed copy sync (dev-only)
