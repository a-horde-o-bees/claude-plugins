# List — show currently promoted skills

## Variables

- {args} — verb arguments: `[--scope <user | project>]`

## Process

1. Parse {args}:
    1. {scope}: value of `--scope` flag if present, else `both`

2. If {scope} not in (`user`, `project`, `both`): Exit process: invalid scope {scope} — expected `user`, `project`, or omit for both
3. For each target in scopes-to-list:
    1. If target is `user`: {target-file} = `~/.claude/CLAUDE.md`
    2. Else: {target-file} = `<project-root>/CLAUDE.md`
    3. If {target-file} doesn't exist:
        1. Render: `{target}: (no CLAUDE.md)`
        2. Continue next
    4. {body}: Read: {target-file}
    5. Locate sentinel block:
        1. {begin-line}: line matching `<!-- BEGIN rules:promoted -->`
        2. {end-line}: line matching `<!-- END rules:promoted -->`
    6. If block missing:
        1. Render: `{target}: (no promotions)`
        2. Continue next
    7. {block-lines}: lines between sentinels (exclusive)
    8. {promoted}: each line matching `Read /<name>` → extract `<name>`
    9. Render: `{target}: {promoted-list}`

4. Exit process: rendered list
