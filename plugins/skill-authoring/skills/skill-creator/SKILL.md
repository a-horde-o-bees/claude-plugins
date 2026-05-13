---
name: skill-creator
description: Use whenever the user wants to create a new skill from scratch — interview, draft, iterate, package — with project authoring discipline applied inline. Companion to skill-composer (compose layers existing sources; create authors from scratch). Trigger on phrases like "create a new skill", "make a skill for X", "design a skill that...", "I want to write a skill", "draft a skill", "skill from scratch".
allowed-tools:
  - Read
  - Edit
  - Write
  - Bash(grep *)
  - Bash(find *)
  - Bash(git *)
---

# skill-creator

From-scratch skill authoring with our project's authoring disciplines applied inline. Pairs with `/skill-authoring:skill-composer` — compose layers existing sources; create authors fresh.

## Dependencies

1. {dependencies}:
    - [[process-flow-notation]]
    - [[progressive-disclosure]]
    - [[workflow-vs-script]]
    - [[description-authoring]]
    - [[markdown]]
2. For each {dependency} in {dependencies}:
    1. {found}: bash: `find ~/.claude <project>/.claude -path "*dependencies/{dependency}.md" -not -path "*/_dependencies/*" -type f 2>/dev/null`
    2. If {found} is empty:
        1. {scope}: `<project>` if `<skill-base>` starts with `<project>`, else `~`
        2. bash: `cp <skill-base>/_dependencies/{dependency}.md {scope}/.claude/dependencies/{dependency}.md`
        3. {path}: the cp target
    3. Else: {path}: first of {found} — prefer user-scope; `rules/dependencies/` over plain `dependencies/`; user-scope skills skip project matches
    4. Read {path} if not in context

## Triggers

| Cognitive moment | Verb |
|---|---|
| User wants to start designing a new skill from scratch | `new` |
| User wants to iterate on an in-progress skill (run tests, review feedback, refine) | `refine <name>` |
| User asks what skills are in flight | `list` |

## Verbs

| Verb | Workflow file |
|---|---|
| `new` | [`_new.md`](_new.md) |
| `refine <name>` | [`_refine.md`](_refine.md) |
| `list` | [`_list.md`](_list.md) |

The community skill-creator source is embedded at `sources/anthropics-skills--skill-creator/` during active development; verb workflows invoke its scripts and agent prompts as needed.

## Workflow

1. {verb}: first token of $ARGUMENTS
2. {verb-args}: remainder of $ARGUMENTS after {verb}
3. If {verb} is `new`: Call: `_new.md`
4. Else if {verb} is `refine`: Call: `_refine.md` ({name}: first token of {verb-args})
5. Else if {verb} is `list`: Call: `_list.md`
6. Else: Exit to user: unrecognized verb {verb} — expected `new`, `refine`, or `list`
