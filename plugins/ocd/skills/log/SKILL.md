---
name: log
description: |
  Capture or manage project log entries — decisions, friction, problems, ideas.
  Reach for this when encountering non-obvious context a future session will need:
  choices with rejected alternatives, process gaps, observed defects, exploratory ideas.
argument-hint: "[add | list | remove]"
allowed-tools:
  - Read
  - Write
  - Glob
  - Bash(rm *)
---

# /log

Create, list, or remove project log entries. Log types and routing guidance live in `.claude/logs/routing.md`; each type's `_template.md` defines entry structure.

## Route

1. Read `.claude/logs/routing.md`
2. If $ARGUMENTS contains "list": {action} = list
3. Else if $ARGUMENTS contains "remove": {action} = remove
4. Else: {action} = add
5. Dispatch Workflow: {action}

## Workflow: Add

1. Determine log type from context using routing guidance
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
- Always read routing.md before creating entries — types may have been customized
- Always read the type's _template.md before creating — structure varies by type
- Remove entries that have been resolved, acted on, or moved to a tracker
