# Tasks

Persistent work tracker for the claude-plugins repository. Each entry points at a `plans/<workstream>.md` or a `logs/<type>/<title>.md`. Sections by status; full per-task detail lives in the linked file.

Project-scoped scan-once view. Per-sandbox `SANDBOX-TASKS.md` files (seeded by the sandbox skill) own per-branch detail; `logs/idea/` holds the wider backlog.

## In progress

- **`skill-architecture` skill** — [plan](plans/skill-architecture.md). **Phase 1+2 complete 2026-05-21** (W1 scaffold + W2 assertions relocated from `logs/assertions/skill-runtime/` + W3 platform-discovery topic with `project-dir-resolution` assertion + W4 architecture.md and confirmed-facts.md). **Awaiting user review.** Phase 3 (W5 `reassert` runner + W6 decommission standing fixtures) gated by plan Open Questions S2 (scratch dir), S3 (test-design parseability), S4 (detection-method automation). Phase 4 (W7 wire `skill-creator` + `skill-composer` as consumers) can start in parallel — lighter weight, depends only on architecture.md being stable.
- **Phase G — permissions plugin authoring** — [plan](plans/architecture-refactor.md). Author a Pattern B skill in `plugins/permissions/` that deploys hook config to `.claude/settings.json` on invocation. Last open piece of Phase G; original setup-system permissions verbs migrate here.
- **Phase I — decision log review** — [plan](plans/architecture-refactor.md). 1 of 19 logs remaining: `logs/decision/progressive-skill-composer.md` (large; defer to focused session).

## Upcoming

- **Transcripts modernization** — [plan](plans/transcripts.md). **In progress 2026-05-31.** Two coupled workstreams: (A) move DB to `~/.claude/transcripts.db` (top-level file; security driver — per-project DB pollutes any project lacking the gitignore entry, while auto-sync pulls all sessions across projects); (B) hash-reference table for repeated content (skill bodies, system-reminder lists) to shrink DB and save read-time context. Workstream A ships first with current-project default scope; B has an empirical gate at B3.
- **Git plugin submodule expansion** — [plan](plans/git-plugin-submodule-expansion.md). Recursive submodule-first commit/push/CI cycle across all 5 git skills. Design aligned 2026-05-21: classifier recurses, always runs submodules, non-blocking on suspicious changes, support script over inline commands. Related pre-rollout adjustments captured in the same plan: `## Dependencies` declarations (PFN universally, prose-discipline skills on /git-commit), frontmatter allowed-tools audit, eventual application of the canonical closing release line once `logs/assertions/skill-runtime/` settles. Submodule recursion itself is grammar-independent and can start any time.
- **Phase D — navigator off MCP** — [plan](plans/architecture-refactor.md). CLI-from-MCP migration pattern is the same as transcripts; navigator's storage-location move should follow the pattern that `plans/transcripts.md` Workstream A lands — top-level path under `~/.claude/` (likely `~/.claude/navigator.db` or similar), informed by skill-architecture's project-dir-resolution assertion. Lands at `plugins/navigator/`.
- **Phase E — remaining ocd-old systems** — 8 systems: needs-map, check, pdf, sandbox, log, navigator, setup, refactor. Each migrates to its target plugin home per Phase G layout. `setup` partially dissolves into the `permissions/` plugin (Phase F/Phase G overlap). `retrospective` migrated 2026-05-21 to `plugins/memory/` (holding bucket for session-boundary / memory-adjacent skills).
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
