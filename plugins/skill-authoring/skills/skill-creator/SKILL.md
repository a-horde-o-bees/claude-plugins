---
name: skill-creator
description: Use whenever the user wants to create a new skill from scratch — interview, draft, iterate, optimize the trigger, and package — with PFN + progressive-disclosure + description-authoring + workflow-vs-script disciplines applied at every authoring moment. Companion to skill-composer (compose layers existing sources; create authors from scratch with discipline). Trigger on phrases like "create a new skill", "make a skill for X", "design a skill that...", "I want to write a skill", "draft a skill", "skill from scratch", or any context where the user is initiating a new skill rather than composing from sources or rebuilding an existing one.
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

Read each if not already in context. Discover via `find ~/.claude <project>/.claude -path "*dependencies/<name>.md" -type f 2>/dev/null`. Selection: prefer user-scope; prefer `rules/dependencies/` over plain `dependencies/`; skill-bundled is last resort. User-scope skills skip project matches.

- [[process-flow-notation]]
- [[progressive-disclosure]]
- [[workflow-vs-script]]
- [[description-authoring]]
- [[markdown]]

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

1. {verb} = first token of $ARGUMENTS
2. {verb-args} = remainder of $ARGUMENTS after {verb}
3. If {verb} is `new`: Call: `_new.md`
4. Else if {verb} is `refine`: Call: `_refine.md` ({name} = first token of {verb-args})
5. Else if {verb} is `list`: Call: `_list.md`
6. Else: Exit to user: unrecognized verb {verb} — expected `new`, `refine`, or `list`
