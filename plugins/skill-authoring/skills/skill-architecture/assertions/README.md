# Assertions

Durable claims about platform behavior, each captured with the probe that verifies it. One claim per file; see [`_template.md`](./_template.md) for the schema.

The platforms we build on evolve — a claim true in v2.1 may not hold in v2.5. Probes reconstitute from the file alone, so we re-verify against future versions without re-deriving methodology.

## Status: ground-up rebuild

The suite is being rebuilt from the foundation up around one goal: **how to write a skill call that is reliable across circumstances.** Earlier assertions grew under a flawed mechanic — single-run observations, self-reported call counts, cache-confounded cost — and are quarantined pending re-derivation. A claim is kept only if it (a) backs a live decision, or (b) is a rung in a simplest→complex regression ladder we'd re-run to find where our understanding breaks. We capture the rungs, not the journey.

## Foundational ladder (ordering provisional)

Each rung is N-sampled — behavior is nondeterministic, so one run is an anecdote — and validated before it justifies the next:

0. **Measurement mechanic** ✓ — count calls and measure cost reliably. → [`runner.py`](./runner.py), [`test-harness/token-volume-invariance.md`](./test-harness/token-volume-invariance.md)
1. A single invocation delivers the skill's full body into context.
2. Repeated direct invocation — does the body re-deliver each time?
3. `## Dependencies` auto-load reliability (early probing suggests *nondeterministic*).
4. Explicit in-body invocation vs. declaration — which loads reliably. *(Closest to the goal.)*
5. Directive persistence and scope.
6. Chains / depth.

Project-root discovery is a standalone rung — see [`project-root-discovery/`](./project-root-discovery/README.md) for the full method landscape (requirements, failure modes, downstream imposition). Provisional lean: `git rev-parse --show-toplevel` + a superproject climb for submodules, marker walk-up as the non-git fallback.

## Topics

| Topic | What it covers |
|---|---|
| [`test-harness/`](./test-harness/) | The `claude -p` runner we verify everything else with — measurement model and cost |
| [`project-root-discovery/`](./project-root-discovery/) | How to resolve the project root — method landscape, tradeoffs, submodule ambiguity (probes pending) |

Topics are added as rebuilt rungs land.

## Tooling

[`runner.py`](./runner.py) runs `claude -p` as the test and extracts ground-truth signals — call counts, cache-invariant token volume, registry/model from the init event; `sample()` repeats a phase N times for distributions. [`runner.md`](./runner.md) is the findings key: what each signal is, the call that gets it, and the caveat that makes it trustworthy.

## Quarantine

[`quarantine/`](./quarantine/) holds the pre-reset files, preserved as reference (question ideas, control-skill bodies), not as trusted claims. Mine them when rebuilding a rung; don't cite them. Everything in there is a temporary artifact destined for deletion once its content is re-derived or confirmed dead.

## Re-verification

[`reassert`](../_reassert.md) re-runs assertions against the current Claude Code version (pending; build plan retired 2026-06-01, reconstruction pending). For now, follow each `## Procedure` manually, using [`runner.py`](./runner.py) to run and measure.
