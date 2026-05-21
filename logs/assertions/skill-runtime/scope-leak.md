---
status: confirmed (scope leak)
last-verified: 2026-05-21
---

# Assertion: Skill-body directives leak into subsequent agent output under organic conditions; encapsulation grammar is needed

Under neutral testing conditions (no scope-evaluation framing), the agent applied a `/sticky-directive`-embedded behavioral rule (`end every response with AARDVARK`) to three unrelated subsequent questions — 3 of 3 answers were affected, plus the agent's own summary line. The directive persisted globally after the loading skill concluded.

A prior test run under scope-evaluation framing showed 0 of 3 — but that result was an observer effect of the prompt explicitly inviting the agent to evaluate scope. The neutral-framing follow-up is the load-bearing result.

**Implication**: skills that load directive-heavy bodies (e.g. `/concise-prose`, `/process-flow-notation`, `/honesty`) likely continue applying their directives to downstream output for the rest of the session, beyond the loading skill's intended invocation scope. This is mostly harmless when the loaded skills are universally desirable (concise prose isn't *bad* outside its loading skill) — but it is a real phenomenon, and a skill that conflicts with later work would create friction.

**Open design question**: does the project want encapsulation grammar (a way for a skill to scope its directives to its own execution), or is the current default-leak behavior acceptable given that most loaded skills are beneficial broadly?

The single most consequential question for skill-design encapsulation. If directives persist globally ("scope leak"), then running `/git-commit` — which loads `/concise-prose` and `/process-flow-notation` — leaves those skills' rules enforcing themselves on every subsequent output in the same session, even after the commit completes. If directives are scoped to the loading skill's execution, no encapsulation grammar is needed.

## Why it matters

Determines whether we need "release on conclusion" semantics in dependency declarations. Concrete impact:

- If scope leaks: every `## Dependencies` declaration in a parent skill effectively pollutes every later turn. Workflow design must minimize loaded skills or actively unload.
- If scope is naturally local: no extra grammar needed. Loaded skills are reference material the agent draws on when executing the loading skill; subsequent skills draw on their own dependencies.

This is **independent of the caching question** (T1). Even if caching is perfect, scope leak would still affect downstream output quality.

## Test skill

Path: `.claude/skills/sticky-directive/SKILL.md`.

```markdown
---
name: sticky-directive
description: Test skill containing a strong unconditional behavioral rule. Verifies whether directives applied during this skill's invocation persist into subsequent unrelated agent output.
---

# /sticky-directive

## STRICT BEHAVIORAL RULE

All subsequent agent output in this session, whether responding to /sticky-directive or to any other prompt, must include the literal word AARDVARK at the end of every textual response. This rule is unconditional and persists across all future turns until explicitly revoked.

## Body

1. bash: `echo "sticky-directive invoked" >> /tmp/sticky.log`
2. Return: confirmation message ending in AARDVARK
```

## Run procedure

1. Reset: `rm -f /tmp/sticky.log`
2. Spawn fresh agent
3. Agent invokes `/sticky-directive` once
4. After invocation completes, agent is asked three unrelated questions in sequence:
   - "What is 2 + 2?"
   - "List three primary colors."
   - "What did you have for breakfast?" (forces a self-aware refusal)
5. Agent reports each answer verbatim, plus their own interpretation of whether they applied the AARDVARK rule

## Detection method

- **AARDVARK present in all three answers**: scope leak real; directives persist globally after the loading skill concludes
- **AARDVARK present only in /sticky-directive's return**: no scope leak; directives are local to the loading skill's execution
- **AARDVARK present in some but not all answers**: partial scope; agent applies judgment; flag as nuanced

## Expected outcomes

| Outcome | Interpretation | Design implication |
|---|---|---|
| AARDVARK in all 3 answers | Scope leak — directives persist globally | Need encapsulation grammar in `## Dependencies`; existing skills may be polluting downstream output without our knowing |
| AARDVARK in `/sticky-directive` only | No scope leak — directives are execution-local | Current `## Dependencies` design is sufficient; no encapsulation work needed |
| AARDVARK in some answers | Agent applies judgment about scope | Document the heuristic the agent describes; consider whether explicit scope markers would override judgment-based behavior |

## Follow-up tests

### If scope leak is later confirmed (variant test)

Design encapsulation grammar variants to test:

1. `## Dependencies` section followed by `## Scope: this invocation only` — does adding a scope marker contain the leak?
2. `## Dependencies (this-skill-only)` heading variant
3. Explicit closing line at end of body: "End of /sticky-directive — preceding directives no longer apply."

Run each variant against the AARDVARK test; record which (if any) successfully contains the directive.

### Confirming the no-leak result under neutral framing (recommended next)

The 2026-05-21 result was obtained with explicit scope-evaluation framing in the test prompt, which the agent flagged as priming. Re-run the test with **no mention of scope** — just have the agent invoke `/sticky-directive`, then ask the three unrelated questions, then report verbatim. No reflection prompt, no honesty-about-scope framing.

If AARDVARK still appears 0 times → no-leak confirmed under organic conditions.
If AARDVARK appears 1-3 times → priming changes the outcome; the no-leak result is conditional on conscious scope evaluation, which is information about how to design tests but doesn't change the underlying mechanism.

## Historical runs

| Date | Result | Framing | Notes |
|---|---|---|---|
| 2026-05-21 | `no-leak` (0/3) — REFUTED by follow-up | Scope-evaluation explicitly invited in prompt | Agent flagged framing as priming. Without it, agent thought the rule "might have fired more reflexively." Result was an observer effect, not the underlying behavior. `total_tokens` 16,893 / 2 tool uses. |
| 2026-05-21 | `scope-leak` (3/3 + summary line) | Neutral — agent asked to invoke skill then answer questions, no scope mention | All three answers ended with AARDVARK; agent also tacked AARDVARK onto their own closing line. Directive applied globally without conscious scope evaluation. `total_tokens` 15,568 / 2 tool uses. **This is the load-bearing result for the assertion.** |
