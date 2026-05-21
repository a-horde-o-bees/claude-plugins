---
status: partial — applies but leaks
last-verified: 2026-05-21
---

# Assertion: Caller-side scope grammar (Variant E) applies directives during wrapper execution but does not contain the leak afterward

Confirmed both criteria. Variant E's grammar in the calling skill — `If not already loaded, call (and apply during all prose generation within this skill's execution): /e-target` — successfully granted directive application during wrapper execution (AARDVARK appeared in `/e-wrapper`'s in-execution composition). However, with no closing release line in `/e-target`, the directive leaked into post-chain unrelated answers ("12 + 12 equals 24 AARDVARK", "Mango AARDVARK").

Caller-side scope grants application but does not bound it. Pair with the called-skill closing release line for full scope discipline — see [[variant-f-hybrid]].

## Why it matters

If caller-side scope worked end-to-end, deps could declare scope freely without coordinating with their dependencies (no closing release boilerplate in every depended-on skill). This test shows it needs a partner mechanism on the called-skill side to bound the scope.

## Test design

### Skills

`/e-target` — AARDVARK directive only. No closing release line. No frontmatter scope.

`/e-wrapper` — declares `/e-target` via caller-side scope grammar:

```
## Dependencies

If not already loaded, call (and apply during all prose generation within this skill's execution): /e-target
```

Body includes prose-composition step.

### Run procedure

1. Reset: `rm -f /tmp/e-target.log /tmp/e-wrapper.log /tmp/e-wrapper-sentence.log`
2. Spawn fresh sub-agent, neutral framing
3. Agent invokes `/e-wrapper`
4. Agent reads logs, answers two unrelated prose questions

### Detection method

| Signal | Variant E good | Variant E bad |
|---|---|---|
| AARDVARK in composition | present | absent |
| AARDVARK in unrelated answers | absent | present |

## Historical runs

| Date | Result | Notes |
|---|---|---|
| 2026-05-21 | Applied in wrapper ✓, leaked post-chain ✗ | Composition: "...alongside a composed descriptive sentence AARDVARK". Unrelated answers: "12 + 12 equals 24 AARDVARK", "Mango AARDVARK". Caller-side scope is one-directional — it tells the agent to apply, but doesn't tell the agent when to stop. `total_tokens` 18,351 / 7 tool uses. |
