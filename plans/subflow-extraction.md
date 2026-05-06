# Sub-flow extraction sweep

Identify workflow components that run only on conditional paths and extract them into separate files (`workflows/<sub>.md` or `components/<sub>.md`) so callers that don't traverse the path never load the content. Same on-demand discipline the conditional-memory plan targets, applied at workflow-component granularity within a single skill or system.

## Goal

Skills and workflows load only the content their actual execution path traverses. Optional sub-flows, conditional reference blocks, and path-specific procedure live in extracted files invoked via `Spawn:` or `Call:` rather than embedded inline.

## Output

Per-skill / per-workflow edits across the project:

- Long workflow files with conditional branches → branches extracted into `workflows/<sub>.md`
- Reference blocks consumed only on certain paths → extracted into `components/<topic>.md`
- SKILL.md files that bundle entire dispatch logic + every verb's body inline → verbs extracted into per-verb workflow files (the `/ocd:git` skill is the canonical pattern)

## Sequence

1. Audit pass — identify workflow files with substantial branching. Candidates: setup orchestration component files, audit-* skills (currently in sandbox), evaluation workflows
2. Extract per the patterns in `system-structure.md` *Extraction criteria*: consumer profile narrows, path-conditional content, mixed access patterns
3. Update callers to `Spawn: Call:` (isolated agent context) or `Call:` (caller's context, on-demand) per the workflow's needs
4. Verify reduction in baseline load by inspecting `/context` before and after on representative invocations

## Decisions

- Extraction is consumer-fit-driven, not size-driven (per `principle-not-symptom.md`)
- Mandatory sub-flows that run on every invocation stay inline; extraction saves no context when the caller always reads them
- `Spawn: Call:` over `Call:` when the sub-flow is autonomous enough to dispatch to an isolated agent — keeps caller context clean

## Open questions

- Some skills may not have substantial branching to extract — that's fine; the sweep is opportunistic, not mandatory
- Component files vs sub-workflow files: a sub-flow is procedural (steps in order); a component is reference (look up a fact). Mixing them in one extracted file misses the point — split per access pattern

## Status

Not started. Lands during system migrations and skill maintenance; a focused sweep can fill remaining gaps after migrations settle.
