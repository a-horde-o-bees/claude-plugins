---
name: ocd-status
description: Show plugin version, rule states, skill infrastructure status, and actionable next steps
---

# /ocd-status

Report plugin infrastructure state — version, rule deployment status, skill infrastructure, and permissions coverage.

## Trigger

User runs `/ocd-status`

## Workflow

1. Run status — bash: `python3 ${CLAUDE_PLUGIN_ROOT}/run.py plugin status`
2. Present output to user as-is

### Report

- Script output presented as-is — no summarization, no reformatting
