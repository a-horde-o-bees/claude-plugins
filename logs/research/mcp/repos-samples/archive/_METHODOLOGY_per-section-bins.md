---
log-role: reference
---

# Methodology — Per-Section Bins Consolidation

How `_CONSOLIDATED.md` (the per-section-bins variant) was produced. Companion to that document; record of process, decisions, and limitations so the synthesis is auditable and reproducible.

## Goal

Consolidate findings across 104 MCP server samples into a synthesis that mirrors `_TEMPLATE.md`'s heading tree exactly — every canonical section gets named patterns, adoption counts against the applicable sample subset, sample exemplars per pattern, and outliers worth elevating. Output is structurally checkable against the template via the compliance verb.

## Inputs

- 104 per-sample files at `logs/research/mcp/repos-samples/<owner>--<repo>.md`, each shaped to `_TEMPLATE.md`'s heading tree
- `_TEMPLATE.md` as the canonical heading tree for the consolidation's structure
- Per-chain corpus content extracted on-demand via `ocd-run log research content "<chain>" --subject mcp` (verbatim per-sample subsections under each chain key)

**Excluded:**

- `_INDEX.md` — pre-aggregated; methodology produces independent synthesis
- `_phase-a-mcp-archive/_synthesis.yaml` — Phase A retrospective (per-batch observations from the original sample-collection process); methodology synthesizes from corpus rather than aggregating prior observations
- Peer documents (`_CONSOLIDATED_template-view.md`, `_CONSOLIDATED_design-view.md`) — parallel-method outputs; synthesis is independent

## Process

### 1. Skeleton

Initialize `_CONSOLIDATED.md` as a clean section-only skeleton — every `## ` and `### ` heading from `_TEMPLATE.md`, no body content. Empty sections are unsynthesized; populated sections carry the canonical synthesis.

### 2. Sizing companion

Run `ocd-run log research sections --subject mcp --size` to get per-chain-key UTF-8 byte counts across all 104 samples. This data drives bin-pack decisions — orchestrator knows the cost (in agent input bytes) of each section before dispatching.

### 3. Orchestrator-driven bin-packed dispatch

Orchestrator computes bin assignments using the trailing-N work-tok-per-byte ratio, targeting 90% of agent context budget per spawn. Each bin is a list of chain keys totaling under capacity (initial seed ratio 2.5; trailing average across 6 actual spawns: 2.11). Agent does not decide what to work on — orchestrator dispatches with explicit `{chains}` assignment list. Bin-plan tracking lives in `_BINS.md` (transient working state, archived alongside this methodology).

### 4. Per-spawn agent flow

Agent reads `_TEMPLATE.md` (canonical structure) + `_CONSOLIDATED.md` (input context — prior bins' synthesis informs new work). For each chain in the assignment list:

- Extract verbatim corpus content via `content "<chain>" --subject mcp`
- Synthesize: name patterns, count adoption, cite sample exemplars, surface outliers, note authoritative-doc alignment
- Write into the chain's section block in `_CONSOLIDATED.md` (replace if empty, extend/refine if already populated)
- Cross-section writes to freeform catch-alls (Notable structural choices, Unanticipated axes observed, Gaps) permitted when an observation surfaces that genuinely belongs there
- Run `compliance --subject mcp` after each chain's write — if outliers/order violations surface, revert and continue

After processing all chains in the assignment, agent reports per-chain status (populated/extended/failed), cross-section writes, and notable corpus observations.

### 5. Calibration loop

After each spawn returns, orchestrator records actual ratio (work_tokens / corpus_bytes), updates trailing-N=3 average, and bins the next dispatch using the refined ratio.

### 6. Sanity check

Once all sections populated, compare new synthesis against `_phase-a-mcp-archive/_legacy-decisions-for-sanity-check.md` (the pre-restructure `## Decisions` block held as reference). Classify divergences as missed findings (re-synthesize), unsupported old claims (drop), or convergent.

## Results

- 6 bin spawns
- 1,183,174 total work tokens
- 561,793 bytes synthesized
- Overall ratio: 2.11 work-tok/byte
- Output: 1538-line `_CONSOLIDATED.md`, 21 top-level `##` sections + ~42 `###` sub-purposes, compliance clean

## Strengths

- Faithful per-section adoption counts with explicit denominators
- Long-tail enumeration (15-30 named exemplars per pattern; readers can locate every sample for every variant)
- Per-section pitfalls / consumer-visible footguns surfaced
- Cross-section provenance — every distinctive claim cites where it is also discussed elsewhere
- Counter-examples / explicit zero counts retained (e.g. "Helm 0/104, systemd 0/104")
- Heading-tree compliance enforced after every section write

## Limitations / Blind spots

- **Cross-cutting threads invisible** — the "dual-deployment posture" (stdio + hosted from one codebase) recurs as evidence in Transport, Distribution, Auth, Tenancy, Hosts, Notable structural choices but never resolves as a single named phenomenon. Section boundaries cut the natural cross-cutting axis
- **Reader fatigue at 1538 lines** — the reader cannot hold the whole picture; specific findings buried 900+ lines deep are effectively lost
- **Heading-tree fidelity over insight** — sections like "Identification > url" produce mild-interest paragraphs because the template required the heading
- **Redundancy across sections** — distinctive samples (e.g. `samuelgursky/davinci-resolve-mcp install.py`) appear 5-7 times across sections rather than once with cross-references
- **Canonicalizable counts over-stated** — host integrations counts (Claude Desktop, Cursor, VS Code) drift high relative to CLI ground truth from `sections --count`. Human-authored consolidations consistently err high; CLI counts are the authority
- **Three legitimate misses** identified during sanity check vs legacy decisions block: `modelcontextprotocol/registry` rare-channel framing, DXT host-portability gotcha, "minimalist-by-design vs enumerate-every-API" tool-surface philosophy axis. All are cross-cutting frames the per-section method does not surface naturally

## When to use this methodology

- When the research target is well-served by mirroring a fixed structural template (entity metadata, axis-by-axis adoption surveys)
- When per-section depth and exhaustive enumeration matter more than cross-cutting framing
- When the audience needs an audit-grade reference, not a builder's handbook
- When a CLI verification pass for canonicalizable fields can supplement the synthesis

## When not to use

- When cross-cutting design axes are the most valuable findings (use design-view methodology instead)
- When the corpus structure should emerge from the samples rather than be imposed (use breadth-then-depth instead)
- When reader navigation matters more than completeness (the encyclopedic shape becomes a liability)
- When tooling-side ground-truth checks are not available (over-counts go unchecked)
