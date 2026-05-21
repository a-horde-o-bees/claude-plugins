---
status: pending
last-verified: never
depends-on: []
---

# Assertion: Does the Skill tool re-inject body on every call, or cache after first?

Two competing hypotheses to discriminate:

- **H-A (re-injection)**: Every Skill-tool invocation returns the full SKILL.md body. Token cost scales linearly with call count.
- **H-B (caching)**: First call returns the body; subsequent calls in the same session return a cached marker / no-op. Token cost is paid once.

## Why it matters

Foundation for every downstream design decision. If H-B is true, much of the idempotent-directive motivation evaporates — Skill calls are cheap regardless of phrasing. If H-A is true, idempotent directives are the only mitigation against runaway cross-skill cost.

Prior interpretations from `dep-test-iterations.md` suggested H-A, but those measurements relied on agent self-reports of "I got the body again" — which could be agents reading their own context (which already had the body from call 1) rather than reporting what the tool actually returned. This test uses ground-truth signals to discriminate.

## Test skill

Path: `.claude/skills/cache-test-bulk/SKILL.md` (to create at run time, delete after).

```markdown
---
name: cache-test-bulk
description: Test skill with a robust self-contained body. Verifies whether repeated invocations re-inject the body or return a cached response. Each invocation appends one line to /tmp/cache-test.log; no cross-skill calls; no dependencies.
---

# /cache-test-bulk

## Reference rules

The following are dummy rules included to give the body realistic bulk (target ~3,000 characters). They have no operational effect.

- Rule 1: Always prefer active voice when describing operations.
- Rule 2: When two parallel claims are similar, render them as a list, not prose.
- Rule 3: Anti-staleness — references to prior states should be removed when the prior state no longer exists.
- Rule 4: Cross-references should only appear when the reader must consult the source to understand the surface.
- Rule 5: Numbered lists imply ordering; bulleted lists do not.
- Rule 6: Headings that introduce a single bullet are unbalanced; either add siblings or fold the bullet into prose.
- Rule 7: Parenthetical lists without "e.g." implicitly claim exhaustiveness.
- Rule 8: Sibling items in a complementary set compact further than items in isolation.
- Rule 9: Surface boundaries (frontmatter, body, error messages) are mechanically distinct; dedup within a surface, not across.
- Rule 10: Length follows information, not prompt length or section count.

UNIQUE-MARKER-PIZZADAEMON-7349

## Body

1. {count}: bash: `cat /tmp/cache-test.counter 2>/dev/null || echo 0`
2. {next-count}: {count} + 1
3. bash: `echo "Hello call {next-count}" >> /tmp/cache-test.log`
4. bash: write `{next-count}` to `/tmp/cache-test.counter`
5. Return: `Hello call {next-count}`
```

The body should be padded to ~3,000 chars total (rules section above can be expanded with more numbered rules if the final character count comes in short).

## Run procedure

1. Reset state: `rm -f /tmp/cache-test.log /tmp/cache-test.counter`
2. Spawn fresh general-purpose agent
3. Agent invokes `/cache-test-bulk` 5 times in sequence via the Skill tool
4. Agent reports:
   - Full content received from call 1 (first ~200 chars + total length)
   - Full content received from call 2 (first ~200 chars + total length)
   - Whether the unique marker `UNIQUE-MARKER-PIZZADAEMON-7349` appears 1 time or 5 times in their conversation history
5. Capture `<usage>` `total_tokens` for total cost

## Detection method

Three independent signals, all should agree:

| Signal | H-A (re-injection) | H-B (caching) |
|---|---|---|
| Call 2 returned content | Same as call 1 | Empty / brief acknowledgment |
| `UNIQUE-MARKER-PIZZADAEMON-7349` occurrences in conversation | 5 | 1 |
| `total_tokens` (with body ~3,000 chars ≈ ~750 tokens) | baseline + 5×750 ≈ +3,750 | baseline + 1×750 + 4×tiny |
| Side-effect file `/tmp/cache-test.log` | 5 lines (`Hello call 1` through `Hello call 5`) | 5 lines (all calls still executed) |

The side-effect file rules out the "silent skip" failure mode — both hypotheses predict 5 lines because the body's bash step runs each time regardless.

## Expected outcomes

| Outcome | Interpretation | Next step |
|---|---|---|
| All three signals say re-injection | H-A confirmed | Proceed to `body-persistence.md` to verify the "stays in context" claim |
| All three signals say caching | H-B confirmed | Throw out cost-based motivation for idempotent directives; redesign |
| Signals disagree | Test design has a confound; document and redesign | — |

## Historical runs

| Date | Result | Notes |
|---|---|---|
| — | — | Not yet run |
