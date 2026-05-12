# Tasks

Persistent work tracker for the claude-plugins repository. Each entry is one line pointing at a `plans/<workstream>.md` (when context is non-trivial) or a `logs/idea/<title>.md` (when the task is awaiting input). Sections by status; full per-task detail lives in the linked file.

Project-scoped scan-once view. Per-sandbox `SANDBOX-TASKS.md` files (seeded by `/ocd:sandbox new`) own per-branch detail; `logs/idea/` holds the full backlog.

## In progress

- **Architecture refactor** — [plan](plans/architecture-refactor.md). Skills-as-atomic-unit architecture; Phase B shipping (progressive-skill-composer + composed-skills bundle). Design rationale and pivot history live in `logs/decision/progressive-skill-composer.md` and the architecture-refactor plan.

    **Next concrete step:** compose `claude-python` as the first end-to-end exercise of the new workflow — `compose new --destination plugins/composed-skills/skills` from the progressive-skill-composer cache. Five exemplar sources identified: `affaan-m/everything-claude-code:python-patterns` + `python-testing`, `laurigates/claude-plugins:uv-run`, `sickn33/antigravity-awesome-skills:python-packaging` + `python-pro`. See `plans/composed-skills-workflow.md` for the maintainer flow.

    Pending phases: Phase C (pilot ocd system conversion), Phase D (MCP unwiring), Phase E (remaining ocd system migrations + retire `bin/ocd-run`), Phase F (permissions to Pattern B), Phase G (plugin compartmentalization), Phase H (conventions migration), Phase I (decision log review).

    **Recent state changes (uncommitted at landing of next checkpoint):** Rules slimming via concise-output (V8) convergence; `principle-not-symptom` merged into `trigger-specificity`; `trigger-specificity` relocated to `shared/dependencies/`; always-on `.claude/rules/ocd/` minimized to 18 files (substantively-revised + new + foundational shared deps); `.claude/conventions/` and `.claude/rules/ocd/systems/` wiped; `convention_gate` hook removed from `plugins/ocd-old/hooks/`. See *Stopgap: manual rules deployment* and *AIA cluster* sections in the architecture-refactor plan.

## Upcoming

- **Git skill migration (HIGH PRIORITY)** — `/ocd:git` (commit, push, ci, checkpoint, release verbs) is currently unloadable in this environment; the manual checkpoint exercise on 2026-05-12 surfaced the gap. Migrate ahead of other Phase E systems so the checkpoint loop is restored. Source at `plugins/ocd-old/systems/git/`; migration target follows the skill-as-atomic-unit shape (hyphenated folder, `scripts/` package, `_<verb>.md` flat layout, AIA cluster deps where applicable).
- **AskUserQuestion interactive workflow check** — small follow-up from prior rules-migration validation. Premise depends on whether setup-style interactive workflows survive the architecture refactor. Re-evaluate when Phase F (permissions to Pattern B) lands and we know what's left of the setup system.
- **Working-directory limitation revocation** — small refactor: revoke the working-directory rule once `bin/` executables are callable from any directory and permission auto-approvals are adjusted accordingly. Standalone task; resolvable independent of the architecture refactor. Note: `working-directory.md` is no longer deployed as always-on (frontmatter-strip-only canonical), but the rule still applies via the `workflow.md` content embedded in current session context until next session start.

## Active sandbox branches

Each carries its own `SANDBOX-TASKS.md`; open the sandbox and run `/ocd:sandbox tasks` to read the running checklist.

| Feature | Branch |
|---------|--------|
| Blueprint plugin parity | `sandbox/blueprint-plugin` |
| audit-governance skill | `sandbox/ocd/audit-governance` (premise needs revisit post-governance/conventions merge) |
| audit-static skill | `sandbox/ocd/audit-static` |
| update-system-docs skill | `sandbox/ocd/update-system-docs` |

## Backlog

Lower-priority and exploratory items remain captured under `logs/idea/<title>.md`. Items promote into the sections above when picked up; the `idea/` directory is the queue, this file is the active view.

Completed work is in `git log`, not here — TASKS.md is a living log of what's active and what's coming, not a historical record.
