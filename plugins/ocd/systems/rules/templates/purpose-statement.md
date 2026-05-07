---
tagline: How to write descriptions for artifacts at any scale — scope and role, no internals
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

## Taglines

A tagline is the purpose statement at the catalog-row boundary — the one-line cell rendered when an item appears in a selection context (e.g., `setup <system> list`, lettered pick lists). Same scope + role concept; condensed to fit one terminal line.

- Hand-write the tagline; do not auto-truncate the longer purpose statement — truncation drops the most important framing first
- Target ≤80 characters so the line fits without wrapping after typical column indent
- Convey scope + role in one sentence; if the artifact's longer purpose has multiple sentences, the tagline is the one naming the principle or behavior
- Live in the artifact's frontmatter (e.g., `tagline:` field on rule and convention templates) so the tagline travels with the file as single source of truth — the matching `setup <system> show <name>` reveals the full body
- Quality test: a reader scanning a long list and seeing only `<name> — <tagline>` recognizes whether this item is what they want without opening the file
