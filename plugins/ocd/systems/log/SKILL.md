---
name: log
description: Capture or manage project log entries — decisions, friction, problems, ideas. Reach for this when encountering non-obvious context a future session will need — choices with rejected alternatives, process gaps, observed defects, exploratory ideas.
argument-hint: "<add | list | remove>"
allowed-tools:
  - Read
  - Write
  - Glob
  - Bash(rm *)
---

# /log

Create, list, or remove project log entries. Log type routing is in always-on context via the log-routing rule; each type's `_template.md` in `logs/{type}/` defines entry structure.

## Rules

- Entry filenames are titles — descriptive, spaces allowed, no sequence numbers
- Always read the type's _template.md before creating — structure varies by type
- Remove entries that have been resolved, acted on, or moved to a tracker

## Workflow

1. If $ARGUMENTS contains "list": Call: `_list.md`
2. Else if $ARGUMENTS contains "remove": Call: `_remove.md`
3. Else: Call: `_add.md`
