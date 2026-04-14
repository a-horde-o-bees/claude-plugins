---
name: init
description: Initialize ocd conventions and skill infrastructure in current project
argument-hint: "[--force] [--permissions]"
allowed-tools:
  - AskUserQuestion
  - Bash(python3 *)
---

# /init

Deploy rules, conventions, and skill infrastructure to the current project. Safe by default — only deploys absent files, skips files the user has edited.

## Trigger

User runs `/init`

## Route

1. If --force: bash: `python3 ${CLAUDE_PLUGIN_ROOT}/run.py plugin init --force`
2. Else: bash: `python3 ${CLAUDE_PLUGIN_ROOT}/run.py plugin init`
3. Present init output to user
4. If not --permissions: Exit to user — init complete

### Permissions Setup

5. Report — bash: `python3 ${CLAUDE_PLUGIN_ROOT}/run.py plugin permissions report`
6. Present report with scope education:

    - **Project scope** (`.claude/settings.json`) — applies to this project only; version controlled; shared with collaborators
    - **User scope** (`~/.claude/settings.json`) — applies to all projects on this machine; personal preference; not shared

7. Ask scope — AskUserQuestion with options: `["Project scope", "User scope"]`
8. {scope} = `project` if user chose "Project scope", else `user`
9. Deploy — bash: `python3 ${CLAUDE_PLUGIN_ROOT}/run.py plugin permissions deploy --scope {scope}`
10. Present deploy results
11. Analyze — bash: `python3 ${CLAUDE_PLUGIN_ROOT}/run.py plugin permissions analyze`
12. If redundancy count > 0:
    1. {other-scope} = opposite of {scope}
    2. If {other-scope} is `user`: Warn — removing from user scope affects all projects on this machine
    3. Ask cleanup — AskUserQuestion with options: `["Clean {other-scope} scope", "Keep both"]`
    4. If cleanup chosen:
        1. Clean — bash: `python3 ${CLAUDE_PLUGIN_ROOT}/run.py plugin permissions clean --scope {other-scope}`
        2. Present clean results

### --force

Overwrites divergent rules and conventions with plugin defaults. Use when deployed files have diverged and the user wants to reset to plugin baseline. Without `--force`, divergent files are preserved.

## Rules

- Permissions deploy to exactly one scope — deploying to both is not an option
- Non-recommended patterns (user's custom additions) are never modified by deploy or clean
- User scope cleanup warns about cross-project impact before proceeding
- Clean only removes patterns that exist in both the template and the other scope
