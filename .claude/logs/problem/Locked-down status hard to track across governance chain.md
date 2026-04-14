# Locked-down status hard to track across governance chain

Each rule, convention, and skill in the governance chain has a "locked-down" state meaning it has been systematically walked through against its current governors and verified coherent. The problem is that the status is not independent per file — it depends on what was updated when, and changes at one level invalidate downstream lock-down state.

## Scope

All rules, conventions, and skills that participate in the governance chain. Currently evaluated via manual walkthrough with the user; no systematic tracking.

## Complexity

The evaluation is inherently bottom-up and outwards:

- **Bottom-up** — a convention cannot be locked down until its governors (rules it `governed_by`s) are themselves locked down. A rule change invalidates the lock-down state of every convention that builds on it.
- **Outwards** — skills that consume a convention need re-verification when the convention changes. evaluate-skill and evaluate-governance both needed alignment after skill-md.md and evaluation-skill-md.md changed.
- **Re-lockdown on change** — any edit to a locked-down file potentially breaks the guarantee for everything above it. There's no automatic way to know what needs re-walking.

## Proposed direction

A skill or workflow that:

- Tracks locked-down status per file
- Detects when a governor changes after a dependent was locked down, invalidating the dependent
- Drives the re-walkthrough workflow in dependency order

This naturally fits the purpose-map evaluation workflow — the dependency DAG is already there, and purpose-map already tracks validated status on entities. But locked-down is finer-grained than validated: a validated component's governance might still need re-walking after a foundation changes.

Could be implemented as:

- A `locked_down_at` column on governance files with a commit hash reference
- Comparison logic that marks a file stale if any governor has a newer lock-down hash
- A report showing the next file ready to walk based on governor state
