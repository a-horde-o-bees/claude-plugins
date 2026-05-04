---
log-role: reference
---

# Methodology — Breadth-Then-Depth Consolidation

Operational reference for running the breadth-then-depth research methodology. Procedures only — for current-state structure see `ARCHITECTURE.md`; for design rationale and trade-offs see `decisions.md`. For each phase's full agent instructions, see the numbered phase files in this folder.

## Inputs

- A corpus of per-sample files at `logs/research/{subject}/{subtopic}-samples/<entity>.md` — one file per entity in the research target list. Each sample carries observable facts about its entity at the granularity that supports functional decomposition
- CLI tooling: `sections`, `references`, `diff`, `check`, `quantify` verbs from `ocd-run log research`

The pre-Pass-1 phases (`01-target-selection`, `02-sample-population`) produce the corpus. Methodology consumers can run those phases or accept a corpus produced externally — the phases are documented for reproducibility, not because the rest of the methodology depends on them being agent-driven.

## Process

The methodology runs as a numbered sequence of phases. Each phase has a companion instruction file in this folder.

### Pre-consolidation: producing the corpus

- **`01-target-selection`** — Define subject scope, enumerate candidates, stratify, sample to a target count. Output: an entity list
- **`02-sample-population`** — For each entity, capture observable facts about its components and what purpose each serves. Per-sample structure is loose; the research-objective checklist is flat, not nested. Apply the "would this distinguish?" test; defer-mark `↗` anything ambiguous

### Consolidation: building the tree

- **`03-gather`** (Pass 1a) — Each agent reads a bin of samples in isolation, identifies functional parts and implementation choices, writes a partial consolidated per bin
- **`04-merge`** (Pass 1b) — Single agent reads all partials, merges by (function, choice) pairs, applies cross-role linking. Output: unified canonical tree

### Convergence: aligning samples and consolidated

- **`05-normalize`** (Pass 2a) — Each agent reads consolidated + its bin's samples; rewrites samples to mirror the role tree; collects refinements in a report. Does NOT modify consolidated
- **`06-reconcile`** (Pass 2b) — Single agent integrates accepted refinements into the consolidated

Phases 05+06 form one normalize cycle. Convergence is reached when a cycle proposes few refinements (mostly sharpenings, no new roles, no bucket splits). 2-3 cycles typically suffice.

### Depth: cross-corpus refinement

- **`07-depth`** — One agent per branching role; pulls supporting sample evidence via `references --show-content`; surfaces description sharpenings, mis-placements, multi-axis structure. Refinement reports flow through `06-reconcile` to integrate tree-level findings; sample-level mis-placements defer to corrective sweep
- **`08-corrective-sweep`** — Single agent applies the deferred sample-level mis-placement corrections (move sections between paths; preserve content)

### Quantification: mechanical adoption tables

- **`09-quantify`** — Mechanical script (`ocd-run log research quantify`). Walks the role tree, counts samples per branching path, inserts idempotent adoption tables into the consolidated

### Optional: re-iteration via gap audit

- **`10-gap-audit`** (opt-in) — Single agent scans the converged + quantified consolidated for shallowness signals; produces a targeted re-research scope. If the user opts into addressing gaps, route the scope back through `02-sample-population` and re-run phases `03` through `09` incrementally

## Resource budgeting and dispatch

Phases that batch work (`03-gather`, `05-normalize`, `07-depth`) need budgeting per spawn.

**Calibration spawn first.** The first spawn establishes the work-tok per byte ratio empirically. Subsequent spawns are sized using the trailing average. Ratio varies by subject; do not hardcode.

**Per-spawn budget targets** (rough; verify against the calibration spawn):

| Phase | Content per spawn | Target work-tok |
|-------|---------|------------------|
| 03-gather | ~40-50KB sample content per bin | ~100K |
| 05-normalize | consolidated (current) + ~40-50KB bin samples | ~150-300K |
| 07-depth | role section + per-role evidence pull (variable) | ~150-250K |

**Bin packing rule.** Group work to fill ~80-90% of budget per spawn, leaving headroom for tooling and report generation. Use `references --size` and `sections --size` to budget content cost before pulling.

**Re-calibration trigger.** If trailing measurements diverge from the initial calibration spawn, re-bin the remaining work before continuing rather than continuing on stale estimates.

**Default sequential.** One spawn at a time for parallel-prone phases. **Batch-parallel (3-4 concurrent) is opt-in** when wall-clock matters and platform tolerance is known. The reconciler/merger phases (`04`, `06`, `08`, `09`) are inherently single-agent.

For rationale on these defaults, see `decisions.md` "Why sequential dispatch is the default."

## Commit cadence

Failure recovery relies on git as the checkpoint mechanism. Commit at these boundaries:

- After `02-sample-population`
- After `04-merge`
- After each `06-reconcile` cycle (when normalize cycles run iteratively)
- After `07-depth` reconciliation
- After `08-corrective-sweep`
- After `09-quantify`
- Before opting into a `10-gap-audit` re-iteration

For users not using git: snapshot artifacts (`cp -r`) at the same boundaries.

## Failure recovery

When a phase agent fails mid-execution (rate limit, crash, timeout), reset before retrying:

1. **Identify the modified surface.** `git status -s` shows samples and reports the failed phase touched
2. **Reset incomplete work.** `git checkout -- <paths>` for samples or consolidated; `rm <_pass{N}-bin{M}-refinements.md>` for partial refinement reports. Depends on the commit cadence above — `git checkout` reverts to the last commit
3. **Re-dispatch with the lesson learned.** If failure was rate-limit at parallelism N, drop to a smaller batch or sequential. If budget overrun, re-calibrate

**Don't retry on top of partial state** — compounds errors silently.

**Preserve completed work** — selective `git checkout -- <specific-paths>` lets you reset only the failed bin and re-dispatch from there.

For rationale on reset-then-retry, see `decisions.md` "Why reset-then-retry over compound-state retry."

## Tooling

| Verb | Purpose |
|------|---------|
| `sections [--subject N] [--count] [--size]` | Chain-key tree across samples; `--count` and `--size` add columns for adoption and byte size |
| `references "<chain>" [--subject N] [--count] [--size] [--show-content]` | List samples containing a section at the chain path. `--show-content` pulls each sample's section body — used by depth pass for cross-corpus inspection |
| `diff [--subject N] [--consolidated <path>]` | Diff sample heading trees against the running consolidated. Surfaces growth and pruning candidates |
| `check <path>` | Verify a markdown file has no sibling-duplicate headings |
| `quantify [--subject N] [--consolidated <path>] [--write]` | Compute adoption tables for branching points. Default prints to stdout; `--write` inserts in place. Idempotent via sentinel comments |
