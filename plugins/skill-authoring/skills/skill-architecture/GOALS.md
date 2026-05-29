# skill-architecture — Goals

> Draft for refinement. The intent here drives every probe we run and every recommendation we ship — settle it before burning more time on tests.

## What skill-architecture is for

`skill-architecture` is a guidance skill: other authoring skills (skill-creator, skill-composer) load it as a dependency to get **recommendations on how to structure a skill** — dependency grammar, scope encapsulation, PFN embedding, state location, project-dir resolution, sub-agent boundaries. Those recommendations live in [`architecture.md`](architecture.md), justified by the digest in [`confirmed-facts.md`](confirmed-facts.md), backed by re-runnable probes in [`assertions/`](assertions/README.md).

The whole thing is only as trustworthy as the facts under it. **Its job is to put skill-authoring decisions on verified ground instead of folklore.**

## Why we stopped to write this

The mechanic that produced the current facts was flawed — single-run observations, self-reported call counts, cache-confounded cost. Re-running with a sound mechanic ([`runner.py`](assertions/runner.py): ground-truth `tool_use` counts, cache-invariant token volume, N-sampling) showed key "facts" were artifacts:

- *"Idempotent loading works — bare=0, imperative=5, cue=1 loads"* → actually **nondeterministic** (three runs, three different patterns).
- *"Project dir resolvable via the session JSONL `cwd`"* → the documented tail-scan returns the **drifted** cwd, not the root; `git rev-parse --show-toplevel` is simpler and correct.

So **`confirmed-facts.md` and `architecture.md` are currently suspect** — this skill ships recommendations to skill-creator/skill-composer that rest on quarantined assertions. Re-grounding them is the point of the rebuild, and the reason this isn't just an `assertions/` cleanup.

## North star

**How do you write a skill call that behaves reliably across circumstances?** — direct invocation, dependency declaration, composition chains, sub-agents, headless `claude -p`. The deliverable is authoring patterns that produce predictable loading, scoping, and cost.

## What we produce

1. **A verified knowledge base** — `assertions/`, each a single claim plus its re-runnable probe.
2. **Trustworthy recommendations** — `architecture.md`, every line traceable to a confirmed fact.
3. **A drift detector** — the assertions, ordered simplest→complex, re-run when behavior seems off to find where our understanding broke.

## How we work (principles)

- **Ground truth over self-report** — count `tool_use`, read the init event; never trust the model's narration.
- **Distributions over anecdotes** — behavior is nondeterministic; N-sample every behavioral claim.
- **Cache-invariant measurement** — token volume, not cost, for cross-phase comparison.
- **Keep only load-bearing tests** — a claim survives only if it backs a decision or is a regression rung. Capture rungs, not the exploratory journey.
- **Ground-up** — answer the most foundational question first; let each validated answer pick the next.

## Open questions (the ladder — provisional)

0. Measurement mechanic ✓ (`runner.py`, `token-volume-invariance`)
1. + 2. Does an invocation reliably deliver the skill body — on the first call, and on every repeat?
3. Is `## Dependencies` auto-load reliable? *(early signal: no)*
4. Explicit in-body invocation vs. declaration — which loads reliably? *(closest to the goal)*
5. Directive persistence and scope.
6. Chains / depth.
- Project-root discovery: `git rev-parse --show-toplevel`.

## To refine — your call

- **Scope out:** what is explicitly NOT this effort? (skill *description*/triggering accuracy? eval harnesses? cost optimization for its own sake?)
- **Definition of enough:** when do we stop probing and start prescribing? (e.g., *"once Q1–Q4 give stable distributions, write the reliable-skill-call pattern and re-ground `architecture.md`."*)
- **Non-goals:** _____
