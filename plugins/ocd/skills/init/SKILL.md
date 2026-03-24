---
name: ocd-init
description: Initialize ocd conventions and skill infrastructure in current project
argument-hint: "[--force]"
---

# /ocd-init

Initialize ocd conventions and skill infrastructure in current project.

## Trigger

User runs `/ocd-init`

## Workflow

1. Run init script — deploy conventions and initialize infrastructure
  ```bash
  python3 ${CLAUDE_PLUGIN_ROOT}/scripts/init.py $ARGUMENTS
  ```
2. Present script output to user

### Report

- Script output presented as-is
