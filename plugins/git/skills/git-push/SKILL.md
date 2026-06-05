---
name: git-push
description: Use when local commits need to reach the remote — explicit signals "push", "push my branch", "push to origin", or any context where publishing committed work is the next action. Recurses depth-first into `.gitmodules`-declared submodules: each is normalized off detached HEAD onto its declared branch, fetched, rebased onto its remote tip, and fast-forward-pushed before the parent. Auto-commits uncommitted changes via /git:git-commit. Requires explicit --branch to confirm the target.
argument-hint: "--branch <name> [--cwd <path>] [--pin-only <path>]..."
allowed-tools:
  - Bash(git *)
  - Skill
---

# /git:git-push

Push local commits to a named remote branch. Recurses depth-first into `.gitmodules`-declared submodules: each is normalized off detached HEAD onto its declared branch, fetched, rebased onto its remote tip, and fast-forward-pushed before the parent.

## Dependencies

- `/git:git-doctor` — submodule conformance pre-check before any push

## Variables

- `{cwd}` — `--cwd <path>` argument; defaults to `.` (top-level invocation). All git operations use `git -C {cwd}`. Recursive calls pass `{cwd}/{sub}` so depth flows through one variable.
- `{pin-only}` — `--pin-only <path>` (repeatable); submodules the parent only pins, never direct-pushes. Set by `/git:git-checkpoint` for PR-governed and vendored submodules — their changes land via their own PR or are read-only.

## Rules

- Pre-check submodule conformance via `/git:git-doctor` at the top level; declines stop the flow
- Submodule recursion uses `.gitmodules` `submodule.<name>.branch` when declared, else falls back to the submodule's currently checked-out branch; it exits only when the submodule is detached AND no `branch =` is declared (no branch to publish). `/git:git-doctor` can write the native `branch =` key
- A `{pin-only}` submodule (PR-governed or vendored) is never direct-pushed — a protected branch refuses direct pushes by design; its changes land via its own PR (`/git:git-checkpoint` runs that lifecycle). The parent pins whatever sha it is on
- `fetch` + `rebase` onto `origin/{branch}` before pushing; conflicts exit to user
- Fast-forward only — the rebase makes fast-forward the steady state, so non-fast-forward pushes are refused by definition
- Explicit `--branch` required at the top level; naming the branch is the confirmation
- Refuse to push from detached HEAD at the parent level — no branch to publish
- Branch mismatch exits with explanation — no prompt, no default action
- When the auto-commit fallback fires: stage by name (never `git add -A`); never amend; never force-push
- Never force-push or run destructive git operations

## Process

1. Top-level pre-check (skip when invoked recursively):
    1. If `--cwd` was provided: skip to step 2
    2. {doctor-result}: skill: `/git:git-doctor`
    3. If {doctor-result} reports `Blocking unresolved: yes` (a BLOCKING problem it did not repair): Exit process — repo not push-safe per git-doctor. A clean report or an ADVISORY-only result (default-branch, CI) never blocks the push — proceed.

2. Recurse into submodules first (depth-first):
    1. {sub-entries}: bash: `git config -f {cwd}/.gitmodules --get-regexp '^submodule\..+\.path$' 2>/dev/null` — emits `submodule.<name>.path <path>` per line; empty if no `.gitmodules`
    2. For each {entry} in {sub-entries}:
        1. {sub-name}: from {entry} — the `<name>` between `submodule.` and `.path`
        2. {sub}: from {entry} — the `<path>` value
        3. If {sub} in {pin-only}: record `pin-only` for {sub} and continue — never direct-push it; the parent pins its current sha
        4. {current}: bash: `git -C {cwd}/{sub} rev-parse --abbrev-ref HEAD`
        5. {declared}: bash: `git config -f {cwd}/.gitmodules submodule.{sub-name}.branch` — if empty AND {current} ≠ `HEAD`: {declared}: {current} (fall back to the checked-out branch)
        6. If {declared} is empty: Exit process — submodule {sub} is detached with no `branch =` in .gitmodules; declare it (`git config -f .gitmodules submodule.{sub-name}.branch <branch>`, or let `/git:git-doctor` write it) or normalize it onto a branch before pushing
        7. If {current} is `HEAD` (detached): normalize onto {declared} without discarding work — {head}: bash: `git -C {cwd}/{sub} rev-parse HEAD`; {decl}: bash: `git -C {cwd}/{sub} rev-parse --verify {declared} 2>/dev/null`. If {decl} is empty: bash: `git -C {cwd}/{sub} checkout -b {declared}`. Else if {decl} == {head}: bash: `git -C {cwd}/{sub} checkout {declared}`. Else: Exit process — {declared} ({decl}) diverges from the detached HEAD ({head}); a commit was made off-branch — resolve manually (commit-time normalization belongs in `/git:git-commit`)
        8. Else if {current} ≠ {declared}: Exit process — submodule {sub} on unexpected branch ({current}, expected {declared}); manual handling
        9. skill: `/git:git-push --cwd {cwd}/{sub} --branch {declared}` — recursive call handles sub-submodules and the fetch+rebase+ff-push of {sub} itself

3. Preconditions (parent level):
    1. {current-branch}: bash: `git -C {cwd} rev-parse --abbrev-ref HEAD`
    2. If {current-branch} is `HEAD`: Exit process: detached HEAD — checkout or create a branch before pushing
    3. If not --branch: Exit process: push requires `--branch <name>`
    4. If {current-branch} ≠ {branch}: Exit process — branch mismatch (current `{current-branch}`, requested `{branch}`). To push the current branch: re-invoke with `--branch {current-branch}`. To move commits to {branch} first: ask for rebase/merge help.

4. Auto-commit pending changes:
    1. {pending}: bash: `git -C {cwd} status --short`
    2. If {pending} non-empty:
        1. skill: `/git:git-commit --cwd {cwd}`
        2. If no commits were produced: Exit process: commit step produced nothing — investigate and re-invoke

5. {upstream-set}: bash: `git -C {cwd} rev-parse --abbrev-ref @{upstream} 2>/dev/null` exits 0

6. If {upstream-set}:
    1. bash: `git -C {cwd} fetch origin {branch}`
    2. {behind}: bash: `git -C {cwd} rev-list HEAD..origin/{branch} --count`
    3. If {behind} > 0:
        1. bash: `git -C {cwd} rebase origin/{branch}` (capture exit)
        2. If exit non-zero: Exit process — needs manual rebase against `origin/{branch}`; aborting push
    4. {unpushed}: bash: `git -C {cwd} log --oneline @{upstream}..HEAD`
    5. If {unpushed} is empty: Exit process: nothing to push — local and remote in sync

7. Present push preview — branch, remote, commit count + oneline list

8. Push:
    1. If {upstream-set}: bash: `git -C {cwd} push origin {branch}`
    2. Else: bash: `git -C {cwd} push -u origin {branch}` — first push sets upstream

## Report

- Per recursed submodule: push status (`in-sync` / `pushed <N>` / `declined` / `manual-required <reason>`), forwarded from each recursive invocation
- Commits pushed at this level: count and branch
- Remote URL and push status
