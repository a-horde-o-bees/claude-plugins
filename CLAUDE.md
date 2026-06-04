# claude-plugins — cold-pickup hub

A Claude Code plugin marketplace + skill development project. Most work is iterative skill authoring.

## Where to start

- **`TASKS.md`** — active workstreams + next concrete steps. The first thing to read.

## Workflow

Plugin work lands via PRs to `main`. Required status checks (`test`, `validate`, `bump-check`) gate the merge. Each affected plugin's patch version is bumped in the PR itself — the deployment signal for `claude plugins update`. The bump is **applied at landing and verified in CI**: `/git-checkpoint` reads `.claude/git/checkpoint.md`, whose **pre-land** augmentation runs `scripts/bump-apply.py --fetch origin/main` to set each changed plugin to `z+1` of the freshly-fetched `main` (idempotent; a manual minor/major bump is respected) *before* the commit, so the bump rides in the PR and CI validates it in one cycle. `bump-check.yml` (`scripts/bump-check.py`), a **required** check, is the belt: it fails a PR that changes `plugins/<name>/` code without a version increment. This replaces both the retired server-side `auto-bump.yml` (which pushed a bump back to `main` after merge, conflicting with branch protection) and the former pre-commit bump hook. After a merge lands, the checkpoint's **on-main** augmentation runs `scripts/checkpoint-sync.py` to refresh plugin delivery. The canonical path is PR-based, driven by `/git-checkpoint`; project specifics live in `.claude/git/checkpoint.md` + those scripts.

Sandboxes live on `sandbox/<name>` branches for isolation (per the Paths table) and are not expected to merge into `main`.

## Paths

| Area | Path |
|---|---|
| Plugin-bundled skills | `plugins/<plugin>/skills/<name>/SKILL.md` |
| Project-level skills (wrappers around plugin skills) | `.claude/skills/<name>/SKILL.md` |
| Plans (workstreams) | `plans/<name>.md` |
| Logs (by type) | `logs/<decision\|friction\|idea\|patterns\|problem\|research>/<title>.md` |
| Sandboxes | `sandbox/<name>/SANDBOX-TASKS.md` per branch |
