---
includes: "*"
governed_by:
  - .claude/rules/ocd/design-principles.md
---

# Log Routing

When the agent encounters information worth preserving for a future session, capture it as a log entry in `.claude/logs/`. Log at the moment of encounter — context degrades when deferred.

## Routing

| Type | When to use |
|------|-------------|
| decision | Non-obvious choice where alternatives were considered and rejected |
| friction | Process gap encountered during work that can't be fixed immediately |
| problem | Observed defect or issue needing investigation later |
| idea | Exploratory idea, future work, or improvement suggestion |

## Routing vs Alternatives

- User preferences or personal context → Claude memory, not log
- Project knowledge any user would benefit from → log, not memory

## Entry Format

Each entry is a file in `.claude/logs/{type}/{Title}.md`. Title is the entry's subject, used as both the filename and the level-1 heading. Read the type's `_template.md` for entry structure specific to that type.

## Lifecycle

Logs are a queue, not an archive. Delete entries when resolved, acted on, or moved to an external tracker.

## Custom Types

To add a log type: create a folder in `.claude/logs/` with a `_template.md` describing what qualifies, what doesn't, and entry structure guidance, then add the type to the routing table above.
