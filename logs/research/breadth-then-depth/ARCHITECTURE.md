---
log-role: reference
---

# Architecture — Breadth-Then-Depth Consolidation

A research methodology that produces a consolidated tree of functional parts and implementation paths from a corpus of per-entity samples. This document covers the system's structure: phases, the consolidated tree schema, agent-coordination patterns, and recovery model.

For operational instructions, see `METHODOLOGY.md`. For design decisions and rationale, see `decisions.md`. For each phase's agent instructions, see the numbered phase files.

## Scope

This methodology is explicitly scoped to **gathering and consolidating sample data within one subtopic**:

- **In scope.** Producing one `_CONSOLIDATED_breadth-then-depth.md` per `{subject}/{subtopic}-samples/` folder, from the entity samples within. The output is a per-subtopic functional decomposition with adoption tables
- **Out of scope: cross-subtopic synthesis.** When a subject has multiple subtopics (e.g., `mcp/repos-samples/` plus a hypothetical `mcp/clients-samples/`), each is consolidated independently. Combining those consolidateds into a subject-level synthesis (RESEARCH.md, ANALYSIS.md) is a separate process. It consumes this methodology's output but uses different procedures and is not addressed here
- **Out of scope: general context gathering.** Subjects often have a `{subject}/context/` folder with specs, official docs, related research, or other supporting material that informs the research without itself being sampled. This methodology does not consolidate context content. Context is research input that may inform target selection (Phase 01) and entity research (Phase 02), but is not part of the corpus the methodology decomposes

The methodology is one component of a research subject's broader workflow. Other processes — cross-subtopic synthesis, context gathering, user-facing analysis authoring — sit alongside it and consume its output, but each has its own discipline.

## Phases

The system runs as a numbered sequence of ten phases, grouped into five stages.

**Pre-consolidation (corpus production):**

- `01-target-selection` — Subject scope, candidate enumeration, stratified sampling. Produces an entity list
- `02-sample-population` — Per-entity research; flat research-objective checklist; output is one sample file per entity

**Consolidation (tree construction):**

- `03-gather` — Per-bin agents derive functional roles + paths from sample content; output is one partial consolidated per bin
- `04-merge` — Single agent merges partials by (function, choice) pairs into a unified tree

**Convergence (sample-tree alignment):**

- `05-normalize` — Per-bin agents rewrite samples to mirror the tree; collect refinements without modifying the consolidated
- `06-reconcile` — Single agent integrates accepted refinements into the consolidated

**Depth (cross-corpus refinement):**

- `07-depth` — Per-role agents pull cross-corpus evidence via `references --show-content`; produce refinement reports for `06-reconcile`
- `08-corrective-sweep` — Single agent applies sample-level mis-placement corrections from depth findings

**Quantification + audit:**

- `09-quantify` — Mechanical script (`ocd-run log research quantify`) inserts adoption tables into the consolidated. Idempotent
- `10-gap-audit` (opt-in) — Single agent surfaces shallowness signals; produces a targeted re-research scope routing back through `02`

## Tree shape (schema)

The consolidated has three structural levels:

- **Top — functional parts.** What the sample DOES at this layer. `## Server runtime`, `## Transport`, etc.
- **Sub — implementation paths.** Alternatives the corpus exhibits, named by choice. `### stdio`, `### Python with FastMCP`
- **Leaf — qualitative description.** What the path is, when appropriate, what it constrains about other parts

Cross-role linking: tools that fill multiple roles (Docker = distribution + test stack + deployment artifact) are named under each role's section, not given a top-level branch.

Provenance is dynamic: `references "Sample > <chain>"` returns supporting samples on demand. No inline citations in the consolidated.

## Two-lens design

The methodology has two distinct lenses on the corpus:

- **Per-bin lens** (Phases `03-gather`, `05-normalize`). Each agent owns 8 whole samples; sees full per-sample context. Settles **what categories exist**
- **Per-role lens** (Phase `07-depth`). Each agent owns ONE branching role and reads every supporting sample's slice via `references --show-content`. Sharpens **how categories are described**

The convergence loop establishes the tree shape; the depth pass refines descriptions. Reconciliation (`06-reconcile`) is shared — the same reconciler integrates findings from either lens into the consolidated.

## Agent-coordination patterns

**Refinement reports as the cross-phase interface.** Per-bin and per-role agents do not modify the consolidated directly. They write refinement reports (`_pass{N}-bin{M}-refinements.md` for normalize, `_depth-{role-slug}-refinements.md` for depth pass). The reconciler reads reports, applies accepted refinements to the consolidated, defers others. This keeps each phase's agent context focused on one artifact at a time.

**Refinement persistence.** Reports are kept under `{subject}/{subtopic}-samples/refinements/` after the run completes — they carry future operational value (gap audit reads them; future runs can inspect deferred items and judgment calls).

## Recovery model

Failure recovery uses git as the checkpoint mechanism. Commit boundaries:

- After `02-sample-population` (corpus stable)
- After `04-merge` (consolidated stable, samples not yet touched)
- After each `06-reconcile` cycle (samples + consolidated stable per cycle)
- After `07-depth` reconciliation
- After `08-corrective-sweep`
- After `09-quantify`
- Before opting into a `10-gap-audit` re-iteration

`git checkout --` reverts to the last commit, which is the reset primitive for failure recovery. Reset-then-retry over partial state, not compound-state retry. Selective recovery (reset only the failed bin's paths) preserves completed work within a failed phase.

## Resource budgeting

Phases that batch work need budgeting per spawn. The first spawn calibrates work-tok per byte empirically; subsequent spawns size against the trailing average. Sequential dispatch is the default; batch-parallel (3-4 concurrent) is opt-in. Reconciler/merger phases (`04`, `06`, `08`, `09`) are inherently single-agent.

| Phase | Content per spawn | Target work-tok |
|-------|---------|------------------|
| 03-gather | ~40-50KB sample content per bin | ~100K |
| 05-normalize | consolidated + ~40-50KB bin samples | ~150-300K |
| 07-depth | role section + per-role evidence pull | ~150-250K |

## File organization

```
breadth-then-depth/
  ARCHITECTURE.md         (this file — current-state structure)
  METHODOLOGY.md          (operational reference — how to run)
  decisions.md            (design decisions and rationale)
  01-target-selection.md
  02-sample-population.md
  03-gather.md
  04-merge.md
  05-normalize.md
  06-reconcile.md
  07-depth.md
  08-corrective-sweep.md
  09-quantify.md
  10-gap-audit.md
```

Mechanical work — adoption-table generation — lives in code at `plugins/ocd/systems/log/research/_quantify.py`, exposed through the `ocd-run log research quantify` CLI verb. Per Determinism by Default, the script handles the deterministic operation while phase files handle agent-judgment work.

The consolidated lives at `logs/research/{subject}/{subtopic}-samples/_CONSOLIDATED_breadth-then-depth.md`; refinement reports under `{subject}/{subtopic}-samples/refinements/`.
