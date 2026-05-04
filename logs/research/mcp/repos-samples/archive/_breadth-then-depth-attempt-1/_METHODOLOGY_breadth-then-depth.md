---
log-role: reference
---

# Methodology — Breadth-Then-Depth Consolidation

How `_CONSOLIDATED_breadth-then-depth.md` is produced. Companion to that document; record of process, decisions, and limitations so the synthesis is auditable and reproducible.

## Goal

Consolidate "what we can learn from our samples" into a single document organized as an emergent categorization tree — one whose shape grows from corpus evidence rather than being prescribed by an upfront template. Atomic knowledge chunks live at the appropriate tree path; per-chunk provenance (which samples support each claim) is recoverable via the `references` verb.

The methodology supersedes the per-section-bins (template-prescribed) and parallel-batches (output-organization-prescribed) approaches archived alongside this file. It addresses their systematic blind spots — cross-cutting threads cut by section boundaries, rare findings buried in sectional density, canonicalizable fields drifting from corpus ground truth — by inverting the relationship: the corpus shapes the consolidated structure, not the other way around.

## Inputs

- The 104 per-sample files in `repos-samples/<entity>.md` — each shaped roughly to the original `_TEMPLATE.md` (now archived). The closeness of existing samples to the breadth-then-depth target shape speeds convergence
- CLI tooling: `sections`, `references`, `diff`, `check` verbs from `ocd-run log research`

**Excluded:**

- `archive/_TEMPLATE.md` — the prior template's structure does not constrain the new categorization tree; it is an artifact for reference only
- `archive/_CONSOLIDATED_*.md` — alternative-method outputs; their content does not seed the new synthesis. Closeness of sample shape (which the prior template imposed on samples during initial collection) is the only structural advantage transferred
- `archive/_METHODOLOGY_*.md` — alternative-method process records
- `_INDEX.md` — pre-aggregated index; its categorization is incidental, not authoritative

## Process

### Pass 1 — Gather (parallel-then-merge)

Goal: every implementation path observable across the corpus has a destination chain in the unified `_CONSOLIDATED_breadth-then-depth.md`. **Quantification is not the goal here — coverage of branching paths is.**

Pass 1 splits into two phases to avoid first-bin precedent locking in suboptimal vocabulary:

**Phase 1a — Parallel partials.** Multi-agent context-aware iteration with ~100K work-token budget per spawn (smaller than per-section-bins's ~200K to preserve synthesis quality). Each agent works in isolation:

1. Read assigned subset of samples (orchestrator-bin-packed by file size to fit budget)
2. **Do not read** the running consolidated — agent works fresh, with no first-bin precedent influencing categorization
3. For each sample, identify atomic knowledge chunks. Place each at the appropriate chain-key path in the agent's own `_CONSOLIDATED_pass1-bin{N}.md` partial, creating branches as needed
4. Cross-section writes are the default — knowledge belongs where it belongs in the agent's tree
5. Cite sample filename inline near each chunk (e.g. `[`AlwaysSany--deepl-fastmcp-python-server`]`) so provenance survives the merge step
6. Agent does not count or quantify
7. Run `ocd-run log research diff --subject mcp --consolidated <partial-path>` to confirm chain-key conventions hold against the agent's own partial
8. Report new chains created, sample rewrites applied/deferred, categorization decisions, open questions

After Phase 1a completes, the samples directory contains `_CONSOLIDATED_pass1-bin1.md`, `_CONSOLIDATED_pass1-bin2.md`, ..., `_CONSOLIDATED_pass1-bin{N}.md` — each a fresh take on the corpus.

**Phase 1b — Merge.** A single merger agent (or a small chain) reads all `_CONSOLIDATED_pass1-bin*.md` partials and produces unified `_CONSOLIDATED_breadth-then-depth.md`. Merger does **not** re-read raw samples — partials carry citations, and the merger trusts those. Where it needs verification, the `references` verb queries on demand.

Merger's task:
- Identify equivalent concepts across partials (`Auth` vs `Authentication` — same concept, different vocabulary)
- Choose canonical names (highest-frequency wording across partials, or canonical tooling vocabulary like `Authentication`)
- Combine sub-trees, preserving every distinct branching path that any partial surfaced
- Detect cross-bin patterns the parallel agents could not see (a pattern that recurs across 5 bins is high-confidence even if no single bin saw 5 instances)
- Resolve conflicts (when two partials categorize the same observation differently, choose the more defensible categorization and surface the alternative in a methodology note)
- Preserve all citations from the partials

After merge, Pass 1 ends with a unified consolidated whose tree shape reflects the corpus broadly, not any single bin's first-touch. Partials are archived (or deleted) in cleanup.

### Pass 2+ — Normalize (tree convergence)

Goal: bring samples and the consolidated into mutual consistency. Each pass: agents read samples + current `_CONSOLIDATED_breadth-then-depth.md`, rewrite samples to match the converging tree where appropriate, deepen consolidated where divergence surfaces. Same context-aware iteration with ~100K budget.

Per-spawn agent flow:

1. Read full `_CONSOLIDATED_breadth-then-depth.md` (current state)
2. Read assigned subset of samples
3. For each sample:
    - Use `diff` (or its data) to identify chain keys present in the sample but not in consolidated, and vice versa
    - Rewrite sample sections to match the consolidated's converging tree when the consolidated already has the right destination
    - When the sample surfaces a knowledge chunk the consolidated does not yet have a node for, add the node to consolidated
    - When the consolidated's tree shape no longer fits how knowledge actually divides in the corpus, restructure the consolidated's tree
4. Run `diff` after the spawn — fewer growth candidates and zero rewrites in a pass signals convergence

**Convergence detection (mechanical):** the orchestrator snapshots the consolidated's chain-key set before and after each pass. Convergence is reached when:

- No new headings added to consolidated this pass
- No samples rewritten this pass (verifiable by file mtimes or git diff)

If either happens, run another pass. The process must be followed to completion — there is no per-pass budget cap; the methodology converges on quality, not on time.

### Final pass — Quantify

Goal: add adoption tables to every branching subheading. A branch is a `##` or `###` heading whose direct children represent mutually-exclusive (or commonly-divergent) implementation paths.

This pass uses `references --count` (and where useful `references --show-content`) to count adoption per leaf chain across all samples. Per-section sweep similar to per-section-bins method but applied to the converged tree, not a prescribed template.

Output: `_CONSOLIDATED_breadth-then-depth.md` with adoption tables under every branching node. Each row of a table is one of the branch's children with `<count>/<denominator>` adoption and a citation list of representative samples.

## Tooling

| Verb | Purpose |
|------|---------|
| `sections [--subject N] [--count] [--size]` | Chain-key tree across samples; `--count` and `--size` add columns for adoption and byte size |
| `references "<chain>" [--subject N] [--count] [--size] [--show-content]` | List samples containing a section at the chain path. `--show-content` includes bodies; the knowledge-chunk → samples reverse index |
| `diff [--subject N] [--consolidated <path>]` | Diff sample heading trees against the running consolidated. Surfaces growth and pruning candidates. Use to scope each pass's work and detect convergence |
| `check <path>` | Verify a markdown file has no sibling-duplicate headings (structural correctness) |

## Strengths (vs archived alternatives)

- **Cross-cutting threads natural** — knowledge chunks find their right home in the categorization tree without per-section silos
- **Rare findings preserved** — Pass 1's "ensure every branching has a destination" goal surfaces every distinct implementation path including 1/N ones
- **Provenance explicit** — `references` is the reverse index from a chain (a claim, a pattern, a path) to its supporting samples
- **Tree shape matches corpus** — no template-vs-corpus mismatch to reconcile; the consolidated's structure is the corpus's structure
- **Reader navigation** — atomic knowledge under a categorization tree, not a 1500-line prose document; readers descend to the depth they need

## Limitations / when not to use

- **Pass count not bounded** — convergence may take many passes; cost compounds. Unsuited when budget is tight or the corpus is unstable (samples actively being added or rewritten during synthesis)
- **Categorization arbitration** — when two passes' agents disagree on tree shape, there is no automatic arbitration; later passes may oscillate. Mitigated by reading the full consolidated as input and biasing toward extension over rewholesale-rewrite
- **Quantification deferred** — gathering and normalizing passes operate without quantification. Stakeholders wanting early "what's the dominant path" answers must wait for the final pass
- **Tree depth unmoderated** — the methodology trusts the corpus to self-limit; if the corpus carries genuinely deep recursion, the consolidated will too, with reader-fatigue cost

## When to use

- When the corpus has genuine cross-cutting design axes that template-prescribed methods would cut into pieces
- When per-claim provenance matters (the `references` reverse index is load-bearing for downstream users)
- When the research budget allows multiple passes (no hard cap on total spawns)
- When building a knowledge artifact that future samples will extend — the emergent tree shape is durable across corpus growth
