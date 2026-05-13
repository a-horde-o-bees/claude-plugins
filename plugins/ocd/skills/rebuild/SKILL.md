---
name: rebuild
description: Use whenever the user says "rebuild X" (or "redo X", "rewrite X from scratch", "reauthor X", "regenerate X") or asks to reconstruct an existing artifact applying currently-loaded rules and disciplines. Re-evaluates the artifact against active rules and rewrites it as if authoring for the first time. Gates on ambiguous scope or structural divergence from the original. Use after a rule has evolved, a rename or split, when a loaded rule was missed at draft, or when discipline drift has accumulated.
allowed-tools:
  - Read
  - Edit
  - Write
  - Bash(grep *)
  - Bash(find *)
---

# rebuild

Re-evaluate an existing artifact against the currently-loaded rule set and rewrite it as if authoring for the first time.

## Dependencies

Read each if not already in context. Discover via `find ~/.claude <project>/.claude -path "*dependencies/<name>.md" -not -path "*/_dependencies/*" -type f 2>/dev/null`. Selection: prefer user-scope; prefer `rules/dependencies/` over plain `dependencies/`. User-scope skills skip project matches. If discovery returns nothing, the dep is not deployed — operate without it.

- [[process-flow-notation]]

## Triggers

| Cognitive moment | Phrasing |
|---|---|
| Reauthor with current discipline | "rebuild X", "redo X", "regenerate X", "rewrite X from scratch", "reauthor X" |
| Audit-and-rewrite after rule evolution | "reapply rules to X", "X needs to follow [discipline]" |
| Discipline-drift cleanup | "X still uses old terminology", "audit X against [discipline]" |

## Workflow

Call: `_rebuild.md` ({artifact} = the target named in the user request)
