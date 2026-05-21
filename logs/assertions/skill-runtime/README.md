# Skill runtime assertions

Claims about how Claude Code's Skill tool handles invocation, body injection, persistence across the session, directive scope, and cross-skill composition.

## Dependency graph

Later tests' design and interpretation depend on earlier results. Run in this order; if an earlier result surprises us, reassess subsequent tests' designs before proceeding.

| # | Assertion | Depends on | Why ordered here |
|---|---|---|---|
| 0 | [`dep-test-iterations.md`](./dep-test-iterations.md) — `## Dependencies` directive phrasing | — | Confirmed; informs every subsequent test's directive design |
| 1 | [`skill-caching.md`](./skill-caching.md) — re-injection vs. cache | — | Foundational; outcome reshapes the cost model for all later tests |
| 2 | [`body-persistence.md`](./body-persistence.md) — body stays in context | 1 | If T1 = re-injection, T2 verifies the "stays loaded" claim that idempotent checks rely on |
| 3 | [`scope-leak.md`](./scope-leak.md) — directives outside the loading skill's execution | — | Independent of T1; answers whether we need encapsulation grammar |
| 4 | [`cross-skill-chain.md`](./cross-skill-chain.md) — idempotent check across separate skills | 1, 2 | Tests whether "still loaded" is honest when a different skill is the one asking |
| 5 | [`surgical-step-apply.md`](./surgical-step-apply.md) — `## Dependencies` + step-level inline | 1, 2 | Determines whether we keep step-level mentions after adopting dependency declarations |

## Active hypotheses unresolved

- Whether the Skill tool dedups body re-injection internally (T1)
- Whether loaded skill directives leak scope beyond their loading skill (T3)
- Whether the agent's self-report distorts our measurements (every test must include ground-truth signals — token usage, side-effect files, body-marker detection — not just agent narration)

## Conventions for tests in this directory

- **No real cross-skill dependencies in test artifacts** — keeps the test self-contained and not coupled to skills we're also evolving.
- **Side-effect file confirms execution** — every test skill writes to `/tmp/<test-name>.log` so we can verify all invocations actually ran, ruling out silent skips.
- **Unique markers in test bodies** — distinctive phrases (e.g. `PIZZADAEMON-7349`) that we can grep for to detect body re-injection without relying on the agent's interpretation.
- **`<usage>` block is ground truth for token cost** — sub-agents return a usage block; consult it directly, don't compute from the agent's narrative.
