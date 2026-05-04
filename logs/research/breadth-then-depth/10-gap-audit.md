# Gap Audit — Shallowness Detection (Opt-In)

Single agent that scans the converged consolidated and surrounding refinement reports for shallowness signals — places where the consolidated has weak understanding because the underlying samples don't carry enough detail to differentiate.

This phase is **opt-in**. It runs after quantify, identifies where understanding is shallow given the corpus we have, and produces a targeted re-research scope. The user reviews the scope and decides whether to invest another methodology cycle. Gap audit doesn't fix anything — it surfaces.

## Variables

- {subject} — Research subject name
- {subtopic} — Optional subtopic
- {consolidated-file} — Required. The post-quantify consolidated to audit
- {refinement-reports} — Optional. Pass 2/3 and depth refinement reports if still present (their "deferred for cause" entries are useful signal)

## Operating principles

**Surface, don't fix.** The audit produces a list of gaps. Closing them — re-research → re-run methodology phases — is a separate decision the user opts into.

**Distinguish "shallow because corpus is shallow" from "shallow because methodology hasn't run far enough."** The audit looks for the former. If the latter is suspected (paths still show structural tension), run another normalize cycle or depth pass first. Gap audit is the last gate, not a substitute for incomplete passes.

**Targeted scope, not corpus-wide.** Each gap finding names specific sample × dimension pairs. Downstream re-research is scoped to those pairs, not a full corpus re-crawl. The cost discipline is what makes gap audit affordable to opt into.

## Signals to scan

The audit reads the consolidated and surrounding refinement reports to surface:

- **Hedging language survival** — path descriptions with "not surfaced," "inferred," "likely," "appears to" that survived through the depth pass. Hedging that survives multiple passes signals samples don't carry the resolving evidence
- **Description-evidence asymmetry** — high-coverage paths whose description text is thin relative to their adoption count, or low-coverage paths with thick description (suggests evidence was captured shallowly relative to the path's importance)
- **Ambiguous reference content** — paths where `references "<chain>" --show-content` returns near-identical or generic content across supporting samples (suggests samples didn't carry differentiating detail at this dimension)
- **Quantification imbalances** — adoption tables where one path dominates with thin distinguishing evidence while sibling paths have richer evidence (suggests the popular path was sampled more shallowly than its long tail)
- **Carried-forward deferred refinements** — items in any reconciler's "deferred for cause" list that flagged "needs more sample evidence" (vs items deferred because they were single-bin idiosyncrasies)
- **Defer-markers (`↗`) accumulated in samples** — explicit signals from Phase 02 researchers that "this might matter, didn't go deep." A path's supporting samples each carrying `↗` on the same dimension is a high-confidence gap

## Process

1. Read {consolidated-file} and any present {refinement-reports}
2. Scan for each signal type above. Record findings with sample × dimension specificity
3. Group findings by suggested action:
    - **Targeted re-research** — researcher should re-investigate this dimension for these specific samples
    - **Accept-as-is** — the gap is real but small, and the consolidated's hedging communicates the uncertainty honestly
    - **Defer to ad-hoc** — the gap matters only when the user picks this implementation path and goes deep then; not worth a corpus-level fix
4. Write `logs/research/{subject}/{subtopic-or-discovered}-samples/_gap-audit.md` summarizing findings
5. Surface highest-impact findings in the report to the orchestrator

## Output

A `_gap-audit.md` report listing:

- Specific samples × dimensions with shallow coverage
- One-line rationale per finding
- Estimated re-research effort per finding (low/medium/high — based on entity research depth needed)
- Recommended action: targeted re-research / accept-as-is / defer to ad-hoc
- Aggregate cost estimate if user opts into the full re-research scope

## Re-iteration loop (opt-in)

If the user opts in to closing identified gaps:

1. Take the audit's targeted re-research scope
2. Route through `02-sample-population` — researchers re-investigate the named dimensions for the named samples (sequential, one sample at a time)
3. Re-run `03-gather` through `08-corrective-sweep` (incremental — most samples didn't change, so most phases run quickly on the changed subset)
4. Re-run `09-quantify` (script, idempotent)
5. Re-run `10-gap-audit`. If scope shrunk meaningfully, optionally loop again. If not, the corpus has been mined for what it can give

> Convergence threshold for the gap audit's loop: when re-iteration produces fewer than ~5 new high-impact findings, the corpus has been substantively mined. Further loops mostly trade tokens for marginal gains.

## Report when returning to caller

- Audit report filename
- Gap counts by signal type
- Top N highest-impact findings (one-line each)
- Recommended action: which findings (if any) merit a re-iteration cycle
- Estimated cost of re-iteration if user opts in
- Convergence assessment relative to prior gap audits (if any) — is the corpus's understanding still improving with each cycle, or are returns diminishing?
