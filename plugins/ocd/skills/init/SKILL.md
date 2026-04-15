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

## Rules

- Permissions deploy to exactly one scope — deploying to both is not an option
- Non-recommended patterns (user's custom additions) are never modified by deploy or clean
- User scope cleanup warns about cross-project impact before proceeding
- Clean only removes patterns that exist in both the template and the other scope

## Workflow

> `--force` overwrites divergent rules and conventions with plugin defaults; without it, divergent files are preserved. `--permissions` enables the permissions deployment subflow.

1. If --force: bash: `python3 ${CLAUDE_PLUGIN_ROOT}/run.py plugin init --force`
2. Else: bash: `python3 ${CLAUDE_PLUGIN_ROOT}/run.py plugin init`
3. Present init output to user
4. If --permissions: Call: `_permissions-setup.md`
