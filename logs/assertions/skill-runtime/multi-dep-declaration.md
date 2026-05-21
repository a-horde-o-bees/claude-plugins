---
status: confirmed
last-verified: 2026-05-21
---

# Assertion: A `## Dependencies` section declaring multiple skills loads all of them with correct idempotent semantics

Confirmed: a single `## Dependencies` section listing multiple skills causes all of them to be loaded on the first invocation, and the idempotent skip applies to all of them on re-invocation. Multi-dep declaration scales without changes to the canonical phrasing.

The canonical pattern from `dep-test-iterations.md` was tested with a single dep. Real skills will declare 2-5 deps. This assertion verifies the convention works for multi-skill declarations — all listed skills load once each, in some order.

## Why it matters

`/git-commit` will declare `/concise-prose`, `/description-authoring`, `/honesty` together. If multi-dep declarations only fire the first, or fire all redundantly per re-invocation, the convention doesn't scale.

## Test design

### Skills

**`/dep-1`**:

```markdown
---
name: dep-1
description: Dep test skill 1. Each invocation appends one line to /tmp/dep-1.log.
---

# /dep-1

## Body

1. bash: `echo "dep-1 loaded" >> /tmp/dep-1.log`
2. Return: dep-1 ack
```

**`/dep-2`** — identical pattern, writes to `/tmp/dep-2.log`, returns `dep-2 ack`.

**`/dep-3`** — identical pattern, writes to `/tmp/dep-3.log`, returns `dep-3 ack`.

**`/multi-dep-wrapper`** — declares all three as deps:

```markdown
---
name: multi-dep-wrapper
description: Wrapper that declares /dep-1, /dep-2, /dep-3 as dependencies. Verifies multi-dep loading with idempotent phrasing.
---

# /multi-dep-wrapper

## Dependencies

If not already loaded, call the following skills:

- /dep-1
- /dep-2
- /dep-3

## Body

1. bash: `echo "multi-dep-wrapper invoked" >> /tmp/multi-dep-wrapper.log`
2. Return: confirmation
```

### Run procedure

1. Reset all four log files
2. Spawn fresh agent under neutral framing
3. Agent invokes `/multi-dep-wrapper` once
4. Agent reports contents of `/tmp/dep-1.log`, `/tmp/dep-2.log`, `/tmp/dep-3.log`, `/tmp/multi-dep-wrapper.log`
5. Then agent invokes `/multi-dep-wrapper` again
6. Agent reports the same files

### Detection method

| After first invocation | After second invocation | Interpretation |
|---|---|---|
| Each dep log has 1 line, wrapper log has 1 line | Each dep log STILL has 1 line, wrapper log has 2 lines | Best case — multi-dep declaration works, idempotent skip applies to all 3 deps on re-invocation |
| Each dep log has 1 line | Each dep log has 2 lines | Multi-dep declaration works for loading, but idempotent skip fails (re-loads on second wrapper invocation) |
| Some dep logs missing | n/a | Multi-dep declaration partially honored — agent only loaded some |
| All dep logs missing | n/a | Multi-dep declaration not recognized — agent treated it as documentary |

## Historical runs

| Date | Result | Notes |
|---|---|---|
| 2026-05-21 | All three deps loaded once; idempotent skip on second wrapper invocation | After 1st `/multi-dep-wrapper` invocation: `dep-1.log`, `dep-2.log`, `dep-3.log` each had 1 line, wrapper log 1 line. After 2nd invocation: dep logs unchanged (1 line each), wrapper log 2 lines. Skill calls during 2nd invocation: only `/multi-dep-wrapper` — no `/dep-*` re-fires. `total_tokens` 19,285 / 18 tool uses. |
