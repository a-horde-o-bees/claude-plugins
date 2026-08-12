---
name: file-decomposition
description: Use when deciding whether to split or merge an agent-consumed file — e.g. module, doc, skill component, config, schema — by how it is loaded and consumed rather than by length or organizational symmetry.
---

# file-decomposition

Use when deciding whether to split or merge an agent-consumed file — e.g. module, doc, skill component, config, schema — by how it is loaded and consumed rather than by length or organizational symmetry.

Each load brings in only what its consumer needs; what travels together stays together.

## Scope

The principle activates when an agent loads a file, or part of one, to understand, reason about, or modify the system — e.g. Python modules, markdown processes, skill components, rule files, configuration, schemas. A file qualifies even when tooling also consumes it, so long as an agent loads it.

Out of scope: files that never enter an agent's context — generated data (e.g. CSV indexes, SQLite databases, pickle caches), build outputs, intermediate state. The data model determines their structure, not agent access patterns.

## Split when

- Different consumers reach for different parts — each loads only what it uses
- Different triggers fire for different parts — each part loads when its trigger fires, not preemptively
- One part is comprehensible without the other — independent disciplines coexist by reference
- Carrying unused content would cost more context than navigating across files

## Merge when

- The same consumer always needs both parts — splitting forces redundant reads
- The same trigger loads both — separate files re-disclose the same scope twice
- Understanding one part requires the other — colocation preserves coherence
- The parts are facets of a single discipline

## Reliability precedence

A split is only as good as the hop that reunites it. When the navigator between parts is the model — a part the consumer must *choose* to open mid-task, rather than one a mechanism loads for it — presume the hop skipped under load: the unopened part is silently absent, and its miss costs more than the split saved. Token relief comes from mechanization — a script performs the work, a build materializes the dependency into the loaded file — never from making the model navigate. Split across a model-mediated hop only when the miss is cheap.

## Anti-patterns

- **Don't split on line count alone** — a file "feels long" but its content is one cohesive domain; size signals the question, not the answer
- **Don't pre-split for hypothetical future consumers** — split when a second consumer actually appears, not before
- **Don't apply file-type-specific criteria** — the same consumer-access pattern earns the same answer whether the file is Python or markdown; a language guide's module rules or a skill folder's process-component split illustrate this principle in one substrate rather than competing with it
- **Don't split for organizational symmetry** — a parent directory "needs" a file, but the content hasn't earned its home

## When in doubt

What does the agent loading this file need right now, and does the rest earn its place in the same load?
