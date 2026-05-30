---
name: git-checkpoint
description: Bundle the development checkpoint cycle for the current branch — commit + push + CI watch — into one call. Submodule recursion is inherited from the leaves (`/git-commit`, `/git-push`, `/git-ci` each walk `.gitmodules`-declared submodules depth-first), so this skill carries no submodule logic of its own. Generic; no marketplace, plugin-lifecycle, or deployment concerns. Branch defaults to current. CI always runs. Projects needing additional steps wrap this in a project-level skill that composes around it.
argument-hint: "[--branch <name>]"
allowed-tools:
  - Skill
  - Bash(git branch *)
---

# /git-checkpoint

Bundle commit + push + CI into one call. Branch defaults to current. CI always runs.

## Dependencies

- `/git-commit`, `/git-push`, `/git-ci` — each leaf recurses depth-first into declared submodules; this skill inherits that recursion for free.

## Rules

- Branch defaults to current when `--branch` is omitted; explicit `--branch` must match current branch (the push sub-flow enforces this)
- Skip silently when nothing to commit AND nothing to push — not an error
- Submodule recursion is the leaves' concern — this skill orchestrates only the commit → push → CI sequence at each level the leaves walk
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
