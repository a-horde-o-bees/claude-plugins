---
name: system-authoring
description: Use when standing up or restructuring a scope's whole documentation set — its architecture, decisions, and procedure docs together — so every fact lands in its owning doc rather than blurring across them. For a single doc, invoke that doc's authoring skill directly.
---

# system-authoring

Author a scope's documentation system as one partitioning pass: every fact about the scope routes to the one doc that owns it, no fact lives in two, and each doc is slimmed and framed by the writing lenses. The defect this prevents is the blended doc — structure, rationale, and steps tangled together, where a reader can't find the fact they need and an executor may run descriptive prose as a step.

## The owners

Each kind of content has one owning doc and one authoring skill; route to it rather than duplicate across docs:

- **Durable shape — structure, boundaries, and external facts a rewrite must honor** → `architecture-authoring` (the scope's `ARCHITECTURE.md`).
- **Why this and not that — a choice made over rejected alternatives** → `decision-authoring` (the scope's `DECISIONS.md`).
- **Executable steps — a flow an agent runs** → `procedure-authoring` (the scope's procedure doc).

Each owner skill carries its own inclusion/exclusion gate and cross-points to the other two, so a fact misrouted into one is pushed back out by that skill's exclusions.

## The lenses

Applied over whatever each owner produces:

- `concise-prose` — slim every doc to its load-bearing content without losing meaning.
- `markdown-authoring` — frame each file with a level-1 heading naming it and a description line. It authors that line per `description-authoring`, so the H1 description is reached in-context; do not invoke `description-authoring` from here.

## Apply

Route every fact to its owner, draft each doc through its authoring skill, and apply both lenses across the set together as one pass — never as successive layers. A fact that seems to fit two docs belongs to one: state it in its owner and cross-reference from the other, never copy it. When the source is a single blended doc, split it along the three owners; when starting fresh, draft each owner doc directly.
