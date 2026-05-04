# Phase 07 — Depth Pass

Per-role agent instructions for the breadth-then-depth methodology. Each agent receives ONE branching role from the converged consolidated and inspects all the supporting sample evidence at once. Where `03-gather` and `05-normalize` work per-bin (8 whole files at a time), this phase works per-role across the corpus — the agent sees every sample's content under a single role, side-by-side, and refines the role's path descriptions based on cross-corpus comparison. The reconciler (`06-reconcile.md`) integrates depth-pass findings.

The phase goal is **description sharpening that the per-bin lens couldn't surface**: nuance from comparing all 23 implementations of a path, mis-placements visible only when path exemplars are stacked, sub-axes that emerge from cross-corpus patterns. Structural changes (new roles, bucket splits) remain rare.

> **Dispatch default: sequential.** One role at a time. Each agent's measurement informs the next. See METHODOLOGY.md "Resource budgeting and dispatch" for budget calibration. Batch-parallel (3-4 concurrent) is opt-in when wall-clock matters; per-role evidence size varies, so calibration discipline within a batch is essential.

## Variables

- {subject} — Research subject name (e.g. `mcp`)
- {subtopic} — Optional subtopic name; single-subtopic auto-resolves; multi-subtopic must pass it
- {role-chain} — Required. Chain key for the role to inspect (e.g. `Sample > Authentication`). The agent inspects all paths under this role
- {consolidated-file} — Required. Filename of the canonical consolidated to read

## Operating principles

**Cross-corpus inspection is the new lens.** Pass 1/2/3 saw samples per-bin; this pass sees one role across all samples. Use that visibility — patterns that span 5+ samples but were never co-located in any bin should surface here.

**Refine descriptions; don't restructure.** The tree shape converged across Pass 1/2/3. New roles, bucket splits, and major reorganizations require strong evidence — single-sample idiosyncrasies don't justify restructuring at this stage. Description sharpening is the primary output.

**Mis-placement detection.** Some samples may be placed under a path that's a poor fit, visible only when other path exemplars are inspected. Surface these in the report — the reconciler decides whether to move them or keep with description adjustment.

**Sub-axis recognition.** Within a single path, samples may cluster into sub-patterns (e.g., "stdio with stdout-clean discipline" vs "stdio without"). If the cluster is large enough across the corpus (3+ samples each), surface as a sub-axis or proposed bucket split.

**Don't fabricate.** If a sample's content doesn't surface a particular fact, don't infer it from neighboring samples. Refinements must be grounded in observable evidence from the inspected samples.

## Process

### Orient

1. Read `logs/research/breadth-then-depth/METHODOLOGY.md` — operating philosophy (skim; you've likely seen it)
2. Read `logs/research/{subject}/{subtopic-or-discovered}-samples/{consolidated-file}` and locate the section at {role-chain}. Note:
    - Role-level description (the prose under `## <role>` before the first `### <path>`)
    - Each path's heading and description
    - The adoption table (current counts per path)

### Pull cross-corpus evidence per path

3. For each `### <path>` under {role-chain}:
    - {path-chain} = `{role-chain} > <path-text>`
    - bash: `plugins/ocd/bin/ocd-run log research references "{path-chain}" --subject {subject} --show-content`
    - The output is `=== <sample-name> ===`-delimited blocks: each supporting sample's section content for that path
4. Read every supporting sample's content for every path under this role. The total content is bounded by the role's footprint — a sweep, not an open-ended dive

> Don't pull content for paths with zero supporting samples; nothing to inspect

### Compare descriptions to evidence

5. For each path:
    - Does the description capture the path accurately for ALL supporting samples? Or does it favor one or two and miss nuance from others?
    - Are there constraints (transport implications, auth dependencies, etc.) the description states but the samples don't actually exhibit, or vice versa?
    - Is there a sub-axis the samples cluster around that the description ignores?
    - Are there mis-placed samples — exemplars that fit a sibling path better?
6. Compare paths to each other within the role:
    - Are sibling paths describing genuinely distinct alternatives, or are two paths the same choice with different framing? (Bucket merge candidate)
    - Should one path split into two because its samples cluster into two distinct patterns?

### Initialize refinement report

7. Create `logs/research/{subject}/{subtopic-or-discovered}-samples/_depth-{role-slug}-refinements.md` where {role-slug} is a lowercase-hyphen form of the role name (e.g., `server-runtime`, `authentication`):

    ```markdown
    # Depth Pass Refinements — {role-chain}

    Per-role cross-corpus refinement proposals from inspecting every sample's content under this role.

    ## Description sharpenings

    > Format: `<role-chain> > <path>` — what the existing description misses; cross-corpus evidence; sharpened text suggestion

    ## Sub-axis observations

    > Format: `<role-chain> > <path>` — sub-pattern observed; supporting sample count; whether to fold into description or propose split

    ## Proposed bucket merges

    > Format: `<path-A> + <path-B>` — why same; supporting samples; canonical name suggestion

    ## Proposed bucket splits

    > Format: `<role-chain> > <path>` — why split; into what; supporting sample distribution

    ## Mis-placed samples

    > Format: `<sample-name>` currently under `<path-A>` better fits `<path-B>` because <evidence>

    ## Cross-corpus observations

    > Patterns visible only with full role visibility — surface even if not actionable now
    ```

8. Populate the report with what you found. Keep proposals concrete — exact text suggestions for sharpenings, exact sample names for moves

### Verify and return

9. The depth pass does NOT modify the consolidated or samples directly. The reconciler integrates accepted refinements
10. Return to caller with the report filename and a convergence assessment

## Report when returning to caller

- **Refinement report filename** — the path you wrote to
- **Role inspected** — the role-chain
- **Paths inspected** — counts: `{N} paths total, {M} with supporting samples`
- **Sample evidence consumed** — total bytes pulled across paths
- **Refinements proposed** — counts by type: `{N} sharpenings, {N} sub-axes, {N} merges, {N} splits, {N} mis-placements`
- **Convergence signal** — does the role look "well-described after Pass 3" (depth pass surfaces mostly minor tweaks) or "under-described" (depth pass surfaces meaningful gaps)? Honest assessment shapes whether the depth pass was worth the cost
- **Most-impactful finding** — the single refinement most likely to improve the consolidated, with one-line rationale
- **Categorization decisions worth flagging for the reconciler** — judgment calls; alternatives considered
- **Notable corpus observations** — patterns surfaced by cross-corpus visibility that the per-bin lens didn't show
