---
name: ocd-commit
description: >
  Commit working tree changes grouped by topic. Analyzes pending changes,
  proposes coherent groupings, drafts messages describing end-state results,
  and executes commits sequentially with version bumps.
argument-hint: "[message]"
---

# /ocd-commit

Commit working tree changes grouped by topic. Analyzes modified, deleted, and untracked files, proposes topic-based groupings, and executes commits sequentially. Each commit bumps plugin version and describes end-state results, not change history.

Runs entirely in main conversation — no agent delegation. Every step is interactive with user confirmation.

## Trigger

User runs `/ocd-commit`

## Route

1. Analyze working tree
  1. Run `git status` — collect modified, deleted, untracked files
  2. If no changes:
    1. EXIT — report clean working tree
  3. Run `git diff --stat` — understand scope of changes
  4. Run `git log --oneline -5` — capture recent commit message style
2. Surface untracked files — present all untracked files to user; confirm which to include or exclude; never skip or ignore untracked files
3. If `$ARGUMENTS` contains message text:
  1. Treat all changes as single group with provided message; skip to step 5
4. Group changes by topic
  1. Evaluate changed files for coherent topics — consider:
    - Skill directory — files in same skill are likely same topic
    - Template and deployed pairs — template with its deployed copy
    - Convention and consumers — convention file with skills it affects
    - Tests with code — test files group with code they test
    - Plugin infrastructure — plugin.json, hooks, init scripts
  2. If all changes are single topic:
    1. Propose single commit with topic summary
  3. Else:
    1. Propose multiple commits — topic label and file list per group
    2. Suggest commit order — dependencies first, consumers after
  4. Present proposed grouping to user for confirmation or modification
  5. User confirms, modifies, or regroups
5. Draft commit messages — one per group
  1. Describe end-state results, not change journey
  2. Follow project's recent commit message style
  3. Present messages to user for confirmation
6. Determine version bumps — identify which plugins have changes per group
7. Dispatch — proceed to Workflow with resolved groups, messages, and version targets

## Workflow

1. For each commit group (in order):
  1. Bump version — read current version from plugin.json, increment z, write back
  2. Stage files — `git add` specific files for this group plus plugin.json
  3. Commit with confirmed message; append co-author trailer
2. Verify — run `git status`; report remaining changes or clean tree

### Report

- Per-commit: version, topic, files included, message
- Summary: total commits, final version, remaining changes if any

## Rules

- Never skip untracked files — always surface for user review before committing
- Every commit bumps z version in `.claude-plugin/plugin.json` for each plugin with changes in that commit
- Commit messages describe end-state results — what the code does now, not what was changed or why during the session
- Never amend previous commits unless user explicitly requests it
- Never force push or run destructive git operations
- Stage specific files by name — never use `git add -A` or `git add .`
- Co-author trailer required: `Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>`
- Single commit when all changes are one coherent topic — do not split artificially
- Commit order matters — if group B depends on changes in group A (e.g., convention before skill that uses it), commit A first
- When user provides message argument, treat all changes as single group — skip topic analysis
