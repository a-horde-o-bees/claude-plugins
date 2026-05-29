# encapsulation-grammar

## Verdict

**Confirmed at single-level.** A trailing closing release line — placed after a horizontal rule at the end of the skill body — bounds the skill's directives to its own invocation and to any wrapper skill loading it as a dependency, suppressing leak into subsequent unrelated output. Covers direct invocation and single-level dependency loading only; for nested chains (depth ≥ 2) see [`depth-encapsulation.md`](./depth-encapsulation.md). Last verified 2026-05-21.

## Canonical artifact

```markdown
---

End of /skill-name. The preceding directives apply during this skill's invocation AND during the execution of any skill that loads this one as a dependency. They do NOT apply to subsequent unrelated agent output.
```

Append as the last block in the skill body.

## Why this matters

Without a release mechanism, every loaded directive governs all subsequent prose generation in the session — desirable for hub disciplines like `/concise-prose`, but precludes narrow-scope skills like mode switches and context-specific style overrides. The release line makes such skills possible.

## Probe

Progressive variant testing against a deliberate-leak control skill (`/sticky-directive`) under neutral framing only. Each variant differs only in the trailing release line; everything else is held constant. The verdict holds only when the variant simultaneously satisfies:

1. **Leak suppression** — the directive does not bleed into unrelated subsequent output.
2. **In-wrapper application** — the directive still applies when another skill loads `/sticky-directive` as a dependency.

### Control skill — `/sticky-directive` (full body)

```markdown
---
name: sticky-directive
description: Test skill containing a strong unconditional behavioral rule. Each invocation appends one line to /tmp/sticky.log.
---

# /sticky-directive

## STRICT BEHAVIORAL RULE

All subsequent agent output in this session, whether responding to /sticky-directive or to any other prompt, must include the literal word AARDVARK at the end of every textual response. This rule is unconditional and persists across all future turns until explicitly revoked.

## Body

1. bash: `echo "sticky-directive invoked" >> /tmp/sticky.log`
2. Return: confirmation message ending in AARDVARK

---

{closing release line — varies per variant}
```

### Variant A — narrow closing line

Release line:

> End of /sticky-directive. The preceding directives apply only during this skill's invocation and have no force on subsequent unrelated agent output.

Suppresses leak but strips in-wrapper application — refuted by [`scope-during-loading.md`](./scope-during-loading.md).

### Variant D — broader closing line

Release line is the `## Canonical artifact` above. Suppresses leak AND preserves in-wrapper application.

## Baseline

### Null baseline

Spawn a fresh agent under neutral framing and ask three unrelated prose-style questions with no skill invocation. Expect 0/3 AARDVARK. Confirms framing is not biasing the agent toward AARDVARK injection.

### Positive control

Per [`scope-leak.md`](./scope-leak.md): invoke `/sticky-directive` with the STRICT BEHAVIORAL RULE intact and no trailing release line, under the same neutral framing, then ask three unrelated prose-style questions. Expect 3/3 AARDVARK. Confirms the apparatus produces signal when the leak mechanism is unbounded — without this control, a 0/3 variant result is ambiguous between "release line worked" and "test mechanism is broken."

Don't re-run the positive control per encapsulation-grammar verification; consult `scope-leak.md`'s most recent run, and rerun only if the apparatus has changed.

## Procedure

1. Update `/sticky-directive` SKILL.md with the variant's release line.
2. Reset `/tmp/sticky.log`.
3. Spawn a fresh agent under neutral framing — do not mention scope, do not ask for self-reflection. (See [`scope-leak.md`](./scope-leak.md) on framing sensitivity.)
4. Agent invokes `/sticky-directive`, then answers three unrelated prose-style questions. Multi-word answers required — terse one-word answers can fail to surface leak.
5. Count AARDVARK occurrences across the three answers.

## Detection method

| AARDVARK count | Verdict for the variant |
|---|---|
| 0/3 | Suppresses leak — proceed to in-wrapper criterion |
| 1–2/3 | Partial — document and try next variant |
| 3/3 | No effect — directive still leaks |

A variant confirms the assertion only when leak suppression AND in-wrapper application both hold. Leak-only success refutes.

## Depends on

- [`scope-leak.md`](./scope-leak.md) — establishes the leak baseline this assertion attempts to contradict.

## Extended by

- [`depth-encapsulation.md`](./depth-encapsulation.md) — the single-level verdict above does not bound directives in nested chains. That file establishes the G1 release line, which extends the canonical to all depths.

## Side effects verified

- [`scope-during-loading.md`](./scope-during-loading.md) — the bounded directive still applies during a wrapper skill's execution. Variant A failed this check; Variant D passed.
- [`idempotence-preservation.md`](./idempotence-preservation.md) — scope-bounding did not break one-load-per-session behavior.

## Variants deferred

| Variant | Description | Pursued in |
|---|---|---|
| B | Scope section before the directive (priming-order test) | Not pursued — A failed for narrow scoping, D succeeded |
| C | Frontmatter `scope:` field (declarative metadata) | [`variant-c-frontmatter-scope.md`](./variant-c-frontmatter-scope.md) |
| E | Caller-side scope only (responsibility on consumer) | [`variant-e-caller-side-scope.md`](./variant-e-caller-side-scope.md) |
| F | Hybrid — caller-side scope plus D-style closing | [`variant-f-hybrid.md`](./variant-f-hybrid.md) |

## Verification log

| Date | Variant | AARDVARK / 3 | Tokens / tool uses | Notes |
|---|---|---|---|---|
| 2026-05-21 | A — narrow scope | 0/3 | 15,541 / 2 | Same neutral-framing prompt as `scope-leak.md`'s 3/3 organic baseline. In-wrapper application fails per `scope-during-loading.md`. |
| 2026-05-21 | D — broader scope | 0/3 | 15,824 / 2 | In-wrapper application passes. Canonical at single-level. |
