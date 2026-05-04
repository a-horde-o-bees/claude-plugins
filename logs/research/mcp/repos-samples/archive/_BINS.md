# Synthesis Bins — mcp / repos-samples

Orchestrator working state for the `_CONSOLIDATED.md` synthesis sweep. Tracks bins (chain assignments per spawned agent), calibration data (trailing-N work-tok/byte ratio), and bin status. **Not committed** — transient working file, deleted after the sweep completes alongside the legacy decisions reference at `_phase-a-mcp-archive/_legacy-decisions-for-sanity-check.md`.

The compliance verb skips `_*-prefixed` files (except `_CONSOLIDATED.md`), so this file is invisible to corpus audits.

## Calibration

- Bin 1 ratio: 1.59 work-tok/byte (127,299 / 79,932)
- Bin 2 ratio: 1.53 work-tok/byte (151,705 / 98,965)
- Bin 3 ratio: 2.16 work-tok/byte (226,075 / 104,653) — higher due to cross-section writes
- Trailing-N=3 average: **1.76 work-tok/byte**
- Agent total context budget: ~250K tokens (revised — Bin 3 used 226K successfully)
- Fixed overhead (instructions + template + consolidated reads + compliance): ~30K
- Available for corpus + synthesis: ~220K
- Target utilization (per context-aware-iteration guidelines): 90% of available
- Current byte capacity at trailing ratio: 0.9 × 220K / 1.76 = **~112KB**
- Bin target: **~100-110KB**

After each spawn, append the actual ratio (work_tokens / bytes_synthesized) and recompute the trailing-N=3 average. Use the running average to size the next bin's chain set.

## Bins

### Bin 1 — completed

- **Chains:** `Sample > Identification`, `Sample > Capabilities exposed`, `Sample > Multi-tenancy`
- **Target bytes:** 79,932
- **Spawn:** `a5a1d5403f24a44aa`
- **Work tokens:** 127,299
- **Ratio:** 1.59 work-tok/byte
- **Outcome:** All three populated; compliance clean. No cross-section writes. Agent noted: peer documents (`_CONSOLIDATED_template-view.md`, `_CONSOLIDATED_design-view.md`) overlap; lifecycle status scattered across sub-purposes (template-revision candidate); tool-count not-captured rate 64/104; tenancy categorization fuzzy at +/- 3-4 boundary cases

### Bin 2 — completed

- **Chains:** `Sample > Notable structural choices`, `Sample > Unanticipated axes observed`, `Sample > Claude Code plugin wrapper`
- **Target bytes:** 98,965
- **Spawn:** `a65392197e92de3f0`
- **Work tokens:** 151,705
- **Ratio:** 1.53 work-tok/byte
- **Outcome:** All three populated; compliance clean. No cross-section writes (assigned chains were two of the three freeform catch-alls). Agent flagged: Unanticipated axes surfaced ~20 recurring cross-sample axes — several (token efficiency, hosted-vs-local, vendor-vs-community trust, capability gating, safety postures, server-managed credentials) are candidate template sections for a future revision. Some samples retain legacy "Decision dimensions this repo reveals:" scaffolding in their Unanticipated axes bodies — corpus cleanup candidate

### Bin 3 — completed

- **Chains:** `Sample > Distribution`, `Sample > Entry point / launch`, `Sample > Container / packaging artifacts`, `Sample > CI`, `Sample > Tests`
- **Target bytes:** 104,653
- **Spawn:** `a7ffac545f35b1c9a`
- **Work tokens:** 226,075
- **Ratio:** 2.16 work-tok/byte (cross-section writes inflated)
- **Outcome:** All five populated; compliance clean. Cross-section writes to Notable structural choices and Unanticipated axes observed (setup-subcommand pattern, container-as-test-stack distinction, system-binary deps, testing-discipline axis, Helm/systemd template-revision candidate)

### Bin 4 — completed

- **Chains:** Transport, Host integrations, Configuration surface, Authentication, Observability
- **Target bytes:** 101,737
- **Spawn:** `a3f60d44658b0f6cd`
- **Work tokens:** 236,508
- **Ratio:** 2.32 work-tok/byte
- **Outcome:** All 5 populated; compliance clean. Observations: Observability has highest "not documented" rate (~55/104); stdout-cleanliness discipline rarely surfaced; canonicalization violations in Host integrations sample-level (~22 generic catch-all entries)

### Bin 5 — completed

- **Chains:** Language and runtime, Repo layout, Example client, Gaps
- **Target bytes:** 86,160
- **Spawn:** `ac89c784cc0ac0e8d`
- **Work tokens:** 182,227
- **Ratio:** 2.11 work-tok/byte
- **Outcome:** All 4 populated; compliance clean. Observations: documentation discoverability is the systematic gap (well-documented at category level, under-documented at operational level); single-file Python script layouts persist (5-6 samples); Polylith adoption unique to one Clojure server

### Bin 6 — completed

- **Chains:** `Sample > Python-specific`
- **Target bytes:** 91,348
- **Spawn:** `acd97b567579bb7fe`
- **Work tokens:** 259,360
- **Ratio:** 2.84 work-tok/byte (highest — single dense section with 10 sub-purposes)
- **Outcome:** Section populated with all 10 sub-purposes; compliance clean. 62/104 Python-carrying denominator confirmed. SDK split: ~24 FastMCP / ~25 raw mcp / ~5 dual-pinned / 3 custom

## Sweep summary

- **Total spawns:** 6
- **Total work tokens:** 1,183,174
- **Total bytes synthesized:** 561,793 (across 21 top-level sections)
- **Overall ratio:** 2.11 work-tok/byte (close to trailing-3 final of 2.42)
- **Final state:** all 21 sections populated; compliance clean (104/104 samples + Consolidated)

## Cleanup pending

- Sanity-check `_CONSOLIDATED.md` against `_phase-a-mcp-archive/_legacy-decisions-for-sanity-check.md` — flag divergences as either (a) findings the new synthesis missed (re-run that section) or (b) old claims the corpus doesn't support (drop)
- Delete `_phase-a-mcp-archive/_legacy-decisions-for-sanity-check.md` after reconciliation
- Delete this `_BINS.md` file (transient working state — no longer needed once sweep is committed)

## Section size reference

From `ocd-run log research sections --subject mcp --size` (run on clean skeleton). Each top-level section's `Sample > X` chain size:

| Section | Bytes |
|---|---|
| Python-specific | 91,348 (oversized — needs sub-purpose batched) |
| Notable structural choices | 49,699 |
| Unanticipated axes observed | 38,580 |
| Distribution | 36,440 |
| Identification | 36,259 |
| Capabilities exposed | 30,826 |
| Entry point / launch | 24,280 |
| Example client / developer ergonomics | 22,776 |
| Language and runtime | 22,742 |
| Host integrations shown in README or repo | 22,588 |
| Configuration surface | 22,548 |
| Authentication | 21,690 |
| Gaps | 21,555 |
| Repo layout | 19,087 |
| Transport | 18,896 |
| Container / packaging artifacts | 16,340 |
| Observability | 16,015 |
| Tests | 14,699 |
| CI | 12,894 |
| Multi-tenancy | 12,847 |
| Claude Code plugin wrapper | 10,686 |
