# Decisions

Non-obvious choices with alternatives considered. Prevents backtracking. Record when the reasoning is not derivable from code or conventions — if an agent arriving fresh would need to re-evaluate from scratch, record it. Detail files in `decisions/` hold full context; entries here are the scannable index.

- **[Criteria-note model](decisions/criteria-note-model.md)** — Link criteria to entity notes for auditable, surgical assessment scoring
- **[MCP domain tools](decisions/mcp-domain-tools.md)** — Replace generic CRUD with domain tools encoding business logic (set/add/remove/clear)
- **[Database engine](decisions/database-engine.md)** — SQLite with WAL mode for zero-dependency file-based agent database
- **[Aggregate star schema](decisions/aggregate-star-schema.md)** — Dynamic FK introspection to cascade deletes through ownership tree
- **[Python import pattern](decisions/python-import-pattern.md)** — Standard packages with relative imports per-plugin, mirroring production isolation in tests
- **[Template-deployed model](decisions/template-deployed-model.md)** — Source files marked template, deployed copies marked deployed in frontmatter
- **[Component extraction](decisions/component-extraction.md)** — Shared skill content in extracted files with explicit read steps per agent
