# Phase 05 — Normalize

Per-bin agent instructions for the breadth-then-depth methodology's convergence cycles. Each agent reads the current consolidated + its bin of samples, rewrites each sample to align with the consolidated's role tree, and collects proposed refinements (new paths, sharper descriptions, missed buckets) in a refinement report. The reconciler (`06-reconcile.md`) integrates accepted refinements.

The phase goal is **convergence**: after one or more cycles, sample heading trees mirror the consolidated's role tree, so chain-key queries via `references` resolve cleanly. Sample content (the factual claims) is preserved; only the structure changes.

> **Dispatch default: sequential.** One bin at a time. See METHODOLOGY.md "Resource budgeting and dispatch" for budget calibration and the rationale for sequential default. Batch-parallel (3-4 concurrent) is opt-in when wall-clock matters and platform tolerance is known.

## Variables

- {subject} — Research subject name (e.g. `mcp`)
- {subtopic} — Optional subtopic name; single-subtopic auto-resolves; multi-subtopic must pass it
- {bin-id} — Required. Integer identifying this agent's bin
- {samples} — Required. Ordered list of sample filenames assigned to this spawn (same partitioning as Pass 1)

## Operating principles

These are the methodology's load-bearing principles for normalize. Re-read whenever in doubt.

**Preserve all factual content.** Each sample carries observable facts about its entity. Rewriting is structural, not editorial — no fact gets dropped, paraphrased into vagueness, or replaced with consolidated-style abstractions. If the sample says the server pins `fastmcp == 2.13.1`, the rewritten sample still says that. Move it under the right role/path; do not abstract it away.

**Mirror the consolidated's role tree.** The rewritten sample's level-2 headings are the consolidated's `##` roles; level-3 are its `###` implementation paths. Only include role/path nodes the sample actually exhibits — do not include empty nodes, "N/A" placeholders, or "not surfaced" notes. The absence of a role from a sample means that sample doesn't take any path under that role.

**One sample, one path per role.** A sample takes exactly one implementation choice per role (or none). If the sample reports two paths under the same role (e.g., supports stdio AND HTTP), include both as siblings — that's a real two-path observation, not a contradiction. The path is the choice; the sample documents which choice(s) it makes.

**Surface unmapped content as proposed refinements, not free-form sample content.** When a sample has factual content that doesn't fit any role/path in the consolidated:

- If the content fits an existing role but no existing path, propose a new path under that role
- If the content fits no role, propose a new role (rare — most novel content is a new path under an existing role)
- If the content sharpens an existing path's description (adds a constraint, edge case, or nuance the consolidated lacks), propose a description sharpening

Unmapped content goes in the refinement report, not in the sample file. Samples are evidence under the canonical tree; refinements update the tree.

**No inline citations in samples.** Each sample is about its own entity. It does not reference other samples. Cross-sample patterns are the consolidated's job; per-sample evidence is the sample's job. Each layer answers a different question.

**No cross-corpus phrasing in sample bodies.** Even without naming other samples, comparative phrases like "rare among X servers," "uncommon for an MCP server," "contrasts with most projects," or "unusual choice" are corpus-level claims smuggled into per-sample evidence. Strip them on sight — re-phrase as direct facts about this entity. "Rare among community MCP servers to use AGPL-3.0" becomes "uses AGPL-3.0 (network-copyleft)." The corpus-level interpretation lives in the consolidated's path descriptions; the sample documents what *this* entity does.

## Process

### Orient

1. Read `logs/research/breadth-then-depth/METHODOLOGY.md` — operating philosophy
2. Read `logs/research/{subject}/{subtopic-or-discovered}-samples/_CONSOLIDATED_breadth-then-depth.md` — the canonical tree your samples must mirror
3. bash: `plugins/ocd/bin/ocd-run log research sections logs/research/{subject}/{subtopic-or-discovered}-samples/_CONSOLIDATED_breadth-then-depth.md` — the role tree at chain-key granularity, useful as a reference

### Initialize the refinement report

4. Create `logs/research/{subject}/{subtopic-or-discovered}-samples/_pass2-bin{bin-id}-refinements.md` with this stub:

    ```markdown
    # Pass 2 Refinements — Bin {bin-id}

    Proposed refinements to `_CONSOLIDATED_breadth-then-depth.md` from rewriting samples in this bin. The reconciler integrates accepted refinements into the next consolidated revision.

    ## Proposed new paths

    > Format: `<role> > <new-path>` — supporting samples — qualitative description draft

    ## Proposed description sharpenings

    > Format: `<role> > <existing-path>` — what the existing description misses; supporting samples; sharpening suggestion

    ## Proposed new roles

    > Format: `<new-role>` — what role this is, why it doesn't fit any existing role, supporting samples

    ## Proposed bucket splits

    > Format: `<role> > <existing-path>` — why it should split, into what, supporting samples

    ## Structural concerns

    > Anything that's hard to fit cleanly under any role/path; questions for the reconciler
    ```

### For each sample in {samples}

5. Read `logs/research/{subject}/{subtopic-or-discovered}-samples/{sample}` in full
6. **Inventory the sample's factual content** — list every observable fact (language, framework, transport(s), distribution channel(s), auth mechanism, etc.). Do not skip facts you find redundant — every fact must be preserved or escalated to a refinement
7. **Map each fact to a role/path in the consolidated.** For each fact, ask:
    - Which role does this answer? (e.g., "Python with FastMCP" answers "Server runtime")
    - Which existing path under that role does this fact match? (e.g., "Python with FastMCP" already exists)
    - If no path matches, mark for refinement (new path or sharpening)
8. **Rewrite the sample** under the new tree shape:
    - Keep the level-1 heading: `# Sample`
    - Add a one-line preamble identifying the entity (e.g., `Mirrors of `<entity-url>`. <one-line description of what this entity does>.`) — preserves entity identification
    - For each role the sample exhibits: add a `## <role-name>` heading matching the consolidated's role exactly
    - Under each role: add `### <path-name>` headings matching the consolidated's path exactly
    - Under each path: write the sample's facts that demonstrate that path. Be concrete and specific — version pins, exact CLI flags, exact env var names, exact command shapes. Three sentences typical, more if the sample has rich detail
    - If the sample takes multiple paths under the same role, include each as a sibling `###`
9. **Surface refinements** in the refinement report:
    - Unmapped facts → new path or new role proposal (with the unmapped fact and the role it would fit under)
    - Facts that sharpen an existing path's description → description sharpening proposal
10. **No inline citations.** Do not write `` [`other-sample-name`] ``. Each sample stands alone

### Verify

11. After processing all samples in {samples}, run `plugins/ocd/bin/ocd-run log research check logs/research/{subject}/{subtopic-or-discovered}-samples/{sample}` for each rewritten sample — confirm no sibling-duplicate headings
12. Spot-check 1-2 rewritten samples: do the level-2 headings exactly match consolidated `##` role names? Do the level-3 headings exactly match consolidated `###` path names? If not, fix — the chain-key match is what makes `references` resolve

### Continue

13. After all assigned samples processed and refinement report written, return to caller

## Report when returning to caller

- **Refinement report filename** — the path you wrote to (`_pass2-bin{bin-id}-refinements.md`)
- **Samples rewritten** — list of filenames
- **Per-sample summary** — for each sample, one line: which roles it exhibits, total path count, any unusual structural choices
- **Refinements proposed** — counts: `{N} new paths, {N} description sharpenings, {N} new roles, {N} bucket splits`. The reconciler reads the refinement file for details
- **Convergence signals** — does this bin look "almost converged" (samples mostly map cleanly, few refinements needed) or "still divergent" (many unmapped facts, many proposed sharpenings)? Honest assessment shapes the orchestrator's decision on whether Pass 3 is needed
- **Categorization decisions worth flagging for the reconciler** — places you weren't sure about role boundaries; alternatives considered; judgment calls
- **Open questions** — sample content that didn't fit anywhere; instruction ambiguities
