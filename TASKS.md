# Tasks

Persistent work tracker for the claude-plugins repository. Each active workstream is one `plans/<topic>.md`; full detail lives there. Sections by status. Scan-once view — completed work is in `git log`, not here.

## Active

- **agentic-os** — **start here.** — [plan](plans/agentic-os.md). Make the live skill folders (`~/.claude/skills/`, project `.claude/skills/`) the source of truth — instant, no checkpoint cycle — with a one-way publish into this repo as the distribution mirror; plus a home-as-repo backup (bare repo, allowlist gitignore, secrets layers, project-remotes manifest). Phase 1 (skill inversion) is the near-term lift; Phase 2 (home repo) is independent.
- **transcripts** — [plan](plans/transcripts.md). Two independent workstreams: content hash-reference dedup (shrink DB + read context) and persisted blocks/topics for billable-time reporting. Either may proceed first.
- **git-plugin** — [plan](plans/git-plugin.md), north star in `plugins/git/GOALS.md`. Full lifecycle shipped; `--auto` runs it hands-off; submodules route by detection (ownership/fork/protection + native `.gitmodules` keys) through one `pr.py routes` pre-flight that halts on any gap. **Remaining (detail in plan):**
  - **Submodule routing** — Phase 2 (cross-fork upstream contribution: `x-contribute` cadence + cross-fork PR); Phase 3 (track/keep-up sync via `update=rebase|merge`); live e2e against a real protected submodule (never exercised — monaco's branches are unprotected); remove dead `pr.py` `protection`/`repo-route` subcommands + unwired `reconcile_merge`; the `git-pr-status`/`git-pr-merge` `pr.py` copies are hand-synced (propagator disabled) — a divergence trap.
  - **CI-domain follow-ons** — `actionlint` wrap, per-stack hardened scaffolder, `tests/` harness, `startup_failure` detector (audit/harden/reconcile core built).
  - default-branch belt-and-suspenders cleanup; `markdown-lint`'s `literal-special-chars` mis-flags PFN notation across skill bodies (a markdown-linter-skill concern).

## Deferred

- **Decision-log review** — walk `logs/decision/*.md` against final implementation and rectify stale references, including dangling links to the plans retired below. Sequenced **after** agentic-os, transcripts, and git-plugin land — rectify once the dev environment is settled and stable. Substantive remainder: `logs/decision/progressive-skill-composer.md` (large), plus the retired-plan links the 2026-06-01 restructure left behind.

## Active sandbox branches

Each carries its own `SANDBOX-TASKS.md`; open the sandbox and run `/sandbox tasks` to read the running checklist.

| Feature | Branch | Status |
|---------|--------|--------|
| Blueprint plugin parity | `sandbox/blueprint-plugin` | Main's blueprint plugin retired; sandbox holds the rebuild attempt pending disposition |
| audit-governance skill | `sandbox/ocd/audit-governance` | Premise needs revisit post-governance/conventions merge |
| audit-static skill | `sandbox/ocd/audit-static` | Active |
| update-system-docs skill | `sandbox/ocd/update-system-docs` | Active |

## Retired 2026-06-01

Dropped rather than tracked — a stale plan only drifts and accrues maintenance. The underlying files get reviewed fresh once the OS is stable (per the agentic-os direction).

- **`architecture-refactor.md`** — the phased master plan (Phases A–I). Its live work is either shipped (skills-as-unit, plugin-deps, compartmentalization) or moved into the topic plans above; its remaining forward item (decision-log review) is now tracked under Deferred.
- **`skill-architecture.md`** — build plan for a skill that is itself under reconstruction (prior recommendations rested on a flawed measurement mechanic and were withdrawn). Revisit when the reconstruction direction is set.
- **permissions plugin / ocd-old legacy migration / navigator-off-MCP** — were Phases F / E / D of architecture-refactor. Not separately tracked; revisit fresh if still wanted.
- **`pr-workflow-migration.md` / `git-plugin-pr-workflow.md` / `git-plugin-submodule-expansion.md`** — consolidated into `git-plugin.md`; the migration plan (server-side auto-bump) is defunct.

## Backlog

Lower-priority and exploratory items remain captured under `logs/idea/<title>.md` — the queue; this file is the active view.
