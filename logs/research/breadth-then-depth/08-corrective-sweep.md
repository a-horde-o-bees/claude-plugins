# Phase 08 — Corrective Sweep

Single-agent instructions for sample-level mis-placement corrections. Applies deferred mis-placement findings from the depth pass (`07-depth.md`) to individual samples. The depth-pass reconciler integrates tree-level refinements (description sharpenings, role-level prose, new paths) but defers sample-level mis-placement findings as out-of-scope for tree reconciliation — those are this phase's job.

This is a targeted edit pass, not a full normalize cycle. The agent moves sample sections between paths without modifying content; the goal is to align sample chain keys with the depth-refined tree so quantification becomes accurate.

## Variables

- {subject} — Research subject name (e.g. `mcp`)
- {subtopic} — Optional subtopic name; single-subtopic auto-resolves; multi-subtopic must pass it
- {refinement-reports} — Required. Glob or list of depth refinement reports (typically `_depth-*-refinements.md`)
- {consolidated-file} — Required. Filename of the canonical consolidated to read (paths must exist here for moves to be valid)

## Operating principles

**Move, don't rewrite.** Every correction relocates an existing section from one path to another. Content is preserved verbatim — only the parent heading chain changes. If the section's content needs editing, that's a separate task.

**Verify before moving.** The proposed path must exist as a heading in the current consolidated. Paths shift during reconciliation; a depth-pass refinement report's "Mis-placed samples" section may name a path that's since been renamed, merged, or split.

**Skip ambiguity rather than guess.** When two refinement reports propose conflicting moves for the same sample, surface both in the report and skip the correction. Manual disambiguation is cheaper than incorrect moves.

**Don't add content.** The corrective sweep does not add factual content to samples. If a sample needs a section under a path it doesn't currently have, that's a Pass 4 normalize task, not a corrective sweep task.

## Process

### Build the corrections queue

1. Read each refinement report in {refinement-reports}. Extract the "Mis-placed samples" section. Each finding specifies:
    - Sample name
    - Current path (where the section is wrongly placed)
    - Proposed path (where it should move)
    - Brief rationale
2. Build a flat corrections queue, keyed by `(sample, current-path)`. If two reports propose different moves for the same key, mark as ambiguous
3. Verify each proposed path exists as a heading in `logs/research/{subject}/{subtopic-or-discovered}-samples/{consolidated-file}`. Mark missing paths as `path-not-found`

### Apply corrections

4. For each non-skipped correction:
    1. Read `logs/research/{subject}/{subtopic-or-discovered}-samples/{sample}`
    2. Find the section at the current path. If absent, mark as `sample-section-missing` and skip
    3. Move the section: change its parent heading chain. If the proposed path's parent role doesn't yet exist in this sample, add the parent role heading
    4. Verify with `plugins/ocd/bin/ocd-run log research check logs/research/{subject}/{subtopic-or-discovered}-samples/{sample}`
5. Track applied vs skipped corrections per sample

### Verify final state

6. Run `plugins/ocd/bin/ocd-run log research check` against every modified sample
7. After this sweep completes, the orchestrator re-runs `ocd-run log research quantify --subject {subject} --consolidated {consolidated-file} --write` to refresh adoption tables (script is idempotent)

## Report when returning to caller

- **Corrections applied** — per-sample list with `from-path` → `to-path` and source refinement report
- **Corrections skipped** — counts and reasons (`ambiguous`, `path-not-found`, `sample-section-missing`)
- **Samples touched** — total count
- **Cross-cutting issues** — patterns observed during the sweep (e.g., consistent path-rename impact on multiple samples)
- **Quantification status** — whether the orchestrator should re-run `quantify` after these moves (always yes if any sample paths shifted)
