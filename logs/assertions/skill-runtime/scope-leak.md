---
status: pending
last-verified: never
depends-on: []
---

# Assertion: Do skill directives apply globally after invocation, or only during the loading skill's execution?

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

## Follow-up tests if scope leak confirmed

Design encapsulation grammar variants to test:

1. `## Dependencies` section followed by `## Scope: this invocation only` — does adding a scope marker contain the leak?
2. `## Dependencies (this-skill-only)` heading variant
3. Explicit closing line at end of body: "End of /sticky-directive — preceding directives no longer apply."

Run each variant against the AARDVARK test; record which (if any) successfully contains the directive.

## Historical runs

| Date | Result | Notes |
|---|---|---|
| — | — | Not yet run |
