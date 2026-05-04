---
log-role: reference
---

# Methodology — Design-View Consolidation

How `_CONSOLIDATED_design-view.md` was produced. Companion to that document; record of process, decisions, and limitations so the synthesis is auditable and reproducible.

## Goal

Test what an unscripted consolidation produces when the agent organizes around the design decisions a builder faces, rather than mirroring `_TEMPLATE.md`'s data-collection heading tree. The user explicitly framed this as a test of "what a completely unscripted version" looks like.

## Inputs and exclusions

**Inputs.** The 104 per-sample files in this directory matching `<owner>--<repo>.md`.

**Excluded by user direction:**
- `_TEMPLATE.md` — excluded so its lens didn't impose template-shaped organization on the synthesis.
- `_CONSOLIDATED.md` — the existing skeleton; user wanted a fresh artifact rather than a fill-in.
- `_INDEX.md` — initially considered as pre-aggregated data, then explicitly excluded because freshness was uncertain ("I don't know if INDEX is up-to-date, or if it's an artifact").
- `_missing--*.md` — not-found records, not source samples.

Final input set: **104 sample files**, read directly.

## Process

### 1. Corpus orientation

Before dispatch, briefly inspected `_TEMPLATE.md` to understand the per-sample heading tree and a portion of `_INDEX.md` for the domain breakdown. The user redirected mid-task to ignore `_INDEX.md`; the orientation read informed the dispatch design but was not used as data for the synthesis.

### 2. Batching

Sorted the 104 sample filenames alphabetically and split into **8 batches of 13** (104 = 8 × 13 evenly). Alphabetical batching was chosen over domain-sliced batching to avoid selection bias — each batch saw a mix of vendor and community, of languages, of transports, of repo sizes.

The eight batches:

| Batch | Range |
|------:|-------|
| 1 | `AlwaysSany--…` through `alpacahq--alpaca-mcp-server` |
| 2 | `apollographql--…` through `cloudflare--mcp-server-cloudflare` |
| 3 | `conikeec--mcpr` through `executeautomation--mcp-playwright` |
| 4 | `feiskyer--…` through `korotovsky--slack-mcp-server` |
| 5 | `ktanaka101--…` through `mongodb-js--mongodb-mcp-server` |
| 6 | `motherduckdb--…` through `reminia--zendesk-mcp-server` |
| 7 | `riza-io--riza-mcp` through `stripe--agent-toolkit` |
| 8 | `supabase-community--…` through `zongmin-yu--…` |

### 3. Parallel agent dispatch

Eight `general-purpose` subagents launched in a single tool-call block (parallel execution per the project's parallel-tool-call rule). Each agent received:

- The 13 file basenames in its batch
- A self-contained briefing on the consolidation goal
- A description of the per-sample template structure (transferred inline rather than asking each agent to read `_TEMPLATE.md`, both to save context and to avoid reinforcing the template lens in their organization)
- A specified output format

The agent prompt template (parameterized on the file list):

```
You're consolidating cross-cutting findings from a research corpus
of 104 MCP server repository samples. Other agents are reading sibling
batches in parallel; your job is one batch of 13.

[per-sample template structure described inline]

Read these 13 files in <directory>:
[file list]

Return findings in this exact format:

## Per-sample observations
One bullet per file: `- <basename>: <≤25 words — language/SDK +
transport + most distinctive structural fact>`. For unremarkable
dead-center defaults, say "dead-center default" then name the
language.

## Cross-cutting patterns in this batch
Free-form prose. Notice what recurs across these 13 — language
clusters, transport choices, distribution mechanisms, launch
commands, auth, tenancy models, capability surfaces (counts when
stated), ops setup, host coverage, plugin wrappers, repo layout,
distinctive structural choices, unanticipated axes. Surface counts
(X/13) for any pattern you cite. ≤500 words.

## Outliers worth flagging
[≤10 bullets]

## Unknowns / signal gaps
[so the consolidating agent knows what wasn't surfaced]
```

The prompt deliberately left organization free at the batch level. Agents were told to surface what they noticed across the 13, not to fill a fixed checklist. This was the key methodological choice for the "unscripted" goal — extraction was loose, synthesis tight.

### 4. Agent output collection

All 8 returned in a single async wait. Each produced ~600–1200 words containing:
- 13 per-sample one-line distinctive observations (104 total across the corpus)
- Free-form prose on cross-cutting batch patterns with X/13 counts
- Outlier callouts (≤10 per batch, ~50–60 total)
- Notes on which sections were sparse or templated

Total agent output: roughly 8000 words of synthesis material.

### 5. Synthesis

Read all 8 batch reports and:

- **Identified emergent design questions** — typology of "what an MCP server actually means here", language/SDK, transport, distribution and launch, configuration & credentials, tenancy, capability surface, operations (tests/CI/observability/containers), host integrations, plugin wrappers, repo layout, emerging axes the framework didn't anticipate.
- **Drafted prose around each**, citing specific repos as evidence with basename references that trace back to verified samples.
- **Summed batch counts** to produce population-level estimates. Where agents reported uniformly across batches, sums were reliable; where reporting was uneven, fell back to qualitative magnitude ("dominant", "minority", "rare").
- **Built an outlier index** of repos that broke the modal shape on at least one axis — short list of "this one is unusual in a way that might matter" entries.
- **Captured research gaps explicitly** in a dedicated section.

### 6. Write

Single-pass write of `_CONSOLIDATED_free-form.md` (renamed `_CONSOLIDATED_design-view.md` after the peer document was added).

## Decisions and rationale

- **8 batches × 13 files.** Even split (104 = 8 × 13). Each batch fits comfortably in an agent context. 8 is enough parallelism for all to run concurrently in a single tool-call block; small enough that I can reason about each batch by reference.
- **Alphabetical batching.** Simpler than domain slicing and avoids any signal leakage from the existing categorization in `_INDEX.md`.
- **`general-purpose` subagent type.** Agents needed to read full file contents and produce structured synthesis. `Explore` reads with excerpts and is read-only — insufficient for this task.
- **Free-form per-batch prose, structured per-sample bullets.** The per-sample bullets normalize for downstream synthesis; the per-batch prose lets agents surface patterns that don't fit a fixed schema.
- **Inline template description, not "read `_TEMPLATE.md`".** Saves agent context and avoids reinforcing the template's organization in their reports.
- **Synthesis organized around design questions.** This was the key "unscripted" decision. The alternative (mirror the template) is what the peer `_CONSOLIDATED_template-view.md` does.
- **Counts as population estimates, not exact tallies.** Honest disclosure in the document; precise tallies would require either a fresh extraction-focused dispatch or programmatic parsing of per-sample files.

## Tools used

| Tool | Use |
|---|---|
| `Read` | Inspect `_TEMPLATE.md`, portions of `_INDEX.md`, and the existing `_CONSOLIDATED.md` skeleton during planning |
| `Bash` | `ls` and `wc` to scope the corpus |
| `Agent` (general-purpose) × 8 | Parallel batch processing |
| `Write` | Final document creation |
| `Edit` | Opening + provenance adjustments after the peer document was added |

No `_INDEX.md` content was fed to agents or referenced in synthesis (per user direction after initial misstep).

## Limitations

- **Counts are approximate.** Reported as "dominant", "roughly a third", "well over half" rather than exact N/104. Exact tallies require re-dispatch with extraction-focused prompts or programmatic parsing.
- **Single synthesizing pass.** No second pass verifying every claim traces to source. Specific repo citations are reliable; aggregate counts are estimates.
- **Agent variance across batches.** Each batch agent had its own writing style, granularity, and emphasis. Synthesis flattened this into a single voice but couldn't fully recover what one agent omitted.
- **Emerging-axes interpretation is subjective.** The "Emerging axes the framework didn't anticipate" section reflects what struck the synthesizer as recurring across batch reports. A different synthesizer might cluster differently.
- **Timing.** All agent dispatch happened in a single batch — no follow-up extraction passes were run.

## Reproducibility

To rebuild from scratch:

1. Sort `*--*.md` files in this directory alphabetically; split into 8 batches of 13.
2. Dispatch 8 parallel `general-purpose` agents with the prompt template above (parameterized on per-batch file lists).
3. Synthesize across the 8 reports, organizing around whatever design questions emerge from the batch-level patterns.

The resulting document will not be byte-identical — agent output varies and synthesis is interpretive — but the architectural shape, the outlier index, and the population estimates should be reproducible to within a few percent.

For a precise-count rebuild, see the modification suggestion in `_METHODOLOGY_template-view.md`.
