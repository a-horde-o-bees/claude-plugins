# Checkpoint

> Bundle the commit + push + ci cycle into one call. Generic — no marketplace, plugin-lifecycle, or deployment assumptions. Projects that need additional steps between commit and push (auto-init, template syncs, dependency rebuild) should compose the underlying verbs piecewise rather than calling this one.

Branch defaults to current. CI runs by default; `--no-ci` skips it (useful when you want to push without watching, or when the project has no GitHub Actions).

### Variables

- {branch} — branch name; defaults to current when not provided
- {no-ci} — boolean flag; when true, skips the CI gate step

### Rules

- Branch defaults to current when --branch is omitted; explicit --branch must match current branch (delegated to Push sub-flow)
- Skips silently when there is nothing to commit AND nothing to push — not an error
- ci is opt-out via --no-ci, not opt-in — projects with GitHub Actions almost always want to know the build state
- Does not orchestrate marketplace refresh, plugin updates, or restart recommendations — those are project-specific concerns that belong in a project-level wrapper

### Process

1. If not {branch}: {branch} = bash: `git branch --show-current`
2. Commit — Call: `_commit.md`
3. Push — Call: `_push.md` ({branch} = {branch})
4. If {no-ci}: skip ci; Return to caller with commit + push reports
5. CI — Call: `_ci.md` ({branch} = {branch})
6. Return to caller:
    - Branch
    - Commits made: count and messages (from Commit sub-flow)
    - Commits pushed: count (from Push sub-flow)
    - CI status (from CI sub-flow): passed, failed, dispatched, or no-runs
    - If nothing was committed AND nothing was pushed: checkpoint complete, no CI check ran
