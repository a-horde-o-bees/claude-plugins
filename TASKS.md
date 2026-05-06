# Tasks

Persistent work tracker for the claude-plugins repository. Each entry is one line pointing at a `plans/<workstream>.md` (when context is non-trivial) or a `logs/idea/<title>.md` (when the task is awaiting input). Sections by status; full per-task detail lives in the linked file.

Project-scoped scan-once view. Per-sandbox `SANDBOX-TASKS.md` files (seeded by `/ocd:sandbox new`) own per-branch detail; `logs/idea/` holds the full backlog.

## In progress

- (None at this checkpoint)

## Pending

- **System migrations to system-structure** — [plan](plans/system-migrations.md). Migrate each ocd system to the layout pioneered by the rules system. Sequenced smallest-first.
- **`ocd:init-python-project` skill** — [plan](plans/init-project-skill.md). Scaffold fresh Python projects with this repo's canonical patterns. Foundation landed in centralize-tools (PR #1); the skill itself is the next branch.

## Upcoming

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

- **Setup refactor + rules migration** — `governed_by` dropped, design-principles split into 24 files, auto-init removed, setup CLI rebuilt around `purposes`/`statuses`/`<system>`/`<system> <verb>` dispatch, governance folded into conventions backbone, rules system migrated to the system-structure layout
- **Convention set rebuilt around system-structure** — `system-structure.md` rule, `workflows-md.md` / `components-md.md` / `plans-md.md` / `tasks-md.md` conventions, `plugin-system.md` updated, `principle-not-symptom.md` consolidated from project-root drafts
- **Project root reorganized** — `plans/`, `components/`, `workflows/` subdirectories; CLAUDE.md collapsed to navigation hub
