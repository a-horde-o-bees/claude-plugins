---
name: sync-templates
description: Push plugin templates to deployed copies for testing without committing
---

# /sync-templates

Push plugin template files (rules, conventions, patterns) from `plugins/` source directories to their deployed locations in `.claude/`. Use when iterating on governance files and need changes to take effect without committing.

## Trigger

User runs `/sync-templates`

## Workflow

1. Sync templates to deployed copies — bash: `python3 scripts/sync-templates.py`
2. If files synced: report which files were updated
3. If no files synced: report all deployed copies are current
4. If rules changed: recommend session restart — rules load at session start and changes take effect only after restart
5. If only conventions or patterns changed: no restart needed — conventions load on demand, patterns are read when referenced
