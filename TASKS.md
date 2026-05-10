# Tasks

Persistent work tracker for the claude-plugins repository. Each entry is one line pointing at a `plans/<workstream>.md` (when context is non-trivial) or a `logs/idea/<title>.md` (when the task is awaiting input). Sections by status; full per-task detail lives in the linked file.

Project-scoped scan-once view. Per-sandbox `SANDBOX-TASKS.md` files (seeded by `/ocd:sandbox new`) own per-branch detail; `logs/idea/` holds the full backlog.

## In progress

- **Architecture refactor** — [plan](plans/architecture-refactor.md). Skills as the atomic unit of distribution; plugins as packaging conveniences for marketplace surface; new `progressive-composer` plugin fills the individual-skill-management gap; rules-system retains the always-on discipline library; conventions become categorical opt-in skills; MCP servers benched until context-cost case justifies reactivation; permissions becomes a Pattern B installer skill. Decisions captured across seven logs (`skill-architecture`, `skill-authoring`, `progressive-composer`, `plugin-compartmentalization`, `hook-scoping`, `mcp-benching`, `yagni-revocation`); two prior decisions survive (`state-location`, `ocd-run-self-update`). Phases A–I.
    - Phase A (decisions + plan) — done, this commit
    - Phase B (build progressive-composer plugin) — next pickup
    - Phases C–I — per plan; system migrations, MCP unwiring, permissions Pattern B, plugin compartmentalization, conventions migration, decision-log review

## Pending

- **`ocd:init-python-project` skill** — [plan](plans/init-project-skill.md). Scaffold fresh Python projects with this repo's canonical patterns. Foundation landed in centralize-tools (PR #1); the skill itself is the next branch. When implemented, follows the new skill-folder format per the architecture refactor (lands under Phase E or as parallel work).

## Upcoming

- **AskUserQuestion interactive workflow check** — small follow-up from prior rules-migration validation. Premise depends on whether setup-style interactive workflows survive the architecture refactor. Re-evaluate when Phase F (permissions to Pattern B) lands and we know what's left of the setup system.
- **Working-directory limitation revocation** — small refactor: revoke the working-directory rule (currently the only content of `working-directory.md`) once `bin/` executables are callable from any directory and permission auto-approvals are adjusted accordingly. Standalone task; resolvable independent of the architecture refactor.

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

## Done (recent)

This session's commits:

- **Rules + conventions — wipe includes/excludes, restructure templates** — wiped `includes:`/`excludes:` from all rule and convention templates (replacement mechanism is the discovery model); tagline frontmatter added across conventions; carved `workflow.md` rule (Hook-Registered File Renames → `components/hook-registered-files.md`, Agents → new `agent-spawning.md` rule, Push Blocking dropped, Working Directory kept under renamed `working-directory.md`); rewrote orphan deployed `mcp-headless-invocation.md` as broader `mcp-engineering.md` rule; removed deployed `.claude/conventions/` and orphan rule
- **Setup CLI — show verb + tagline-driven catalog** — adds `show <name>` to standard verbs; `list` returns brief taglines; full purposes via `show`; rule templates carry `tagline:` frontmatter; install/uninstall workflows clarified to use AskUserQuestion for scope and lettered Q/A for target selection
- **Setup status — wide table per scope** — rules and permissions return per-rule × per-scope grids via shared `setup.status_table` helper; aggregated `setup status` and per-system `setup <system> status` both render the wide format; row count for rules halves (60 → 30)
- **Setup CLI — generic verb dispatch + permissions promotion** — discovery contract loosened to require only `purpose()`; standard verbs (status / list / install / uninstall) tried first, fallback to `mod.dispatch(verb, args)` for systems with custom verb shapes; permissions promoted from special-case to regular migrated system; meta verbs renamed (`purposes` → `list`, `statuses` → `status`); misleading `<system> <verb>` generalization line dropped from banner
- **Setup CLI — list verb + multi-target install/uninstall** — universal `list` discovery verb (calls system's `list_items()`); install/uninstall accept multiple positional targets or `--all` flag; lettered selection stays in the agent-interactive workflow layer
- **Conventions — system-dormancy contract** — codifies the dormancy contract (invisible until installed, zero tokens, zero side effects, hook bail-out pattern); fires on hook files, MCP servers, system `__init__.py`, `SKILL.md`
- **System structure split** — `system-structure` (universal: 3-doc model + workflows/components) and `project-structure` (project-root: TASKS.md + plans/ + logs/ + project-only entry points) as separate conventions; both moved to `conventions/templates/`
- **CLAUDE.md format — Paths section default** — every CLAUDE.md follows the Required Sections framework (heading + purpose, optional inline, Paths table per enumeration rule, one-line cold-pickup); `claude-md.md` and `system-structure.md` codify the format
- **Rules migration validation — done** — Validated rules + permissions through cached install; AskUserQuestion check carried over to Upcoming

Earlier:

- **Setup refactor + rules migration** — `governed_by` dropped, design-principles split into 24 files, auto-init removed, setup CLI rebuilt around `purposes`/`statuses`/`<system>`/`<system> <verb>` dispatch, governance folded into conventions backbone, rules system migrated to the system-structure layout
- **Convention set rebuilt around system-structure** — `system-structure.md` rule, `workflows-md.md` / `components-md.md` / `plans-md.md` / `tasks-md.md` conventions, `plugin-system.md` updated, `principle-not-symptom.md` consolidated from project-root drafts
- **Project root reorganized** — `plans/`, `components/`, `workflows/` subdirectories; CLAUDE.md collapsed to navigation hub
