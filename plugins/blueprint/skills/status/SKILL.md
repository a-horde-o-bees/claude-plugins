---
name: status
description: Show blueprint plugin version, rule states, research database status, and actionable next steps
allowed-tools:
  - Bash(python3 *)
---

# /status

Report blueprint plugin infrastructure state.

## Trigger

User runs `/status`

## Workflow

1. Run status script
    ```
    python3 ${CLAUDE_PLUGIN_ROOT}/run.py plugin status
    ```
2. Present output to user as-is

### Report

- Script output presented as-is — no summarization, no reformatting
