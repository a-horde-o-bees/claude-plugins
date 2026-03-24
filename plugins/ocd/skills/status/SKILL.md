---
name: ocd-status
description: Show plugin version, rule states, skill infrastructure status, and actionable next steps
---

# /ocd-status

Report plugin infrastructure state.

## Trigger

User runs `/ocd-status`

## Workflow

1. Run status script
  ```
  python3 ${CLAUDE_PLUGIN_ROOT}/scripts/status.py
  ```
2. Present output to user as-is

### Report

- Script output presented as-is
