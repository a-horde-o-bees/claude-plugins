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

1. {dependencies}:
    - [[<dep-name>]]
    - ... (one per dep)
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
| <cognitive moment 1> | `<verb-1>` |
| ... (one row per trigger) |

## Verbs

| Verb | Workflow file |
|---|---|
| `<verb-1>` | [`_<verb-1>.md`](_<verb-1>.md) |
| ... (one row per verb) |

## Workflow

1. {verb}: first token of $ARGUMENTS
2. {verb-args}: remainder of $ARGUMENTS after {verb}
3. If {verb} is `<verb-1>`: Call: `_<verb-1>.md`
4. ... (one branch per verb)
5. Else: Exit to user: unrecognized verb {verb} — expected <verb-list>
