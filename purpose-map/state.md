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

### Sandbox full-exercise test findings

Surfaced by `/ocd:sandbox exercise` (then named `test`) run against commit `1cb3f4e` (v0.0.292 ocd plugin). Each item is independent; take them one at a time. Ordered critical → cosmetic.

**Critical — sandbox skill itself:**

- [x] **Worktree subagent missing `AskUserQuestion` and agent-spawn tools.** *Resolved.* Worktree verb now drops `Spawn (isolation: "worktree"):` in favor of an executor-driven model: the invoking session creates an explicit git worktree at `.claude/worktrees/<topic>/`, drives test steps directly (bash via `env -C`, skills via Skill tool, prompts via `AskUserQuestion`), and cleans up at the end. Route Selection documents two residuals honestly: MCP tools bound at parent session start still see main's `CLAUDE_PROJECT_DIR`, and nested `Spawn:` inside invoked skills still hits the subagent tool-surface limit (executor drives those manually).
- [ ] **Sensitive-file gate behavior in worktree — unverified under new model.** Prior test showed writes to `.claude/logs/idea/*.md` completing without prompting inside the spawned subagent. Under the new executor-driven worktree the write should route through the parent session's permission context, where the gate's actual behavior applies. Re-validate by re-running the worktree portion of the full-exercise test after the skill rewrite lands.

**Skill surface issues:**

- [ ] **`/ocd:log <bogus-type>` dispatches without validating the type.** Skill routes to `_add.md` without pre-checking whether the type exists under `.claude/logs/`. Add a pre-dispatch validation that lists valid types.
- [ ] **`/ocd:pdf` setup requires `.claude/ocd/pdf/css/` mkdir that the sensitive-file gate blocks.** Skill's Workflow has no documented escape hatch. Either document the `--css <preset>` bypass, move the gated mkdir behind a lazy initializer invoked only when the user has explicitly opted into custom CSS, or provide a flag that skips the directory creation and uses the plugin-cache preset directly.

**Polish:**

- [ ] **Scan output omits `staled N parent(s)` phrase when a single parent cascades.** DB state is correct (parent row's `stale` flips to 1), but the user-visible summary only emits "Added N, removed N, changed N" without the staled-parent count in the single-parent case.
- [ ] **`setup init` (no `--force`) on a current install still prints all subsystem sections and "Done."** Cosmetic — the output doesn't convey "nothing to do" when deploy was a no-op.
- [ ] **`setup badverb` error comes from argparse, not the SKILL.md unrecognized-verb branch.** Either the SKILL.md fallback is dead code (remove), or argparse should not shadow it (reshape so skill-level handling runs first).
- [ ] **`paths_upsert` returns `action: "updated"` for the first-ever purpose on a scan-inserted row.** Semantics track row existence, not purpose transitions — the scan inserts a null-purpose row before the user's first upsert, which then "updates." Document or change so `"added"` covers the first meaningful purpose assignment.

### Cut v0.2.0

Once audit-* skills are locked down (and optionally update-system-docs has landed), branch v0.2.0 from main using the same release-branch process: strip dev-only content, regenerate consumer-facing docs for release scope, tag.

## Deferred Post-v1

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
- **`<plugin>-run` binary naming convention not codified** — established in practice for ocd (`bin/ocd-run` with suffix-style, object_action shape), and reasoned in commit `f31e0b5`. Not yet written into a convention doc. When a second plugin with a `<plugin>-run` wrapper lands, promote the pattern into a `plugin-layout.md` convention (or extend `skill-md.md`) so future plugins follow uniformly.
- **`install_deps.sh` plugin-binary collision check** — currently no guard for cases where `bin/<plugin>-run` collides with a command already on PATH. Low risk since `<plugin>-run` is inherently unique-ish, but a simple `command -v` probe during install_deps could warn the author proactively.
- **`test_deploy_exits_zero` permissions test fixture** — pre-existing failure in `tests/test_invocation.py`. The test invokes `plugin permissions deploy --scope project` in a tmp dir, but `recommended-permissions.json` isn't on the expected path so deploy reports "not found" instead of "added". Needs fixture rework to place the template where the deploy code looks for it.
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
- `plugins/ocd/systems/{rules,conventions,patterns,log,permissions}/templates/*` — governance and content templates (colocated with each system's deployer)
- `plugins/ocd/systems/*/SKILL.md` — skills (released set on v0.1.0 branch; full set on main)
- `plugins/ocd/systems/navigator/` — navigator system (SKILL + CLI + MCP server + tests, colocated)
- `plugins/ocd/systems/governance/` — governance library (own README + architecture)
- `plugins/ocd/systems/navigator/server.py` — navigator MCP server (thin adapter)
- `plugins/ocd/bin/ocd-run` — PATH-accessible Python dispatcher (resolves plugin venv, execs run.py)
- `plugins/ocd/run.py` — module launcher; auto-promotes bare names to `systems.<name>` when present
- `plugins/ocd/systems/framework/` — plugin framework (generic, shared across plugins; propagated to non-ocd plugins via pre-commit hook)
- `plugins/ocd/hooks/` — auto-approval, convention_gate, and install_deps hooks
- `scripts/auto_init.py` — auto-init orchestrator: force-run every system's init, prune orphans, reconcile DB backups, navigator scan (invoked by `/checkpoint`)
