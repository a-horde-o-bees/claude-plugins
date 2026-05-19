# Tasks

Persistent work tracker for the claude-plugins repository. Each entry points at a `plans/<workstream>.md` or a `logs/<type>/<title>.md`. Sections by status; full per-task detail lives in the linked file.

Project-scoped scan-once view. Per-sandbox `SANDBOX-TASKS.md` files (seeded by the sandbox skill) own per-branch detail; `logs/idea/` holds the wider backlog.

## In progress

- **Phase G — permissions plugin authoring** — [plan](plans/architecture-refactor.md). Author a Pattern B skill in `plugins/permissions/` that deploys hook config to `.claude/settings.json` on invocation. Last open piece of Phase G; original setup-system permissions verbs migrate here.
- **Phase I — decision log review** — [plan](plans/architecture-refactor.md). 1 of 19 logs remaining: `logs/decision/progressive-skill-composer.md` (large; defer to focused session).

## Upcoming

- **Phase D — navigator off MCP** — [plan](plans/architecture-refactor.md). Migration pattern (bash CLI, drop MCP server bits) is the same as transcripts. Lands at `plugins/navigator/`.
- **Phase E — remaining ocd-old systems** — 9 systems: needs-map, check, pdf, sandbox, log, navigator, setup, retrospective, refactor. Each migrates to its target plugin home per Phase G layout. `setup` partially dissolves into the `permissions/` plugin (Phase F/Phase G overlap).
- **Universal always-on subset** — which discipline skills to promote via `/rules add <skill>`. Candidates: `honesty`, `concise-prose`, `principled-pushback`, `fix-foundations-not-symptoms`. User decides which to promote.
- **`claude-python` composition** — unblocked by Phase G defining domain plugin layout.
- **AskUserQuestion interactive workflow check** — small follow-up; re-evaluate when permissions plugin lands.
- **Working-directory limitation revocation** — standalone refactor; resolvable independently.

## Active sandbox branches

Each carries its own `SANDBOX-TASKS.md`; open the sandbox and run `/sandbox tasks` to read the running checklist.

| Feature | Branch | Status |
|---------|--------|--------|
| Blueprint plugin parity | `sandbox/blueprint-plugin` | Main's blueprint plugin retired; sandbox holds the rebuild attempt pending disposition |
| audit-governance skill | `sandbox/ocd/audit-governance` | Premise needs revisit post-governance/conventions merge |
| audit-static skill | `sandbox/ocd/audit-static` | Active |
| update-system-docs skill | `sandbox/ocd/update-system-docs` | Active |

## Backlog

Lower-priority and exploratory items remain captured under `logs/idea/<title>.md`. Items promote into the sections above when picked up; the `idea/` directory is the queue, this file is the active view.

Completed work is in `git log`, not here — TASKS.md is a living log of what's active and what's coming, not a historical record.
