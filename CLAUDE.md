# claude-plugins — cold-pickup hub

A Claude Code plugin marketplace + skill development project. Most work is iterative skill authoring.

## Where to start

- **`TASKS.md`** — active workstreams + next concrete steps. The first thing to read.

## Workflow

Plugin work lands via PRs to `main`. Required status checks (`test`, `validate`, `bump-check`) gate the merge. Each affected plugin's patch version is bumped in the PR itself — that bump is the deployment signal for `claude plugins update` via `/checkpoint`. The bump is **applied automatically client-side, then verified in CI**: `.githooks/pre-commit` runs `scripts/bump-apply.py` to set each changed plugin to `z+1` of `origin/main` (idempotent; a manual minor/major bump is respected), and `/checkpoint` recomputes against a freshly-fetched `main` at landing time so the version stays `z+1` of the latest base — no server-side push-back. `bump-check.yml` (`scripts/bump-check.py`), a **required** check, is the belt: it fails a PR that changes `plugins/<name>/` code without a version increment. This replaces the retired `auto-bump.yml`, which bumped on merge by pushing back to `main` (conflicting with branch protection). The canonical path is PR-based.

Sandboxes live on `sandbox/<name>` branches for isolation (per the Paths table) and are not expected to merge into `main`.

## Paths

| Area | Path |
|---|---|
| Plugin-bundled skills | `plugins/<plugin>/skills/<name>/SKILL.md` |
| Project-level skills (wrappers around plugin skills) | `.claude/skills/<name>/SKILL.md` |
| Plans (workstreams) | `plans/<name>.md` |
| Logs (by type) | `logs/<decision\|friction\|idea\|patterns\|problem\|research>/<title>.md` |
| Sandboxes | `sandbox/<name>/SANDBOX-TASKS.md` per branch |
