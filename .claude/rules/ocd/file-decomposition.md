---
includes: "*.md"
---

# File Decomposition

When a file should be split — or merged — is governed by how an agent loads and consumes it, not by the file's extension, length, or organizational symmetry. The decision is the operational form of progressive disclosure and agent-context protection: each load brings in only what its consumer needs at that moment, and what travels together stays together.

The principle applies uniformly to any agent-consumable artifact — Python modules, markdown workflows, skill components, rule files, configuration, schemas. File-type-specific guidance (e.g., python.md's *Module Decomposition* section, the workflow-component split in skill folders) illustrates the principle in one substrate; this rule names the underlying mechanism.

## Out of scope

Files that exist purely as machine-to-machine artifacts — generated data (CSV indexes, SQLite databases, pickle caches), build outputs, intermediate state — are not subject to this principle. Their structure is determined by the data model and the tool that reads them, not by agent access patterns. A large CSV does not "split" because consumers query by relevant columns regardless of size; an SQLite database does not "split" because each table serves a different consumer.

The principle activates when a file is part of agent cognitive context — an agent loads it (or some part of it) to understand, reason about, or modify the system. Source code, documentation, configuration, schemas, workflow definitions, and rule files qualify even when also consumed by tooling. If the file is purely tooling-to-tooling and never enters an agent's context, the decomposition decision belongs to its data model, not to this rule.

## Split when

- Different consumers reach for different parts — splitting lets each consumer load only what it uses
- Different cognitive triggers fire for different parts — each part loads when its trigger fires, not preemptively
- One part is comprehensible without the other — independent disciplines coexist by reference rather than by colocation
- Carrying unused content would cost more context than navigating across files would

## Merge when

- The same consumer always needs both parts together — splitting forces redundant imports or reads without saving context
- Understanding one part requires the other — colocation preserves coherence
- The same trigger loads both — separate files would re-disclose the same scope twice
- The parts are facets of a single discipline — splitting fragments what is conceptually one thing

## Anti-patterns

- **Line-count splitting** — splitting a long file because it "feels long" when its content is one cohesive domain; size signals the question, not the answer
- **Preemptive splitting for hypothetical future consumers** — split when a second consumer appears, not before; speculative splitting fragments code that has no proven need to fragment
- **File-type-specific reasoning** — applying different criteria to Python vs markdown when the consumer-access pattern is identical
- **Organizational symmetry splitting** — creating a file because a parent directory "needs" one, not because the content earns its own home

## Related principles

The decomposition criteria are the operational form of:

- `progressive-disclosure` — reveal in layers; split content along disclosure boundaries
- `separation-of-concerns` — each component does one thing; split when concerns diverge
- `composability` — small composable pieces; merge when colocation serves no consumer
- `economy-of-expression` — every element earns its place; both splitting and merging are subject to this test
- `borrow-before-build` — don't extract a shared piece until a second consumer proves the need

When in doubt, ask: *what does the agent loading this file need right now, and does the rest of the file's content earn its place in the same load?*
