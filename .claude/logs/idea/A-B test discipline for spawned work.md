# A-B test discipline for spawned work

## Purpose

When running an A/B test or any workflow that spawns background agents, explicitly terminate or resume them before pivoting focus. Observed during the evaluate-governance workflow A/B test on 2026-04-13: two agents were spawned for level 0 findings, the session then pivoted to the update-system-docs design work, and the A/B test agents were never resumed or explicitly closed out. The partial findings were left unrealized.

## Direction

A lightweight discipline for any session that spawns long-running work:

- Declare the spawned work's termination condition up front — either a success criterion (wave complete) or an explicit abandonment (pivoted, no longer needed)
- On pivot: decide between continue, pause (capture state, resume later), or terminate (release resources)
- Never leave orphaned agents as a silent byproduct of context shifts

This is already partially addressed by the `research-and-design` skill's Cleanup step, which terminates spawned work at session end. For ad-hoc spawned work outside that skill, the discipline is a project-level habit rather than a skill mechanism.

## Scope

Observed in this project's workflow. Not specific to a single file or artifact. The principle belongs in CLAUDE.md operational procedures if it crystallizes; for now, capture as idea pending a more concrete direction.
