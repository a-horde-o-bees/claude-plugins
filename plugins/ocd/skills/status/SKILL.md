---
description: Report plugin infrastructure state
allowed-tools:
  - Bash(python3 *)
---

# /status

Report plugin infrastructure state.

## Trigger

User runs `/status`

## Workflow

1. Run status — bash: `python3 ${CLAUDE_PLUGIN_ROOT}/run.py plugin status`
2. Present output to user

### Report

- Plugin status CLI output

## Rules

- Present script output without summarization or reformatting

## Error Handling

- If script fails: report the failure with exit code and any error output
