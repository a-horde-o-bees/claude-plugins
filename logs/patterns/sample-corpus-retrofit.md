# Sample Corpus Retrofit

Reshape an existing population of research-sample files to a new structure while learning what the new structure should be. The structure is unknown at the start — it emerges from reading the corpus. Each batch's observations refine the canonical sub-purpose vocabulary and shape rules for the next batch; a final verification sweep re-applies late-batch rules to early-batch files. Pairs with [context-aware-iteration](context-aware-iteration.md) for batch sizing.

## When to use

- A research subject's `samples/<entity>.md` files exist in an old shape (bullet-with-colon, free prose, mixed structures) and need to migrate to a new shape that supports cross-sample tallying via `consolidate_section` or similar tooling.
- The new shape is partially known (canonical section list) but the *sub-purpose vocabulary* — the `### subheadings` under each section — needs to be discovered or normalized from the corpus.
- The migration is a learning exercise as much as a normalization: per-section observations fed into Phase B template design come from the rewrite, not from a separate analysis pass.

When NOT to use:

- A pure mechanical rename or schema migration with a fully-specified target — use [mass-rename](mass-rename.md) or a regex codemod, not this pattern.
- A first-time research wave gathering samples from external sources — that's research authoring, not retrofit.
- Re-extraction from upstream sources (re-reading the original repos/files the samples summarize) — that's resampling, a different research wave.

## Process

```
1. {subject} = research subject whose samples directory is being retrofitted (e.g. "mcp", "claude-marketplace")
2. {samples-dir} = `logs/research/{subject}/samples/`
3. {target-shape} = canonical section list and sub-purpose vocabulary, possibly partial at start
4. {agent-instructions} = per-batch agent prompt — see "Agent instruction shape" below
5. {queue} = {samples-dir}/<entity>.md × N, with measured_size (bytes)
6. {budget} = sub-agent total context budget

> Phase 0 — Calibrate. Run a small first batch (3-5 files) covering shape variety,
> not just size variety. The first batch carries instruction-interpretation overhead
> the rest don't (the "first-batch tax" — see context-aware-iteration).

7. Pick {n=3-5} files spanning closed-set, open-enumeration, and freeform sections
8. Spawn first batch with {agent-instructions} and the picked files
9. Capture cost: per-byte ratio, per-section sub-purpose counts, anomalies
10. Save batch YAML at {samples-dir}/../_phase-a-batch-01.yaml

> Phase 1+ — Iterate. Each batch's observations refine the canonical sub-purpose
> list. Update {agent-instructions} between batches with new canonical labels,
> dedup rules, contamination-handling rules, and any other discoveries. Do not
> apply the new rules retroactively yet; they accumulate forward.

11. While pending samples remain in {queue}:
    1. {ratio} = trailing-N work-tokens-per-byte from spawn log (per context-aware-iteration)
    2. {batch} = bin-pack pending files up to {budget}/{ratio} byte cap
    3. Spawn batch with current {agent-instructions} and {batch}
    4. Save batch YAML
    5. Read observations: any new sub-purpose label seen? new structural pattern? recurring contamination? Update {agent-instructions} forward
    6. Mark batch files as completed in {queue}

> Phase N — Verification sweep. Late-batch rules need to be applied to
> early-batch files retroactively. The sweep is a focused read-and-fix pass,
> not a full rewrite — cheaper than another rewrite cycle.

12. {late-rules} = rules added to {agent-instructions} after the early batches were processed
13. {early-batch-files} = files from batches that ran before {late-rules} existed
14. Spawn one verification agent with: {late-rules} + {early-batch-files}
15. Agent reads each file, applies {late-rules}, edits only when issues found, reports per-file diff summary
16. Audit corpus: bash: `ocd-run log research compliance --subject {subject}` — confirms every sample's heading tree matches the template's (no outliers, no order violations, expected canonical chains present)

> Output: structurally normalized corpus + per-section semantic observations
> ready for Phase B template synthesis.

17. Aggregate batch YAMLs into a single per-section observations document
18. Hand off to Phase B (template synthesis) with the aggregated observations
```

## Agent instruction shape

Per-batch agent prompts have a recurring structure:

- **Path discipline** — paths are absolute; cwd may differ from the orchestrator's cwd in worktree-isolated runs
- **Per-file rewrite procedure** — read in full; identify each section's substance; rewrite from scratch with canonical heading + `### sub-purpose` + paragraph content; preserve facts faithfully; do not invent
- **Canonical sub-purpose list per section** — the discovered-so-far vocabulary, updated batch-by-batch
- **Section shape rules** — `closed-set` (stable sub-purposes), `open-enumeration` (one `###` per item), `freeform` (paragraphs, no `###`)
- **Cleanup rules accumulated from prior batches** — meta-instruction stripping, source-split consolidation, cross-section relocation, within-file dedup
- **Per-batch observation accumulation** — for each section, record sub_purposes_seen counts, shape, common_description, outliers, issues
- **Output schema** — single YAML block, no preamble or commentary

The instruction set lives at a stable path (e.g. `{samples-dir}/../_phase-a-agent-instructions.md`) so the orchestrator and agent both read the same source-of-truth. Each batch's prompt references the path, not embedded content; updates between batches are picked up automatically.

## Single-subject discipline

**Never mix subjects in a single batch.** Mixing breaks per-section sample-count denominators — "10 of 15 samples have section X" only makes sense when all 15 belong to the same subject. The orchestrator processes one subject's queue to completion, then starts the next.

This also keeps observations per-subject: mcp samples have different sub-purpose vocabularies than claude-marketplace samples even when section names overlap. Mixing produces averaged observations that match neither subject.

## Read-understand-rewrite vs regex transform

A regex-shaped pass (`- **Name**: content` → `### Name\n\ncontent`) is fast and cheap but produces shallow observations: label-drift counts and structural anomalies, but no semantic summary of what each section is *about* across the corpus. The shallow output is insufficient for Phase B template design.

The semantic rewrite is 2-3× more expensive per byte but produces:

- Proposed canonical sub-purpose names (not just label-drift counts)
- Per-section shape assessment (closed-set / open-enumeration / freeform)
- Common-description prose per section across the batch
- Outlier-and-why per section
- Template-design issues per section ("section 11 is uniformly negative — fold into yes/no axis")

The cost premium pays for itself when Phase B template design is the real goal.

## Iterative instruction refinement

Each batch surfaces new patterns. Examples from a real run:

- Batch 1 calibration: original instructions
- After batch 1: add "strip meta-instruction scaffolding" + "consolidate source-split sub-purposes"
- After batch 3: add "relocate cross-section content contamination"
- After batch 4: add "drop within-file Gaps duplication"

Earlier batches are rewritten without later rules. The verification sweep at Phase N is what makes this acceptable: rules accumulate forward; a final pass applies them retroactively without redoing the rewrites.

## Pitfalls

- **Mixing subjects in one batch.** Per-section sample-count denominators become meaningless. Strict single-subject batches.
- **Underestimating cost.** Read-understand-rewrite is 2-3× a regex pass per byte. Calibrate with a small first batch and let trailing-N ratio drive subsequent batch sizes.
- **First-batch tax baked into lifetime average.** The first batch's instruction-interpretation overhead inflates per-byte cost; lifetime average never recovers. Use trailing-N (per context-aware-iteration's SOP).
- **Skipping the verification sweep.** Files processed before rule X exists carry rule-X-violations forever. The sweep is what makes iterative refinement honest.
- **Letting shallow observations propagate to Phase B.** A regex pass's "label-drift counts" cannot answer "should section 11 stay or fold into section 10?" — the semantic observation does.
- **Treating the rule set as final after batch N.** Rules can keep emerging. Be willing to add a late rule and let the verification sweep catch up.

## Anti-patterns

- **Single-pass regex sweep when template design is the goal.** Produces structurally clean files and shallow observations. Phase B template design then has no semantic raw material to work from. The whole pattern exists because a regex pass was tried first and produced un-actionable observations.
- **Lifetime-average ratio for batch sizing.** Anchors forever to the first-batch tax. See context-aware-iteration's SOP.
- **Per-batch fresh agent context.** Without instruction caching, every batch pays the full instruction-interpretation overhead. Stable instruction-set path + repeated agent invocations is what amortizes the cost over batches.
- **Spawning multiple batches in parallel before the ratio converges.** Parallel batches use the same (still-noisy) ratio; if it's wrong, every parallel spawn is mis-sized. Run sequentially until trailing-N is stable, then parallelize if throughput matters.

## See also

- [context-aware-iteration](context-aware-iteration.md) — the batch-sizing layer this pattern composes with
- [mass-rename](mass-rename.md) — sibling for fully-specified mechanical transforms (the alternative when target shape is fully known)
- `logs/research/<subject>/_template.md` — research-subject template that the rewritten samples conform to
- `ocd-run log research compliance --subject <name>` — verifies a sample corpus matches its template's heading tree; the canonical Phase N audit step
