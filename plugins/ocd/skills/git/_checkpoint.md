# Checkpoint

> Bundle commit + push + ci into one call. Generic — no marketplace, plugin-lifecycle, or deployment assumptions; projects needing additional steps compose the underlying verbs piecewise.

> Branch defaults to current. CI runs by default; `--no-ci` skips it.

### Variables

- {branch} — branch name; defaults to current when omitted
- {no-ci} — boolean flag; when true, skips the CI gate step

### Rules

- Branch defaults to current when `--branch` is omitted; explicit `--branch` must match current branch (the push sub-flow enforces this)
- Skip silently when nothing to commit AND nothing to push — not an error
- CI is opt-out via `--no-ci`, not opt-in — projects with GitHub Actions almost always want to know the build state
- Does not orchestrate marketplace refresh, plugin updates, or restart recommendations — those are project-specific concerns for a project-level wrapper

### Process

1. If not {branch}: {branch}: bash: `git branch --show-current`

2. {commit-report}: Call: `_commit.md`

3. {push-report}: Call: `_push.md` ({branch}: {branch})

4. If {no-ci}: Return to caller (CI skipped, see ### Report)

5. {ci-report}: Call: `_ci.md` ({branch}: {branch})

### Report

Return to caller:

- Branch: {branch}
- {commit-report}: count and messages
- {push-report}: count pushed
- {ci-report}: status (passed, failed, dispatched, incomplete, no-runs) — present only when CI ran
- If nothing was committed AND nothing was pushed: checkpoint complete, CI not invoked
