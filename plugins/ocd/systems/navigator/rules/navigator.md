---
includes: "*"
governed_by:
  - .claude/rules/ocd/design-principles.md
---

# Navigator Usage

When to reach for the navigator MCP server for project-structure queries versus Grep or Glob.

## Purpose-Based Queries

Prefer navigator tools when the query is about what a file does rather than what it contains:

- Find files by purpose → `paths_search` (navigator indexes human-written descriptions; Grep searches content)
- Browse structure with descriptions → `paths_get` (start with `.` for top-level overview)
- Locate a skill across discovery locations → `skills_resolve`
- Trace file reference graphs → `references_map` or `scope_analyze`

## Content and Name Queries

Prefer Grep for content patterns — function names, string literals, regex matching. Prefer Glob for file name patterns — extensions, naming conventions.

## Orientation Order

Navigator first for orientation in unfamiliar areas, then Grep or Glob for specific searches once the relevant directories are known. Reading every file to find the right one is wasted context when purposes are already indexed.
