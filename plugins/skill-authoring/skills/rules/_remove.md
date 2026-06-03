# Remove — demote an always-on skill

## Variables

- {args} — verb arguments: `<skill> [--scope <user | project>]`

## Process

1. Parse {args}:
    1. {skill}: first positional token, stripped of leading `/` if present
    2. {scope}: value of `--scope` flag if present, else `user`

2. If {skill} is empty: Exit process: skill name required — usage: `/rules remove <skill> [--scope <user | project>]`
3. If {scope} not in (`user`, `project`): Exit process: invalid scope {scope} — expected `user` or `project`
4. Resolve {target-file}:
    - If {scope} is `user`: {target-file} = `~/.claude/CLAUDE.md`
    - Else: {target-file} = `<project-root>/CLAUDE.md`

5. If {target-file} doesn't exist: Exit process: `/{skill}` not promoted at {scope} scope — {target-file} doesn't exist
6. {body}: Read: {target-file}
7. Locate the sentinel block in {body}:
    - {begin-line}: index of line matching `<!-- BEGIN rules:promoted -->`
    - {end-line}: index of line matching `<!-- END rules:promoted -->`

8. If block missing: Exit process: `/{skill}` not promoted at {scope} scope — no sentinel block in {target-file}
9. {block-lines}: lines between sentinels (exclusive)
10. If `Read /{skill}` not in {block-lines}: Exit process: `/{skill}` not promoted at {scope} scope — no matching line in block
11. Remove the line `Read /{skill}` from {block-lines}
12. If {block-lines} is empty after removal:
    1. Strip both sentinels and any single trailing blank line
    2. {new-body}: {body} with the entire block removed
    3. Write: {target-file} ← {new-body}
    4. Exit process: demoted `/{skill}` at {scope} scope — block emptied, sentinels removed from {target-file}

13. Else block retains other promotions:
    1. Write: {target-file} ← updated {body}
    2. Exit process: demoted `/{skill}` at {scope} scope — removed line from block in {target-file}
