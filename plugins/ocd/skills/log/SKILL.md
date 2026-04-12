---
description: Capture or manage project log entries — decisions, friction, problems, ideas. Reach for this when encountering non-obvious context a future session will need — choices with rejected alternatives, process gaps, observed defects, exploratory ideas.
argument-hint: "[add | list | remove]"
allowed-tools:
  - Read
  - Write
  - Glob
  - Bash(rm *)
---

# /log

Create, list, or remove project log entries. Log type routing is in always-on context via the log-routing rule; each type's `_template.md` in `.claude/logs/{type}/` defines entry structure.

## Route

1. If $ARGUMENTS contains "list": {action} = list
2. Else if $ARGUMENTS contains "remove": {action} = remove
3. Else: {action} = add
4. Dispatch Workflow: {action}

## Workflow: Add

1. Determine log type from context using the log-routing rule
2. Read `.claude/logs/{type}/_template.md`
3. {title} = descriptive title for the entry
4. Create `.claude/logs/{type}/{title}.md`:
    1. `# {title}`
    2. `## Purpose` — what this entry captures
    3. Body content following _template.md guidance

### Report

- File path created, log type, and title

## Workflow: List

1. For each type directory in `.claude/logs/`:
    1. Glob: `*.md` excluding `_template.md`
2. Present entry titles grouped by type

### Report

- Entry count per type with titles

## Workflow: Remove

1. If no path in $ARGUMENTS: list entries, ask which to remove
2. Delete the specified file
3. Confirm removal

### Report

- Path of removed entry

## Rules

- Entry filenames are titles — descriptive, spaces allowed, no sequence numbers
- Always read the type's _template.md before creating — structure varies by type
- Remove entries that have been resolved, acted on, or moved to a tracker
