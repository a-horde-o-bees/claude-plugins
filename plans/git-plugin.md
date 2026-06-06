# Git plugin — full-lifecycle orchestration

North star and principles: [`plugins/git/GOALS.md`](../plugins/git/GOALS.md) — read first. The full lifecycle has shipped; this plan tracks only what remains.

> **Handoff flag (resolve next session):** ~24 parked working-tree files from another session (skill-authoring, transcripts, `agentic-os.*`, `ARCHITECTURE.md`, logs, retired-plan deletions) are uncommitted and untouched — the user's to land. This plan's reconciliation and the `TASKS.md` git entry ride in that parked set; the non-git parked edits are another session's to reconcile.

## Open / remaining

1. **Submodule routing — Phase 2 & 3.** Phase 2: cross-fork upstream contribution — an `x-contribute = never|prompt|always` native `.gitmodules` key driving a cross-fork PR (`gh pr create --repo <parent> --head <owner>:<branch>`), with a pre-flight report of every protected branch a `--auto` sweep would admin-merge. Phase 3: track/keep-up sync — `update=rebase|merge` integrating upstream before edits, and the parent-pin churn it implies.
2. **Submodule routing — validation & cleanup.** Live e2e of the recursive-PR landing against a real protected submodule (never exercised — monaco's `monaco-overlays`/`main` are unprotected, so they route `direct`); a throwaway protected fixture is the smallest real test. Remove dead `pr.py` subcommands `protection` and `repo-route` (superseded by `routes`) and the unwired `reconcile_merge` (checkpoint reconciles inline). **Live trap:** `pr.py` is duplicated in `git-pr-status/` and `git-pr-merge/` and must be hand-synced — the pre-commit propagator is disabled (`core.hooksPath=.githooks`, `.githooks/` retired).
3. **CI domain (`_ci`) follow-ons** — wrap `actionlint` as a deeper validator; a per-stack hardened scaffolder; a `tests/` harness; a `startup_failure` detector. The audit/harden/reconcile core exists.
4. **Default-branch resolution** — `_default-branch` sets `origin/HEAD` at the root, making every inline `symbolic-ref` resolver correct; the remaining inline `… | fallback main` sites are belt-and-suspenders, not load-bearing.

## Where the remaining work lands

- **Routing engine** — `pr.py` (duplicated, hand-synced in `git-pr-{status,merge}/scripts/`): the `routes` pre-flight + pure `classify_repo`/`branch_gap`. Phase 2/3 and the dead-code cleanup live here.
- **Orchestrator** — `plugins/git/skills/git-checkpoint/`: the `routes` pre-flight gate + the recursive landing loop.
- **Doctor** — `plugins/git/skills/git-doctor/_submodule.md` + `scripts/detect.sh`: routing-gap detection and native-key writes.
- **Tests** — `tests/plugins/git/`, run via `bin/project-run tests --plugin git`.

## Out of scope

Per `GOALS.md`: PR review automation, auto-merge policy ownership, stacked-PR management, release-after-merge orchestration.
