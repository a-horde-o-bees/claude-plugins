---
status: pending
last-verified: never
---

# Assertion: When skill A loads /X and later skill B also declares /X, B's idempotent check correctly skips

Tests whether the "already loaded" check is honest across separate skills' invocations. If both skills correctly recognize /X as still loaded, the idempotent directive works repo-wide. If the check resets between skills, we get redundant loads across a workflow.

## Why it matters

The realistic workflow pattern: `/git-checkpoint` runs `/git-commit`, then `/git-push`, then `/git-ci`. If all three declare `/process-flow-notation` as a dependency:

- Best case: PFN loads once at the first skill that needs it, others skip → 1 load total
- Worst case: each skill loads PFN independently because their idempotent checks don't see the prior load → 3 loads, 3× cost

This test discriminates between those.

## Test skills

Three skills required. All in `.claude/skills/`.

### `/chain-skill-A`

```markdown
---
name: chain-skill-A
description: Test skill A. Declares /dep-payload as a dependency. Invocation appends to /tmp/chain.log.
---

# /chain-skill-A

## Dependencies

If not already loaded, call the following skills:

- /dep-payload

## Body

1. bash: `echo "A invoked" >> /tmp/chain.log`
2. Return: confirmation
```

### `/chain-skill-B`

```markdown
---
name: chain-skill-B
description: Test skill B. Declares /dep-payload as a dependency. Invocation appends to /tmp/chain.log.
---

# /chain-skill-B

## Dependencies

If not already loaded, call the following skills:

- /dep-payload

## Body

1. bash: `echo "B invoked" >> /tmp/chain.log`
2. Return: confirmation
```

### `/dep-payload`

```markdown
---
name: dep-payload
description: Payload skill loaded as a dependency. Each load appends to /tmp/dep-payload.log so we can count actual load events.
---

# /dep-payload

Unique marker: CHAIN-PAYLOAD-OCELOT-9981

## Body

1. bash: `echo "dep-payload loaded $(date +%s%N)" >> /tmp/dep-payload.log`
2. Return: confirmation
```

## Run procedure

1. Reset: `rm -f /tmp/chain.log /tmp/dep-payload.log`
2. Spawn fresh agent
3. Agent invokes `/chain-skill-A`
4. Agent invokes `/chain-skill-B`
5. Agent reports `/tmp/dep-payload.log` contents — line count = number of actual `/dep-payload` loads
6. Capture `<usage>` `total_tokens`

## Detection method

- **`/tmp/dep-payload.log` has 1 line**: idempotent check correctly skipped in B; cross-skill idempotence works
- **`/tmp/dep-payload.log` has 2 lines**: idempotent check failed across skills; B re-loaded the dependency
- **Agent's narration of "is /dep-payload loaded" before each skill**: cross-check against the file

## Expected outcomes

| `/tmp/dep-payload.log` lines | Interpretation | Design implication |
|---|---|---|
| 1 | Cross-skill idempotence works | Adopt `## Dependencies` repo-wide; expected cost = 1 load per session per skill |
| 2 | Each skill re-fires its declared deps | Idempotent phrasing only works within a single skill's runs; cross-skill cost is unavoidable with current convention |
| 0 | Neither skill loaded the dep (severe bug) | Investigate; possibly the directive was ignored because B saw a fresh context |

## Follow-up if outcome is "2 lines"

Try variant phrasings to see if any achieve cross-skill idempotence:

- "If `/dep-payload` is already loaded in this session, skip; otherwise load it."
- "Load `/dep-payload` if and only if it has not been loaded by this session."
- Explicit session-scope marker

## Historical runs

| Date | Result | Notes |
|---|---|---|
| — | — | Not yet run |
