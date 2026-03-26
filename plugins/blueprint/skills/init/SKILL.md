---
name: blueprint-init
description: Initialize blueprint research infrastructure in current project
argument-hint: "[--force]"
---

# /blueprint-init

Initialize blueprint research infrastructure in current project.

## Trigger

User runs `/blueprint-init`

## Workflow

1. Run init script — deploy rules and initialize research database
  ```bash
  python3 ${CLAUDE_PLUGIN_ROOT}/scripts/plugin_cli.py init $ARGUMENTS
  ```
2. Present script output to user

### Report

- Script output presented as-is — no summarization, no reformatting
