# Co-Equal Evidence Deconfliction

Reconcile two artifacts that purport to define the same structure — template + samples, schema + production data, API contract + actual usage, architecture docs + implementation — by treating them as co-equal evidence rather than authority + subject. Inventory each independently, compute the structural diff, categorize each delta with explicit rationale, and produce a canonical structure plus (optional) migration manifest. Default-privileging either side inserts bias and buries real findings.

## Why this shape

When two artifacts define the same structure, the temptation is to anchor on one and conform the other. The doc-anchored stance ("the schema is canonical; fix the data") buries cases where production discovered patterns the schema should anchor. The data-anchored stance ("the code is reality; infer the doc") loses structural intent encoded by the original authors. Both stances are bias dressed as decision-making — the choice should be evidence-driven, per delta, not blanket.

Co-equal treatment changes the framing from "which one is right" to "where do they disagree, and why" — which produces a better master and a smaller, conscious migration.

## Pattern

```
1. {artifact_a} = the prescriptive artifact (template, schema, contract, docs)
2. {artifact_b} = the descriptive artifact (samples, data, usage, code)

> Inventory phase. Each artifact is read on its own terms.
> Imposing one onto the other during inventory is the bias step
> we are explicitly avoiding.

3. {inventory_a} = structural fingerprint of artifact_a
    - For schemas: {fields, types, constraints}
    - For templates: heading tree, required sections, ordering
    - For contracts: endpoints, methods, status codes, parameters
4. {inventory_b} = same structural fingerprint applied to artifact_b
    - For data: observed fields per record, observed null rates, observed types
    - For samples: heading trees per sample, coverage map
    - For usage: actually-called endpoints, observed request/response shapes
    - For code: implemented endpoints / methods

> Diff phase. The diff is the conversation surface.

5. {diff} = symmetric difference between inventory_a and inventory_b
    - In A only — prescribed but unused
    - In B only — present but unprescribed
    - In both with shape mismatch — drift requiring naming

6. For each {delta} in {diff}:
    1. {category} = classify the delta:
        - **Over-specified** — A prescribed something B never adopted; remove from A
        - **Discovered** — B uses something A doesn't anchor; add to A
        - **Drift** — both have it but shape differs; reconcile (rename, retype, restructure)
        - **Vestigial** — neither still needs it; delete from both
        - **Legitimate variance** — A is canonical, B has corpus-specific extension; keep both, document
    2. {rationale} = short prose for why this category fits this delta

> Synthesis phase. Outputs are the master + the operations to converge.

7. {master} = canonical structure — A's structure with deltas applied per category
8. {migration_manifest} = ordered list of operations to bring B in line with master
    - Renames, moves, consolidations, additions
    - Empty manifest is a valid outcome (master = A; B already conforms)

> Apply phase. Mechanical when the manifest allows; agentic when content
> needs to follow structure.

9. Apply migration_manifest to bring artifact_b into structural conformance
10. Where structural changes require content judgment (e.g., section content reflowing into a renamed parent), defer to human or scoped agent — do not auto-rewrite content as part of structural migration
```

## Decision points are the artifact

The diff isn't an intermediate — it's the canonical record of what was reconciled and why. Save it. The migration manifest is downstream of it; the master structure is downstream of it; future deconfliction passes consume it as prior art. Without the diff written down, the next deconfliction has to re-derive every category, which loses institutional memory of "we considered removing this and decided to keep it because Y".

## When to use

- Two artifacts describe the same structure but were authored at different times by different processes
- Either side might have meaningful deltas the other doesn't anchor
- The cost of running deconfliction is lower than the cost of accumulated drift
- A migration step is plausible — i.e., bringing artifact_b in line with the master is a real outcome, not an academic exercise

## When NOT to use

- One artifact is *generated* from the other (schema → migrations; OpenAPI → SDK; protobuf → bindings) — the source is canonical by construction; deconfliction reduces to "regenerate"
- The artifacts describe different scopes that happen to overlap — they aren't co-equal evidence, they're parallel concerns
- The diff is empty or trivially small — overhead exceeds value
- Either artifact is so large the inventory cost dominates — sample first, deconflict on the sample, generalize cautiously

## Anti-patterns this prevents

- **Doc supremacy.** "The architecture says X; the code is wrong; fix the code." Sometimes the code is wrong. Sometimes the architecture missed a real constraint. Co-equal treatment surfaces which.
- **Code supremacy.** "The code is reality; rewrite the docs to match." Loses authorial intent and design rationale; regresses to documentation-as-stenography.
- **Mass overwrite without inventory.** Running the migration without inventorying first means delta categorization happens implicitly, in code review, after the fact. Inventory + diff + categorize is the cheap step that prevents expensive churn.
- **Conflating drift with bug.** Drift is the system telling you the spec missed a case. Treating every drift as a bug to squash discards real signal.

## Operational notes

- **Parallel inventory is fine.** A and B are independent; agents or processes can inventory both concurrently without coordination.
- **Drift categorization needs human judgment in most cases.** Mechanical detection of deltas is cheap; categorizing them ("is this over-specification or is this just variance worth preserving?") usually isn't.
- **Empty migration manifests are wins.** If deconfliction produces zero migration ops, you've confirmed the artifacts already agree — that's a meaningful audit result, not a wasted pass.

## See also

- `logs/research/_TEMPLATE.md` (and corpus templates) — example of artifact_a in the research domain
- `logs/research/<subject>/samples/` — example of artifact_b in the research domain
- `plugins/ocd/systems/log/research/_sample_tools.py` — `count_sections` and `consolidate_section` are the inventory primitives for markdown heading trees
- `pattern:context-aware-iteration` — how to run inventory at scale when the corpus exceeds a single agent's budget
