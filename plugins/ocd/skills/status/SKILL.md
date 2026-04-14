---
name: status
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
2. Present output to user — no summarization or reformatting

### Report

- Plugin version
- Rules, conventions, and patterns deployment status (per-file current/absent/stale)
- Log template status
- Navigator operational status and entry counts
- Skills list
- Permissions coverage (project and user pattern counts)

## Error Handling

- If script fails: report the failure with exit code and any error output
