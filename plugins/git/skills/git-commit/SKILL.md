---
name: git-commit
description: Use when uncommitted working-tree changes should land in git history — explicit signals "commit", "commit my changes", "stage and commit", "save these edits", or any context where committing is the natural next step. Recurses depth-first into `.gitmodules`-declared submodules, normalizing each detached submodule onto its declared branch before committing so its work isn't orphaned; submodule commits land before the parent records its pin advance. Multi-topic working trees produce multiple atomic commits grouped by topic; single-topic produces one. Each commit message is authored against the diff, not the change journey. Under `pr` integration it refuses to commit onto the repo's default branch — the change belongs on a feature branch; `--on-base` overrides.
argument-hint: "[--cwd <path>] [--on-base] [<pathspec>...]"
allowed-tools:
  - Bash(git *)
  - Skill
  - AskUserQuestion
---

# /git:git-commit

Commit working-tree changes as one or more topic-grouped commits. Recurses depth-first into `.gitmodules`-declared submodules: each submodule's commits land before the parent records its pin advance.

## Dependencies

- `/writing:concise-prose`, `/writing:description-authoring`, `/communication:honesty` — the commit messages are authored under these (applied at step 8; the inline mention there is the surgical reminder).
- `/git:git-doctor` — submodule conformance pre-check; refusing to commit through Tier 1 drift is what prevents escalation into Tier 2 history pollution.

## Variables

- `{cwd}` — `--cwd <path>` argument; defaults to `.` (top-level invocation). All git operations use `git -C {cwd}`. Recursive calls pass `{cwd}/{sub}` so depth flows through one variable.
- `{paths}` — optional trailing pathspec(s) (the non-flag arguments). When given, only matching working-tree paths are inspected and committed; everything else is left untouched (scoped commit). Top-level only — not passed into submodule recursion.
- `{on-base}` — `--on-base` present: permit committing onto the repo's default branch even under `pr` integration (the base-branch guard skips). For an intentional admin/base commit; `/git:git-checkpoint` passes it in base-mode.

## Rules

- Pre-check submodule conformance via `/git:git-doctor` at the top level — never commit through Tier 1 drift; declines stop the flow
- Under `pr` integration (`Path: pr` in `.claude/git/checkpoint.md`), refuse to commit onto the repo's default branch — the change belongs on a feature branch. Point to `/git:git-checkpoint` (it auto-creates one named from the change topic) or a manual branch; `--on-base` overrides. Recursive calls (`--cwd`) and `direct`/unconfigured projects are exempt
- Group by topic for readable history: one commit when all changes are one coherent topic or grouping is ambiguous; multi-commit only when topics are clearly separable
- No minimum commit size — a single-file change is a valid commit if it's a distinct topic
- Commit order: dependencies first, consumers after; submodule commits land before the parent commit that records their pin advance
- Normalize a detached submodule onto its declared `branch =` (`.gitmodules`) before committing in it — a commit made on a detached HEAD is orphaned when the branch is later checked out; if the declared branch has diverged from the checked-out sha, surface rather than discard
- Stage specific files by name; never `git add -A` or `git add .`
- When {paths} is given, inspect and commit only matching paths — the rest of the working tree is left parked untouched (a scoped commit, for landing one coherent slice of a mixed tree)
- Submodule pin advance is explicit — never bumped as a silent side effect of recursion; bumps require approval and are surfaced in the parent commit's diff
- Surface suspicious untracked files (large generated dirs, credentials, build artifacts) before staging
- Never amend previous commits unless the user explicitly requests it
- Never force-push or run destructive git operations

## Process

1. Top-level pre-check (skip when invoked recursively):
    1. If `--cwd` was provided: skip to step 2
    2. {doctor-result}: skill: `/git:git-doctor`
    3. If {doctor-result} reports `Blocking unresolved: yes` (a BLOCKING problem it did not repair): Exit process — repo not commit-safe per git-doctor; resolve before retrying. A clean report or an ADVISORY-only result (default-branch, CI) never blocks the commit — proceed.
    4. Base-branch guard (skip if `--on-base`): {integration}: `Path:` from `.claude/git/checkpoint.md` if that file exists, else none; {default}: bash: `git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's@^origin/@@'` (fallback `main`). If {integration} is `pr` AND current branch == {default}: Exit process — `pr` integration forbids committing onto {default}; create a feature branch (or run `/git:git-checkpoint`, which auto-creates one from the change topic), or pass `--on-base` for an intentional admin commit.

2. Recurse into submodules first (depth-first):
    1. {sub-entries}: bash: `git config -f {cwd}/.gitmodules --get-regexp '^submodule\..+\.path$' 2>/dev/null` — emits `submodule.<name>.path <path>` per line; empty if no `.gitmodules`
    2. For each {entry} in {sub-entries}:
        1. {sub-name}: from {entry} — the `<name>` between `submodule.` and `.path`; {sub}: the `<path>` value
        2. {current}: bash: `git -C {cwd}/{sub} rev-parse --abbrev-ref HEAD`
        3. If {current} is `HEAD` (detached) — normalize onto the declared branch before committing, so a new commit lands on a branch rather than an orphaned detached HEAD:
            1. {declared}: bash: `git config -f {cwd}/.gitmodules submodule.{sub-name}.branch`
            2. If {declared} is empty: Exit process — submodule {sub} is detached with no `branch =` in .gitmodules; declare it (`git config -f .gitmodules submodule.{sub-name}.branch <branch>`) or handle the submodule manually before committing
            3. {head}: bash: `git -C {cwd}/{sub} rev-parse HEAD`; {decl}: bash: `git -C {cwd}/{sub} rev-parse --verify {declared} 2>/dev/null` (empty if no local branch)
            4. If {decl} is empty: bash: `git -C {cwd}/{sub} checkout -b {declared}` — create the branch at the current sha
            5. Else if {decl} == {head}: bash: `git -C {cwd}/{sub} checkout {declared}` — attach at the same sha; nothing lost
            6. Else: Exit process — submodule {sub}'s `{declared}` ({decl}) diverges from its checked-out HEAD ({head}); resolve manually rather than discard work
        4. skill: `/git:git-commit --cwd {cwd}/{sub}` — recursive call walks any sub-submodules first, then commits {sub} on its declared branch

3. Inspect the working tree (scoped to {paths} when given — `-- {paths}` with no scope lists everything):
    1. bash: `git -C {cwd} status -- {paths}`
    2. If no changes in scope: Exit process: clean working tree (within scope {paths})
    3. bash: `git -C {cwd} diff --stat -- {paths}`

4. Resolve submodule pin advances:
    1. For each {sub} in {submodules}: bash: `git -C {cwd} diff --quiet -- {sub}`; non-zero exit means the pin at HEAD differs from the submodule's working-tree HEAD (the submodule advanced)
    2. For each advancing {sub}:
        1. {pinned-sha}: bash: `git -C {cwd} ls-tree HEAD -- {sub} | awk '{print $3}'`
        2. {head-sha}: bash: `git -C {cwd}/{sub} rev-parse HEAD`
        3. {advance-log}: bash: `git -C {cwd}/{sub} log --oneline {pinned-sha}..{head-sha}`
        4. AskUserQuestion — show {advance-log} and the new {head-sha}; offer **consume** (stage the pin advance in the parent commit) or **revert** (restore the submodule to {pinned-sha})
        5. If consume: the pin advance enters the staging set for grouping in step 7
        6. If revert: bash: `git -C {cwd} submodule update -- {sub}` — restores HEAD to {pinned-sha}; the diff disappears

5. {suspicious-untracked}: untracked files matching suspicious patterns (large generated dirs, credentials, build artifacts)
6. If {suspicious-untracked} non-empty: surface to the user; confirm include, exclude, or `.gitignore` before proceeding

7. {commit-groups}: partition changes by topic. Indicators of a shared topic:
    - Tests beside the code they exercise
    - Configuration beside the consuming implementation
    - Files within one directory
    - Approved submodule pin advances grouped with the parent-level change that consumes them

    One group when changes are coherent or grouping is ambiguous; multiple groups only when topics are clearly separable. Multi-group order: dependencies before consumers.

8. {commit-messages}: draft one message per group — subject + body. Apply /writing:concise-prose, /writing:description-authoring, /communication:honesty. Body lines describe end-state results visible in the diff or decisions not visible there. Strip process narration (`reauthored`, `sweep applied`), restated principles when the diff already shows the principle applied, and meta-commentary about earlier steps in the change journey. Project-internal phase labels (`Phase G`, `Sprint 4`) are meaningless to future readers — strip them. Pin-advance lines name the submodule and summarize the consumed commits.

9. {co-author}: bash: `git -C {cwd} config --get user.claude-coauthor`

10. For each {group} in {commit-groups}:
    1. bash: `git -C {cwd} add <files-in-group>` — pin-advance entries stage as `git -C {cwd} add <submodule-path>`
    2. {message}: corresponding entry from {commit-messages}; if {co-author} is `true`, append a `Co-Authored-By:` trailer with the current model name and `<noreply@anthropic.com>`
    3. bash: `git -C {cwd} commit -m "{message}"`

11. {final-status}: bash: `git -C {cwd} status --short`

## Report

- Per recursed submodule: commit count + pin advance summary (none / consumed `<sha-range>` / declined), forwarded from each recursive invocation
- Per parent-level commit: topic, files included, message
- Summary: total commits made at this level
- {final-status}: remaining changes if any, else `clean tree`
