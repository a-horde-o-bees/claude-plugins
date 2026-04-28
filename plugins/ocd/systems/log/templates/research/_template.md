---
log-role: reference
---

# Research

Long-form investigation of a subject — an ecosystem, a population of artifacts, a design space — producing consolidated findings backed by per-entity samples. Research accumulates under `logs/research/<subject>/` with one directory per subject. Samples live in a nested `samples/` directory and mirror the consolidated doc's purpose structure so cross-sample tallying produces comparable counts.

## What Qualifies

A subject worth investigating systematically — multiple artifacts to compare, adoption counts to establish, or a design space to characterize.

Signals a subject is worth a research log rather than an idea or decision:

- The investigation requires multiple samples (repos, files, implementations) to reach a defensible conclusion.
- Findings get applied across more than one downstream decision. A one-shot investigation with a single downstream consumer is usually a decision, not research.
- Evidence should persist beyond the current session so future work can extend or refresh the conclusions.

## What Does Not Qualify

- Single-source investigations → decision or commit message
- Exploratory "I wonder if" notes → idea
- Observed defects in specific artifacts → problem
- Tool performance metrics, benchmarks → problem or a dedicated measurement log
- Documentation of completed work → commit message + the artifact itself

## Subject Discipline

A research subject converges on a **purpose-organized** methodology: break the subject into the purposes (axes, dimensions, questions) that matter, then characterize each purpose using evidence from samples.

- **Purposes are subject-specific and discovered through research.** The first wave identifies purposes; later waves refine them when samples surface concerns the existing purposes don't capture.
- **Each purpose gets a section in the consolidated doc.** The consolidated doc reads purpose-by-purpose, not sample-by-sample.
- **Per-purpose content** typically includes: observed paths with adoption counts against the applicable sample subset, per-entity citations, pitfalls, and — where relevant — docs-prescribed markers for paths the ecosystem's authoritative reference calls out.

The consolidated doc is not a dump of sample observations; it's the synthesis. Samples are the evidence behind the synthesis.

## Subject Directory Shape

```
logs/research/<subject>/
├── consolidated.md              — synthesized findings, purpose-organized
├── <research-wave>.md           — optional: outputs from specific research passes
│                                    (surveys, resamples, diff-style audits between waves)
├── samples/                     — per-entity evidence (see samples template)
│   ├── _INDEX.md                — optional: per-sample overview table
│   ├── _TEMPLATE.md             — optional: subject-specific sample template
│   ├── <entity>.md              — per-sample entry
│   └── ...
├── context/                     — optional: external docs and references that informed
│   │                                the research (API docs, tool readmes, blog posts)
│   └── ...
└── scripts/                     — optional: tallying and maintenance scripts (e.g. walk
    │                                samples and aggregate per-purpose data points)
    └── ...
```

Multiple docs at subject root are fine when later research waves produce standalone artifacts (a missing-dimensions survey, a comprehensive resample) that contribute to but don't replace the consolidated doc. Leave each wave's output as a dated or topically-named file alongside the consolidated synthesis.

`context/` and `scripts/` are subject-specific and optional. Use them when external docs need archiving alongside the research (to survive source-side changes), or when scripted maintenance is worth preserving (e.g. a script that retrofits new purposes into every sample file when the consolidated doc's purpose set evolves).

## Samples Discipline

Samples live under `samples/` and each mirrors the consolidated doc's purpose structure for cross-sample tallying. See `_samples-template.md` at the research log-type root for per-sample entry structure.

## Tallying

Adoption counts in the consolidated doc come from sampling the `samples/` directory. A count of "14/54 repos declare non-trivial `userConfig`" is verifiable by scanning the relevant purpose section across all 54 sample files. Keeping sample structure consistent is what makes the counts defensible.

When a new purpose surfaces mid-research that samples didn't address, the refresh cycle:

1. Add the purpose section to each sample (or mark "not captured" when the sample file's research template didn't target it).
2. Tally across samples for the new purpose.
3. Update the consolidated doc's counts and citation pool.

Scripts that assist tallying — walking the `samples/` directory, extracting per-purpose data points, producing refined counts — can live at `logs/research/<subject>/scripts/`. Subject-specific transforms go there.

## Heading-Tree Tooling

Cross-subject heading-tree analysis is provided by `ocd-run log research` verbs:

| Verb | Purpose |
|------|---------|
| `check <path>` | Verify one markdown file has no sibling-duplicate headings. Run before consolidating to catch heading collisions early |
| `count-sections --subject <name>` | Print chain-key coverage across the samples directory — which headings are near-universal vs rare |
| `consolidate --chain "<key>" --subject <name>` | Print every sample's content under one chain key (e.g. `Sample > Authentication > flow`). The unit of synthesis when authoring `consolidated.md` per purpose |
| `compliance --subject <name>` | Diff every sample against `_TEMPLATE.md`. Surfaces outlier headings (chain keys in samples but not in template — typos, non-canonical labels, or template-revision candidates) and reports order violations |

Run `compliance` after retrofitting samples or before tallying — it confirms the corpus matches the template's heading tree (the single source of truth for sample structure). Outliers under open-enumeration sections (marked by a `<placeholder>` heading in the template) are not flagged; they are the section's content vocabulary.

When `consolidated.md` is the goal, reach for `consolidate` per template section rather than reading every sample top-down. The output is bounded (one section's evidence at a time), grounded (returned content is verbatim from the samples), and composes naturally — each `consolidate` pass produces one section's worth of synthesized findings, ready to merge into the larger doc.

## Consuming Research

Research outputs are consulted when:

- Authoring a new pattern or methodology that should reflect ecosystem convention.
- Auditing the project's alignment against observed conventions (see `alignment-audit.md` pattern).
- Reassessing a decision whose underlying landscape may have shifted.

They are not loaded into session context by default — agents reach for them when the subject is relevant.

## Canonical Example

`logs/research/claude-marketplace/` studies the Claude Code plugin marketplace ecosystem across 54 public repos. Its shape:

- `consolidated.md` — purpose-organized pattern with per-purpose adoption counts and citations.
- `survey-missing-factors.md` — output of a later research wave that identified dimensions the consolidated doc hadn't captured.
- `resample-corrections.md` — output of a comprehensive resample that refined adoption counts across all 54 samples after the survey landed.
- `samples/<owner>--<repo>.md × 54` — per-repo sample entries with per-purpose observations.

When authoring a new research subject, reference this structure. Diverge where the subject's nature requires (a research subject studying files rather than repos may use `samples/<path>.md`), but keep the purpose-organized consolidated + evidence-bearing samples pattern.

## Lifecycle

Semi-permanent — like decisions and patterns, research does not expire when "acted on." Research accumulates as long as it's referenced or extended. Update when new waves refine findings. Delete entire subjects only when the research is subsumed by a replacement or genuinely obsolete.

Users own deployed copies — they can edit, extend, or delete. Skills and agents consult research as reference material, not as an execution dependency; research being absent or customized must not break any skill.
