---
name: plugin
description: Manage ocd plugin infrastructure — deploy governance files and subsystems, report current state, or walk through guided setup.
argument-hint: "<list | install | guided> [--force]"
allowed-tools:
  - AskUserQuestion
  - Bash(python3 *)
---

# /plugin

Manage ocd plugin infrastructure — deploy governance files and subsystems, report current state, or walk through guided setup.

## Rules

- Permissions deploy to exactly one scope — deploying to both is not an option
- Non-recommended patterns (user's custom additions) are never modified by deploy or clean
- User scope cleanup warns about cross-project impact before proceeding
- Clean only removes patterns that exist in both the template and the other scope

## Workflow

1. If not $ARGUMENTS: Exit to user: skill description and argument-hint

> Verb dispatch — list reports, install deploys, guided walks through interactively.

2. If {verb} is `list`:
    1. Call: List
3. Else if {verb} is `install`:
    1. Call: Install
4. Else if {verb} is `guided`:
    1. Call: Guided
5. Else: Exit to user: unrecognized verb {verb} — expected list, install, or guided

## List

> Report current infrastructure state without changing anything.

1. bash: `python3 ${CLAUDE_PLUGIN_ROOT}/run.py plugin list`
2. Present output to user — no summarization or reformatting
3. Return to caller

### Report

- Plugin version
- Per-subsystem deployment and operational status (rules, conventions, patterns, logs, navigator, permissions)
- Skills list

## Install

> Deploy every lib subsystem — rules, conventions, patterns, logs, navigator. Safe by default — only deploys absent files, skips divergent. `--force` overwrites divergent files with plugin defaults.

1. If --force: bash: `python3 ${CLAUDE_PLUGIN_ROOT}/run.py plugin install --force`
2. Else: bash: `python3 ${CLAUDE_PLUGIN_ROOT}/run.py plugin install`
3. Present install output to user
4. Return to caller

## Guided

> Interactive walkthrough — show current state, explain what install will do, confirm with user, then deploy. Offers permissions setup as an optional final step.

1. bash: `python3 ${CLAUDE_PLUGIN_ROOT}/run.py plugin list`
2. Present current state to user — explain what each section means and what actions are available
3. If any files show `absent` or `stale`: explain that install will deploy or update them
4. If any files show `divergent`:
    1. If --force: explain that force mode will overwrite divergent files with plugin defaults
    2. Else: explain that divergent files will be preserved; offer to enable force mode
5. Ask user to confirm — AskUserQuestion with options: `["Proceed with install", "Cancel"]`
6. If cancel: Exit to user: setup cancelled
7. Call: Install
8. Ask user about permissions — AskUserQuestion with options: `["Configure permissions", "Skip"]`
9. If configure: Call: `_permissions-setup.md`
10. Return to caller
