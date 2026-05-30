# claude-plugins — cold-pickup hub

A Claude Code plugin marketplace + skill development project. Most work is iterative skill authoring.

## Where to start

- **`TASKS.md`** — active workstreams + next concrete steps. The first thing to read.

## Workflow

Avoid feature branches in this repo. Plugin work commits directly to `main` — the pre-commit hook (`.githooks/pre-commit`) auto-bumps each affected plugin's patch version on every commit to `main`, and that bump is the deployment signal for `claude plugins update` via `/checkpoint`. Feature branches and PRs bypass the hook entirely, so the bump never fires and `/checkpoint`'s marketplace sync becomes a no-op against unchanged versions.

Sandboxes are the exception — they live on `sandbox/<name>` branches for isolation (per the Paths table) and are not expected to merge into `main`.

## Paths

| Area | Path |
|---|---|
| Plugin-bundled skills | `plugins/<plugin>/skills/<name>/SKILL.md` |
| Project-level skills (wrappers around plugin skills) | `.claude/skills/<name>/SKILL.md` |
| Plans (workstreams) | `plans/<name>.md` |
| Logs (by type) | `logs/<decision\|friction\|idea\|pattern\|problem\|research>/<title>.md` |
| Assertions (durable platform-behavior tests) | `logs/assertions/<topic>/<assertion>.md` — re-runnable; see `logs/assertions/README.md` |
| Sandboxes | `sandbox/<name>/SANDBOX-TASKS.md` per branch |
