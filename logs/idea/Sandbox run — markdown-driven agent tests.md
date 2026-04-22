# Sandbox run — markdown-driven agent tests

Teach `/ocd:sandbox` a new verb — `ocd-run sandbox run <test.md>` — that loads an agent-test markdown file, spins up an ephemeral sandbox worktree via existing primitives, invokes `claude -p` with the spec as prompt, and collects standardized output for batch-aggregated test results. The sandbox system is already this project's canonical disposable-workspace mechanism; adding a markdown-driver on top extends it to the "mass integration testing of agent-driven behavior" use case without duplicating infrastructure.

## Prior design note

Observation O6 in `tests/plugins/ocd/systems/sandbox/integration/lifecycle-test.md`:

> This test should be driven by `/ocd:sandbox exercise`, not hand-routed. The sandbox skill's `exercise` verb already classifies concerns per the Interactivity criterion and routes them to the right substrate — that is exactly the job I did manually on the first run. [...] Deferred follow-up: teach `/ocd:sandbox exercise` to load a sandbox-test.md directly (`/ocd:sandbox run <system>`), eliminating the hand-authored prompt.

## What the verb would do

- Accept a markdown file path or a skill/system name that resolves to a conventionally-located spec (e.g. `<system>/integration/<name>-test.md`)
- Parse the spec: User Perspective, Setup, Scenarios, Known Observations
- Classify each scenario via the Interactivity criterion (already in sandbox SKILL.md) — fresh-install bucket vs. interactive bucket
- Spin up the matching substrate(s) via `worktree_setup` / `project_setup`
- Invoke `claude -p` with the scenario content as prompt, capturing structured output
- Aggregate results into a standardized schema — per-scenario pass/fail, findings, token cost, evidence paths
- Preserve or tear down the substrate per user choice

## Standardized output shape

A JSON envelope that downstream test-aggregation tooling can consume without per-test parsing. Fields needed:

- `spec`: path to the markdown file
- `scenarios`: array of `{name, bucket, outcome, findings, evidence_paths, tokens, cost_usd}`
- `observations`: new findings the agent surfaced that weren't in the spec's Known Observations list
- `substrate_paths`: the sibling paths used, so a follow-up run can inspect state

## Why this belongs in sandbox, not in a separate system

- Sandbox already owns the substrate primitives — `worktree_setup/teardown`, `project_setup/teardown`, `cleanup`
- Sandbox already implements the Interactivity classifier — `exercise` does this today
- `run <markdown>` is a different input shape (file vs. free-text description) but routes through the same internal mechanics
- Keeping it in sandbox avoids fragmenting the "disposable sandbox" mental model

## Consumers

- **Pytest integration tests** (via `sandbox_worktree` fixture) remain the way to run single-process, deterministic integration checks
- **Skill integration tests** use `sandbox run <test.md>` — one standardized entrypoint, batched via `sandbox run-suite` eventually
- **Lifecycle-test.md** becomes the first consumer, replacing its current hand-routed execution

## Prerequisites

- Stable markdown spec schema — what sections are required, how scenarios are structured
- Standardized output envelope agreed across consumers
- Interactivity classifier promoted from `exercise`-only to a shared helper

## Why not in v0.1.0

Substantial feature — new verb, new spec schema, new aggregation envelope. The immediate release need (worktree isolation for `test_convention_agent.py`) is handled by the `sandbox_worktree` pytest fixture, which consumes the same sandbox primitives this future work would extend. Both approaches use the same underlying mechanism; this idea is the richer markdown-driven extension that comes later.
