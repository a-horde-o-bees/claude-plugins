# Log: Add

Create a new log entry under the appropriate type.

## Process

1. Determine log type from context using the log-routing rule
2. Read `.claude/logs/{type}/_template.md`
3. {title} = descriptive title for the entry
4. Create `.claude/logs/{type}/{title}.md`:
    1. `# {title}`
    2. `## Purpose` — what this entry captures
    3. Body content following _template.md guidance

## Report

- File path created, log type, and title
