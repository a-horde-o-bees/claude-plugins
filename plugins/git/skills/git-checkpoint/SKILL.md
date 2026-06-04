---
name: git-checkpoint
description: Bundle the development checkpoint for the current branch into one call. On a feature branch it runs the full lifecycle — commit → push → CI → open PR → merge (gated) → cleanup + sync base — taking a messy tree to a merged, up-to-date base. On the base branch it runs commit → push → CI. Submodule recursion is inherited from the leaves (`/git-commit`, `/git-push`, `/git-ci` each walk `.gitmodules`-declared submodules depth-first). Generic git automation; project-specific delivery (deployment, artifact publishing) stays in a project-level wrapper. Branch defaults to current.
argument-hint: "[--branch <name>]"
allowed-tools:
  - Skill
  - Bash(git *)
---

# /git-checkpoint

Bundle the checkpoint for the current branch. Branches on context: the full feature-branch lifecycle to a merged base, or commit + push + CI on the base branch. The orchestrator owns the sequence; the leaves own their gates, recursion, and message authoring.

## Dependencies

- `/process-flow-notation` — this body uses PFN.
- `/git-commit`, `/git-push`, `/git-ci` — the commit/push/CI leaves; each recurses depth-first into declared submodules, inherited here for free.
- `/git-pr-status`, `/git-pr-open`, `/git-pr-merge` — the feature-branch PR loop. Gating lives in these; this skill only sequences them.

## Variables

- `{branch}` — `--branch <name>`; defaults to current. Explicit `--branch` must match current (the push leaf enforces this).

## Rules

- **The orchestrator sequences; the leaves gate.** Checkpoint does not re-check CI, mergeability, or reviews — it calls the leaves, which gate and exit-to-user with the surface. A leaf's exit halts the checkpoint.
- **Context is the branch.** `{branch}` == the repo's default branch → base-mode (commit + push + CI). Otherwise → feature-mode (full lifecycle).
- **No optimistic merge.** Merge runs through `/git-pr-merge`, whose hard gate (red or pending CI, conflicts, behind-base) exits rather than merging on unknown state. If CI is still in flight at the merge gate, checkpoint stops there and the merge completes on a re-invocation once green — honest about the async-CI boundary.
- **Skip the commit/push portion silently when nothing is pending** — not an error. The PR/merge phase still proceeds on a feature branch (you may checkpoint solely to land an already-pushed branch).
- Project-specific delivery — deployment, artifact publishing, environment sync, post-merge automation — is not this skill's concern; a project-level wrapper composes around it for those. The plugin skill carries none.

## Process

1. Resolve branch:
    1. {branch}: bash: `git branch --show-current`
    2. If {branch} is empty (detached HEAD): Exit process — detached HEAD; checkout a branch first
    3. If `--branch` given and ≠ {branch}: Exit process — branch mismatch; re-invoke with `--branch {branch}` or switch branches
    4. {default-branch}: bash: `git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's@^origin/@@'` — fallback `main`

2. Commit + push + CI (every context):
    1. {commit-report}: skill: `/git-commit`
    2. {push-report}: skill: `/git-push --branch {branch}`
    3. {ci-report}: skill: `/git-ci --branch {branch}`

3. If {branch} == {default-branch}: base-mode complete — emit the ### base-mode report and stop. Project delivery is the wrapper's concern.

4. Feature-branch lifecycle (when {branch} ≠ {default-branch}):
    1. {pr-status}: skill: `/git-pr-status --branch {branch}`
    2. If {pr-status} reports no open PR: skill: `/git-pr-open`
    3. {merge-report}: skill: `/git-pr-merge --cleanup` — gates internally; on pending/red CI, conflicts, behind-base, or unmet team reviews it exits with the surface and checkpoint stops here. On merge-ready (or confirmed solo bypass) it merges, deletes the head, and syncs the base.

5. Emit the ### feature-mode report

## Report

### base-mode

```
Branch: {branch} (base)
Commit: {commit-report} — count + messages
Push: {push-report} — count pushed
CI: {ci-report} — status
Checkpoint complete (commit + push + CI). Project delivery, if any, runs in the project wrapper.
```

### feature-mode

```
Branch: {branch} → {default-branch}
Commit: {commit-report} — count + messages
Push: {push-report} — count pushed
CI: {ci-report} — status
PR: {opened #N | already open #N}
Merge: {merge-report} — merged via <strategy> + cleanup | halted at gate (<surface>)
```
