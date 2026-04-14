---
name: sync-templates
description: Sync plugin governance files from source templates to deployed copies for testing without committing
---

# /sync-templates

Sync plugin governance files from source templates to deployed copies for testing without committing.

## Workflow

1. Sync templates to deployed copies — bash: `python3 scripts/sync-templates.py`
2. If files synced:
    1. Report which files were updated
    2. If rules changed: recommend session restart — rules load at session start and changes take effect only after restart
    3. Else: no restart needed — conventions load on demand, patterns are read when referenced, log templates are read when logging
3. Else: report all deployed copies are current

## Error Handling

- If script fails: report the failure with exit code and any error output
