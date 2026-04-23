---
includes: "*"
governed_by:
  - .claude/rules/ocd/design-principles.md
---

# Log Routing

Captures information worth preserving for a future session. Log at the moment of encounter — context degrades when deferred.

## Log vs Memory

First decide whether to log at all:

- User preferences or personal context → Claude memory, not log
- Project knowledge any user would benefit from → log, not memory

## Routing

| Type | Lifecycle | When to use |
|------|-----------|-------------|
| decision | reference | Non-obvious choice where alternatives were considered and rejected |
| pattern | reference | Reusable workflow shape, methodology, or architectural template |
| research | reference | Long-form investigation of a subject (ecosystem, population of artifacts, design space) backed by per-entity samples |
| friction | working | Gap between how a process should work and how it actually works — workflow-level, not artifact-level |
| problem | working | Concrete defect in an artifact — wrong output, broken invariant, incorrect behavior |
| idea | working | Exploratory idea, future work, or improvement suggestion |

## Lifecycle Cohorts

Log types split into two lifecycle cohorts:

- **Reference** (decision, pattern, research) — semi-permanent. Entries persist as long as they are referenced or applied. Update when direction evolves. Delete only when obsolete or subsumed.
- **Working** (friction, idea, problem) — transient. Entries describe work to act on. Delete when resolved, acted on, or moved to an external tracker.

When capturing, pick the type that matches both *what the content is* and *how long it should persist*. A pattern recorded as an idea will be deleted the next time a cleanup pass runs; a friction recorded as a decision will outstay its relevance.

## Entry Format

Each entry is a file in `logs/{type}/{Title}.md`. Title is the entry's subject, used as both the filename and the level-1 heading — short enough to scan in a directory listing, detailed enough to distinguish from siblings. Read the type's `_template.md` for entry structure specific to that type.

**Research is the exception** — research entries are directories, not single files. `logs/research/{subject}/` holds a consolidated synthesis doc, optional per-wave research outputs, and a `samples/` subdirectory with per-entity evidence files. See `logs/research/_template.md` and `logs/research/_samples-template.md` for the structure.

## Custom Types

To add a log type: create a folder in `logs/` with a `_template.md` describing what qualifies, what doesn't, entry structure guidance, and the lifecycle cohort. Add the type to the routing table above.
