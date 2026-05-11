---
log-role: reference
---

# Filesystem truth over frontmatter flags

When a fact about a system can be derived from filesystem state (does this file exist? is this directory non-empty?), prefer deriving it over maintaining a parallel frontmatter flag that has to be kept in sync. Filesystem state is the system; a flag describing the system is a duplicate that can drift.

## When to use

- Adding a status field to a frontmatter or config: ask first whether filesystem already tells the same story.
- Encountering a sync bug between a flag and the actual state it describes: the flag is the bug.
- Removing fields during a schema cleanup: filesystem-derivable ones go first.

## Pattern

State is encoded once, at its natural location:

- "Skill is deployed" → `SKILL.md` exists in the skill folder.
- "Composition has sources" → frontmatter `sources` list is populated (the list IS the data, not a flag describing it).
- "Skill folder exists" → directory exists, not a `created: true` flag.

Operations that gate on state read the filesystem at decision time, not a cached flag.

## Pitfalls

- "But it's expensive to check the filesystem every time" — usually a non-issue at human timescales. Profile before adding a flag for performance.
- Caching the filesystem check is fine when the operation runs in a tight loop; the cache is implementation detail, not a serialized flag.

## Anti-patterns

- `build_status: built | draft` flag when "is SKILL.md present?" answers the same question.
- `last_built: <timestamp>` when `os.stat(SKILL.md).st_mtime` answers it.
- `operational: true | false` when the live skill's behavior is the observable fact.

## See also

- progressive-skill-composer composition.md schema — explicitly dropped `last_build` and `build_status` in favor of SKILL.md presence (`logs/decision/progressive-skill-composer.md` § *composition.md as alignment doc, not blueprint*).
- `single-source-of-truth` rule.
