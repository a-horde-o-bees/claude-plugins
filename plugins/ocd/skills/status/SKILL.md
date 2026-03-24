---
name: ocd-status
description: Show plugin version, rule states, skill infrastructure status, and actionable next steps
---

# /ocd-status

Report plugin infrastructure state with analysis.

## Trigger

User runs `/ocd-status`

## Route

1. Run status script
  ```
  python3 ${CLAUDE_PLUGIN_ROOT}/scripts/status.py
  ```
2. Present output to user as-is
3. Analyze output — add observations that are actionable or non-obvious from the raw output itself
