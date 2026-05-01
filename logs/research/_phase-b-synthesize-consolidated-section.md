# Synthesize `_CONSOLIDATED.md` Section

Per-section synthesis instructions for populating `_CONSOLIDATED.md`. A spawned agent reads this file, finds the next unsynthesized `##` section in the target `_CONSOLIDATED.md`, pulls verbatim corpus content for that section's chain key, synthesizes findings, writes the synthesis into the section, and continues until context tightens or all sections are populated.

## Variables

- {subject} — Research subject name (e.g. `mcp`)
- {subtopic} — Optional subtopic name (e.g. `repos`); single-subtopic subjects auto-resolve, omit the flag in CLI calls; multi-subtopic subjects must pass it. Resolves to `logs/research/<subject>/<subtopic>-samples/`
- {sections-limit} — Optional integer; when set, agent processes at most this many sections then returns. Used to bound test runs
- {sections-completed} — Loop counter; initialized to 0 in Setup

## Process

### Setup

1. {sections-completed} = 0

### Orient

2. Read `logs/research/{subject}/{subtopic-or-discovered}-samples/_TEMPLATE.md` — canonical heading tree, sub-purpose vocabulary, and per-section purpose statements
3. Read `logs/research/{subject}/{subtopic-or-discovered}-samples/_CONSOLIDATED.md` — note which `##` sections are populated vs empty

> A section is **empty** when its `## Heading` is followed only by `###` sub-headings and blank lines (no body text at any depth) before the next `##` heading or EOF. A section is **populated** when it carries body text under any heading at any level.

### Select

4. Identify the first empty `##` section in `_CONSOLIDATED.md`
5. If no empty section: Return to caller: all sections populated
6. {section} = the section's heading text without the `## ` prefix

### Extract

7. bash: `ocd-run log research consolidate --chain "Sample > {section}" --subject {subject}` — append `--subtopic {subtopic}` only when the subject has multiple `<subtopic>-samples/` folders
8. {corpus} = stdout — every sample's content under that chain key, separated by `=== <filename> ===` markers

### Synthesize

9. Read {corpus} carefully — every sample's evidence for this section

> Goal: a synthesis a reader can scan to learn (a) which implementation paths dominate, with adoption counts; (b) which sub-purpose values are common vs rare; (c) which samples exemplify each pattern; (d) what outliers reveal about the design space; (e) where corpus practice tensions with authoritative documentation.

10. Identify named patterns — distinct implementation paths, design choices, or value clusters observed across the samples. Use canonical labels drawn from `_TEMPLATE.md`'s sub-purpose vocabulary where applicable; coin labels when the corpus surfaces a pattern the template doesn't name
11. Count adoption per pattern: `<count>/<denom>`. Denominator follows applicability — full sample (e.g. 104) for universal sub-purposes, applicable subset for conditional ones; state the denominator's basis in narrative when not the full sample. Worked example: a Python-specific path adopted by 32 of the 62 Python-carrying repos is recorded as `32/62` with narrative naming "62 = Python-primary + Python+TS-mixed"
12. Cite sample exemplars per pattern — filenames without path, comma-separated; cap explicit citation lists at ~5 representative entries when a pattern has many adopters
13. Surface outliers — samples that diverge from dominant patterns; name the divergence and what it reveals about the design space, not just the fact of difference
14. When the section has authoritative documentation prescribing a path (spec, SDK README, host docs): note alignment or conflict between docs and corpus practice

### Format

15. Section shape inside `_CONSOLIDATED.md`:

    ```
    ## {section}

    {One-paragraph framing under the section heading, before the first sub-purpose}

    ### {Sub-purpose 1 from _TEMPLATE.md}

    {Synthesis: dominant patterns, adoption table or distribution, narrative on outliers and tensions}

    ### {Sub-purpose 2}

    {...}
    ```

16. Adoption table format — default shape when the section reports implementation paths with authoritative-docs alignment (Transport, Distribution, Authentication, Python SDK / framework, etc.):

    ```
    | Implementation path | Docs | Adoption |
    |---|---|---|
    | <path>              | <★/☆/blank>  | <count>/<denom> |
    ```

    > ★ — explicitly prescribed by authoritative docs. ☆ — shown valid without endorsement. (blank) — docs silent; adoption is the only signal.

17. For descriptive sections (Identification, Repo layout, License, etc.) the three-column shape degenerates because there's no docs-prescribed path. Use whatever table or narrative shape best conveys the distribution — bucketed counts for skewed numerics (stars), license-vs-adoption two-column, dominant-vs-tail split, or pure narrative when no tabular form fits

18. Sections without natural sub-purpose structure (`## Notable structural choices`, `## Unanticipated axes observed`, `## Gaps`) take freeform body — bullets or short paragraphs. Skip the framing paragraph in those cases

### Write

19. Replace the empty `## {section}` block in `_CONSOLIDATED.md` with the synthesized content
20. Heading text and level remain unchanged — {section} appears verbatim as `## {section}`; canonical sub-purposes from `_TEMPLATE.md` appear verbatim as `### <sub-purpose>`
21. Verify compliance:
    1. bash: `ocd-run log research compliance --subject {subject}` — append `--subtopic {subtopic}` only when multi-subtopic
    2. If `Consolidated:` line reports outliers or order violations: revert the section's content; surface to caller — synthesis introduced a structural mismatch
    3. Else: section accepted

### Continue

22. {sections-completed} = {sections-completed} + 1
23. If {sections-limit} set and {sections-completed} >= {sections-limit}: Return to caller
24. If context budget feels constrained (~50% consumed): Return to caller
25. Else: Go to step 3. Read `_CONSOLIDATED.md` — re-read to find the next empty section

## Report when returning to caller

- **Sections synthesized this spawn** — ordered list of `## {name}` headings populated
- **Section abandoned mid-work** (if any) — heading and reason: context tight, source unconsumable (corpus too large for one synthesis pass), compliance failure (and which check failed)
- **Notable corpus observations** the orchestrator should know — patterns spanning multiple sections, outliers worth re-examining, template-revision concerns surfaced during synthesis
