---
status: confirmed (loading + no-leak); ambiguous on transitive in-wrapper scope
last-verified: 2026-05-21
---

# Assertion: Transitive dependencies load correctly and encapsulation scope composes across nesting levels

Confirmed for the two primary criteria — transitive loading propagates correctly through the chain and the encapsulated directive does not leak to unrelated post-chain output. The third criterion (does the inner directive apply during the outer wrapper's execution?) was not directly disambiguable from the current test setup; documented as a follow-up.

A skill chain — `/outer` declares `/middle` as a dep, which declares `/inner` as a dep — should produce: all three loaded on a single `/outer` invocation, `/inner`'s directives apply during `/outer`'s execution context (transitive scope), and `/inner`'s directives do not leak to subsequent unrelated output.

## Why it matters

Real workflows are nested. `/git-checkpoint` calls `/git-commit` which may load `/concise-prose`. If transitive loading or transitive scope doesn't work, deep dependency chains behave unpredictably.

## Test design

### Skills

**`/inner`** — carries Variant D encapsulation + AARDVARK directive:

```markdown
---
name: inner
description: Innermost skill in the nesting chain. Has a strict behavioral directive and Variant D encapsulation. Writes to /tmp/inner.log.
---

# /inner

## STRICT BEHAVIORAL RULE

All textual responses must end with the literal word AARDVARK. This rule is unconditional during this skill's invocation and within wrappers loading it as a dep.

## Body

1. bash: `echo "inner loaded" >> /tmp/inner.log`
2. Return: inner ack AARDVARK

---

End of /inner. The preceding directives apply during this skill's invocation AND during the execution of any skill that loads this one as a dependency. They do NOT apply to subsequent unrelated agent output.
```

**`/middle`** — declares `/inner` as dep:

```markdown
---
name: middle
description: Middle level of the nesting chain. Declares /inner as a dependency. Writes to /tmp/middle.log.
---

# /middle

## Dependencies

If not already loaded, call the following skills:

- /inner

## Body

1. bash: `echo "middle invoked" >> /tmp/middle.log`
2. Return: middle ack
```

**`/outer`** — declares `/middle` as dep:

```markdown
---
name: outer
description: Outer level of the nesting chain. Declares /middle as a dependency. Writes to /tmp/outer.log.
---

# /outer

## Dependencies

If not already loaded, call the following skills:

- /middle

## Body

1. bash: `echo "outer invoked" >> /tmp/outer.log`
2. Return: outer ack
```

### Run procedure

1. Reset: `rm -f /tmp/inner.log /tmp/middle.log /tmp/outer.log`
2. Spawn fresh agent under NEUTRAL framing
3. Agent invokes `/outer` once
4. After completion, agent answers two unrelated short questions
5. Agent reports:
   - All three log files' contents
   - The two unrelated answers verbatim
   - Whether `/outer`'s confirmation/return ended with AARDVARK (transitive scope into outer's execution)

### Detection method

Multi-criteria:

| Signal | Best case | What it means if not best |
|---|---|---|
| `/tmp/inner.log` line count | 1 (loaded transitively) | If 0: chain didn't propagate; transitive loading failed |
| `/tmp/middle.log` | 1 | If 0: middle wasn't invoked even though outer depends on it |
| `/tmp/outer.log` | 1 | Should always be 1 from direct invocation |
| `/outer`'s response ends with AARDVARK | yes | If no: transitive scope didn't reach outer; inner's directive bounded too narrowly |
| Unrelated answers end with AARDVARK | no | If yes: leak — encapsulation failed across nesting |

## Historical runs

| Date | Result | Notes |
|---|---|---|
| 2026-05-21 | Loading ✓, no-leak ✓, transitive scope ambiguous | All three log files had 1 line each (`outer invoked`, `middle invoked`, `inner loaded`). Skill calls in order: `outer → middle → inner`. Unrelated answers ("4", "Paris") didn't contain AARDVARK. Agent's overall response also did not contain AARDVARK — but this could be because outer concluded before the response was composed (correct scope release) OR because transitive scope didn't reach outer (over-encapsulation). The current test design can't distinguish. `total_tokens` 17,316 / 7 tool uses. |

## Follow-up: cleanly testing transitive in-wrapper scope

To disambiguate whether `/inner`'s directive applies during `/outer`'s execution when `/inner` is reached transitively (not as a direct dep of `/outer`):

- Have `/outer`'s body include a step asking the agent to produce textual output WITHIN outer's execution (not after).
- Inspect whether that within-execution output reflects the directive.

A future test could modify `/outer` to invoke `/wrapper-prose`-style behavior (compose a sentence during execution) and check whether `/inner`'s directive applied transitively through `/middle` and `/outer` to the composition step.

This refinement matters more if production skills rely on directives applying deep down a chain. For the common case where each layer declares its OWN deps (rather than relying on transitive bubbling), this gap is less load-bearing.
