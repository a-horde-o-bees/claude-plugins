# Lessons from MCP Phase A — proposed integrations

Lessons surfaced while running the read-understand-rewrite-accumulate workflow over MCP samples. Each entry names a candidate destination — in-place updates land after Phase A wrap-up to keep the working ground stable.

## Already integrated (live)

- **Trailing-window ratio in context-aware-iteration.** Lifetime average lags when costs trend (here: dropping ~15% per batch as instruction-set caching kicks in). Updated `logs/patterns/context-aware-iteration.md`: trailing-N is now the default SOP for ratio estimation; lifetime average is reserved for diagnosis. Added Token-exhaustion handling and Anomaly-exclusion sections. Spawn-log schema now includes `anomaly` and `notes` columns.

## Observed inconsistencies in the produced corpus

- **Batch 4 dropped `### pitfalls observed` subheadings entirely** for 7 awslabs/apollographql files when the slot was "none noted" or a duplicate of section 20. The other 97 files keep the empty subhead with "none noted in this repo". The batch-4 form is technically more accurate (no empty subsections) but breaks structural consistency. Phase B template design should pick one form as canonical:
    - **Form A — keep the subheading with "none noted":** uniform structure, simpler `consolidate_section` aggregation, but every closed-set section ships a 16-section pitfall scaffold even when 95% of cells are empty.
    - **Form B — omit the subheading when there's no pitfall:** denser, but requires `consolidate_section` to handle two distinct shapes per section.

  16 file-level fixes across 23 verified files removed within-file Gaps duplication; 0 cross-section relocations were needed (the rule was a candidate for fixes that didn't exist in this corpus).

## Proposed for context-aware-iteration

- **Per-byte vs per-item ratio.** When work scales with content volume (file rewriting, summarization), measure `work_tokens / bytes`. When work scales with item count (discrete tool calls), measure `work_tokens / item`. The current pattern is silent on which to pick — could note that the choice depends on whether per-item overhead or content-volume dominates per-batch cost.

- **Byte-budget for content-bound work.** When per-byte ratio is the right unit, the picker should pack to a byte cap, not an item count. Worth calling out explicitly so callers don't size by item count when their work is content-bound.

- **Calibration across shape variety, not just size.** First-batch picks should cover representative *shapes* (closed-set, open-enumeration, freeform) not just min/median/max sizes. Cost-per-byte varies with content shape; sampling shape early stabilizes the ratio faster.

## Proposed for log/research-template

The research log type's _samples-template currently describes the per-sample shape but not how a Phase A retrofit should be run when sample shape evolves. Two additions:

- **Pattern reference.** When migrating sample-file structure (e.g., bullet-form → subheading-form), the canonical workflow is the read-understand-rewrite-accumulate pattern in this lessons file (or a dedicated pattern). Cross-reference it from the research-template Lifecycle section.

- **Per-section observation accumulation.** Phase A discovered that the highest-value output of a sample-restructure run is not the cleaned files alone — it's the *per-section semantic observations* (proposed canonical labels, shape, common description, outliers, issues) that drive consolidated.md template design. Worth documenting as part of how research subjects evolve.

## Proposed as a new pattern

**Sample-corpus retrofit.** This Phase A workflow is a distinct pattern worth its own entry, separate from context-aware-iteration. The combination of:

- Single-subject batches (cross-subject mixing breaks per-section sample-count denominators)
- Read-understand-rewrite (not regex transform — produces shallow observations otherwise)
- Iterative instruction refinement between batches (canonical-label list, dedup rules, contamination handling — discovered during the run, threaded forward)
- Per-batch semantic observations YAML (not just commit messages)
- Final verification sweep against late-batch instruction additions

…is a recurring shape for "we need to retrofit a sample corpus to a new structure while learning what the new structure should be." Distinct from a one-shot regex sweep. Distinct from a fresh research wave (this isn't gathering new samples — it's reshaping existing ones). Belongs as a sibling pattern to `mass-rename` and `context-aware-iteration`.

Candidate filename: `logs/patterns/sample-corpus-retrofit.md`.

## Proposed for research-migration sandbox tasks (lifecycle hand-off)

After mcp Phase A wraps:

- **Phase B: master template design.** Synthesize the per-batch observations (now ~15 batch YAMLs once mcp completes) into a master `samples/_TEMPLATE.md` for mcp. Same exercise, different decision: whether sections like 17/18/20 should remain freeform, whether section 11 should be a yes/no, whether `pitfalls observed` per section is worth keeping after dedup, whether section 10's open-enumeration is the right model.

- **Phase B subject ordering.** Run mcp Phase B before starting marketplace Phase A — the lessons from mcp's template design (e.g., what canonical labels look like, when to fold pitfalls, how to handle freeform sections) inform how marketplace's sample-corpus retrofit gets framed.

- **Sample-corpus retrofit pattern (drafted above) before marketplace.** If extracted as a standalone pattern, marketplace becomes a clean second application of the pattern with a stabilized methodology rather than a rerun of the same iteration.
