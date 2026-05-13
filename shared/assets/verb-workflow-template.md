# <Verb Name>

> <purpose statement — scope + role per description-authoring>

### Variables

- {<variable-name>} — <description>
- ... (one per variable)

### Dependencies

[Include this section only if the verb has its own runtime deps beyond the skill's declared deps; omit otherwise.]

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

### Rules

- <rule>
- ... (one per rule)

### Process

1. <step>
2. ... (numbered, PFN-structured)

### Report

[Include this section only if the verb returns structured data; omit otherwise.]

<return template shape using literal text + {variable} substitution>
