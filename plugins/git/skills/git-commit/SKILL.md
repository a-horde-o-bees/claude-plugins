---
name: git-commit
description: Use when uncommitted working-tree changes should land in git history — explicit signals "commit", "commit my changes", "stage and commit", "save these edits", or any context where committing is the natural next step. Recurses depth-first into `.gitmodules`-declared submodules so submodule commits land before the parent records its pin advance. Multi-topic working trees produce multiple atomic commits grouped by topic; single-topic produces one. Each commit message is authored against the diff, not the change journey.
argument-hint: "[--cwd <path>] [<pathspec>...]"
allowed-tools:
  - Bash(git *)
  - Skill
  - AskUserQuestion
---

# /git-commit

Commit working-tree changes as one or more topic-grouped commits. Recurses depth-first into `.gitmodules`-declared submodules: each submodule's commits land before the parent records its pin advance.

## Dependencies

- `/process-flow-notation` — this body uses PFN; a cold session needs the spec in context.
- `/concise-prose`, `/description-authoring`, `/honesty` — the commit messages are authored under these (applied at step 8; the inline mention there is the surgical reminder).
- `/git-doctor` — submodule conformance pre-check; refusing to commit through Tier 1 drift is what prevents escalation into Tier 2 history pollution.

## Variables

- `{cwd}` — `--cwd <path>` argument; defaults to `.` (top-level invocation). All git operations use `git -C {cwd}`. Recursive calls pass `{cwd}/{sub}` so depth flows through one variable.
- `{paths}` — optional trailing pathspec(s) (the non-flag arguments). When given, only matching working-tree paths are inspected and committed; everything else is left untouched (scoped commit). Top-level only — not passed into submodule recursion.

## Rules

- Pre-check submodule conformance via `/git-doctor` at the top level — never commit through Tier 1 drift; declines stop the flow
- Group by topic for readable history: one commit when all changes are one coherent topic or grouping is ambiguous; multi-commit only when topics are clearly separable
- No minimum commit size — a single-file change is a valid commit if it's a distinct topic
- Commit order: dependencies first, consumers after; submodule commits land before the parent commit that records their pin advance
- Stage specific files by name; never `git add -A` or `git add .`
- When {paths} is given, inspect and commit only matching paths — the rest of the working tree is left parked untouched (a scoped commit, for landing one coherent slice of a mixed tree)
- Submodule pin advance is explicit — never bumped as a silent side effect of recursion; bumps require approval and are surfaced in the parent commit's diff
- Surface suspicious untracked files (large generated dirs, credentials, build artifacts) before staging
- Never amend previous commits unless the user explicitly requests it
- Never force-push or run destructive git operations

## Process

1. Top-level pre-check (skip when invoked recursively):
    1. If `--cwd` was provided: skip to step 2
    2. {doctor-result}: skill: `/git-doctor`
    3. If {doctor-result} is not `healthy` or `repaired-and-verified`: Exit process — repo not commit-safe per git-doctor; resolve before retrying

2. Recurse into submodules first (depth-first):
    1. {submodules}: bash: `git config -f {cwd}/.gitmodules --get-regexp '^submodule\..+\.path$' 2>/dev/null | awk '{print $2}'` — direct submodules at this level; empty if no `.gitmodules`
    2. For each {sub} in {submodules}: skill: `/git-commit --cwd {cwd}/{sub}` — recursive call walks any sub-submodules first by the same step 2 before its own local commit

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

8. {commit-messages}: draft one message per group — subject + body. Apply /concise-prose, /description-authoring, /honesty. Body lines describe end-state results visible in the diff or decisions not visible there. Strip process narration (`reauthored`, `sweep applied`), restated principles when the diff already shows the principle applied, and meta-commentary about earlier steps in the change journey. Project-internal phase labels (`Phase G`, `Sprint 4`) are meaningless to future readers — strip them. Pin-advance lines name the submodule and summarize the consumed commits.

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
