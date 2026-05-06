---
includes: "*"
---

# Purpose Statement

Canonical guidance for how agents write descriptions of any artifact at any scale. A purpose statement tells a reader what something is and whether to go deeper — present at every structural boundary where a reader makes an include-or-skip decision, from a directory down to a single function.

- When writing a description for any artifact (e.g., directory, file, section heading within a document, module docstring, class or function docstring, skill description, navigator entry, tool help text, frontmatter field): follow Purpose Statement guidance

A purpose statement conveys:

- **Scope** — what domain or responsibility the thing covers
- **Role** — what kind of thing it is (e.g., business logic, CLI, config, convention, rule, section within a larger document, function in a module)

A purpose statement excludes:

- Internal mechanics — how algorithms work, what patterns are used, implementation details
- Content listing — section names, function names, class names
- History — why it exists, what it replaced, when it was added

The same scope + role test applies regardless of the artifact's size. A plugin's purpose is coarser than a function's, but both answer the same questions at their own level. What differs across scales is the abstraction level of the domain and role, not the structure of the statement.

Quality tests:

- If two artifacts share the same purpose statement: it is too vague
- If the purpose statement would change when internals are refactored but responsibility stays the same: it is too detailed
- If the same purpose statement would fit at two different scales (e.g., fits a module and one of its functions): one of the two is the wrong granularity for what is being described

Purpose statements appear at every disclosure boundary: directory listings, file headings, section headings within files, module docstrings, class and function docstrings, skill descriptions, navigator entries, tool help text, frontmatter description fields. The same thing described at different boundaries uses the same purpose statement — single source of truth for what it is.
