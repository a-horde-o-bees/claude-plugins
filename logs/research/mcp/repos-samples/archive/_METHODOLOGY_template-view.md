---
log-role: reference
---

# Methodology — Template-View Consolidation

How `_CONSOLIDATED_template-view.md` was produced. Companion to that document; record of process, decisions, and limitations so the synthesis is auditable and reproducible.

## Goal

Provide a section-by-section consolidation that mirrors `_TEMPLATE.md`'s heading tree and surfaces adoption metrics — the structured, axis-by-axis view as a peer to the design-decision-organized `_CONSOLIDATED_design-view.md`. Same evidence, different organizing principle.

## Inputs

**Primary input:** the 8 batch reports produced by the dispatch documented in `_METHODOLOGY_design-view.md`. Those reports contained:

- 104 per-sample one-line distinctive observations (13 × 8)
- 8 batch-level cross-cutting pattern descriptions with within-batch X/13 counts
- 8 outlier lists (~50–60 items total)
- 8 research-gap notes

**Structural input:** `_TEMPLATE.md`'s heading tree was used as the organizing scaffold — explicit goal here, unlike the design-view sibling.

**Not re-read:** `_INDEX.md`, `_CONSOLIDATED.md`, and the per-sample files themselves. The data source for this consolidation was exclusively the existing batch reports plus `_TEMPLATE.md`'s structure.

## Process

### 1. Considered re-dispatch for exact counts

The cleanest path to precise per-axis tallies would be follow-up extraction prompts to the same 8 agents — their contexts still held the file content read in the original dispatch, so they could re-traverse without re-reading. The Agent tool's documentation describes this pattern (resume an existing agent via `SendMessage` with the agent's ID).

### 2. SendMessage tool unavailable

Searched the deferred tool registry for `SendMessage`:

```
ToolSearch: select:SendMessage → No matching deferred tools found
```

Re-dispatching fresh agents would have repeated the original token cost (104 file reads × 8 agents). Decided instead to work from the existing batch reports and frame counts explicitly as estimates summed from per-batch tallies — honest disclosure of imprecision over hidden re-dispatch cost.

### 3. Population estimate derivation

For each template axis, walked the 8 batch reports and summed the X/13 counts agents had reported. Where an axis wasn't uniformly reported across batches, fell back to:

- Per-sample observations (which batch agents had captured for all 104 files)
- Outlier callouts (which named distinctive samples by basename)
- Research-gap notes (which flagged where reporting was thin)

The resulting counts are reliable for **relative magnitude** — "dominant", "minority", "rare" — and reasonable as approximate N/104. They are not exact tallies. The document's opening states this explicitly.

### 4. Section-by-section structure

Mirrored `_TEMPLATE.md`'s heading tree exactly:

- Identification (skipped count-style aggregation since these are per-sample identity facts; surfaced cross-cutting observations like license distribution and lifecycle signals)
- Language and runtime (with sub-tables for SDK and Python version floor)
- Transport (supported transports + selection mechanisms + pitfalls)
- Distribution (every channel + package names + install commands + pitfalls)
- Entry point / launch
- Configuration surface
- Authentication
- Multi-tenancy
- Capabilities exposed (primary combination + add-ons + tool-count buckets + capability gating)
- Observability
- Host integrations (with distribution-shape commentary)
- Claude Code plugin wrapper (and sibling ecosystems + co-shipped agent context files)
- Tests
- CI
- Container / packaging artifacts
- Example client / developer ergonomics
- Repo layout
- Notable structural choices (cross-cutting design facts that recur)
- Unanticipated axes observed (candidates for future template revisions)
- Python-specific (conditional, applies to ~58 Python primaries)
- Gaps

### 5. Adoption tables per section

Each axis received a `Path | Count | Representative repos` table. Counts were marked as estimates in the document's opening framing. Representative repos cited specific samples whose batch-report observations confirmed inclusion in that path.

### 6. Outlier and pitfall callouts

Each section has either a "pitfalls observed" or analogous notes section, capturing the recurring observations from the agent reports. These were extracted from the outlier lists and "unknowns / signal gaps" sections of the 8 batch reports.

### 7. Cross-document linkage

Updated `_CONSOLIDATED_design-view.md`'s opening and closing to reference the new peer; opened `_CONSOLIDATED_template-view.md` with a reference to its peer. Symmetric framing — neither document is canonical, both organize the same evidence differently.

### 8. Renames

`_CONSOLIDATED_free-form.md` → `_CONSOLIDATED_design-view.md` to better describe its content (design-decision-organized) rather than its production process (free-form). The new pair `_design-view` / `_template-view` is symmetric and accurate to organizing principle.

Naming alternatives considered and rejected:
- `_decisions` / `_axes` — too terse; "axes" overloads vocabulary used inside the documents (the "emerging axes" section).
- `_narrative` / `_matrices` — `_matrices` undersells the prose context per section.
- `_design-view` / `_template-view` — chosen. Symmetric, reads cleanly, accurate.

## Decisions and rationale

- **Reuse existing batch reports rather than re-dispatch.** With `SendMessage` unavailable, fresh dispatch would have repeated the entire token cost of the original 8 agents reading 104 files. Existing reports already contained the relevant aggregations; the cost of imprecise counts was lower than the cost of re-dispatch.
- **Estimates explicit upfront.** The document's opening names the count derivation method and flags numbers as estimates. Honest disclosure beats artificial precision.
- **Mirror `_TEMPLATE.md` structure exactly.** A reader who knows the per-sample shape can read this document section-by-section and find each axis where they expect it. Departing from the template would defeat the document's purpose.
- **Tables for adoption signals, prose for structural facts.** Tables compress count + representative-repos efficiently; prose handles "Notable structural choices" and "Unanticipated axes" where the structure is open-ended.
- **Pitfalls as section closers.** Pitfalls collected per section make this view scannable for "what should I avoid on this axis" — a builder use case the design-view doesn't directly serve.

## Tools used

| Tool | Use |
|---|---|
| `Bash` | `mv` (rename) and `ls`/`wc` (verification) |
| `ToolSearch` | Check whether `SendMessage` was available (it wasn't) |
| `Read` | Verify the design-view doc's opening before editing |
| `Edit` | Update design-view opening + provenance to reference the new peer |
| `Write` | Final document creation |

No fresh agent calls were made for this consolidation. The 8 batch reports from the design-view dispatch were the entire data source.

## Limitations

- **Counts are estimates summed from per-batch X/13 reports.** Agents counted with different precision per axis. Reported counts are reliable for relative magnitude (dominant / minority / rare) but should not be cited as exact tallies. Where a count is critical, regenerate against per-sample files directly.
- **Pitfalls reflect what agents flagged in their batch reports.** Sections where no batch agent flagged a pitfall may have undocumented pitfalls in the source samples.
- **Sub-tables under Python-specific are coarse.** The original design-view dispatch wasn't extraction-focused; precise FastMCP version distribution within the FastMCP 2.x bucket isn't recoverable without re-reading.
- **Identification section doesn't aggregate.** Per-sample identity facts (URL, stars, last-commit, license) don't form adoption matrices. The section surfaces cross-cutting observations instead but is structurally lighter than the rest.
- **No verification pass.** No second pass confirming every cell of every adoption table traces to a specific batch-report assertion. Specific repo citations are reliable; counts are aggregations of agent claims.

## Reproducibility

To rebuild this document from scratch:

1. Run the dispatch documented in `_METHODOLOGY_design-view.md`.
2. For each `_TEMPLATE.md` section, walk the 8 batch reports and sum X/13 counts; cite specific repos from the per-sample observations.
3. Write a section-by-section document mirroring `_TEMPLATE.md`'s heading tree, one adoption table per axis where adoption matters, prose where it doesn't.

For a precise-count rebuild, modify the agent prompt template in `_METHODOLOGY_design-view.md` to request per-axis X/13 tallies for every template section, not just free-form patterns. Suggested addition to the prompt:

```
## Per-template-axis tallies
For each template section listed below, report X/13 with the specific
file basenames matching each path. Sections: Language, Transport,
Distribution, Entry point, Configuration, Authentication, Multi-tenancy,
Capabilities, Observability, Host integrations, Plugin wrapper, Tests,
CI, Container artifacts, Dev ergonomics, Repo layout, Python-specific
(where applicable).

For each section, list the dominant paths observed and which of the
13 batch repos fell into each. Use the canonical sub-purpose vocabulary
from the template where possible.
```

This roughly doubles per-batch agent output but yields directly summable tallies. The existing dispatch could not have done this without nearly doubling agent context size, which is why the original prompt left axis-by-axis extraction implicit and let agents surface patterns conversationally instead.
