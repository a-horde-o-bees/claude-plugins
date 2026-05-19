# Add — promote a skill to always-on

### Variables

- {args} — verb arguments: `<skill> [--scope <user | project>]`

### Process

1. Parse {args}:
    1. {skill}: first positional token, stripped of leading `/` if present
    2. {scope}: value of `--scope` flag if present, else `user`

2. If {skill} is empty: Exit to user: skill name required — usage: `/rules add <skill> [--scope <user | project>]`

3. If {scope} not in (`user`, `project`): Exit to user: invalid scope {scope} — expected `user` or `project`

4. Resolve {target-file}:
    - If {scope} is `user`: {target-file} = `~/.claude/CLAUDE.md` (expand `~`)
    - Else: {target-file} = `<project-root>/CLAUDE.md`

5. {body}:
    - If {target-file} doesn't exist: empty string
    - Else: Read: {target-file}

6. Locate the sentinel block in {body}:
    - {begin-line}: index of line matching exactly `<!-- BEGIN rules:promoted -->`
    - {end-line}: index of line matching exactly `<!-- END rules:promoted -->`

7. If block missing (no sentinels):
    1. {new-block} = 3 lines: `<!-- BEGIN rules:promoted -->\nRead /{skill}\n<!-- END rules:promoted -->`
    2. {new-body} = {body} with {new-block} appended (preceded by blank line if {body} non-empty and doesn't end in blank)
    3. Write: {target-file} ← {new-body}
    4. Exit to user: promoted `/{skill}` to always-on at {scope} scope — created sentinel block in {target-file}

8. Else block exists:
    1. {block-lines}: lines between sentinels (exclusive)
    2. If any line equals `Read /{skill}`: Exit to user: `/{skill}` already promoted at {scope} scope — no change
    3. Insert `Read /{skill}` as the last line inside the block (before END sentinel)
    4. Write: {target-file} ← updated {body}
    5. Exit to user: promoted `/{skill}` to always-on at {scope} scope — appended to existing block in {target-file}
