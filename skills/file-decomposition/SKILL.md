---
name: file-decomposition
description: Use when deciding whether to split or merge an agent-consumed file — module, doc, skill component, config, schema — by how it is loaded and consumed rather than by length or organizational symmetry.
---

# File Decomposition

Whether to split or merge a file is governed by how an agent loads and consumes it — not by extension, length, or organizational symmetry. Each load brings in only what its consumer needs; what travels together stays together.

The principle activates when an agent loads a file, or part of one, to understand, reason about, or modify the system — Python modules, markdown processes, skill components, rule files, configuration, schemas. A file qualifies even when tooling also consumes it, so long as an agent loads it. File-type-specific guidance (e.g. python.md's *Module Decomposition*, the process-component split in skill folders) illustrates the principle in one substrate; this rule names the mechanism.

## Out of scope

Files that never enter an agent's context — generated data (e.g. CSV indexes, SQLite databases, pickle caches), build outputs, intermediate state. The data model determines their structure, not agent access patterns.

## Split when

- Different consumers reach for different parts — each loads only what it uses
- Different cognitive triggers fire for different parts — each part loads when its trigger fires, not preemptively
- One part is comprehensible without the other — independent disciplines coexist by reference
- Carrying unused content would cost more context than navigating across files

## Merge when

- The same consumer always needs both parts — splitting forces redundant reads
- Understanding one part requires the other — colocation preserves coherence
- The same trigger loads both — separate files re-disclose the same scope twice
- The parts are facets of a single discipline

## Anti-patterns

- **Don't split on line count alone** — a file "feels long" but its content is one cohesive domain; size signals the question, not the answer
- **Don't pre-split for hypothetical future consumers** — split when a second consumer actually appears, not before
- **Don't apply file-type-specific criteria** — Python vs markdown when the consumer-access pattern is identical
- **Don't split for organizational symmetry** — a parent directory "needs" a file, but the content hasn't earned its home

When in doubt: what does the agent loading this file need right now, and does the rest earn its place in the same load?
