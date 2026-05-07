# Tasks

Persistent work tracker for the claude-plugins repository. Each entry is one line pointing at a `plans/<workstream>.md` (when context is non-trivial) or a `logs/idea/<title>.md` (when the task is awaiting input). Sections by status; full per-task detail lives in the linked file.

Project-scoped scan-once view. Per-sandbox `SANDBOX-TASKS.md` files (seeded by `/ocd:sandbox new`) own per-branch detail; `logs/idea/` holds the full backlog.

## In progress

- (none)

## Pending

- **System migrations to system-structure** — [plan](plans/system-migrations.md). Migrate each ocd system to the layout pioneered by the rules system. Sequenced smallest-first. Unblocked: rules-migration-validation done.
- **`ocd:init-python-project` skill** — [plan](plans/init-project-skill.md). Scaffold fresh Python projects with this repo's canonical patterns. Foundation landed in centralize-tools (PR #1); the skill itself is the next branch.

## Upcoming

- **Components relocation** — [plan](plans/components-relocation.md). Move workflow-scoped components into the workflows that need them; re-type cross-cutters (rule + ARCHITECTURE.md). Empty out `components/`, drop the enumeration from project-root CLAUDE.md.
- **AskUserQuestion interactive workflow check** — small follow-up from `rules-migration-validation`. Invoke `/ocd:setup rules install` (no args) via slash command and verify the agent picks `AskUserQuestion` for scope + lettered target selection per `workflows/install.md`. Standalone check; no plan needed.
- **Conditional memory loading** — [plan](plans/conditional-memory.md). Per-rule trigger-conditioned auto-load to reduce always-on token floor. Needs Anthropic-side coordination.
- **Prose → PFN sweep** — [plan](plans/pfn-sweep.md). Convert prose procedures to Process Flow Notation across the project.
- **Sub-flow extraction sweep** — [plan](plans/subflow-extraction.md). Extract conditional sub-flows into separate workflow/component files.

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

- **Setup status — wide table per scope** — rules and permissions return per-rule × per-scope grids via shared `setup.status_table` helper; aggregated `setup status` and per-system `setup <system> status` both render the wide format; row count for rules halves (60 → 30)
- **Setup CLI — generic verb dispatch + permissions promotion** — discovery contract loosened to require only `purpose()`; standard verbs (status / list / install / uninstall) tried first, fallback to `mod.dispatch(verb, args)` for systems with custom verb shapes; permissions promoted from special-case to regular migrated system; meta verbs renamed (`purposes` → `list`, `statuses` → `status`); misleading `<system> <verb>` generalization line dropped from banner
- **Setup CLI — list verb + multi-target install/uninstall** — universal `list` discovery verb (calls system's `list_items()`); install/uninstall accept multiple positional targets or `--all` flag; lettered selection stays in the agent-interactive workflow layer
- **Conventions — system-dormancy contract** — codifies the dormancy contract (invisible until installed, zero tokens, zero side effects, hook bail-out pattern); fires on hook files, MCP servers, system `__init__.py`, `SKILL.md`
- **System structure split** — `system-structure` (universal: 3-doc model + workflows/components) and `project-structure` (project-root: TASKS.md + plans/ + logs/ + project-only entry points) as separate conventions; both moved to `conventions/templates/`
- **CLAUDE.md format — Paths section default** — every CLAUDE.md follows the Required Sections framework (heading + purpose, optional inline, Paths table per enumeration rule, one-line cold-pickup); `claude-md.md` and `system-structure.md` codify the format
- **Rules migration validation — done** — see [plan](plans/rules-migration-validation.md). Validated rules + permissions through cached install; AskUserQuestion check carried over to Upcoming

Earlier:

- **Setup refactor + rules migration** — `governed_by` dropped, design-principles split into 24 files, auto-init removed, setup CLI rebuilt around `purposes`/`statuses`/`<system>`/`<system> <verb>` dispatch, governance folded into conventions backbone, rules system migrated to the system-structure layout
- **Convention set rebuilt around system-structure** — `system-structure.md` rule, `workflows-md.md` / `components-md.md` / `plans-md.md` / `tasks-md.md` conventions, `plugin-system.md` updated, `principle-not-symptom.md` consolidated from project-root drafts
- **Project root reorganized** — `plans/`, `components/`, `workflows/` subdirectories; CLAUDE.md collapsed to navigation hub
