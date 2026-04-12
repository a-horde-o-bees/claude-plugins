---
includes: "*"
governed_by:
  - .claude/rules/ocd/design-principles.md
---

# Log Routing

When the agent encounters information worth preserving for a future session, capture it as a log entry in `.claude/logs/`. Log at the moment of encounter — context degrades when deferred.

## Routing

## Log vs Memory

First decide whether to log at all:

- User preferences or personal context → Claude memory, not log
- Project knowledge any user would benefit from → log, not memory

## Routing

| Type | When to use |
|------|-------------|
| decision | Non-obvious choice where alternatives were considered and rejected |
| friction | Gap between how a process should work and how it actually works — workflow-level, not artifact-level |
| problem | Concrete defect in an artifact — wrong output, broken invariant, incorrect behavior |
| idea | Exploratory idea, future work, or improvement suggestion |

## Entry Format

Each entry is a file in `.claude/logs/{type}/{Title}.md`. Title is the entry's subject, used as both the filename and the level-1 heading — short enough to scan in a directory listing, detailed enough to distinguish from siblings. Read the type's `_template.md` for entry structure specific to that type.

## Lifecycle

Logs are a queue, not an archive. Delete entries when resolved, acted on, or moved to an external tracker.

## Custom Types

To add a log type: create a folder in `.claude/logs/` with a `_template.md` describing what qualifies, what doesn't, and entry structure guidance, then add the type to the routing table above.
