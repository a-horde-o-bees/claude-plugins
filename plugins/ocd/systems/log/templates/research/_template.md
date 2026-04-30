---
log-role: reference
---

# Research

Long-form investigation of a subject — an ecosystem, a population of artifacts, a design space — producing user-facing takeaways and agent-facing synthesis backed by per-entity samples and supporting context. Research accumulates under `logs/research/<subject>/` with one directory per subject.

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
- **Each purpose gets a section in the per-subtopic `_CONSOLIDATED.md`.** That doc reads purpose-by-purpose; samples are the evidence behind each purpose's section.
- **Per-purpose content** typically includes: observed paths with adoption counts against the applicable sample subset, per-entity citations, pitfalls, and — where relevant — docs-prescribed markers for paths the ecosystem's authoritative reference calls out.

`_CONSOLIDATED.md` aggregates within one subtopic. Cross-subtopic synthesis lives in `RESEARCH.md`. User-facing takeaways live in `ANALYSIS.md`. Supporting reference material lives in `context/`.

## Subject Directory Shape

```
logs/research/<subject>/
├── RESEARCH.md                    — agent-facing synthesis across all subtopics; form follows
│                                     findings (not bound to any single template)
├── ANALYSIS.md                    — user-facing takeaways derived from RESEARCH.md
├── context/                       — supporting sources (specs, docs, blogs, talks, papers,
│   │                                 datasets, code references); free-form body with minimal
│   │                                 frontmatter; see `_context-template.md`
│   └── <source>.md
├── <subtopic>-samples/            — template-structured examples of the target. May be one
│   │                                 folder (the common case); may be many when the research
│   │                                 needs distinct paths of inquiry with different shapes
│   │                                 that can't share a template
│   ├── _TEMPLATE.md               — canonical heading-tree shape for this subtopic
│   ├── _CONSOLIDATED.md           — heading-by-heading accumulation of supporting samples and
│   │                                 notes; mirrors `_TEMPLATE.md`; same compliance contract
│   │                                 as samples
│   └── <entity>.md                — per-sample entry; see `_samples-template.md`
└── <other-subtopic>-samples/      — when research needs distinct paths of inquiry
    └── ...
```

Single-subtopic case degenerates naturally: one `<subject>-samples/` folder, one `_TEMPLATE.md`, one `_CONSOLIDATED.md`. Multi-subtopic earns its keep when the research surfaces distinct inquiry paths whose samples have genuinely different shapes (e.g. studying both implementations and authoritative reference docs for the same domain).

## Subtopic Discipline

A subtopic is a path of inquiry with its own evidence shape. Split into subtopics when:

- The samples you'd collect for path A and path B require different `_TEMPLATE.md` headings — forcing them into one template loses information from one or both.
- The adoption-count denominators differ across the paths in a way that footnotes can't cleanly express ("5/26 TypeScript repos" vs "12/58 Python repos" tallied separately is cleaner than "5/X and 12/Y" with mid-table denominator switches).

Otherwise stick with a single subtopic. Most research subjects are single-subtopic.

## Context Discipline

`context/` is for supporting information sources outside of examples of the target — specs, SDK docs, blogs, talks, papers, datasets, code references, discussion threads. Files are not template-structured; each captures one source in whatever shape that source's value takes. Universal frontmatter (`source`, `captured`, `type`, `relevance`) provides citation and justification — see `_context-template.md`.

Context files do not feed cross-sample tallying. Their role is informing how `RESEARCH.md` interprets samples, surfacing prescriptions the corpus may or may not align with, and providing citations for `ANALYSIS.md`.

## Samples Discipline

Samples live under `<subtopic>-samples/<entity>.md` and each mirrors that subtopic's `_TEMPLATE.md` for cross-sample tallying. See `_samples-template.md` for per-sample entry structure.

## Tallying

Adoption counts in `_CONSOLIDATED.md` come from sampling the `<subtopic>-samples/` directory. A count of "14/54 repos declare non-trivial `userConfig`" is verifiable by scanning the relevant purpose section across all 54 sample files. Keeping sample structure consistent is what makes the counts defensible.

When a new purpose surfaces mid-research that samples didn't address, the refresh cycle:

1. Add the purpose section to each sample (or mark "not captured" when the sample file's research template didn't target it).
2. Tally across samples for the new purpose.
3. Update `_CONSOLIDATED.md`'s counts and citation pool.

`_CONSOLIDATED.md` mirrors `_TEMPLATE.md` heading-for-heading. The compliance verb checks both samples and `_CONSOLIDATED.md` against the same template, so both stay aligned as the template evolves.

## Heading-Tree Tooling

Cross-subject heading-tree analysis is provided by `ocd-run log research` verbs:

| Verb | Purpose |
|------|---------|
| `check <path>` | Verify one markdown file has no sibling-duplicate headings. Run before consolidating to catch heading collisions early |
| `count-sections --subject <name>` | Print chain-key coverage across the samples directory — which headings are near-universal vs rare |
| `consolidate --chain "<key>" --subject <name>` | Print every sample's content under one chain key (e.g. `Sample > Authentication > flow`). The unit of synthesis when authoring `_CONSOLIDATED.md` per purpose |
| `compliance --subject <name>` | Diff every sample (and `_CONSOLIDATED.md`) against `_TEMPLATE.md`. Surfaces outlier headings and reports order violations at every depth |

Run `compliance` after retrofitting samples or before tallying — it confirms the corpus matches the template's heading tree (the single source of truth for sample structure). Outliers under open-enumeration sections (marked by a `<placeholder>` heading in the template) are not flagged; they are the section's content vocabulary.

When `_CONSOLIDATED.md` is the goal, reach for `consolidate` per template section rather than reading every sample top-down. The output is bounded (one section's evidence at a time), grounded (returned content is verbatim from the samples), and composes naturally — each `consolidate` pass produces one section's worth of synthesized findings, ready to merge into the larger doc.

## Authoring `RESEARCH.md` and `ANALYSIS.md`

`RESEARCH.md` synthesizes across all subtopics' `_CONSOLIDATED.md` outputs and pulls in `context/` as evidence and background. Its shape is **form follows findings** — not bound to any single subtopic's template, since the cross-subtopic story may require headings that don't exist in any one subtopic.

`ANALYSIS.md` derives from `RESEARCH.md` and surfaces user-facing takeaways: when to apply the research, canonical shapes, gotchas, checklists. It is the artifact a downstream reader (a developer making a decision, a future research wave) consults first.

Both are agent-authored from the empirical layers below them. They are not places to record working state, hypotheses, or in-flight notes — those go in research-wave files at the subject root.

## Consuming Research

Research outputs are consulted when:

- Authoring a new pattern or methodology that should reflect ecosystem convention.
- Auditing the project's alignment against observed conventions (see `alignment-audit.md` pattern).
- Reassessing a decision whose underlying landscape may have shifted.

Reach for `ANALYSIS.md` first — it's the user-facing entry point. Descend into `RESEARCH.md` for the synthesis that backs it, into `<subtopic>-samples/_CONSOLIDATED.md` for per-purpose detail, and into individual samples or `context/` files when specific evidence or sources need to be cited.

Research is not loaded into session context by default — agents reach for it when the subject is relevant.

## Lifecycle

Semi-permanent — like decisions and patterns, research does not expire when "acted on." Research accumulates as long as it's referenced or extended. Update `_CONSOLIDATED.md` when new samples land; refresh `RESEARCH.md` when subtopic synthesis shifts; refresh `ANALYSIS.md` when takeaways change. Delete entire subjects only when the research is subsumed by a replacement or genuinely obsolete.

Users own deployed copies — they can edit, extend, or delete. Skills and agents consult research as reference material, not as an execution dependency; research being absent or customized must not break any skill.
