# Promote helper-centralization to architecture or rule

The Helper Centralization pattern (`logs/patterns/helper-centralization.md`) was discovered and applied during the needs-map migration: when two systems duplicate orchestration, extract it to a `tools.*` helper that mirrors an existing helper pattern (`setup.deploy_files`). The pattern is now documented but lives only in the patterns log — agents authoring new systems may not consult it before adding orchestration code.

## Proposed shapes

Three possible homes, from lightest to heaviest:

**Pattern only** (current state) — the pattern log captures the discipline; agents who consult patterns when planning will find it. Doesn't fire automatically.

**Architecture mention** — `plugins/ocd/ARCHITECTURE.md` (or the parent `ARCHITECTURE.md`) gets a short subsection under "Shared Infrastructure" describing the centralized-helper discipline as a structural principle: the project converges on `setup.deploy_files`-shaped helpers when systems duplicate orchestration. References the pattern log for depth. Adds a place new-system authors look first.

**Design principle** — promote to a project-level rule under `plugins/ocd/systems/rules/templates/design-principles.md`, e.g. as a case bullet under *Reuse Before Create* or as its own principle:

> **Helper Centralization.** When two systems duplicate orchestration of existing primitives, extract the orchestration into a `tools.*` helper that mirrors the closest existing pattern. Each system declares; the helper resolves. New systems adopt the helper rather than re-implementing the flow.

This would fire on every pre-add review of new system code — strongest enforcement.

## Tradeoffs

- Pattern-only is current discipline; lightweight but easy to miss
- Architecture mention surfaces it during reading-for-orientation but not at code-write time
- Design principle fires every time the agent considers writing orchestration in a new system; may produce false-positive "should I extract this?" pauses on legitimately-unique flows

The heaviest bar (rule) seems right for "extract when two systems duplicate" because the failure mode (a third duplication shipping before someone notices) compounds. Lighter bars trade enforcement for less ceremony.

## Adjacent

- *Reuse Before Create* (existing rule) — overlaps; helper centralization is a specific application of "check what exists before building new." Could fold in as a case bullet rather than a standalone principle.
- *DRY* (well-known anti-duplication discipline) — different scope; DRY is line-level, this pattern is orchestration-level.

## Origin

Surfaced and applied during the needs-map migration sandbox (PR #8). User framed the convergence question: "we already converged on helpers for files; we hadn't for DBs?" That reframing was the move that made the helper extraction obvious. Codifying the pattern means the same reframing happens automatically the next time two systems duplicate orchestration.
