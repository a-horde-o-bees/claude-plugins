# Tasks

Persistent work tracker for the claude-plugins repository. Each entry points at a `plans/<workstream>.md` (for non-trivial workstreams) or a `logs/idea/<title>.md` (for backlog items). Sections by status; full per-task detail lives in the linked file.

Project-scoped scan-once view. Per-sandbox `SANDBOX-TASKS.md` files (seeded by the sandbox skill) own per-branch detail; `logs/idea/` holds the wider backlog.

## In progress

- **Phase G — Plugin compartmentalization** — [plan](plans/architecture-refactor.md). Active next phase. Break the `ocd` plugin into domain buckets (proposed: `git`, `discipline`); retire the `composed-skills` bucket — composed skills land in their domain bucket with `composition.md` marking origin. `skill-authoring` stays as-is (the domain IS skill authoring). Per-domain plugin manifests update `marketplace.json` so downstream consumers can `/plugin install <domain>@a-horde-o-bees` per bucket.

    **Distribution model after reorg.** Two parallel channels remain first-class:

    1. **Plugin install (marketplace)** — `/plugin install <plugin>@a-horde-o-bees` for downstream users who want bundles. Marketplace listing continues to increment as skills evolve.
    2. **Individual skill install (npx)** — `npx skills add a-horde-o-bees/claude-plugins --skill <name> -g` for users who want one skill at a time. This project uses npx for its own consumption per `.claude/installed-skills.json`.

- **Phase I — Decision log review** — review `logs/decision/*.md` against final implementation; slim scaffolding, remove obsolete options-considered branches, drop logs whose decisions are superseded. Active this session.

## Upcoming

- **Phase D — Transcripts and navigator off MCP** — [plan](plans/architecture-refactor.md). Both systems still live in `plugins/ocd-old/systems/`. Migrate each to skill format bridging the existing `ocd-run` CLI; remove MCP server registration to recover always-on context cost.

- **Phase E — Remaining `ocd-old/systems/` migrations** — [plan](plans/architecture-refactor.md). Pending systems with `SKILL.md` in `plugins/ocd-old/systems/`: transcripts, needs-map, check, pdf, sandbox, log, navigator, setup, retrospective, refactor. Each migrates as its own focused commit; on the last one, `bin/ocd-run` + `bin/ocd-path` + dependency-script propagation rules retire. Migrated systems land in the appropriate domain plugin folder per Phase G.

- **Phase F — Permissions to Pattern B** — [plan](plans/architecture-refactor.md). Permissions becomes a standalone Pattern B skill that, on invocation, deploys hook config to `<scope>/.claude/settings.json`. Setup system loses one of its reasons to exist and may fully dissolve.

- **Phase H — Conventions as situational-load skill** — [plan](plans/architecture-refactor.md). Conventions stay as dependency files (`<scope>/.claude/dependencies/<name>.md`); a new user-facing skill lets users call a convention into context on demand for any task. Same root files; two access patterns — skill-declared deps that auto-load when their skill fires, and on-demand user-driven load via the new skill. Pre-work done: `convention_gate` hook removed; `.claude/conventions/` directory wiped; canonicals remain at `plugins/ocd-old/systems/conventions/templates/` as source-of-truth.

- **`claude-python` composition** — first end-to-end exercise of the composed-skills workflow, reframed to land in a domain plugin (likely a new `python` plugin or similar). Five exemplar sources identified: `affaan-m/everything-claude-code:python-patterns` + `python-testing`, `laurigates/claude-plugins:uv-run`, `sickn33/antigravity-awesome-skills:python-packaging` + `python-pro`. Lands after Phase G defines the domain plugin layout.

- **AskUserQuestion interactive workflow check** — small follow-up from prior rules-migration validation. Premise depends on whether setup-style interactive workflows survive Phase F. Re-evaluate when Phase F lands.

- **Working-directory limitation revocation** — small refactor: revoke the working-directory rule once `bin/` executables are callable from any directory and permission auto-approvals are adjusted. Standalone task; resolvable independent of the architecture refactor.

## Active sandbox branches

Each carries its own `SANDBOX-TASKS.md`; open the sandbox and run `/sandbox tasks` to read the running checklist.

| Feature | Branch | Status |
|---------|--------|--------|
| Blueprint plugin parity | `sandbox/blueprint-plugin` | Plugin failed to load in marketplace; sandbox holds the rebuild |
| audit-governance skill | `sandbox/ocd/audit-governance` | Premise needs revisit post-governance/conventions merge |
| audit-static skill | `sandbox/ocd/audit-static` | Active |
| update-system-docs skill | `sandbox/ocd/update-system-docs` | Active |

## Backlog

Lower-priority and exploratory items remain captured under `logs/idea/<title>.md`. Items promote into the sections above when picked up; the `idea/` directory is the queue, this file is the active view.

Completed work is in `git log`, not here — TASKS.md is a living log of what's active and what's coming, not a historical record.
