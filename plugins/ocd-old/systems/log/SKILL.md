---
name: log
description: Capture or manage project log entries (decisions, friction, problems, ideas) and analyze research corpora. Reach for this when encountering non-obvious context a future session will need, or when auditing heading-tree structure across research samples.
argument-hint: "<add | list | remove | research <verb>>"
allowed-tools:
  - Read
  - Write
  - Glob
  - Bash(rm *)
  - Bash(ocd-run:*)
---

# /log

Create, list, or remove project log entries, or run structural analysis against research corpora. Log type routing is in always-on context via the log-routing rule; each type's `_template.md` in `logs/{type}/` defines entry structure. Research analysis operates on markdown samples under `logs/research/<subject>/samples/` — safe, read-only inspection of heading trees, coverage, and cross-sample section content.

## Rules

- Entry filenames are titles — descriptive, spaces allowed, no sequence numbers
- Always read the type's _template.md before creating — structure varies by type
- Remove entries that have been resolved, acted on, or moved to a tracker
- `research` verbs analyze existing samples without modifying them — safe to run repeatedly during deconfliction

## Workflow

1. If $ARGUMENTS starts with "research": Call: `_research.md`
2. Else if $ARGUMENTS contains "list": Call: `_list.md`
3. Else if $ARGUMENTS contains "remove": Call: `_remove.md`
4. Else: Call: `_add.md`
