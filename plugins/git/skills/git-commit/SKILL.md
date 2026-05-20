---
name: git-commit
description: Use when uncommitted working-tree changes should land in git history — explicit signals "commit", "commit my changes", "stage and commit", "save these edits", or any context where committing is the natural next step. Multi-topic working trees produce multiple atomic commits grouped by topic; single-topic produces one. Each commit message is authored against the diff, not the change journey.
allowed-tools:
  - Bash(git *)
  - AskUserQuestion
---

# /git-commit

Commit working-tree changes as one or more topic-grouped commits.

## Rules

- Group by topic for readable history: one commit when all changes are one coherent topic or grouping is ambiguous; multi-commit only when topics are clearly separable
- No minimum commit size — a single-file change is a valid commit if it's a distinct topic
- Commit order: dependencies first, consumers after
- Stage specific files by name; never `git add -A` or `git add .`
- Surface suspicious untracked files (large generated dirs, credentials, build artifacts) before staging
- Never amend previous commits unless the user explicitly requests it
- Never force-push or run destructive git operations

## Process

1. Inspect the working tree:
    1. bash: `git status`
    2. If no changes: Exit to user: clean working tree
    3. bash: `git diff --stat`

2. {suspicious-untracked}: untracked files matching suspicious patterns
3. If {suspicious-untracked} non-empty: surface to the user; confirm include, exclude, or `.gitignore` before proceeding

4. {commit-groups}: partition changes by topic. Indicators of a shared topic:
    - Tests beside the code they exercise
    - Configuration beside the consuming implementation
    - Files within one directory

    One group when changes are coherent or grouping is ambiguous; multiple groups only when topics are clearly separable. Multi-group order: dependencies before consumers.

5. {commit-messages}: draft one message per group — subject + body. Apply /concise-prose, /description-authoring, /honesty. Body lines describe end-state results visible in the diff or decisions not visible there. Strip process narration (`reauthored`, `sweep applied`), restated principles when the diff already shows the principle applied, and meta-commentary about earlier steps in the change journey. Project-internal phase labels (`Phase G`, `Sprint 4`) are meaningless to future readers — strip them.

6. {co-author}: bash: `git config --get user.claude-coauthor`

7. For each {group} in {commit-groups}:
    1. bash: `git add <files-in-group>`
    2. {message}: corresponding entry from {commit-messages}; if {co-author} is `true`, append a `Co-Authored-By:` trailer with the current model name and `<noreply@anthropic.com>`
    3. bash: `git commit -m "{message}"`

8. {final-status}: bash: `git status --short`

## Report

- Per-commit: topic, files included, message
- Summary: total commits made
- {final-status}: remaining changes if any, else `clean tree`
