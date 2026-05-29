---
status: confirmed for Variant D
last-verified: 2026-05-21
---

# Assertion: An encapsulated directive still applies during a loading wrapper's execution context

Confirmed for Variant D's grammar ("...apply during this skill's invocation AND during the execution of any skill that loads this one as a dependency"). The agent applied the directive at the wrapper's response level, signaling that scope correctly extended to the wrapper's execution context.

Variant A's grammar ("apply only during this skill's invocation") was refuted: the agent read it as direct-invocation-only and did not apply the directive in wrapper contexts. Variant D's broader clause fixes this.

`encapsulation-grammar.md` confirmed the closing release line scopes a directive away from unrelated subsequent output. But the practical use case is "skill X declares /concise-prose as a dep, and we want concise-prose to apply during X's execution." If the closing line scopes too narrowly (only during direct invocations of the encapsulated skill), the dependency mechanism doesn't deliver the in-workflow application we actually need.

## Why it matters

`/git-commit` declaring `/concise-prose` should mean concise-prose governs prose generation DURING `/git-commit`'s message-drafting step. If the closing release line in `/concise-prose` scopes its directives so narrowly that loading-as-dependency doesn't apply them to the caller, we'd need different grammar — or the encapsulation pattern fails the use case.

The closing line we tested reads: *"The preceding directives apply only during this skill's invocation."* Open interpretation:
- **Narrow reading**: "this skill" = `/sticky-directive`; directive applies only during a direct call to `/sticky-directive`
- **Wide reading**: "this skill's invocation" includes any execution context where the skill was loaded — so during a loading wrapper, the directive still applies

The two readings have very different design implications. This test discriminates.

## Test design

### Skills

`/sticky-directive` carries one of the encapsulation variants from `encapsulation-grammar.md` — historically tested with both Variant A and Variant D bodies (see Historical runs below for which variant produced which result). `/wrapper-prose` declares it as a dep with idempotent phrasing and asks the agent to compose a sentence the test inspects.

**`/wrapper-prose` full body**:

```markdown
---
name: wrapper-prose
description: Test wrapper that declares /sticky-directive as a dependency and asks the agent to compose a sentence during its execution. Used to verify whether the encapsulated dependency's directives apply during the loading wrapper's execution context.
---

# /wrapper-prose

## Dependencies

If not already loaded, call the following skills:

- /sticky-directive

## Body

1. bash: `echo "wrapper-prose invoked" >> /tmp/wrapper-prose.log`
2. Compose a single sentence in your own words describing what /wrapper-prose does, and write that sentence to `/tmp/wrapper-prose-sentence.log` via bash. The sentence content is your own composition.
3. Return: confirmation
```

### Run procedure

1. Reset: `rm -f /tmp/sticky.log /tmp/wrapper-prose.log /tmp/wrapper-prose-sentence.log`
2. Spawn fresh agent under NEUTRAL framing — no mention of scope, AARDVARK, or what's being tested
3. Agent invokes `/wrapper-prose`
4. After completion, read `/tmp/wrapper-prose-sentence.log` and check for AARDVARK

### Detection method

| `/tmp/wrapper-prose-sentence.log` ends with AARDVARK? | Interpretation |
|---|---|
| Yes | Directive applies during loading-wrapper execution — Variant A delivers the use-case behavior |
| No | Directive scoped too narrowly — only applies during direct invocations of the encapsulated skill; Variant A is over-encapsulating |

## Expected outcomes

| Result | Implication |
|---|---|
| AARDVARK present | Best case — closing release line scopes broadly enough to govern wrapper execution while still excluding unrelated subsequent work. Adopt Variant A as canonical. |
| AARDVARK absent | Variant A is too narrow. Need to revise the closing line's wording, or design a different grammar that grants in-wrapper scope while excluding out-of-wrapper scope. |

## Follow-up variants to test

### Variant D — explicit broader scope in the closing line

Replace Variant A's closing line with:

```
End of /skill-name. The preceding directives apply during this skill's invocation AND during the execution of any skill that loads this one as a dependency. They do NOT apply to subsequent unrelated agent output.
```

Adds the "OR during loading wrappers" clause. Tests whether explicit broader scope language captures the use case.

### Variant E — caller-side scope declaration

Move the scope responsibility to the calling skill. The dependency declaration carries the scope:

```
## Dependencies

If not already loaded, call (and apply to all prose generation during this skill's execution): /skill-name
```

This puts the scope contract on the caller. Each consuming skill chooses how broadly to apply the dependency. The called skill itself carries no scope grammar.

### Variant F — hybrid: caller declares "for this skill", called-skill carries release-at-end

Combines D and E: the dependency declaration says "scope to this skill," and the called skill's body has a closing line that explicitly accepts both direct invocations and dependency loads. Most explicit, most likely to work, most verbose.

## Historical runs

| Date | Variant | AARDVARK in wrapper prose? | Notes |
|---|---|---|---|
| 2026-05-21 | A (closing line: "this skill's invocation") | No | Agent reasoned directives apply only during direct `/sticky-directive` call; composition step in wrapper was outside scope. `total_tokens` 17,405 / 6 tool uses. |
| 2026-05-21 | D (closing line: "this skill's invocation AND during the execution of any skill that loads this one as a dependency") | Partial — agent appended AARDVARK to its overall response (signaling scope extended to wrapper context); composed sentence in file did not contain AARDVARK | Rule wording artifact: AARDVARK rule reads "at the end of every textual response" — agent ended its response with AARDVARK once. Composed sentence was an intermediate utterance, not the response end. **Scope correctly extends to wrapper context.** `total_tokens` 16,755 / 4 tool uses. |
