---
name: git-checkpoint
description: Bundle the development checkpoint cycle for the current branch — commit + push + CI watch — into one call. Generic; no marketplace, plugin-lifecycle, or deployment concerns. Branch defaults to current. CI always runs. Projects needing additional steps wrap this in a project-level skill that composes around it.
argument-hint: "[--branch <name>]"
allowed-tools:
  - Skill
  - Bash(git branch *)
---

# /git-checkpoint

Bundle commit + push + CI into one call. Branch defaults to current. CI always runs.

## Rules

- Branch defaults to current when `--branch` is omitted; explicit `--branch` must match current branch (the push sub-flow enforces this)
- Skip silently when nothing to commit AND nothing to push — not an error
- Does not orchestrate marketplace refresh, plugin updates, or restart recommendations — those are project-specific concerns for a project-level wrapper

## Process

1. If not {branch}: {branch}: bash: `git branch --show-current`
2. {commit-report}: skill: `/git-commit`
3. {push-report}: skill: `/git-push --branch {branch}`
4. {ci-report}: skill: `/git-ci --branch {branch}`

## Report

Return to caller:

- Branch: {branch}
- {commit-report}: count and messages
- {push-report}: count pushed
- {ci-report}: status (passed, failed, dispatched, incomplete, no-runs)
- If nothing was committed AND nothing was pushed: checkpoint complete
