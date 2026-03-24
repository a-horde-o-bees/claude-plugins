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
3. Analyze output — review rule states, skill states, and pending actions; add observations:
  - Modified rules may need redeploying with `/ocd-init --force`
  - Undescribed navigator entries from new files added during session
  - Missing convention files or untracked conventions needing manifest updates
  - Skills without init/status (no infrastructure to report)
4. Present analysis after status output — only include observations that are actionable or non-obvious from the output itself
