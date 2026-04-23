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

| Type | Role | When to use |
|------|------|-------------|
| decision | reference | Non-obvious choice where alternatives were considered and rejected |
| pattern | reference | Reusable workflow shape, methodology, or architectural template |
| research | reference | Long-form investigation of a subject (ecosystem, population of artifacts, design space) backed by per-entity samples |
| friction | queue | Gap between how a process should work and how it actually works — workflow-level, not artifact-level |
| problem | queue | Concrete defect in an artifact — wrong output, broken invariant, incorrect behavior |
| idea | queue | Exploratory idea, future work, or improvement suggestion |

## Roles

Log types split into two roles that drive their lifecycle behavior:

- **Reference** (decision, pattern, research) — semi-permanent knowledge. Entries persist as long as they are referenced or applied. Update when direction evolves. Delete only when obsolete or subsumed.
- **Queue** (friction, idea, problem) — transient work items. Entries describe something to act on. Delete when resolved, acted on, or moved to an external tracker.

When capturing, pick the type that matches both *what the content is* and *how long it should persist*. A pattern recorded as an idea will be deleted the next time a cleanup pass runs; a friction recorded as a decision will outstay its relevance.

**Role declaration.** Each log type's `_template.md` declares its role in YAML frontmatter:

```yaml
---
log-role: queue
---
```

This is the machine-readable source of truth — tools and scripts scanning the log system (cleanup verbs, review reports, lifecycle enforcement) read `logs/<type>/_template.md` frontmatter to determine how to treat entries of that type. The prose table above is the human-scannable view; the `log-role` field is authoritative.

## Entry Format

Each entry is a file in `logs/{type}/{Title}.md`. Title is the entry's subject, used as both the filename and the level-1 heading — short enough to scan in a directory listing, detailed enough to distinguish from siblings. Read the type's `_template.md` for entry structure specific to that type.

**Research is the exception** — research entries are directories, not single files. `logs/research/{subject}/` holds a consolidated synthesis doc, optional per-wave research outputs, and a `samples/` subdirectory with per-entity evidence files. See `logs/research/_template.md` and `logs/research/_samples-template.md` for the structure.

## Custom Types

To add a log type:

1. Create a folder in `logs/<type-name>/`.
2. Add `_template.md` with:
    - YAML frontmatter declaring `log-role: queue` or `log-role: reference`.
    - Prose describing what qualifies, what doesn't, and entry structure guidance.
    - A Lifecycle section that elaborates the declared role's behavior for this specific type.
3. Add the type to the routing table above.

The frontmatter `log-role` field is what tooling keys off of — it must match the prose role assignment and the routing table entry, or cleanup scripts will treat the type inconsistently.
