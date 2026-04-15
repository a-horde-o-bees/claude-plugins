---
name: status
description: Report plugin infrastructure state
allowed-tools:
  - Bash(python3 *)
---

# /status

Report plugin infrastructure state.

## Workflow

1. Collect plugin state — bash: `python3 ${CLAUDE_PLUGIN_ROOT}/run.py plugin status`
2. Present output to user — no summarization or reformatting

### Report

- Plugin version
- Rules, conventions, and patterns deployment status (per-file current/absent/stale)
- Log template status
- MCP Servers — per-server deployment and operational status
- Skills list
- Permissions coverage (project and user pattern counts)
