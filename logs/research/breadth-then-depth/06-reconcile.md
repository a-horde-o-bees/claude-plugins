# Phase 06 — Reconcile

Single-agent reconciler instructions for the breadth-then-depth methodology. The reconciler reads N refinement reports (each produced by an isolated `05-normalize` agent or a `07-depth` agent) and integrates accepted refinements into a new revision of the canonical consolidated.

This same instruction set serves any reconciliation pass — runs after each normalize cycle or depth pass completes, produces an updated `_CONSOLIDATED_breadth-then-depth.md`.

## Variables

- {subject} — Research subject name (e.g. `mcp`)
- {subtopic} — Optional subtopic name; single-subtopic auto-resolves; multi-subtopic must pass it
- {refinement-reports} — Required. Ordered list of refinement-report filenames to process
- {consolidated-file} — Required. The canonical consolidated filename to update in place

## Operating principles

**Cross-bin agreement is the strongest signal.** When the same refinement (or substantially the same refinement) appears in multiple bins' reports, it has high cross-corpus support — accept it. When a refinement appears in only one bin, scrutinize: is it a corpus-wide pattern that just happened to surface there, or a one-sample idiosyncrasy that doesn't warrant tree change?

**Sharpening descriptions is cheap; restructuring is expensive.** Description sharpenings (adding a constraint, edge case, or nuance) integrate with low risk — they make the consolidated more accurate. New paths are moderate-cost — they expand the tree but don't disturb existing chain keys. New roles and bucket splits are high-cost — they change chain-key shapes and may invalidate already-rewritten samples. Apply low-cost refinements liberally; raise the bar for high-cost ones.

**No inline citations.** The consolidated stays qualitative. If any refinement proposal includes citations (legacy from earlier methodology versions or accidental sample naming), strip them during integration.

**Functional decomposition still rules.** When a refinement proposes a new role, verify it's actually a function (not a technology). When it proposes a new path, verify the path is named by its choice (e.g., "stdio" not "JSON-RPC over stdin/stdout").

**Convergence is the goal.** The point of reconciliation is to make the next Pass 2 cycle (if needed) propose fewer refinements. If you accept a refinement, the underlying samples should now map cleanly under the new tree. If accepting a refinement would just shift where the friction lives, surface it for discussion rather than applying.

## Process

### Orient

1. Read `logs/research/breadth-then-depth/METHODOLOGY.md` and `ARCHITECTURE.md` — operational reference and tree-shape overview
2. Read `logs/research/{subject}/{subtopic-or-discovered}-samples/{consolidated-file}` — the current canonical tree you'll be updating
3. Read each refinement report in {refinement-reports}

### Build the refinement queue

4. Aggregate refinements across reports into one queue. Group by type:
    - **New paths** — `<role> > <new-path>` proposals
    - **Description sharpenings** — `<role> > <existing-path>` proposals
    - **New roles** — `<new-role>` proposals
    - **Bucket splits** — `<role> > <existing-path>` proposals to split
5. For each refinement, count cross-bin support — how many bins independently proposed it (or substantially the same thing)? Record the count
6. For each refinement, classify cost:
    - **Low** — description sharpening
    - **Moderate** — new path under existing role
    - **High** — new role, bucket split, role rename

### Decide which refinements to apply

7. Apply all **low-cost refinements** (description sharpenings) by default unless they introduce contradictions. When two bins propose different sharpenings of the same path, integrate both nuances into one description if compatible; if incompatible, use `references "Sample > <chain>" --show-content --subject {subject}` to inspect the underlying samples and pick the more accurate
8. Apply **moderate-cost refinements** (new paths) when:
    - At least 2 bins propose substantially the same new path, OR
    - One bin proposes it but the new path captures meaningful corpus diversity (not an idiosyncrasy)
9. Apply **high-cost refinements** (new roles, bucket splits) when:
    - At least 3 bins independently surface the same need, AND
    - The current tree genuinely has no place for the content (not just "fits awkwardly")
10. Reject refinements that contradict accepted ones. Document the rejection in your report

### Apply accepted refinements

11. **Description sharpenings** — Use `Edit` to replace the existing description text with the sharpened version (which integrates the original plus the new nuance)
12. **New paths** — Use `Edit` to add the new `### <path>` section under the appropriate `## <role>`. Place alphabetically or in adoption-rank order (use Pass-1 stage-1 ordering as a guide; final order set in the quantification pass)
13. **New roles** — Use `Edit` to add the new `## <role>` section. Place at the end of the role list before "Cross-role tools" (which stays last)
14. **Bucket splits** — Replace the existing `### <path>` with two new `### <path-A>` and `### <path-B>` sections. Distribute the existing description text appropriately. Note that already-rewritten samples may now point to the wrong path — flag in your report so a corrective sweep can run
15. After every 5-10 edits, verify: `plugins/ocd/bin/ocd-run log research check logs/research/{subject}/{subtopic-or-discovered}-samples/{consolidated-file}` — confirm no sibling-duplicate headings

### Strip any citations

16. Verify no `` [`sample-name`] ``-style citations crept in via refinement proposals. Grep the consolidated; remove any found

### Compute convergence signal

17. Across all refinement reports, what fraction of refinements were applied vs deferred vs rejected? What does the bin-by-bin honest-assessment "convergence signals" field say? This is the input for deciding whether Pass 3 is needed

## Report when returning to caller

- **Consolidated updated** — confirm the file path
- **Refinements applied** — counts by type: `{N} sharpenings, {N} new paths, {N} new roles, {N} bucket splits`
- **Refinements deferred** — counts and rationale (insufficient support, conflicts with another refinement, etc.)
- **Refinements rejected** — counts and rationale (contradicts accepted refinement, would violate functional decomposition, etc.)
- **Cross-bin agreement examples** — 2-3 places where multiple bins surfaced the same need; high confidence in acceptance
- **Single-bin acceptances** — places where one bin's refinement was applied because it captured genuine corpus diversity; lower confidence; flag for Pass-3 verification
- **Bucket-split impact** — if any bucket splits applied, list the affected paths so a corrective sample-resweep can target them
- **Convergence assessment** — based on per-bin signals + applied/deferred ratio: is the corpus close to convergence (Pass 3 likely unnecessary), partially converged (Pass 3 will surface fewer refinements), or still substantially divergent (Pass 3 needed; tree shape may shift further)?
- **Notable corpus observations** — patterns surfaced by aggregating refinements that wouldn't be visible from any single bin
