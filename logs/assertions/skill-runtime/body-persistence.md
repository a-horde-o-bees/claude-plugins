---
status: pending
last-verified: never
depends-on: [skill-caching.md]
---

# Assertion: Once injected, a skill body persists in context for the rest of the session

Claude Code docs claim: *"the rendered SKILL.md content enters the conversation as a single message and stays there for the rest of the session."* This assertion verifies that claim experimentally. The idempotent-dependency directive relies on it — if bodies drop out of context, the "already loaded" check would fail honestly and re-fire.

## Why it matters

If bodies persist reliably, idempotent loading is sufficient. If bodies drop out (context compaction, eviction policies), we need a more robust mechanism — e.g., periodic re-verification, explicit context-pressure checks, or a different convention.

## Test skill

Path: `.claude/skills/marker-skill/SKILL.md`.

```markdown
---
name: marker-skill
description: Test skill whose body contains a distinctive unique marker phrase. Verifies that injected bodies persist in conversation context across subsequent tool calls.
---

# /marker-skill

Unique marker phrase: PERSIST-CHECK-MARMOSET-3142

## Body

1. bash: `echo "marker-skill invoked" >> /tmp/marker.log`
2. Return: confirmation
```

## Run procedure

1. Reset: `rm -f /tmp/marker.log`
2. Spawn fresh agent
3. Agent invokes `/marker-skill` once
4. Agent performs ~10 unrelated tool calls (file reads, bash commands, simple computations)
5. Without re-invoking `/marker-skill`, agent is asked: *"Quote the unique marker phrase from /marker-skill's body verbatim."*

## Detection method

- **Agent quotes `PERSIST-CHECK-MARMOSET-3142`**: body persisted in context
- **Agent says "not in my context" or hallucinates a marker**: body did NOT persist
- **Agent re-invokes the skill to retrieve the marker**: signals it didn't trust its context, but isn't a clean refutation — flag as ambiguous

The marker phrase must be unique enough that it can't be guessed or confused with anything else. `MARMOSET-3142` should not appear in training data or in any other file the agent reads during the experiment.

## Expected outcomes

| Outcome | Interpretation |
|---|---|
| Marker quoted verbatim | Body persists; idempotent check is sound |
| Marker missing / hallucinated | Body evicted; idempotent check would mis-skip; need alternative mechanism |
| Agent re-invokes to retrieve | Ambiguous; rerun with explicit "do not re-invoke" instruction |

## Historical runs

| Date | Result | Notes |
|---|---|---|
| — | — | Not yet run |
