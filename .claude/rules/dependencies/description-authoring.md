# Description Authoring

How to write any description. The most common surface is the `description:` field — skill SKILL.md frontmatter, plugin manifests, MCP tool registrations, `package.json` / `pyproject.toml` / `Cargo.toml`, YAML frontmatter in docs. Same discipline applies to file headers, section openings, function docstrings, README leads, commit messages, CHANGELOG entries, log openings. Whatever the surface, a description tells a reader what something is and whether to go deeper; required at every structural boundary where a reader makes an include-or-skip decision.

A description conveys:

- **Scope** — what domain or responsibility it covers
- **Role** — what kind of thing it is (e.g., business logic, CLI, config, rule, section, function)

A description excludes:

- Internal mechanics — how algorithms work, what patterns are used
- Content listing — section names, function names, class names
- History — why it exists, what it replaced, when it was added

The same scope + role test applies at every size — abstraction level scales, structure does not.

Quality tests:

- If two descriptions are interchangeable: too vague
- If the description would change when internals are refactored but responsibility stays the same: too detailed
- If the same statement would fit at two different scales: one is the wrong granularity

The same artifact described across boundaries uses the same description — single source of truth.
