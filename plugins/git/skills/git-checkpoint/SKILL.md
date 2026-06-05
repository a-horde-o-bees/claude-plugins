---
name: git-checkpoint
description: Bundle the development checkpoint for the current branch into one call. Reads `.claude/git/checkpoint.md` for the project's integration path (`pr` — feature branch → PR → merge; or `direct` — commit straight to the base) and any augmentation steps (e.g. a version bump before commit, a delivery sync after landing on the base), bootstrapping that config on first run. On `pr`, a feature branch runs the full lifecycle — commit → push → CI → open PR → merge (gated) → cleanup + sync base — and checkpointing from the base branch auto-creates a feature branch named from the change topic to run it; `--base-mode` lands directly on the base instead. On `direct`, any branch runs commit → push → CI. `--auto` runs the whole lifecycle hands-off — threaded to the PR-open and merge leaves, which skip their prompts, watch pending CI to green, and admin-override where the viewer has rights. Submodule recursion is inherited from the leaves. Generic git automation; every project specific lives in the config + the scripts it names.
argument-hint: "[--branch <name>] [--path pr|direct] [--base-mode] [--paths <pathspec>...] [--auto]"
allowed-tools:
  - Skill
  - Read
  - Bash(git *)
  - Bash(python3 *)
  - Bash(uv run *)
  - AskUserQuestion
---

# /git:git-checkpoint

Bundle the checkpoint for the current branch. Branches on the project's configured path: the full feature-branch lifecycle to a merged base, or commit + push + CI on the base. The orchestrator owns the sequence; the leaves own their gates, recursion, and message authoring; the project owns its augmentations via `.claude/git/checkpoint.md`.

## Dependencies

- `/git:git-commit`, `/git:git-push`, `/git:git-ci` — the commit/push/CI leaves; each recurses depth-first into declared submodules, inherited here for free.
- `/git:git-pr-status`, `/git:git-pr-open`, `/git:git-pr-merge` — the feature-branch PR loop (the `pr` path). Gating lives in these; this skill only sequences them.
- `.claude/git/checkpoint.md` — the project config: integration `Path:` + `## Augmentations` steps. Bootstrapped by `_bootstrap.md` on first run.

## Variables

- `{branch}` — `--branch <name>`; defaults to current. Explicit `--branch` must match current (the push leaf enforces this).
- `{path}` — `--path`; else the config's `Path:`; else `pr`.
- `{paths}` — optional `--paths <pathspec>...`; scopes the whole checkpoint to those paths — only they are committed and landed, the rest of the working tree stays parked. Empty = the whole tree. Passed to `/git:git-commit` and exposed to the pre-land augmentation for scoping its bump.
- `{base-mode}` — `--base-mode` present: land directly on the base branch (the admin/direct-land exception) instead of auto-creating a feature branch under `pr`.
- `{auto}` — `--auto` present: hands-off. Threaded verbatim to `/git:git-pr-open` and `/git:git-pr-merge`; the leaves own what it bypasses (the description review gate; soft-blocker prompts; the pending-CI watch). Checkpoint adds no auto behavior of its own.
- `{feature-branch}` — the topic-derived `<area>/<topic>` branch auto-created when checkpointing from the base branch under `pr`.

## Rules

- **The orchestrator sequences; the leaves gate.** Checkpoint does not re-check CI, mergeability, or reviews — it calls the leaves, which gate and exit with the surface. A leaf's exit halts the checkpoint.
- **Path selects the flow.** `pr` → on a feature branch, run the PR lifecycle; on the base branch with pending in-scope changes, auto-create a feature branch named from the change topic, then run it. `direct` → any branch runs commit + push + CI, no PR. Landing directly on the base under `pr` is the explicit exception — `--base-mode`.
- **Submodules get no PR of their own.** Recursion (the commit/push/CI leaves) commits and pushes each submodule direct to its declared branch; only the superproject runs the PR lifecycle. The `pr` path is single-repo — for PR-governed submodules, land their PRs first, then checkpoint the superproject to pin the merged shas.
- **Augmentations are honored, not hardcoded.** `checkpoint.md` may declare project steps to run *before the commit* (pre-land — e.g. the version bump) and *after content reaches the base* (on-main — e.g. a delivery sync). This skill runs them at those points and carries none of their content; the project owns its bump, delivery, and the scripts they name. Absent config ⇒ pure generic flow.
- **No optimistic merge.** Merge runs through `/git:git-pr-merge`, whose hard gate (red or pending CI, conflicts, behind-base) exits rather than merging on unknown state. If CI is still in flight at the merge gate, checkpoint stops there and the merge completes on a re-invocation once green. Under `--auto`, the merge leaf watches in-flight CI to green and merges in the same run instead of stopping; only a hard failure (red CI, conflict, behind-base) halts.
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

3. Branch under `pr` (auto-create as needed) — when {path} is `pr` AND {branch} == {default-branch} AND no `--base-mode`:
    1. {pending}: bash: `git status --short -- {paths}` — pending changes in scope
    2. If {pending} is empty: skip — nothing to branch for; the flow falls through to base-mode (a no-op) or, if a PR is already open for an existing branch, drives it
    3. {feature-branch}: author a kebab-case `<area>/<topic>` name from the in-scope change — {area} the single plugin or directory the scope sits under (else a short domain word), {topic} what the change does (e.g. `writing/rules-self-carrying-polarity`). Derive from the diff, not from prompt text.
    4. bash: `git checkout -b {feature-branch}` — carries the working tree onto the new branch
    5. {branch}: {feature-branch} — subsequent steps route to the feature-PR lifecycle

4. Pre-land — if {pre-land}: bash: run it (e.g. the version bump), before committing so CI validates the result. When {paths} is set, scope the augmentation to it (the augmentation references `{paths}` — e.g. the bump runs `--paths {paths}`) so only in-scope plugins bump.

5. Commit + push + CI (every context):
    1. {commit-report}: skill: `/git:git-commit {paths}` — pass `--on-base` when {branch} == {default-branch} (an intentional base commit) so the leaf's base guard permits it
    2. {push-report}: skill: `/git:git-push --branch {branch}`
    3. {ci-report}: skill: `/git:git-ci --branch {branch}`

6. Base mode — when {path} is `direct` OR {branch} == {default-branch}:
    1. If {on-main}: bash: run it (content is on the base now — e.g. delivery sync); {sync-report}: its output
    2. Emit the ### base-mode report and stop

7. Feature-PR lifecycle — when {path} is `pr` AND {branch} ≠ {default-branch}:
    1. {pr-status}: skill: `/git:git-pr-status --branch {branch}`
    2. If {pr-status} reports no open PR: skill: `/git:git-pr-open` + ` --auto` if {auto}
    3. {merge-report}: skill: `/git:git-pr-merge --cleanup` + ` --auto` if {auto} — runs the shared gate script directly (fresh, no skill round-trip) and gates internally; on pending/red CI, conflicts, behind-base, or unmet reviews it exits with the surface and checkpoint stops here. Under `--auto` it instead watches in-flight CI to green and admin-overrides soft blockers where the viewer has rights. On merge-ready it merges, deletes the head, and syncs the base.
    4. If the merge completed and {on-main}: bash: run it (content just landed on the base); {sync-report}: its output

8. Emit the ### feature-mode report

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
Branch: {branch} → {default-branch}  (auto-created from topic | existing)
Commit: {commit-report} — count + messages
Push: {push-report} — count pushed
CI: {ci-report} — status
PR: {opened #N | already open #N}
Merge: {merge-report} — merged via <strategy> + cleanup | halted at gate (<surface>)
On-main: {sync-report or — not reached}
```
