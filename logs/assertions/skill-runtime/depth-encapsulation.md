---
status: confirmed — strengthened release line (G1) is depth-safe; basic Variant D/F and structural flattening (FLAT) are not
last-verified: 2026-05-21
---

# Assertion: Scope grammar at depth — Variant D and Variant F leak; strengthened release language (G1/G2) bounds the directive correctly

Confirmed across four chain configurations at depth 2 (outer → middle → inner). The basic closing release lines used in single-level tests (Variant D / Variant F) fail to suppress the directive in post-chain unrelated output. A strengthened closing release line that explicitly addresses transitive depth AND post-chain output bounds the directive correctly.

## Why it matters

Production skill chains will exceed depth 1 routinely (e.g. `/git-checkpoint → /git-commit → /concise-prose`). Without a depth-safe closing release line, behavioral directives loaded deep in a chain will leak to whatever the agent produces after the chain returns — including final user-facing summaries.

Refines the conclusion from [[encapsulation-grammar]] (single-level Variant D works), [[scope-during-loading]] (Variant D in single-level wrapper works), and [[variant-f-hybrid]] (single-level Variant F works) — all of which were tested at depth ≤ 1.

## Test design

Four 3-layer chains, each with composition step at the outermost level and AARDVARK directive in the innermost. Each tested with prose-style unrelated post-chain questions.

### Variants

**Variant F (baseline at depth)** — caller-side scope in each caller + standard Variant D closing line in `/f-deep-inner`:

```
End of /f-deep-inner. The preceding directives apply during this skill's invocation AND during the execution of any skill that loads this one as a dependency. They do NOT apply to subsequent unrelated agent output.
```

**Variant G1** — strengthened closing release line in `/g1-inner` only; caller-side scope at each layer above:

```
End of /g1-inner. The preceding directives are bounded by this skill's invocation and the execution bodies of any skill that loaded this one — directly OR transitively (e.g. an ancestor of a wrapper that loaded it). These directives are RELEASED immediately upon return from the outermost loading skill in the chain. Agent text generated AFTER that outermost return — including subsequent responses, unrelated answers, summaries, or any prose — is OUT OF SCOPE. These directives MUST NOT apply to such post-chain output.
```

**Variant G2** — same strengthened release wording in inner PLUS each middle/outer wrapper also carries a release line addressing transitively-loaded directives. Defense-in-depth.

**Variant FLAT** — outer declares BOTH `/flat-middle` AND `/flat-inner` as direct deps (so inner's standard Variant D closing line treats outer as a direct loader, not transitive). Tests whether structural flattening avoids the depth problem.

### Run procedure (per variant)

1. Reset all 4 variant-prefixed `/tmp` log files
2. Spawn fresh sub-agent, neutral framing
3. Agent invokes the outer skill (`/f-deep-outer`, `/g1-outer`, `/g2-outer`, `/flat-outer`)
4. Agent reads all 4 log files
5. Agent answers two unrelated prose questions

### Detection method

| Signal | Depth-safe | Failing |
|---|---|---|
| Three layer logs each at 1 line | loaded | one or more missing |
| AARDVARK in outer's composition file | applied during outer execution | scope didn't reach |
| AARDVARK in post-chain unrelated answers | absent → bounded | present → LEAKED |

## Historical runs

| Variant | Date | Loading | Composition | Post-chain leak? | Notes |
|---|---|---|---|---|---|
| F (basic) | 2026-05-21 | ✓ | AARDVARK present | **LEAKED** | Unrelated answers: "Eleven plus eleven equals twenty-two AARDVARK", "The Pacific Ocean is one of the world's oceans AARDVARK". `total_tokens` 19,065 / 10 tool uses. |
| G1 (strengthened release in inner) | 2026-05-21 | ✓ | AARDVARK present | **NO LEAK** ✓ | Unrelated answers: "Thirteen plus thirteen equals twenty-six.", "The coast redwood is a tall coniferous tree native to the Pacific coast of North America." `total_tokens` 20,069 / 12 tool uses. (First sub-agent went off-script and invoked /g1-inner directly; re-dispatched with explicit "start with /g1-outer" instruction succeeded.) |
| G2 (release at every layer) | 2026-05-21 | ✓ | AARDVARK present | **NO LEAK** ✓ | Agent explicitly articulated the release: "The /g2-outer skill has fully returned, releasing all directives loaded during its execution (including the AARDVARK rule from /g2-inner). Subsequent output is unrelated agent output and the released directives do not apply." Unrelated: "Fourteen plus fourteen equals twenty-eight.", "A common fruit is an apple." `total_tokens` 19,280 / 9 tool uses. |
| FLAT (outer direct-deps inner) | 2026-05-21 | ✓ | AARDVARK present | **LEAKED** | Confirms structural rearrangement doesn't help — wording is what matters. With `/flat-outer` declaring `/flat-inner` as a DIRECT dep, the standard Variant D closing line still failed to bound post-chain output. Unrelated: "Fifteen plus fifteen equals thirty AARDVARK", "A dolphin lives in water AARDVARK". `total_tokens` 18,939 / 9 tool uses. |

## Canonical recommendation at depth

The minimum sufficient grammar for skill chains expected to exceed depth 1:

**1. Caller side — `## Dependencies` with caller-side scope** (same as Variant F):

```markdown
## Dependencies

If not already loaded, call (and apply during all prose generation within this skill's execution): /dep-skill
```

**2. Called side — strengthened closing release line** (G1 wording):

```markdown
---

End of /dep-skill. The preceding directives are bounded by this skill's invocation and the execution bodies of any skill that loaded this one — directly OR transitively. These directives are RELEASED immediately upon return from the outermost loading skill in the chain. Agent text generated AFTER that outermost return — including subsequent responses, unrelated answers, summaries, or any prose — is OUT OF SCOPE. These directives MUST NOT apply to such post-chain output.
```

The strengthening from basic Variant D matters in three places:

- Explicit "directly OR transitively" — addresses the transitive-loader case
- Explicit "outermost loading skill in the chain" — gives the agent a clear release anchor
- Explicit enumeration of post-chain output types ("subsequent responses, unrelated answers, summaries, or any prose") — closes the gap where Variant D's terse "subsequent unrelated agent output" was insufficient

G2's per-layer redundancy works too but is heavier with no demonstrated additional safety over G1.

## Open question — depth-1 wording

Does G1's strengthened wording in directive-carrying skills also work cleanly at depth 1, or does the verbose release language introduce any side effects (e.g. preventing in-wrapper application at depth 1)?

Re-running the [[scope-during-loading]] test with G1 wording in place of Variant D would resolve this. If G1 works at depth 1 too, it becomes the universal canonical and Variant D can be retired.
