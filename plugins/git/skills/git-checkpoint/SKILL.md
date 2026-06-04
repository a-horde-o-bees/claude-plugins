---
name: git-checkpoint
description: Bundle the development checkpoint for the current branch into one call. Reads `.claude/git/checkpoint.md` for the project's integration path (`pr` — feature branch → PR → merge; or `direct` — commit straight to the base) and any augmentation steps (e.g. a version bump before commit, a delivery sync after landing on the base), bootstrapping that config on first run. On `pr` a feature branch runs the full lifecycle — commit → push → CI → open PR → merge (gated) → cleanup + sync base; the base branch runs commit → push → CI. Submodule recursion is inherited from the leaves. Generic git automation; every project specific lives in the config + the scripts it names.
argument-hint: "[--branch <name>] [--path pr|direct]"
allowed-tools:
  - Skill
  - Read
  - Bash(git *)
  - Bash(python3 *)
  - Bash(uv run *)
  - AskUserQuestion
---

# /git-checkpoint

Bundle the checkpoint for the current branch. Branches on the project's configured path: the full feature-branch lifecycle to a merged base, or commit + push + CI on the base. The orchestrator owns the sequence; the leaves own their gates, recursion, and message authoring; the project owns its augmentations via `.claude/git/checkpoint.md`.

## Dependencies

- `/process-flow-notation` — this body uses PFN.
- `/git-commit`, `/git-push`, `/git-ci` — the commit/push/CI leaves; each recurses depth-first into declared submodules, inherited here for free.
- `/git-pr-status`, `/git-pr-open`, `/git-pr-merge` — the feature-branch PR loop (the `pr` path). Gating lives in these; this skill only sequences them.
- `.claude/git/checkpoint.md` — the project config: integration `Path:` + `## Augmentations` steps. Bootstrapped by `_bootstrap.md` on first run.

## Variables

- `{branch}` — `--branch <name>`; defaults to current. Explicit `--branch` must match current (the push leaf enforces this).
- `{path}` — `--path`; else the config's `Path:`; else `pr`.

## Rules

- **The orchestrator sequences; the leaves gate.** Checkpoint does not re-check CI, mergeability, or reviews — it calls the leaves, which gate and exit with the surface. A leaf's exit halts the checkpoint.
- **Path selects the flow.** `pr` → a feature branch runs the PR lifecycle; the base branch runs commit + push + CI (the direct/admin exception). `direct` → any branch runs commit + push + CI, no PR.
- **Augmentations are honored, not hardcoded.** `checkpoint.md` may declare project steps to run *before the commit* (pre-land — e.g. the version bump) and *after content reaches the base* (on-main — e.g. a delivery sync). This skill runs them at those points and carries none of their content; the project owns its bump, delivery, and the scripts they name. Absent config ⇒ pure generic flow.
- **No optimistic merge.** Merge runs through `/git-pr-merge`, whose hard gate (red or pending CI, conflicts, behind-base) exits rather than merging on unknown state. If CI is still in flight at the merge gate, checkpoint stops there and the merge completes on a re-invocation once green.
- **Skip the commit/push portion silently when nothing is pending** — not an error. The PR/merge phase still proceeds on a feature branch.

## Process

1. Resolve branch:
    1. {branch}: bash: `git branch --show-current`
    2. If {branch} is empty (detached HEAD): Exit process — detached HEAD; checkout a branch first
    3. If `--branch` given and ≠ {branch}: Exit process — branch mismatch; re-invoke with `--branch {branch}` or switch branches
    4. {default-branch}: bash: `git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's@^origin/@@'` — fallback `main`

2. Load project config:
    1. {config}: `.claude/git/checkpoint.md`
    2. If {config} does not exist AND no `--path` given: Call: `_bootstrap.md` ({config}: {config})
    3. {path}: `--path` if given, else `Path:` read from {config}, else `pr`
    4. If {config} exists: Read it — bind its `## Augmentations` steps ({pre-land}, {on-main}), each empty if not declared

3. Pre-land — if {pre-land}: bash: run it (e.g. the version bump), before committing so CI validates the result

4. Commit + push + CI (every context):
    1. {commit-report}: skill: `/git-commit`
    2. {push-report}: skill: `/git-push --branch {branch}`
    3. {ci-report}: skill: `/git-ci --branch {branch}`

5. Base mode — when {path} is `direct` OR {branch} == {default-branch}:
    1. If {on-main}: bash: run it (content is on the base now — e.g. delivery sync); {sync-report}: its output
    2. Emit the ### base-mode report and stop

6. Feature-PR lifecycle — when {path} is `pr` AND {branch} ≠ {default-branch}:
    1. {pr-status}: skill: `/git-pr-status --branch {branch}`
    2. If {pr-status} reports no open PR: skill: `/git-pr-open`
    3. {merge-report}: skill: `/git-pr-merge --cleanup` — gates internally; on pending/red CI, conflicts, behind-base, or unmet reviews it exits with the surface and checkpoint stops here. On merge-ready it merges, deletes the head, and syncs the base.
    4. If the merge completed and {on-main}: bash: run it (content just landed on the base); {sync-report}: its output

7. Emit the ### feature-mode report

## Report

### base-mode

```
Branch: {branch} (base, path={path})
Commit: {commit-report} — count + messages
Push: {push-report} — count pushed
CI: {ci-report} — status
On-main: {sync-report or none}
Checkpoint complete.
```

### feature-mode

```
Branch: {branch} → {default-branch}
Commit: {commit-report} — count + messages
Push: {push-report} — count pushed
CI: {ci-report} — status
PR: {opened #N | already open #N}
Merge: {merge-report} — merged via <strategy> + cleanup | halted at gate (<surface>)
On-main: {sync-report or — not reached}
```
