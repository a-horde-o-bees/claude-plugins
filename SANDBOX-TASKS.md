# Sandbox: ocd/research-migration

Phase A of the research-corpus retrofit landed by the `sandbox/log-research` merge — restructure MCP and claude-marketplace samples and gather per-section observations using the `context-aware-iteration` pattern over the new `sample_tools` primitives. Output feeds Phase B (master template design); does not retire the legacy `mcp/scripts/_retrofit_samples_to_template.py` (Phase C/D scope).

## Pointers

- `logs/decision/log.md` — Phase A/B/C/D plan (section "Sandbox scope excludes retrofit engine, work-queue tooling, and migration manifests")
- Recovered log-research SANDBOX-TASKS (git history, commit `1ff5461^:SANDBOX-TASKS.md`) — full handoff plan including Phase A methodology
- `logs/patterns/context-aware-iteration.md` — prescribed methodology: pre-measure → baseline spawn → calibrated iteration → accumulated observations
- `logs/research/claude-marketplace/` — 54 samples, already passes `check`; consolidated.md cited as canonical example in the new template
- `logs/research/mcp/` — ~100 samples, passes `check`; has corpus-specific `scripts/_retrofit_samples_to_template.py` (retires in Phase C/D, not here)
- `plugins/ocd/systems/log/research/_sample_tools.py` — `parse_headings`, `count_sections`, `consolidate_section`, `check_no_duplicate_headings` primitives
- `ocd-run log research check | count-sections | consolidate` — the CLI surface this phase exercises end-to-end

## Observations gathered so far (recon phase)

These feed into the per-section observation work but are also worth surfacing now since they affect methodology:

- **Sample format is hybrid heading/bullet.** Top-level purposes are headings (`## 1. Marketplace discoverability`, `## Identification`); sub-purposes are bullets-with-colons (`- **Manifest layout**: ...`). The `count_sections` walker only sees headings, so chain-key resolution stops at top-level purposes — sub-purpose granularity isn't reachable through the tooling
- **`consolidate` does not aggregate cross-sample.** The level-1 heading is the entity ID (`# 123jimin-vibe/plugin-prompt-engineer`), so chain-key matching in `_find_section` descends from a per-entity root. `consolidate --chain "1. Marketplace discoverability"` returns 0 results; only entity-prefixed chains find one specific sample. Either samples need restructuring to drop entity-id-as-level-1 (entity in metadata instead), or `_find_section` needs a level-skip mode
- **Both subjects pass `check`** — no duplicate-sibling-heading violations in either corpus
- **Stale `logs/research/_scripts/__pycache__/`** — log-research sandbox removed `_scripts/` source but pyc cache regenerated post-merge. Delete the directory; it serves nothing under the new system

## Tasks

### Phase A.0 — Observation methodology setup

- [ ] Decide observation output location per subject (proposed: `logs/research/<subject>/phase-a-observations.md` as a research-wave file alongside `consolidated.md`)
- [ ] Decide work-queue + spawn-log location (proposed: `logs/research/_phase-a-queue.csv` + `logs/research/_phase-a-log.csv`, root-level since the queue spans subjects)
- [ ] Design the agent instruction set for per-section observation spawns — what to read, what patterns to capture, output format. The instructions go through baseline spawn unchanged
- [ ] Decide per-item granularity. Proposed: one queue row per (subject, top-level chain key). E.g. `("claude-marketplace", "1. Marketplace discoverability")`. `measured_size` = total bytes of that section's content concatenated across all samples in the subject. The agent's job: read those slices, observe, write to the subject's observation file under a heading matching the chain key

### Phase A.1 — Build the work queue

- [ ] Run `count-sections` against both subjects to enumerate chain keys
- [ ] Strip entity-id prefix to derive cross-sample top-level section names
- [ ] For each (subject, section name) pair: collect all sample files containing that section and sum their section-content byte sizes — this is `measured_size`
- [ ] Write the queue CSV with `path,measured_size,status,batch_id,notes` columns where `path` is the synthetic key `<subject>::<section name>`

### Phase A.2 — Baseline spawn

- [ ] Spawn one agent with the full Phase A instruction set + "do nothing; reply ACK; return" — capture `total_tokens` as `B`. This isolates fixed overhead from per-item cost
- [ ] Append `batch_00` row to spawn log

### Phase A.3 — Calibrated iteration

- [ ] First batch: bin-pack pending items up to `(0.9 × budget − B) / seed_ratio`. Seed ratio is a conservative overestimate (e.g. 5 tokens per measured byte). Spawn, capture tokens, compute actual ratio
- [ ] Subsequent batches: use running-average ratio for capacity; iterate until queue is empty or all remaining items are oversized
- [ ] On each batch return: append spawn log row; update queue rows to `done` (or `failed`/`unconsumable`)
- [ ] Watch for ratio divergence (`|ratio_k − running_avg| / running_avg > 0.3`) and re-baseline if input distribution shifts

### Phase A.4 — Cleanup and handoff

- [ ] Delete `logs/research/_scripts/` (stale pyc cache only — confirmed no source files remain)
- [ ] Verify both subjects' observation files are complete and pass `check`
- [ ] Promote Phase B and Phase C/D to durable homes per the recovered handoff plan (`logs/idea/` entries or `TASKS.md` entries — original tracker doesn't survive unpack)
- [ ] Run full plugin test suite; verify no regressions

## Open Questions

- **Restructure samples in this phase, or only observe?** The recovered plan says Phase A restructures + observes, but Phase B owns the master template. Reading carefully: "restructure" likely means apply the master-template-shape only after Phase B emits one. So Phase A is **observation-first**; structural changes wait. Confirm before iteration starts
- **Do observations need to capture sub-purpose patterns** (the bullet-with-colon items inside each section)? The tooling can't reach them, but they're load-bearing for understanding what the section actually conveys. Likely yes — the agent reads raw content, the tooling is just an entry point
- **Output shape for observation file** — per-section heading with structured observations underneath, or a flat list of findings with cross-references? The decision shapes whether Phase B can scan the observations efficiently

## Ready-to-start checklist

When the three open questions are answered:

- Queue + log CSVs initialized
- Agent instruction set drafted and reviewed
- Baseline spawn dispatched
- First calibrated batch dispatched
