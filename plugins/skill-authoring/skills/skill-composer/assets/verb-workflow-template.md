# <Verb Name>

> <purpose statement — scope + role per description-authoring>

### Variables

- {<variable-name>} — <description>
- ... (one per variable)

### Dependencies

[Include this section only if the verb has its own runtime deps beyond the skill's declared deps; omit otherwise.]

Read each if not already in context. Discover via `find ~/.claude <project>/.claude -path "*dependencies/<name>.md" -not -path "*/_dependencies/*" -type f 2>/dev/null`. Selection: prefer user-scope; prefer `rules/dependencies/` over plain `dependencies/`. User-scope skills skip project matches. If discovery returns nothing, the dep is not deployed — operate without it.

- [[<dep-name>]]
- ... (one per dep)

### Rules

- <rule>
- ... (one per rule)

### Process

1. <step>
2. ... (numbered, PFN-structured)

### Report

[Include this section only if the verb returns structured data; omit otherwise.]

<return template shape using literal text + {variable} substitution>
