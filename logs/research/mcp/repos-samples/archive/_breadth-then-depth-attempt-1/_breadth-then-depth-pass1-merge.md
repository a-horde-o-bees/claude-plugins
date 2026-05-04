# Pass 1 Phase 1b — Breadth-Then-Depth: Merge

Merger agent instructions for the breadth-then-depth methodology, parallel-then-merge mode. The merger reads N partial consolidateds (each produced by an isolated Pass 1 Phase 1a agent on its own bin of samples) and produces a unified consolidated. The merger does NOT re-read raw samples — partials carry citations, and `references` queries on-demand when verification is needed.

This same instruction set serves staged merging — Stage 1 half-mergers (input: raw partials → intermediate output) and Stage 2 final merger (input: intermediates → canonical unified consolidated) follow the same process.

## Variables

- {subject} — Research subject name (e.g. `mcp`)
- {subtopic} — Optional subtopic name; single-subtopic auto-resolves; multi-subtopic must pass it
- {input-partials} — Required. Ordered list of partial filenames to merge (e.g. `["_CONSOLIDATED_pass1-bin1.md", "_CONSOLIDATED_pass1-bin2.md", ...]`)
- {output-file} — Required. Filename to write the merged result to (e.g. `_CONSOLIDATED_pass1-merge-stage1-half-a.md` for an intermediate, or `_CONSOLIDATED_breadth-then-depth.md` for a final unified output)

## Process

### Orient

1. Read `logs/research/{subject}/{subtopic-or-discovered}-samples/_METHODOLOGY_breadth-then-depth.md` — the methodology is your operating philosophy; pay attention to Phase 1b's role description
2. Read each partial in {input-partials}, in order. Note the categorization choices each made — top-level axes, sub-tree shapes, naming vocabulary, where each placed cross-cutting observations

> Do NOT read raw sample files (`<entity>.md`). Partials carry the synthesis with citations; raw samples would duplicate evidence already represented and bust your context budget. Use `ocd-run log research references "<chain>" --subject {subject} --show-content` only when a specific claim needs verification (e.g. when two partials assign incompatible categorizations to the same sample and you need to inspect to arbitrate).

### Build a vocabulary map

3. Scan all input partials for equivalent concepts under different names:
    - `Auth` vs `Authentication` vs `Credentials`
    - `SDK / framework` vs `MCP framework` vs `Framework choice`
    - `Distribution channels` vs `Distribution mechanisms` vs `Package managers`
    - Any bin-specific neologism that's also expressed in another bin's vocabulary
4. Choose canonical names per concept. Prefer:
    - The form used by the most partials (frequency-weighted)
    - Conventional tooling vocabulary (e.g. `Authentication` over `Auth`)
    - The most descriptive form when frequency is tied
    - Match the original sample-template's heading text when the concept aligns (eases Pass 2 sample normalization)
5. Record canonical-name decisions in your report so the next merge stage (or downstream Pass 2) can audit

### Identify cross-bin patterns

6. Note axes that recur across multiple partials — these are high-confidence corpus-level axes:
    - An axis appearing in ≥3 partials is a load-bearing categorization; preserve as a top-level or near-top-level branch in the merged tree
    - An axis appearing in 1-2 partials is a candidate; preserve the path (per the methodology's "every distinct branching has a destination") but it may demote to a sub-branch
    - Axes that 1 partial promoted to top level but no others surfaced may be a single-bin overreach; consider demoting

7. Note recurring observation patterns — distinct partials surfacing the same finding from different samples:
    - Pattern X observed in 3+ samples across multiple bins is a high-confidence corpus claim
    - Pattern X surfaced by only 1 partial may be a singleton or may be a missed observation in others; preserve regardless

### Build the merged tree

8. Starting from the canonical-named axes, construct the merged categorization tree:
    - Each axis surfaces from one or more partials; its sub-branches are the union of distinct paths each partial assigned under that axis
    - Where two partials assign incompatible structures (e.g. one nests `SDK` under `Language`, another puts `SDK` at top level), prefer the more defensible categorization for the corpus and surface the alternative in the report. Frequency-weight the choice when defensibility is similar
    - Preserve every distinct **implementation path** any partial surfaced (tree structure) — even singletons. The methodology's "ensure a section exists for every possible branching" goal applies to STRUCTURE
    - **Aggressively deduplicate observation content (bullet-level)**. When multiple partials make the same observation about the same sample(s), produce ONE canonical bullet — pick the clearest phrasing, drop the alternatives. Union the citations. The goal is the smallest possible output that preserves the corpus's information; redundant phrasings of the same finding inflate the output without adding signal
    - Apply to: same observation about same samples (drop alternative phrasings), overlapping bullets that say the same thing (collapse to one), redundant cross-references (keep one canonical mention; drop secondary)

9. Resolve conflicts:
    - When two partials make incompatible claims about the same sample, use `references "<chain>" --show-content` to inspect the source. Pick the more accurate categorization
    - When two partials disagree on naming for the same concept, apply the canonical-name decision from step 4
    - When partials disagree on whether something is its own axis or a sub-branch of another, prefer the more granular treatment (split rather than absorb) unless one partial's reasoning is clearly stronger

### Preserve provenance

10. Every observation in the merged consolidated must cite one or more samples (using the same inline-backtick-citation form the partials use, e.g. `[`AlwaysSany--deepl-fastmcp-python-server`]`)
11. When merging chunks from multiple partials about the same observation, the citation list is the union of all citing samples across partials
12. If a partial cites a sample for an observation but you've decided to drop or relocate the observation, surface in the report — never silently lose a citation

### Write the merged output (incrementally — important)

The merged output may be large (~50-100KB or more). Generating that as one Write call risks stalling. Build the file incrementally instead:

13. **Initialize**: Use Write to create the output file at `logs/research/{subject}/{subtopic-or-discovered}-samples/{output-file}` with just the level-1 heading and a one-line preamble:

    ```markdown
    # Sample

    Pass 1 Phase 1b merge of {N} partials into {output-file}. See `_BINS.md` for input partials list.
    ```

14. **Append each top-level `##` section as a separate Edit call**. Use Edit with `old_string` matching the END of the file (after the previous section, or after the preamble for the first section) and `new_string` adding the new section content. Each Edit handles one `##` section's full subtree (one heading + all its `###` children + bullets/prose under each)

15. Use `# Sample` as the level-1 heading so chain keys align with samples and downstream consumers

16. Verify structure after each Edit: optionally run `ocd-run log research check logs/research/{subject}/{subtopic-or-discovered}-samples/{output-file}` after every 3-4 sections to confirm no sibling-duplicate headings sneak in

17. Final verification: after all sections written, `ocd-run log research check` on the output file must report no sibling-duplicate headings

## Report when returning to caller

- **Output filename** — the path you wrote to
- **Input partials processed** — list of partial filenames you read
- **Canonical-name decisions** — for each concept where partials used different names, the canonical chosen and the alternates dropped (with frequency or rationale). Audit trail
- **Cross-bin pattern recognition** — axes that recurred across multiple partials with frequency counts (e.g. "Authentication appears in 13/13 partials"; "Hosting responsibility appears in 4/13 partials"); observations that recurred across bins
- **Conflicts resolved** — places where partials disagreed and the choice made, with rationale
- **Singletons preserved** — branching paths surfaced by only 1 partial that were preserved per the methodology, with rationale
- **Singletons dropped or demoted** — branching paths from 1 partial that were demoted or absorbed, with rationale
- **Citations carried forward** — confirm no orphan citations (every cited sample in the partials has at least one citation in the merged output)
- **Notable corpus observations the next stage or Pass 2 should know** — methodology notes, vocabulary tensions, structural patterns worth elevating
- **Categorization decisions worth flagging** — places where you weren't sure about the merge, alternatives considered, oscillation risks for downstream merge stages or Pass 2
