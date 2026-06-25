---
name: architecture-authoring
description: Use when writing or revising an ARCHITECTURE.md doc — to capture the durable shape of a scope and the external facts it conforms to, scoped to what a full reimplementation would have to reproduce.
---

# architecture-authoring

An architecture record holds the durable shape of a scope: how it is built and the external facts it conforms to, written so it survives any reimplementation. The code shows the current implementation; the architecture doc is the map that outlives it — the structure, boundaries, and external truth a reader needs *before* the code makes sense, and that a full rewrite would have to reproduce.

## The reimplementation test — the gate on every line

For each statement ask: **would a full rewrite of this scope's code have to honor this?**

- **Yes** → keep it. It is architecture: an external fact the scope conforms to, a structural boundary, or an invariant that holds regardless of implementation.
- **No** → it belongs elsewhere. A choice made over rejected alternatives is a decision (→ `DECISIONS.md`). A detail a reader derives by reading the current code is description — cut it, keep only the orienting pointer. Status, counts, and progress are tracker state.

This is the slim test specialized to architecture. A line that feels essential but fails the test is usually *curse of knowledge* — it reads as load-bearing to the author who built it, but the reader gets the same fact from the code or the external spec.

## What a record contains

- **External facts the scope conforms to** — the truths of the systems it integrates that constrain every implementation: source-system structure, sentinels, entity shapes, a chart of accounts, protocol constraints. Not our choice; the ground the scope is built on.
- **Durable structure** — how the scope divides into parts and the contracts across their seams: what each part is responsible for, what crosses the boundary. The map a reader needs before the code, stated at the level that survives a rewrite — never the line-by-line mechanics the code already shows.
- **Invariants** — what must stay true across any reimplementation: an ordering guarantee, a balance that must hold, a one-way data-flow direction.

## Cut

- **Decisions** — a choice with alternatives and rejected reasoning lives in `DECISIONS.md`; architecture states *what is*, not *why this and not that*. Link.
- **Code mechanics** — the current implementation's step-by-step; the code is the authority. Describe the shape, not the lines.
- **External specs better linked** — point to the source-of-truth spec; restate only the facts the scope is built around, not the spec itself.
- **Status, dates, counts, progress** — tracker state; it rots fastest.

## Supersede, never accrete

An architecture doc describes the current shape only. When the structure changes, rewrite the affected section to the new shape — never leave the old structure beside the new with a "previously" note. The doc is *what is*, not how it got here.

## Form

Lead with the scope's purpose and the external facts it conforms to, then the structure, then the invariants. Slim with /concise-prose once the reimplementation test has set the content.
