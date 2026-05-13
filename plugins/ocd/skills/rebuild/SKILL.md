---
name: rebuild
description: Use whenever the user says "rebuild X" (or "redo X", "rewrite X from scratch", "reauthor X", "regenerate X") or asks to reconstruct an existing artifact from the ground up. Anti-patching alternative to surgical edits — rewrites the target applying its own declared rules, preserving identity. Stackable on any prompt that names a target (file, section, function, or other addressable artifact).
allowed-tools:
  - Read
  - Edit
  - Write
  - Bash(find *)
  - Bash(diff *)
  - Bash(mkdir *)
  - Bash(cp *)
  - Task
  - AskUserQuestion
---

# rebuild

Anti-patching discipline. Reconstruct the target from scratch applying its own declared rules; preserve identity. Three-agent orchestration — extract, compose, verify — each in an isolated spawned context so composition is structurally insulated from patch-bias. The audit-applicable rules come from the target's own `## Dependencies` declaration; rebuild doesn't impose its own ruleset.

## Dependencies

1. {dependencies}:
    - [[process-flow-notation]]
2. For each {dependency} in {dependencies}:
    1. {found}: bash: `find ~/.claude <project>/.claude -path "*dependencies/{dependency}.md" -not -path "*/_dependencies/*" -type f 2>/dev/null`
    2. If {found} is empty:
        1. {scope}: `<project>` if `<skill-base>` starts with `<project>`, else `~`
        2. bash: `cp <skill-base>/_dependencies/{dependency}.md {scope}/.claude/dependencies/{dependency}.md`
        3. {path}: the cp target
    3. Else: {path}: first of {found} — prefer user-scope; `rules/dependencies/` over plain `dependencies/`; user-scope skills skip project matches
    4. Read {path} if not in context

## Triggers

| Cognitive moment | Phrasing |
|---|---|
| Reauthor with current discipline | "rebuild X", "redo X", "regenerate X", "rewrite X from scratch", "reauthor X" |
| Audit-and-rewrite after rule evolution | "reapply rules to X", "X needs to follow [discipline]" |
| Discipline-drift cleanup | "X still uses old terminology", "audit X against [discipline]" |
| Anti-patching modifier on any rebuild request | User wants the target reconstructed from scratch, not surgically patched |

## When NOT to use

- Adding a new rule or discipline that didn't previously exist — that's a content change, not a rebuild. Add the rule directly.
- Fixing a localized bug in one workflow step — use a targeted edit; rebuild's overhead isn't warranted.
- Verifying conformance without changing the artifact — use `/ocd:check` if available, or audit the file in place.
- Renaming a symbol or moving a file — that's a refactor, not a rebuild.

## Workflow

Call: `_rebuild.md` ({artifact}: the target named in the user request)
