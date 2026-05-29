---
name: rules
description: Use to manage always-on agent guidance via CLAUDE.md. /rules add <skill> appends a `Read /<skill>` directive to user-scope or project-scope CLAUDE.md so Claude loads that skill's body every session, making the skill effectively always-on. /rules remove undoes. /rules list shows currently promoted skills. Trigger on phrases like "promote /honesty to always-on", "add an always-on rule", "what rules are deployed", "remove always-on rule X", or any request to manage the always-on skill layer.
argument-hint: "<add | remove | list> [<skill>] [--scope <user | project>]"
allowed-tools:
  - Read
  - Edit
  - Write
  - Bash(ls *)
  - AskUserQuestion
---

# rules

Promote an installed skill to always-on by appending a `Read /<skill>` directive to CLAUDE.md between dedicated sentinel comments. The directive prompts Claude to load the skill's body every session — making it effectively always-on without enlarging the description budget.

## Triggers

| Cognitive moment | Verb |
|---|---|
| User wants to promote a skill to always-on | `add <skill> [--scope <user\|project>]` |
| User wants to demote an always-on skill | `remove <skill> [--scope <user\|project>]` |
| User wants to see what's currently promoted | `list [--scope <user\|project>]` |

## Scope and target files

| Scope | Target file | Effect |
|-------|-------------|-------|
| `user` (default) | `~/.claude/CLAUDE.md` | Every project the user works in |
| `project` | `<project>/CLAUDE.md` | Only when working in that project |

## CLAUDE.md edit pattern

Promoted skills land between dedicated sentinel comments so this skill can find and modify them idempotently:

```markdown
<!-- BEGIN rules:promoted -->
Read /honesty
Read /concise-prose
Read /principled-pushback
<!-- END rules:promoted -->
```

`add` inserts the block (or adds a line to an existing block); `remove` strips the matching line and prunes an emptied block; `list` reads the block.

Idempotency rules:

- `add /X` to a file that already contains `Read /X` in the block is a no-op
- `remove /X` from a file that doesn't contain `Read /X` is a no-op (reports "not promoted")
- If `remove` empties the block, the sentinels and block are stripped together

## Workflow

1. {verb}: first token of $ARGUMENTS
2. {verb-args}: remainder of $ARGUMENTS after {verb}
3. If {verb} is empty: Exit to user: skill description and argument-hint
4. Else if {verb} is `add`: Call: `_add.md` ({args}: {verb-args})
5. Else if {verb} is `remove`: Call: `_remove.md` ({args}: {verb-args})
6. Else if {verb} is `list`: Call: `_list.md` ({args}: {verb-args})
7. Else: Exit to user: unrecognized verb {verb} — expected `add`, `remove`, or `list`
