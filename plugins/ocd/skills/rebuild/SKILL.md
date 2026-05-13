---
name: rebuild
description: Use whenever the user says "rebuild X" (or "redo X", "rewrite X from scratch", "reauthor X", "regenerate X") or asks to reconstruct an existing artifact from the ground up. Anti-patching discipline: extract what the artifact carries (scope + role + callable surface), set the original aside, compose fresh applying the artifact's own declared rules, then diff to confirm identity preserved. Stackable on any prompt that names a target — file, section, function, or other addressable artifact. Triggers explicitly when the user signals rebuild rather than patch.
allowed-tools:
  - Read
  - Edit
  - Write
  - Bash(find *)
  - Bash(diff *)
  - AskUserQuestion
---

# rebuild

Anti-patching discipline for reconstructing artifacts from scratch. The audit-applicable rules come from the target's own `## Dependencies` declaration; the only rule this skill loads is PFN (needed to interpret `Call:` and the workflow component's process steps).

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

## Workflow

Call: `_rebuild.md` ({artifact}: the target named in the user request)
