---
status: pending
last-verified: never
depends-on: [skill-caching.md, body-persistence.md]
---

# Assertion: `## Dependencies` and step-level inline mentions (`Apply /X`) coexist without redundant loads

Current skills (e.g. `/git-commit`) use inline step-level mentions like *"Apply /concise-prose, /description-authoring, /honesty"* within a procedural step. If we add `## Dependencies` declarations at the top, the question is whether those step-level mentions become:

- **Redundant loads** (full re-injection on top of the dependency declaration)
- **Soft references** (interpreted as "use the already-loaded guidance," no new load)
- **Conflicting signals** (agent doesn't know which to trust)

## Why it matters

The step-level mention is the surgical-application mechanism — it tells the agent *when* during the workflow to apply that skill's guidance. The `## Dependencies` mechanism handles *whether* the body is loaded. If they don't compose cleanly, we lose one or the other:

- If step-level triggers redundant loads, we can't keep surgical application
- If `## Dependencies` is sufficient on its own, the step-level mention is dead documentation

## Test skill

Path: `.claude/skills/dual-mode/SKILL.md`.

```markdown
---
name: dual-mode
description: Test skill that declares /marker-helper as a dependency AND mentions it inline at step 3. Verifies whether the step-level mention triggers a redundant load.
---

# /dual-mode

## Dependencies

If not already loaded, call the following skills:

- /marker-helper

## Body

1. bash: `echo "dual-mode step 1" >> /tmp/dual.log`
2. bash: `echo "dual-mode step 2" >> /tmp/dual.log`
3. Apply `/marker-helper` to format the next bash output, then bash: `echo "dual-mode step 3" >> /tmp/dual.log`
4. bash: `echo "dual-mode step 4" >> /tmp/dual.log`
5. Return: confirmation
```

And the helper:

```markdown
---
name: marker-helper
description: Helper skill loaded as a dependency by /dual-mode. Each load appends a timestamped line to /tmp/marker-helper.log.
---

# /marker-helper

Unique marker: DUAL-HELPER-NEWT-5527

## Body

1. bash: `echo "marker-helper loaded $(date +%s%N)" >> /tmp/marker-helper.log`
2. Return: confirmation
```

## Run procedure

1. Reset: `rm -f /tmp/dual.log /tmp/marker-helper.log`
2. Spawn fresh agent
3. Agent invokes `/dual-mode` twice
4. Agent reports `/tmp/marker-helper.log` line count + their interpretation of how the step-3 mention was handled
5. Capture `<usage>` `total_tokens`

## Detection method

| `/tmp/marker-helper.log` lines | Interpretation |
|---|---|
| 1 | `## Dependencies` loaded once; step-3 mention treated as a soft reference (no new load) |
| 2 | `## Dependencies` loaded once per invocation of `/dual-mode` (2 invocations × 1 = 2); step-3 still soft |
| 3-4 | Step-3 mention triggered an additional load — surgical mention conflicts with dependency declaration |
| 0 | Neither convention recognized — investigate |

## Expected outcomes

| Lines | Interpretation | Design implication |
|---|---|---|
| 1 | Best case: cross-invocation idempotence (depends on cross-skill-chain.md outcome) + soft step mention | Keep both conventions; step mention is surgical reminder |
| 2 | Per-invocation idempotence holds; step mention is soft | Keep both conventions; step mention costs nothing |
| 3-4 | Step mention triggers loads | Drop step-level mentions; rely on `## Dependencies` alone, lose surgical scoping |
| 0 | Convention regression | Re-verify dep-test-iterations.md result |

## Historical runs

| Date | Result | Notes |
|---|---|---|
| — | — | Not yet run |
