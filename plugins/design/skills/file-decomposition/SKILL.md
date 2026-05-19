---
name: file-decomposition
description:
---

# File Decomposition

Whether to split or merge a file is governed by how an agent loads and consumes it — not by extension, length, or organizational symmetry. Each load brings in only what its consumer needs; what travels together stays together.

Applies to any agent-consumable artifact: Python modules, markdown workflows, skill components, rule files, configuration, schemas. File-type-specific guidance (e.g., python.md's *Module Decomposition*, the workflow-component split in skill folders) illustrates the principle in one substrate; this rule names the mechanism.

## Out of scope

Files that never enter an agent's context — generated data (CSV indexes, SQLite databases, pickle caches), build outputs, intermediate state. Their structure is determined by the data model, not agent access patterns.

The principle activates when an agent loads a file (or part of it) to understand, reason about, or modify the system. Source code, documentation, configuration, schemas, workflow definitions, and rule files qualify even when also consumed by tooling.

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

- **Line-count splitting** — splitting because a file "feels long" when its content is one cohesive domain; size signals the question, not the answer
- **Preemptive splitting for hypothetical future consumers** — split when a second consumer appears, not before
- **File-type-specific reasoning** — applying different criteria to Python vs markdown when the consumer-access pattern is identical
- **Organizational symmetry splitting** — creating a file because a parent directory "needs" one, not because the content earns its home

When in doubt: what does the agent loading this file need right now, and does the rest earn its place in the same load?
