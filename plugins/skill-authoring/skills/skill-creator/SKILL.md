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

The community skill-creator source is referenced at `sources/anthropics-skills--skill-creator/`; verb workflows invoke its scripts and agent prompts as needed. The directory is gitignored — `composition.md` records the canonical url + pinned commit, and `scripts/_sources.py` clones into `sources/<slug>/` on demand, idempotent on the pin. First-time invocations fetch; subsequent invocations reuse the cache.

## Workflow

1. bash: `cd <THIS-FILE-DIR> && uv run python -m scripts._sources` — ensures upstream sources are present at their pinned commits; clones missing sources from each entry in `composition.md`, reusing cached checkouts at the pin
2. {verb}: first token of $ARGUMENTS
3. {verb-args}: remainder of $ARGUMENTS after {verb}
4. If {verb} is `new`: Call: `_new.md`
5. Else if {verb} is `refine`: Call: `_refine.md` ({name}: first token of {verb-args})
6. Else if {verb} is `list`: Call: `_list.md`
7. Else: Exit process: unrecognized verb {verb} — expected `new`, `refine`, or `list`
