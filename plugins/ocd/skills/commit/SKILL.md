---
name: commit
allowed-tools:
  - Bash(git *)
  - Bash(python3 scripts/sync-templates.py)
description: >
  Commit working tree changes grouped by topic. Analyzes pending changes,
  groups by topic for readable history, drafts messages describing end-state
  results, and executes commits sequentially with version bumps.
---

# /commit

Commit working tree changes grouped by topic for readable git history. Each commit represents one coherent topic — easy to find how specific change was implemented when examining history later. Grouping separates unrelated changes so each commit is narrow, focused window into what was done and why.

Fully automated — analyzes changes, groups by topic, drafts messages, executes commits. No user confirmation needed for grouping or messages. When grouping is ambiguous, keep changes together rather than splitting incorrectly.

## Trigger

User runs `/commit`

## Workflow

1. Analyze working tree
    1. Run `git status` — collect modified, deleted, untracked files
    2. If no changes: Exit to user — report clean working tree
    3. Run `git diff --stat` — understand scope of changes
    4. Run `git log --oneline -5` — capture recent commit message style
2. Include untracked files — group with related changes using same topic logic as modified files
    1. If any untracked file seems suspicious (e.g., large generated directories missing from .gitignore, credentials, build artifacts):
        1. Surface exceptions to user before committing — they may belong to group or need exclusion
    2. Else:
        1. Proceed without user approval
3. Group changes by topic — goal is readable history where each commit is focused window into related changes
    1. Evaluate changed files for coherent topics — consider:
        - Skill directory — files in same skill are likely same topic
        - Template with convention or skill it affects
        - Convention and consumers — convention file with skills it affects
        - Tests with code — test files group with code they test
        - Plugin infrastructure — plugin.json, hooks, init scripts
    2. If all changes are single topic: single commit
    3. Else:
        1. Multiple commits — one per topic
        2. Order commits — dependencies first, consumers after
    4. If grouping is ambiguous: keep together — consequences of grouping related changes are negligible compared to splitting incorrectly
4. Draft commit messages — one per group
    1. Describe end-state results, not change journey
    2. Follow project's recent commit message style
5. Determine version bumps — identify which plugins have changes per group
6. For each {group} in {commit-groups}:
    1. Bump version — read current version from plugin.json, increment z, write back
    2. Stage files — `git add` specific files for this group plus plugin.json
    3. Commit with drafted message; append co-author trailer
7. Verify — run `git status`; report remaining changes or clean tree

### Report

- Per-commit: version, topic, files included, message
- Summary: total commits, final version, remaining changes if any

## Rules

- Purpose of grouping is readable history — each commit should be focused window into related changes so specific implementations are easy to find later
- When grouping is ambiguous, keep changes together — do not split; slightly broad commit is better than incorrectly split one
- No minimum commit size — single-file change is valid commit if it represents distinct topic
- Single commit when all changes are one coherent topic — do not split artificially
- Untracked files are grouped with related changes — only surface to user when suspicious (generated directories, credentials, build artifacts)
- Every commit bumps z version in `.claude-plugin/plugin.json` for each plugin with changes in that commit
- Commit messages describe end-state results — what code does now, not what was changed or why during session
- Never amend previous commits unless user explicitly requests it
- Never force push or run destructive git operations
- Stage specific files by name — never use `git add -A` or `git add .`
- Co-author trailer required: `Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>`
- Commit order matters — if group B depends on changes in group A (e.g., convention before skill that uses it), commit A first
- Templates in `plugins/` are the committed source of truth — deployed copies in `.claude/` are gitignored and synced by the pre-commit hook
