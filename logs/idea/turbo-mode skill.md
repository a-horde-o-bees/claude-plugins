# turbo-mode skill

A skill that asserts an aggressive parallelism stance: take every opportunity where spawning multiple agents leads to faster results.

## Context

Default agent behavior is sequential — read, analyze, edit, repeat. Many sessions surface natural fan-outs (per-file audits, per-skill evaluations, parallel research probes, multi-target refactors) where the work decomposes cleanly into independent parts. Without an explicit prompt, the agent often defaults to serial execution because each per-item step looks small in isolation.

`turbo-mode` would be a stance switch: while active, before any multi-item operation, the agent must consider whether spawning N parallel agents is faster than processing serially, and prefer parallel when items are independent.

## Approach sketch

- Activates as a session-scoped mode (`/turbo-mode on` / `off`)
- Adds a stance to the agent's context: "Before processing N items serially, ask: are they independent? If yes, spawn N agents in parallel"
- Surfaces the cost trade-off (multi-agent token usage vs wall-clock savings) when N is large
- Complements existing per-skill agent-spawning prescriptions; doesn't override them, just biases ad-hoc work toward parallelism

## Open questions

- Does this belong as a stance/mode, a rule bullet under design-principles' Agents section, or a skill?
- How does it interact with the `Agents` rule in workflow.md ("Minimize agent count for ad-hoc work")? That rule pushes the opposite direction. Need to reconcile — maybe turbo-mode is the explicit override for cases where wall-clock matters more than token cost.
