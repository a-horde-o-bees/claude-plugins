---
name: status
description: Report plugin infrastructure state — version, rule deployment status, skill infrastructure, and permissions coverage
allowed-tools:
  - Bash(python3 *)
---

# /status

Report plugin infrastructure state — version, rule deployment status, skill infrastructure, and permissions coverage.

## Trigger

User runs `/status`

## Workflow

1. Run status — bash: `python3 ${CLAUDE_PLUGIN_ROOT}/run.py plugin status`
2. Present output to user

### Report

- CLI output from `python3 ${CLAUDE_PLUGIN_ROOT}/run.py plugin status`, unmodified

## Rules

- Present script output without summarization or reformatting

## Error Handling

- If script fails: report the failure with exit code and any error output
