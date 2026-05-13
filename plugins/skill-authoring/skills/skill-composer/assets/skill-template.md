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

Read each if not already in context. Discover via `find ~/.claude <project>/.claude -path "*dependencies/<name>.md" -not -path "*/_dependencies/*" -type f 2>/dev/null`. Selection: prefer user-scope; prefer `rules/dependencies/` over plain `dependencies/`. User-scope skills skip project matches. If discovery returns nothing, the dep is not deployed — operate without it.

- [[<dep-name>]]
- ... (one per dep)

## Triggers

| Cognitive moment | Verb |
|---|---|
| <cognitive moment 1> | `<verb-1>` |
| ... (one row per trigger) |

## Verbs

| Verb | Workflow file |
|---|---|
| `<verb-1>` | [`_<verb-1>.md`](_<verb-1>.md) |
| ... (one row per verb) |

## Workflow

1. {verb} = first token of $ARGUMENTS
2. {verb-args} = remainder of $ARGUMENTS after {verb}
3. If {verb} is `<verb-1>`: Call: `_<verb-1>.md`
4. ... (one branch per verb)
5. Else: Exit to user: unrecognized verb {verb} — expected <verb-list>
