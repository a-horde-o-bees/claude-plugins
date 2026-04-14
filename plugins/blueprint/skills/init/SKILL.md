---
name: init
description: Initialize blueprint research infrastructure in current project
argument-hint: "[--force]"
allowed-tools:
  - Bash(python3 *)
---

# /init

Initialize blueprint research infrastructure in current project.

## Trigger

User runs `/init`

## Workflow

1. Run init script — deploy rules and initialize research database
    ```bash
    python3 ${CLAUDE_PLUGIN_ROOT}/run.py plugin init $ARGUMENTS
    ```
2. Present script output to user

### Report

- Script output presented as-is — no summarization, no reformatting
