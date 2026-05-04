# Pass 1 (Phase 1a) — Breadth-Then-Depth: Parallel Partials

Pass-1 Phase-1a agent instructions for the breadth-then-depth consolidation methodology, parallel-then-merge mode. Each agent works in isolation on its assigned bin of samples, writing to its own `_CONSOLIDATED_pass1-bin{N}.md` partial. The agent does **not** read the running consolidated or other agents' partials — Phase 1a's parallelism is the antidote to first-bin precedent locking in suboptimal vocabulary.

The pass goal is **coverage of branching paths**, not adoption counts. By the end of Pass 1 (after Phase 1b merge), every distinct implementation path observable across the corpus should have a destination chain in the consolidated, even if rare (1/N samples). Convergence is bilateral — both consolidated and samples evolve toward the best structural representation of global knowledge.

## Variables

- {subject} — Research subject name (e.g. `mcp`)
- {subtopic} — Optional subtopic name; single-subtopic subjects auto-resolve, omit in CLI calls; multi-subtopic must pass it
- {bin-id} — Required. Integer identifying this agent's bin (e.g. `2`). Determines the partial filename: `_CONSOLIDATED_pass1-bin{bin-id}.md`
- {samples} — Required. Ordered list of sample filenames assigned to this spawn (e.g. `["AlwaysSany--deepl-fastmcp-python-server.md", "Azure--azure-mcp.md"]`). Orchestrator bin-packed by file size. Each sample is assigned to exactly one Pass 1 agent — no two agents touch the same file in Pass 1

## Process

### Orient

1. Read `logs/research/{subject}/{subtopic-or-discovered}-samples/_METHODOLOGY_breadth-then-depth.md` — the methodology is your operating philosophy
2. **Do not read** `_CONSOLIDATED_breadth-then-depth.md` or any other `_CONSOLIDATED_pass1-bin*.md` partial. You're working fresh — your bin's partial is your private workspace. Phase 1b's merger agent will unify your partial with the others later

### Initialize your partial

3. Create `logs/research/{subject}/{subtopic-or-discovered}-samples/_CONSOLIDATED_pass1-bin{bin-id}.md` with a minimal stub:

    ```markdown
    # Sample

    Pass-1 Phase-1a partial for bin {bin-id}. Atomic knowledge chunks from {samples}, organized by divergence axes. Phase-1b merger will unify with other partials.
    ```

    Use `# Sample` as the level-1 heading so chain keys align with samples and the eventual unified consolidated.

### For each sample in {samples}

4. Read `logs/research/{subject}/{subtopic-or-discovered}-samples/{sample}` in full

#### Tree growth (primary goal)

5. Identify atomic knowledge chunks the sample carries — observable facts, named patterns, distinctive choices, branching observations
6. For each chunk:
    - **Find or create the right chain-key path** in your partial
    - If your partial already has a node at the right path (from an earlier sample in this same bin), write the chunk under that node. Mirror existing tone and shape (bullets if existing uses bullets; prose if prose)
    - If the partial lacks a destination, **create the right tree node** — add new `##`, `###`, etc. headings at the depth needed to capture the categorization
    - **Categorization principle**: when samples diverge at an implementation choice, the divergence becomes subsections under a common category. Parent heading captures the goal/purpose; children capture the alternatives
7. Cite the sample filename inline near the chunk (e.g. "[`AlwaysSany--deepl-fastmcp-python-server`]") so provenance survives the merge step in Phase 1b

> **Cross-section writes within your partial are the default, not the exception.** Knowledge belongs where it belongs in the tree, regardless of which sample surfaced it. Your bin assignment names which SAMPLES you SOURCE FROM, not where you can write within your own partial.

#### Sample rewriting (when obvious)

7. While processing each sample, evaluate whether reorganization is clearly beneficial. **Apply rewrites only for unambiguous cases**:

    **Apply (low risk, high confidence):**
    - Sample has a heading with non-canonical wording when the canonical exists in consolidated (e.g. sample says `## Setup`; consolidated has converged on `## Installation`). Rename
    - Sample has duplicate or near-duplicate content under different headings within itself. Merge under the canonical heading
    - Sample has structural errors that `ocd-run log research check <path>` would flag (sibling-duplicate headings). Fix per the conflict-resolution rule
    - Sample has empty sections (heading present, no body, no children). Remove
    - Sample's heading text uses inconsistent casing or punctuation when the canonical form is established (e.g. sample has `## installation`; canonical is `## Installation`). Normalize

    **Defer (ambiguous — flag in report, do not apply):**
    - Sample's content represents a NEW implementation path not yet in your partial. Add the path to your partial; do not restructure the sample yet (Pass 2 will handle after merge stabilizes the unified consolidated)
    - Sample's structure significantly diverges from your partial's emerging tree (multiple sections need restructuring, not just renaming). Note in report; Pass 2 normalizes
    - Categorization is genuinely ambiguous — multiple plausible homes for a chunk. Pick one, write the chunk, but flag the alternative in the report
    - Cross-sample inconsistencies you suspect but can't verify within your assigned subset. Flag in report; the merger or Pass 2 confirms

9. Maintain provenance: when you rewrite a sample, the structural change should preserve all knowledge content. If you're tempted to drop a chunk because it doesn't fit anywhere, instead add a node to your partial for it — every chunk has a home

### Verify

10. After processing all samples in {samples}, run `ocd-run log research diff --subject {subject} --consolidated logs/research/{subject}/{subtopic-or-discovered}-samples/_CONSOLIDATED_pass1-bin{bin-id}.md` (append `--subtopic {subtopic}` only when multi-subtopic). Confirm chain-key conventions hold within your partial
11. If `diff` reports something unexpected, surface in the report — don't try to silently fix

### Continue

12. After all assigned samples processed, return to caller

## Report when returning

- **Partial filename** — the path you wrote to (e.g. `_CONSOLIDATED_pass1-bin{bin-id}.md`)
- **Samples processed** — list of filenames; for each, a brief note (1-2 sentences) on what knowledge it surfaced
- **New chains created in your partial** — chain keys you added, with rationale (why this categorization, what existing chain it sits under)
- **Sample rewrites applied** — for each sample you rewrote, the change shape (e.g. "renamed `## Setup` → `## Installation`", "merged duplicate `## Tests` and `## Test Setup` content")
- **Sample rewrites deferred (Pass 2 candidates)** — sample filenames + 1-line reason per flagged sample
- **Categorization decisions worth flagging for the merger** — places you weren't sure how to categorize, alternative tree shapes considered, oscillation risks
- **Open questions** — knowledge chunks that didn't fit cleanly anywhere, sample-specific weirdnesses, instruction ambiguities
- **Notable corpus observations** — patterns spanning multiple samples in your bin, outliers worth re-examining, things the merger or Pass 2 should watch for
