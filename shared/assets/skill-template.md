---
name: <skill-name>
description: <one-line trigger description — see description-authoring>
allowed-tools:
  - <tool pattern>
  - ... (one per tool)
---

# <skill-name>

<brief purpose line — scope + role>

## Dependencies

[Include this section only if the skill declares runtime deps; omit otherwise.]

Run on first load of this file:

bash: `python <THIS-FILE-DIR>/_read_deps.py <dep-name> <another-dep-name>`

## Triggers

| Cognitive moment | Verb |
|---|---|
| <cognitive moment 1> | `<verb-1>` |

Add one row per trigger.

## Verbs

| Verb | Workflow file |
|---|---|
| `<verb-1>` | [`_<verb-1>.md`](_<verb-1>.md) |

Add one row per verb.

## Workflow

1. {verb}: first token of $ARGUMENTS
2. {verb-args}: remainder of $ARGUMENTS after {verb}
3. If {verb} is `<verb-1>`: Call: `_<verb-1>.md`
4. ... (one branch per verb)
5. Else: Exit process: unrecognized verb {verb} — expected <verb-list>
