# Phase 09 — Quantify

Mechanical adoption-table generation for the breadth-then-depth methodology. The work is encoded as a script (`ocd-run log research quantify`) rather than agent instructions — adoption counts are deterministic given a stable sample corpus and a converged consolidated, so the operation belongs in code per Determinism by Default. This phase file exists for visibility in the enumerated sequence and to document invocation, idempotency, and re-run discipline.

## Variables

- {subject} — Research subject name (e.g. `mcp`)
- {subtopic} — Optional subtopic; single-subtopic auto-resolves; multi-subtopic must pass it
- {consolidated-file} — Optional. Auto-resolves to the single `_CONSOLIDATED*.md` in the samples directory; pass explicitly when multiple matches exist

## When to run

After `08-corrective-sweep` completes — at that point sample chain keys align with the depth-refined tree, and counts are accurate.

Re-run any time samples or consolidated tree shape change:

- After each `10-gap-audit` re-iteration cycle (samples may have shifted)
- After any manual sample rewrite or addition
- After any consolidated path rename, addition, or removal
- During development, freely — the script is idempotent and cheap

## What the script does

1. Walks the consolidated's role tree and identifies every branching point — any heading with 2+ direct heading children at the next level
2. For each branching point, queries `count_sections` to count samples exhibiting each child path's chain key
3. Computes coverage as `count / parent_total` — applicability-aware, so a 20-sample role doesn't dilute by 84 samples that don't have the role at all
4. Renders an adoption table per branching point, wrapped in `<!-- adoption-table -->` ... `<!-- /adoption-table -->` sentinels
5. With `--write`, inserts (or replaces) tables in the consolidated in place

## Idempotency

Re-runnable by design:

- Re-running on the same consolidated + sample set produces byte-identical output
- Re-running with updated sample counts replaces existing tables between sentinels — no duplication, no accumulation of stale tables, no manual cleanup needed
- Safe to bake into automation that fires whenever samples or the consolidated change
- The sentinel comments are the contract — agents and tools editing the consolidated must not strip them or insert content between them, because the script's replace logic relies on the sentinel pair

## Invocation

```bash
# Print tables to stdout (default; read-only inspection)
ocd-run log research quantify --subject {subject}

# Write tables in place into the consolidated (idempotent)
ocd-run log research quantify --subject {subject} --write

# Pass explicit consolidated path when auto-resolution can't disambiguate
ocd-run log research quantify --subject {subject} --consolidated <path> --write

# Use --dir instead of --subject for an explicit samples directory
ocd-run log research quantify --dir <path> --consolidated <path> --write
```

## Output

Each branching point gets a Markdown table inserted under its parent heading:

```markdown
<!-- adoption-table -->

Adoption — {N} samples exhibit `{parent-chain}`.

| Path                | Count | Coverage |
| ------------------- | ----: | -------: |
| {top-path}          |    23 |     22% |
| {next-path}         |    18 |     17% |

<!-- /adoption-table -->
```

The "Adoption — N samples exhibit..." line is the role's denominator (samples that exhibit the parent at all). Path-level percentages are computed against that denominator, not against the total corpus, so an 18-sample role's "85% coverage" path is informative even if the overall corpus is 104 samples.

## Notes

- This phase is the only one in the methodology not driven by an agent. The mechanical operation belongs in code
- The script must run from a checkout where the `ocd` plugin is installed and on the path (`plugins/ocd/bin/ocd-run` in this project)
- No structural changes to the consolidated — only tables are inserted or replaced. Descriptions, paths, role names, and prose are untouched
- After running, validate with `ocd-run log research check <consolidated-path>` to confirm no sibling-duplicate headings (the script does not verify; the user does)
