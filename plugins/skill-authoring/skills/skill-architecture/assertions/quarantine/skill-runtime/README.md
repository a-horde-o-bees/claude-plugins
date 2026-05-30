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
│       │                                  └─→  8. surgical-step-apply (Dependencies + inline mention)
│       │                                  └─→  9. multi-dep-declaration (multi-skill deps load all + idempotent)
│       │                                  └─→ 10. nested-encapsulation (chain loading + scope across levels)
│       │                                  └─→ 11. direct-invocation-after-dep-load
│       │                                  └─→ 12. sub-agent-context-inheritance
│       │
└── 3. scope-leak ──→ 4. encapsulation-grammar ──→ 6. scope-during-loading ─┐
    (leak by default)  (Variant D scopes at         (Variant D scopes at    │
                        single-level)                single-level wrapper)  │
                                                                            ↓
                                           13. variant-c-frontmatter-scope
                                           14. variant-e-caller-side-scope
                                           15. variant-f-hybrid (single-level)
                                           16. depth-encapsulation ─→ G1 depth-safe canonical
```

Full table with per-test status below.

| # | Assertion | Depends on | Status | Why ordered here |
|---|---|---|---|---|
| 0 | [`dep-test-iterations.md`](./dep-test-iterations.md) — `## Dependencies` directive phrasing | — | confirmed | Informs every subsequent test's directive design |
| 1 | [`skill-caching.md`](./skill-caching.md) — re-injection vs. cache | — | confirmed (re-injection) | Foundational; cost model for all later tests |
| 2 | [`body-persistence.md`](./body-persistence.md) — body stays in context | 1 | confirmed | Idempotent checks rely on this |
| 3 | [`scope-leak.md`](./scope-leak.md) — directives outside the loading skill's execution | — | confirmed (leak) | Drove the pivot to encapsulation-grammar testing |
| 4 | [`encapsulation-grammar.md`](./encapsulation-grammar.md) — grammar that scopes a skill's directives | 3 | confirmed at single-level (Variant D) | Variant sweep against the AARDVARK leak test |
| 5 | [`idempotence-preservation.md`](./idempotence-preservation.md) — encapsulation preserves 1-load-per-session | 0, 2, 4 | confirmed | Side-effect verification — scope didn't break the load-once convention |
| 6 | [`scope-during-loading.md`](./scope-during-loading.md) — encapsulated directive applies during a loading wrapper's execution | 4 | confirmed for Variant D at single-level | Side-effect verification — scope didn't over-encapsulate and lose wrapper application |
| 7 | [`cross-skill-chain.md`](./cross-skill-chain.md) — idempotent check across separate skills | 1, 2 | deferred (substantially answered by 5) | The wrapper-A/wrapper-B test in #5 already shows cross-skill idempotence |
| 8 | [`surgical-step-apply.md`](./surgical-step-apply.md) — `## Dependencies` + step-level inline mention | 1, 2 | confirmed — step-level mention is a soft reference | Both conventions compose; step-level mention costs nothing |
| 9 | [`multi-dep-declaration.md`](./multi-dep-declaration.md) — multiple skills in one `## Dependencies` section | 0, 2 | confirmed | All listed deps load on first invocation, idempotent skip on re-invocation |
| 10 | [`nested-encapsulation.md`](./nested-encapsulation.md) — transitive loading + scope across nesting levels | 0, 2, 4 | loading ✓; **LEAK at depth** under Variant D (refined 2026-05-21); resolved by G1 in #16 | Variant D's closing release line failed to bound the directive in nested chains. See #16 for fix. |
| 11 | [`direct-invocation-after-dep-load.md`](./direct-invocation-after-dep-load.md) — direct call to a skill that was already loaded as a dep | 1, 2, 4 | confirmed | Body re-injects (no silent skip); scope releases correctly at single level |
| 12 | [`sub-agent-context-inheritance.md`](./sub-agent-context-inheritance.md) — sub-agent sees parent's loaded skills? | 1, 2 | confirmed — fresh context per sub-agent; registry shared | Side finding: general-purpose sub-agents don't have access to the Agent tool — cannot spawn nested sub-agents |
| 13 | [`variant-c-frontmatter-scope.md`](./variant-c-frontmatter-scope.md) — `scope: dependency-only` frontmatter field | 4 | partial — over-suppresses | Frontmatter field IS honored as a behavioral constraint, but the wording suppresses both wrapper-application and post-chain leak |
| 14 | [`variant-e-caller-side-scope.md`](./variant-e-caller-side-scope.md) — caller-side scope grammar inside `## Dependencies` | 4 | partial — applies but leaks | Caller-side scope alone is one-directional — grants application, doesn't bound |
| 15 | [`variant-f-hybrid.md`](./variant-f-hybrid.md) — caller-side scope + called-skill Variant D closing line | 4, 6, 14 | confirmed at single-level; **LEAKS at depth** (superseded by #16) | Worked single-level; refuted at depth 2. Superseded by G1. |
| 16 | [`depth-encapsulation.md`](./depth-encapsulation.md) — depth-safe scope grammar across 4 variants | 14, 15 | **confirmed — G1 (strengthened release line) is depth-safe** | Tested F, G1, G2, FLAT at depth 2. G1/G2 hold; F/FLAT leak. G1 wording is the recommended canonical for production chains. |

## Canonical patterns confirmed

### Idempotent loading (in calling skill) — robust across all scenarios

```markdown
## Dependencies

If not already loaded, call the following skills:

- /skill-name
- /other-skill
```

### Scope grammar — depth determines which release line to use

**Single-level deps** (caller directly invokes one skill carrying a directive) — Variant D closing line in the called skill is sufficient:

```markdown
---

End of /skill-name. The preceding directives apply during this skill's invocation AND during the execution of any skill that loads this one as a dependency. They do NOT apply to subsequent unrelated agent output.
```

**Nested chains (depth ≥ 2) or production skills used as both direct and transitive deps** — Variant G1 strengthened closing line:

```markdown
---

End of /skill-name. The preceding directives are bounded by this skill's invocation and the execution bodies of any skill that loaded this one — directly OR transitively. These directives are RELEASED immediately upon return from the outermost loading skill in the chain. Agent text generated AFTER that outermost return — including subsequent responses, unrelated answers, summaries, or any prose — is OUT OF SCOPE. These directives MUST NOT apply to such post-chain output.
```

In both cases, callers pair the closing line with caller-side scope in their `## Dependencies` block:

```markdown
## Dependencies

If not already loaded, call (and apply during all prose generation within this skill's execution): /skill-name
```

Variant D **alone** leaked at depth ([[nested-encapsulation]] refined run, [[depth-encapsulation]] f-deep + FLAT tests). Variant F's caller-side scope did not compensate. Variant E alone (caller-side without any closing release line) leaked even at single-level. The strengthening that makes G1 work is three-fold:

- Explicit "directly OR transitively" — addresses the transitive-loader case
- Explicit "outermost loading skill in the chain" — gives the agent a clear release anchor
- Explicit enumeration of post-chain output types — closes the gap where Variant D's terse "subsequent unrelated agent output" was insufficient

### Surgical step-level mention (optional)

Inline mentions like `Apply /concise-prose` in step text are confirmed as **soft references** ([[surgical-step-apply]]) — they cost nothing (no re-load) and act as procedural reminders for when during the body to apply a loaded dep's directives.

## Untested gaps

| Gap | Why it matters | Priority |
|---|---|---|
| **G1 wording at single-level (depth 0/1)** — does the strengthened release line still let the directive apply correctly during direct invocations and depth-1 wrappers? | If yes, G1 becomes the universal canonical and Variant D can be retired. If the verbose language introduces side effects at low depth, we keep two grammars (D for single-level, G1 for chains). | **Medium** — would simplify the recommendation set |
| **G1 at depth 3+** — confirmed at depth 2; does the strengthened wording hold at 3+ layers? | Production chains may eventually exceed depth 2 (`/orchestrator → /git-checkpoint → /git-commit → /concise-prose`). | Medium |
| **Transitive in-wrapper scope** — when `/inner` is reached through a chain, does its directive apply during `/outer`'s execution context (not just `/inner`'s own)? | Both nested-encapsulation runs left this ambiguous because composition was a file write, not a textual response. G1 depth test composition contained AARDVARK — suggests scope DOES reach outer; needs a clean disambiguation. | Medium |
| **Context compaction effect** — what if the body is evicted from context window due to compaction? Does the idempotent check honestly evaluate "not loaded" and re-fire? | Affects long sessions. Re-load on eviction would be the correct behavior, but mechanically unverified. Hard to drive deterministically from a test harness. | Medium |
| **Better frontmatter scope wording** — `scope: applies-in-wrapper`, `scope: cascade`, or composite field | [[variant-c-frontmatter-scope]] confirmed frontmatter IS honored; finding wording that means "apply during wrappers, release after" would yield the cleanest grammar of the family. | Low |

## Conventions for tests in this directory

- **No real cross-skill dependencies in test artifacts** — keeps the test self-contained and not coupled to skills we're also evolving.
- **Side-effect file confirms execution** — every test skill writes to `/tmp/<test-name>.log` so we can verify all invocations actually ran, ruling out silent skips.
- **Unique markers in test bodies** — distinctive phrases (e.g. `PIZZADAEMON-7349`) that we can grep for to detect body re-injection without relying on the agent's interpretation.
- **`<usage>` block is ground truth for token cost** — sub-agents return a usage block; consult it directly, don't compute from the agent's narrative.
- **Prose-style unrelated answers** — when probing for scope leak, ask questions that elicit prose answers (multi-word sentences). Terse one-word answers ("4", "Paris") can fail to surface a leak because the directive's "textual response" rule may not engage on a fragment.
- **Sub-agent task prompts must explicitly anchor "start from the outer skill"** — the G1 first run failed because the sub-agent invoked `/g1-inner` directly. Including a sharp "if you invoke X directly without going through Y first, you have failed" instruction in the prompt prevented re-occurrence.
