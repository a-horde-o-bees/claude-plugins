# claude-plugins — cold-pickup hub

A Claude Code plugin marketplace + skill development project. Most work is iterative skill authoring.

## Where to start

- **`TASKS.md`** — active workstreams + next concrete steps. The first thing to read.

## Workflow

Plugin work lands via PRs to `main`. Required status checks (`test`, `validate`) gate the merge; the server-side workflow `.github/workflows/auto-bump.yml` bumps each affected plugin's patch version on merge, and that bump is the deployment signal for `claude plugins update` via `/checkpoint`. The local `.githooks/pre-commit` is a belt for direct-to-main edge cases (admin bypass on `main`); the canonical path is PR-based.

Sandboxes live on `sandbox/<name>` branches for isolation (per the Paths table) and are not expected to merge into `main`.

## Paths

| Area | Path |
|---|---|
| Plugin-bundled skills | `plugins/<plugin>/skills/<name>/SKILL.md` |
| Project-level skills (wrappers around plugin skills) | `.claude/skills/<name>/SKILL.md` |
| Plans (workstreams) | `plans/<name>.md` |
| Logs (by type) | `logs/<decision\|friction\|idea\|pattern\|problem\|research>/<title>.md` |
| Assertions (durable platform-behavior tests) | `logs/assertions/<topic>/<assertion>.md` — re-runnable; see `logs/assertions/README.md` |
| Sandboxes | `sandbox/<name>/SANDBOX-TASKS.md` per branch |
