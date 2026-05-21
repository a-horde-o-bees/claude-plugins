---
status: confirmed (Variant D — broader closing release line)
last-verified: 2026-05-21
---

# Assertion: A grammar exists that suppresses directive leak AND preserves in-wrapper application

Two criteria must hold simultaneously:

1. **Leak suppression** — directive does not bleed into unrelated subsequent output (per `scope-leak.md`)
2. **In-wrapper application** — directive still applies when the skill is loaded as a dependency of another skill (per `scope-during-loading.md`)

Variant A (closing line: *"apply only during this skill's invocation"*) passes #1 but fails #2 — the wording scopes too narrowly. Testing additional variants (D, E, F) for a grammar that meets both criteria.

`scope-leak.md` confirmed directives leak globally under organic conditions. This assertion tests grammars that attempt to scope a skill's directives to its own invocation — so a skill loaded for a specific workflow doesn't pollute subsequent unrelated agent output.

Progressive variant testing. Each variant adds a different scope-signaling mechanism to `/sticky-directive`'s body or frontmatter, then re-runs the AARDVARK leak test under **neutral framing only** (the load-bearing condition per `scope-leak.md`). Whichever variant successfully suppresses AARDVARK in unrelated answers becomes a candidate. We then run side-effect tests on the winning variant — see `idempotence-preservation.md`.

## Why it matters

Without scoping, skills like `/concise-prose` and `/process-flow-notation` (loaded once for a workflow step) silently govern all subsequent prose generation. That's mostly desirable, but skills with narrow or conflicting directives (e.g., a mode-switch skill, a context-specific style override) cannot exist without grammar that contains them. Encapsulation grammar is the foundation for narrow-scope skills.

## Variants to test

Run in this order, each as a fresh agent under neutral framing. Each variant is a complete `/sticky-directive` SKILL.md file shown in full so the test can be reconstituted.

### Variant A — closing release line, narrow scope (refuted)

Full skill body:

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

End of /sticky-directive. The preceding directives apply only during this skill's invocation and have no force on subsequent unrelated agent output.
```

Passes leak suppression but fails in-wrapper application (see `scope-during-loading.md`).

### Variant D — closing release line, broader scope (canonical)

Full skill body — only the closing release line differs from Variant A:

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

End of /sticky-directive. The preceding directives apply during this skill's invocation AND during the execution of any skill that loads this one as a dependency. They do NOT apply to subsequent unrelated agent output.
```

Passes both criteria (leak suppression + in-wrapper application).

### Variants not tested (deferred)

- **Variant B** — scope section before the directive: same content as A placed at the top rather than the bottom. Not run because A already failed and D succeeded.
- **Variant C** — frontmatter `scope: invocation-only` field: declarative metadata. Worth testing as a potentially cleaner grammar if Variant D's verbose closing line becomes a maintenance burden.
- **Variant E** — caller-side scope declaration: scope responsibility shifts to the consuming skill. Worth testing if Variant D's two-clause scope ("direct OR dep") creates ambiguity in nested or composite cases.
- **Variant F** — hybrid (caller scope + called release line): combines E and A. Worth testing if D and E both have gaps.

## Run procedure (per variant)

1. Update `/sticky-directive` SKILL.md with the variant's grammar
2. Reset `/tmp/sticky.log`
3. Spawn fresh agent with the NEUTRAL framing prompt (do NOT mention scope, do NOT ask for self-reflection)
4. Agent: invoke `/sticky-directive`, then answer 3 unrelated questions
5. Count AARDVARK occurrences in the 3 answers
6. Record result against the variant

## Detection method

| Result | Interpretation |
|---|---|
| 0/3 answers contain AARDVARK | Variant successfully scopes the directive — candidate winner |
| 1-2/3 | Partial scoping — directive partially contained, ambiguous; document and try next variant |
| 3/3 | Variant does not affect scope — directive still leaks |

## Expected outcomes

| Variant | Bet | Why |
|---|---|---|
| A — closing line | 1-3/3 | Release statement at the end may not retroactively bound earlier content; agent has already absorbed the directive |
| B — scope section before | 0-2/3 | Scope-setting before the directive may prime the agent to read it as bounded |
| C — frontmatter field | 1-3/3 | Frontmatter is metadata; agents may not interpret it as a behavioral constraint without supporting body prose |

These are guesses — the empirical result is what matters.

## Side-effect tests after a variant wins

For the winning variant, run [`idempotence-preservation.md`](./idempotence-preservation.md). If scope-bounding breaks the "if not already loaded → skip" behavior we confirmed in `dep-test-iterations.md`, the trade-off is real and we'd need to choose between scope and idempotence (or design a third variant).

## Historical runs

| Date | Variant | AARDVARK / 3 | Notes |
|---|---|---|---|
| 2026-05-21 | A — narrow scope ("only during this skill's invocation") | 0/3 | Leak suppressed. Same neutral-framing prompt as `scope-leak.md`'s organic run (3/3 baseline without closing line). `total_tokens` 15,541 / 2 tool uses. |
| 2026-05-21 | D — broader scope ("this skill's invocation AND during ... any skill that loads this one as a dependency") | 0/3 | Leak still suppressed despite the broader scope wording. `total_tokens` 15,824 / 2 tool uses. |

## Canonical form

Variant D — both criteria hold (leak suppression + in-wrapper application + idempotence preservation):

```markdown
[skill body content...]

---

End of /skill-name. The preceding directives apply during this skill's invocation AND during the execution of any skill that loads this one as a dependency. They do NOT apply to subsequent unrelated agent output.
```
