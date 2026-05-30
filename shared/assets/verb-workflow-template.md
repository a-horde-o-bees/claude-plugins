# <Verb Name>

> <purpose statement — scope + role per description-authoring>

## Variables

- {<variable-name>} — <description>
- ... (one per variable)

## Dependencies

[Include this section only if the verb has its own runtime deps beyond the skill's declared deps; omit otherwise.]

Run on first load of this file:

bash: `python <THIS-FILE-DIR>/_read_deps.py <dep-name> <another-dep-name>`

## Rules

- <rule>
- ... (one per rule)

## Process

1. <step>
2. ... (numbered, PFN-structured)

## Report

[Include this section only if the verb returns structured data; omit otherwise.]

<return template shape using literal text + {variable} substitution>
