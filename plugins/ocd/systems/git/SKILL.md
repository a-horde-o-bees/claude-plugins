---
name: git
description: Manage local git operations — topic-grouped commits and branch pushes.
argument-hint: "<commit | push --branch <branch-name>>"
allowed-tools:
  - Bash(git *)
---

# /git

Manage local git operations. Two verbs:

- `commit` — commit working tree changes grouped by topic for readable history
- `push` — push local commits to a named branch on the remote

## Workflow

1. If not $ARGUMENTS: Exit to user: skill description and argument-hint

> Verb dispatch — commit groups and records changes, push sends a branch to remote.

2. If {verb} is `commit`:
    1. Call: Commit
3. Else if {verb} is `push`:
    1. Call: Push
4. Else: Exit to user: unrecognized verb {verb} — expected commit or push

## Commit

> Commit working tree changes grouped by topic for readable git history. Each commit represents one coherent topic — easy to find how a specific change was implemented when examining history later. Grouping separates unrelated changes so each commit is a narrow, focused window into what was done and why.

Fully automated — analyzes changes, groups by topic, drafts messages, executes commits. No user confirmation needed for grouping or messages. When grouping is ambiguous, keep changes together rather than splitting incorrectly.

### Rules

- Purpose of grouping is readable history — each commit should be a focused window into related changes so specific implementations are easy to find later
- When grouping is ambiguous, keep changes together — do not split; a slightly broad commit is better than an incorrectly split one
- No minimum commit size — a single-file change is a valid commit if it represents a distinct topic
- Single commit when all changes are one coherent topic — do not split artificially
- Untracked files are grouped with related changes — only surface to user when suspicious (generated directories, credentials, build artifacts)
- Commit messages describe end-state results — what the code does now, not what was changed or why during the session
- Never amend previous commits unless user explicitly requests it
- Never force push or run destructive git operations
- Stage specific files by name — never use `git add -A` or `git add .`
- Commit order matters — if group B depends on changes in group A (e.g., convention before skill that uses it), commit A first

### Process

1. Analyze working tree
    1. Run `git status` — collect modified, deleted, untracked files
    2. If no changes: Exit to user: clean working tree
    3. Run `git diff --stat` — understand scope of changes
    4. Run `git log --oneline -5` — capture recent commit message style
2. Include untracked files — group with related changes using same topic logic as modified files
    1. If any untracked file seems suspicious (e.g., large generated directories missing from .gitignore, credentials, build artifacts):
        1. Surface exceptions to user before committing — they may belong to group or need exclusion
3. {commit-groups} = Group changes by topic — goal is readable history where each commit is a focused window into related changes
    1. Evaluate changed files for coherent topics — consider:
        - Tests with code — test files group with code they test
        - Configuration with implementation — config changes group with the code that uses them
        - Related directories — files in the same directory are likely the same topic
    2. If all changes are single topic or grouping is ambiguous: single commit — consequences of grouping related changes are negligible compared to splitting incorrectly
    3. Else:
        1. Multiple commits — one per topic
        2. Order commits — dependencies first, consumers after
4. Draft commit messages — one per group
    1. Describe end-state results, not change journey
    2. Follow project's recent commit message style
5. {co-author} = bash: `git config --get user.claude-coauthor`
6. For each {group} in {commit-groups}:
    1. Stage files — `git add` specific files for this group
    2. If {co-author} is `true`: append `Co-Authored-By:` trailer with current model name and `<noreply@anthropic.com>`
    3. Commit with drafted message
7. Verify — run `git status`; report remaining changes or clean tree

### Report

- Per-commit: topic, files included, message
- Summary: total commits, remaining changes if any

## Push

> Push local commits to remote. Requires explicit branch name — no default target. Ensures working tree is committed first, previews unpushed commits, then pushes.

### Rules

- Never force push
- Explicit --branch is required — no default push target; naming the branch is the confirmation
- Branch mismatch exits with explanation — no prompt, no default action; user re-invokes with correct intent or asks for help
- Commit step is fully automated via the Commit sub-flow — no double-confirmation on commit content

### Process

1. If not --branch: Exit to user: push requires `--branch <branch-name>`
2. {current-branch} = current git branch
3. If {current-branch} does not match {branch}:
    1. Exit to user:
        - branch mismatch — current branch is {current-branch}, requested {branch}
        - To push the current branch: re-invoke with `--branch {current-branch}`
        - To move commits to {branch} first: ask for help with rebase/merge
4. Check for uncommitted changes
    1. Run `git status --short`
    2. If changes exist:
        1. Call: Commit
        2. If commit fails or produces no commits: Exit to user: commit failed
5. {upstream-set} = bash: `git rev-parse --abbrev-ref @{upstream}` exits 0
6. If {upstream-set}:
    1. Run `git log --oneline @{upstream}..HEAD`
    2. If no unpushed commits: Exit to user: Nothing to push — local and remote are in sync
7. Present push preview — branch name, remote, commit count and list (oneline format)
8. Push to remote:
    1. If {upstream-set}: bash: `git push origin {branch}`
    2. Else: bash: `git push -u origin {branch}` — first push, set upstream
9. Report result

### Report

- Commits pushed: count and branch
- Remote URL and status
