# Purpose Statement

How to write descriptions of any artifact at any scale. A purpose statement tells a reader what something is and whether to go deeper — required at every structural boundary where a reader makes an include-or-skip decision, from a directory to a single function.

A purpose statement conveys:

- **Scope** — what domain or responsibility it covers
- **Role** — what kind of thing it is (e.g., business logic, CLI, config, rule, section, function)

A purpose statement excludes:

- Internal mechanics — how algorithms work, what patterns are used
- Content listing — section names, function names, class names
- History — why it exists, what it replaced, when it was added

The same scope + role test applies at every size — abstraction level scales, structure does not.

Quality tests:

- If two artifacts share the same purpose statement: too vague
- If it would change when internals are refactored but responsibility stays the same: too detailed
- If the same statement would fit at two different scales: one is the wrong granularity

The same artifact described across boundaries uses the same purpose statement — single source of truth.
