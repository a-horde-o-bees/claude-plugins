# Synthesize `_CONSOLIDATED.md` Section

Per-section synthesis instructions for populating `_CONSOLIDATED.md`. A spawned agent reads this file, processes the explicitly-assigned chain keys in order, and returns when done. The orchestrator (calling context) bin-packs assignments under a context budget using `sections --size` data — agents have no introspection on context consumption, so work is divvied out at dispatch time, not self-paced.

## Variables

- {subject} — Research subject name (e.g. `mcp`)
- {subtopic} — Optional subtopic name (e.g. `repos`); single-subtopic subjects auto-resolve, omit the flag in CLI calls; multi-subtopic subjects must pass it. Resolves to `logs/research/<subject>/<subtopic>-samples/`
- {chains} — Required. Ordered list of chain keys to process this spawn (e.g. `["Sample > Language and runtime", "Sample > Transport"]`). Orchestrator computed via `sections --size` bin-packing; agent processes exactly these, in order, then returns

## Process

### Orient

1. Read `logs/research/{subject}/{subtopic-or-discovered}-samples/_TEMPLATE.md` — canonical heading tree, sub-purpose vocabulary, and per-section purpose statements
2. Read `logs/research/{subject}/{subtopic-or-discovered}-samples/_CONSOLIDATED.md` — confirm that each {chain} in the assignment list resolves to an empty `##` section

> A section is **empty** when its `## Heading` is followed only by `###` sub-headings and blank lines (no body text at any depth) before the next `##` heading or EOF. If an assigned chain's section is already populated, skip it and surface to caller in the report — do not overwrite.

### For each chain in {chains}

3. {chain} = next chain key from the assignment list
4. {section} = the chain key's leaf heading (e.g. `Language and runtime` for `Sample > Language and runtime`; `SDK / framework variant` for `Sample > Python-specific > SDK / framework variant`)

### Extract

5. bash: `ocd-run log research content "{chain}" --subject {subject}` — append `--subtopic {subtopic}` only when the subject has multiple `<subtopic>-samples/` folders
6. {corpus} = stdout — every sample's content under that chain key, separated by `=== <filename> ===` markers

### Synthesize

7. Read {corpus} carefully — every sample's evidence for this section

> Goal: a synthesis a reader can scan to learn (a) which implementation paths dominate, with adoption counts; (b) which sub-purpose values are common vs rare; (c) which samples exemplify each pattern; (d) what outliers reveal about the design space; (e) where corpus practice tensions with authoritative documentation.

8. Identify named patterns — distinct implementation paths, design choices, or value clusters observed across the samples. Use canonical labels drawn from `_TEMPLATE.md`'s sub-purpose vocabulary where applicable; coin labels when the corpus surfaces a pattern the template doesn't name
9. Count adoption per pattern: `<count>/<denom>`. Denominator follows applicability — full sample (e.g. 104) for universal sub-purposes, applicable subset for conditional ones; state the denominator's basis in narrative when not the full sample. Worked example: a Python-specific path adopted by 32 of the 62 Python-carrying repos is recorded as `32/62` with narrative naming "62 = Python-primary + Python+TS-mixed"
10. Cite sample exemplars per pattern — filenames without path, comma-separated; cap explicit citation lists at ~5 representative entries when a pattern has many adopters
11. Surface outliers — samples that diverge from dominant patterns; name the divergence and what it reveals about the design space, not just the fact of difference
12. When the section has authoritative documentation prescribing a path (spec, SDK README, host docs): note alignment or conflict between docs and corpus practice

### Format

13. Section shape inside `_CONSOLIDATED.md` depends on the chain's depth:

    **Top-level chain (e.g. `Sample > Language and runtime`)** — the leaf is a `##` heading; populate the whole section including framing and all sub-purposes:

    ```
    ## {section}

    {One-paragraph framing under the section heading, before the first sub-purpose}

    ### {Sub-purpose 1 from _TEMPLATE.md}

    {Synthesis: dominant patterns, adoption table or distribution, narrative on outliers and tensions}

    ### {Sub-purpose 2}

    {...}
    ```

    **Sub-purpose chain (e.g. `Sample > Python-specific > SDK / framework variant`)** — the leaf is a `###` heading; populate just that sub-purpose's body, leaving the parent `##` structure untouched:

    ```
    ### {leaf-heading}

    {Synthesis for this sub-purpose: patterns, adoption, exemplars}
    ```

    When sub-purpose chains for one parent are processed across multiple spawns, a separate wrap-up assignment may add the parent's framing paragraph at the end.

14. Adoption table format — default shape when the section reports implementation paths with authoritative-docs alignment (Transport, Distribution, Authentication, Python SDK / framework, etc.):

    ```
    | Implementation path | Docs | Adoption |
    |---|---|---|
    | <path>              | <★/☆/blank>  | <count>/<denom> |
    ```

    > ★ — explicitly prescribed by authoritative docs. ☆ — shown valid without endorsement. (blank) — docs silent; adoption is the only signal.

15. For descriptive sections (Identification, Repo layout, License, etc.) the three-column shape degenerates because there's no docs-prescribed path. Use whatever table or narrative shape best conveys the distribution — bucketed counts for skewed numerics (stars), license-vs-adoption two-column, dominant-vs-tail split, or pure narrative when no tabular form fits

16. Sections without natural sub-purpose structure (`## Notable structural choices`, `## Unanticipated axes observed`, `## Gaps`) take freeform body — bullets or short paragraphs. Skip the framing paragraph in those cases

### Write

17. Locate the heading in `_CONSOLIDATED.md` matching the chain's leaf (depth-2 `##` for top-level chains; depth-3 `###` for sub-purpose chains). Replace the empty block (heading + body up to the next sibling/parent heading) with the synthesized content
18. Heading text and level remain unchanged — verbatim from `_TEMPLATE.md` for both the leaf heading and any nested sub-purposes
19. Verify compliance:
    1. bash: `ocd-run log research compliance --subject {subject}` — append `--subtopic {subtopic}` only when multi-subtopic
    2. If `Consolidated:` line reports outliers or order violations: revert this chain's content; record the failure in the report; continue to the next chain in {chains}
    3. Else: chain accepted

### Continue

20. If more chains remain in {chains}: Go to step 3. Process next chain
21. Else: proceed to Report

## Report when returning to caller

- **Sections synthesized this spawn** — ordered list of `## {name}` headings populated
- **Section abandoned mid-work** (if any) — heading and reason: context tight, source unconsumable (corpus too large for one synthesis pass), compliance failure (and which check failed)
- **Notable corpus observations** the orchestrator should know — patterns spanning multiple sections, outliers worth re-examining, template-revision concerns surfaced during synthesis
