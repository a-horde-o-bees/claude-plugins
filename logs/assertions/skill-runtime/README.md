# Skill runtime assertions

Claims about how Claude Code's Skill tool handles invocation, body injection, persistence across the session, directive scope, and cross-skill composition.

## Dependency tree

Read top-down. Each test's design and interpretation depend on the tests above it. If you re-verify the foundation tests against a future platform version and a result flips, reassess every test downstream of that node.

```
Foundation
├── 0. dep-test-iterations ──────────────┐
│   (## Dependencies directive phrasing) │
│                                         ↓
├── 1. skill-caching                  5. idempotence-preservation
│   (body re-injection cost)          (encapsulation + 1-load-per-session compose)
│       ↓                                 ↑
│   2. body-persistence ──────────────────┤
│   (body stays in context across calls)  │
│       │                                  └─→  9. multi-dep-declaration (multi-skill deps load all + idempotent)
│       │                                  └─→ 10. nested-encapsulation (chain loading + scope across levels)
│       │                                  └─→ 11. cross-skill-chain (deferred — wrapper A/B in #5 substantially answered)
│       │                                  └─→ 12. surgical-step-apply (pending)
│       │
└── 3. scope-leak ──→ 4. encapsulation-grammar ──→ 6. scope-during-loading
    (leak by default)  (Variant D scopes correctly)  (scope reaches wrapper context)
```

Full table with per-test status below.

| # | Assertion | Depends on | Status | Why ordered here |
|---|---|---|---|---|
| 0 | [`dep-test-iterations.md`](./dep-test-iterations.md) — `## Dependencies` directive phrasing | — | confirmed | Informs every subsequent test's directive design |
| 1 | [`skill-caching.md`](./skill-caching.md) — re-injection vs. cache | — | confirmed (re-injection) | Foundational; cost model for all later tests |
| 2 | [`body-persistence.md`](./body-persistence.md) — body stays in context | 1 | confirmed | Idempotent checks rely on this |
| 3 | [`scope-leak.md`](./scope-leak.md) — directives outside the loading skill's execution | — | confirmed (leak) | Drove the pivot to encapsulation-grammar testing |
| 4 | [`encapsulation-grammar.md`](./encapsulation-grammar.md) — grammar that scopes a skill's directives | 3 | confirmed (Variant D) | Variant sweep against the AARDVARK leak test |
| 5 | [`idempotence-preservation.md`](./idempotence-preservation.md) — encapsulation preserves 1-load-per-session | 0, 2, 4 | confirmed | Side-effect verification — scope didn't break the load-once convention |
| 6 | [`scope-during-loading.md`](./scope-during-loading.md) — encapsulated directive applies during a loading wrapper's execution | 4 | confirmed for Variant D | Side-effect verification — scope didn't over-encapsulate and lose wrapper application |
| 7 | [`cross-skill-chain.md`](./cross-skill-chain.md) — idempotent check across separate skills | 1, 2 | deferred (substantially answered by 5) | The wrapper-A/wrapper-B test in #5 already shows cross-skill idempotence |
| 8 | [`surgical-step-apply.md`](./surgical-step-apply.md) — `## Dependencies` + step-level inline | 1, 2 | pending | Determines whether step-level mentions are still useful given the encapsulated dependency mechanism |
| 9 | [`multi-dep-declaration.md`](./multi-dep-declaration.md) — multiple skills in one `## Dependencies` section | 0, 2 | confirmed | Best case: all listed deps load on first invocation, idempotent skip on re-invocation |
| 10 | [`nested-encapsulation.md`](./nested-encapsulation.md) — transitive loading + scope across nesting levels | 0, 2, 4 | confirmed (loading + no-leak); ambiguous on transitive in-wrapper scope | Real workflows are nested; chain composition verified for the main criteria |

## Canonical patterns confirmed

From the assertions above, two grammars are the canonical forms for cross-skill dependencies:

**1. Idempotent loading (in calling skill)**:

```markdown
## Dependencies

If not already loaded, call the following skills:

- /skill-name
- /other-skill
```

**2. Encapsulated scope (in called skill body, after the directive content)**:

```markdown
---

End of /skill-name. The preceding directives apply during this skill's invocation AND during the execution of any skill that loads this one as a dependency. They do NOT apply to subsequent unrelated agent output.
```

These two compose: loading skills declare deps with grammar 1; depended-on skills carry grammar 2 to prevent global leak.

## Untested gaps

Things we have NOT verified that could matter for production rollout:

| Gap | Why it matters | Priority |
|---|---|---|
| **Transitive in-wrapper scope** — when `/inner` is reached through a chain, does its directive apply during `/outer`'s execution context (not just `/inner`'s own)? | `nested-encapsulation.md` confirmed loading + no-leak but couldn't distinguish "directive applied during outer but outer's explicit return overrode it" from "directive didn't propagate to outer." Disambiguation needs `/outer`'s body to produce free-form prose during execution. | Medium |
| **Sub-agent context inheritance** — does a sub-agent inherit the parent's loaded skills, or start fresh? | Affects any skill that spawns sub-agents. Likely fresh-start, but unverified. | Medium |
| **Direct invocation after dependency load** — Variant D names two scopes ("direct" and "as dep"). Does invoking the skill directly AFTER it was loaded as a dep behave correctly? | Edge case but realistic in workflows that load a skill early then revisit. | Medium |
| **Context compaction effect** — what if the body is evicted from context window due to compaction? Does the idempotent check honestly evaluate "not loaded" and re-fire? | Affects long sessions. Re-load on eviction would be the correct behavior, but mechanically unverified. | Medium |
| **Variant E (caller-side scope)** and **Variant F (hybrid)** — alternatives to Variant D that might be cleaner | If Variant D's verbose two-clause closing line becomes a maintenance burden, alternatives may be preferable. | Low |
| **Variant C — frontmatter `scope` field** — declarative metadata alternative | Cleanest possible grammar IF agents honor frontmatter fields as behavioral constraints. Worth testing if metadata-only declarations become valuable. | Low |

## Conventions for tests in this directory

- **No real cross-skill dependencies in test artifacts** — keeps the test self-contained and not coupled to skills we're also evolving.
- **Side-effect file confirms execution** — every test skill writes to `/tmp/<test-name>.log` so we can verify all invocations actually ran, ruling out silent skips.
- **Unique markers in test bodies** — distinctive phrases (e.g. `PIZZADAEMON-7349`) that we can grep for to detect body re-injection without relying on the agent's interpretation.
- **`<usage>` block is ground truth for token cost** — sub-agents return a usage block; consult it directly, don't compute from the agent's narrative.
