# Project Log

Structured capture of non-obvious context that future sessions need. Each log type has its own folder; each entry is a markdown file named for its title.

## When to Log

Log at the moment of encounter. Context degrades when deferred.

## Routing

| Type | When to use |
|------|-------------|
| decision | Non-obvious choice where alternatives were considered and rejected |
| friction | Process gap encountered during work that can't be fixed immediately |
| problem | Observed defect or issue needing investigation later |
| idea | Exploratory idea, future work, or improvement suggestion |

**Routing vs alternatives:**

- Settled choice with rationale → decision
- Mid-workflow gap or broken process → friction or problem
- User preferences or personal context → Claude memory, not log
- Project knowledge any user would benefit from → log, not memory

## Entry Format

Filename is the title. Content opens with the title heading and a purpose statement.

```
.claude/logs/{type}/{Title}.md
```

```markdown
# Title

## Purpose

What this entry captures and why it matters.
```

Each type's `_template.md` describes additional structure specific to that type.

## Lifecycle

Logs are a queue, not an archive. Delete entries when resolved, acted on, or moved to an external tracker.

## Custom Types

Add a folder to `.claude/logs/` with a `_template.md` describing what qualifies, what doesn't, and any entry structure guidance. The folder name is the type name.
