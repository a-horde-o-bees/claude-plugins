# claude-plugins — cold-pickup hub

A Claude Code plugin marketplace + skill development project. Most work is iterative skill authoring.

## Where to start

- **`TASKS.md`** — active workstreams + next concrete steps. The first thing to read.

## Workflow

Plugin work lands via PRs to `main`. Required status checks (`test`, `validate`) gate the merge. Each affected plugin's patch version is bumped in the PR itself, and that bump is the deployment signal for `claude plugins update` via `/checkpoint`. The server-side `auto-bump.yml` that previously bumped on merge was retired — its push-back conflicts with branch protection. The in-PR bump is now enforced by `bump-check.yml` (`scripts/bump-check.py`), which fails a PR that changes `plugins/<name>/` code without incrementing that plugin's version; add it to branch protection as a required check to gate merges. The local `.githooks/pre-commit` bumps on direct-to-main commits (admin-bypass belt on `main`) and retires once `bump-check.yml` is enforced as required; the canonical path is PR-based.

Sandboxes live on `sandbox/<name>` branches for isolation (per the Paths table) and are not expected to merge into `main`.

## Paths

| Area | Path |
|---|---|
| Plugin-bundled skills | `plugins/<plugin>/skills/<name>/SKILL.md` |
| Project-level skills (wrappers around plugin skills) | `.claude/skills/<name>/SKILL.md` |
| Plans (workstreams) | `plans/<name>.md` |
| Logs (by type) | `logs/<decision\|friction\|idea\|patterns\|problem\|research>/<title>.md` |
| Sandboxes | `sandbox/<name>/SANDBOX-TASKS.md` per branch |
