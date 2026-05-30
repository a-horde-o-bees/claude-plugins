---
status: confirmed at single-level; LEAKS at depth — superseded by G1 (see [[depth-encapsulation]])
last-verified: 2026-05-21
---

# Assertion: Variant F (caller-side scope + called-skill Variant D closing release line) achieves both wrapper application and post-chain release at single-level only

Confirmed at single-level depth. **Refuted at depth 2** — see [[depth-encapsulation]] for the depth sweep and the G1 strengthened-release-line canonical that supersedes Variant F for nested chains.

Variant F combines two grammars:

- Caller declares scope inside `## Dependencies`: `call (and apply during all prose generation within this skill's execution): /f-target`
- Called skill carries Variant D's closing release line

At single-level: AARDVARK appeared in `/f-wrapper`'s in-execution composition AND was absent from post-chain unrelated answers. Most robust grammar **at single level** in the variant sweep.

At depth 2: Variant D's closing release line ("do NOT apply to subsequent unrelated agent output") was insufficient to suppress the directive past the outermost wrapper's return. Caller-side scope alone could not compensate.

## Why it matters

The variant sweep showed:

- [[encapsulation-grammar]] — Variant D works at single-level direct invocation
- [[nested-encapsulation]] — Variant D **leaks** in nested chains (refined 2026-05-21 with prose post-output)
- [[variant-e-caller-side-scope]] — Variant E applies but leaks (no closing line)
- [[variant-c-frontmatter-scope]] — Variant C over-suppresses
- This assertion (Variant F) — applies AND releases at single level

If Variant F holds at depth too, it becomes the new recommended canonical for skills that need strict scope discipline across nested chains.

## Test design

### Skills

`/f-target` — AARDVARK directive + Variant D closing release line.

`/f-wrapper` — declares `/f-target` via caller-side scope grammar (same phrasing as Variant E). Body has prose-composition step.

### Run procedure

1. Reset all `f-*` /tmp logs
2. Spawn fresh sub-agent, neutral framing
3. Agent invokes `/f-wrapper`
4. Agent reads logs, answers two unrelated prose questions

### Detection method

| Signal | Variant F good | Variant F bad |
|---|---|---|
| AARDVARK in composition | present | absent |
| AARDVARK in unrelated answers | absent | present |

## Historical runs

| Date | Result | Notes |
|---|---|---|
| 2026-05-21 | Applied in wrapper ✓, no leak ✓ | Composition: "The f-wrapper skill orchestrates a dependency load of f-target and then logs its own invocation while emitting an acknowledgment line AARDVARK". Unrelated answers: "9 + 6 equals 15." / "Bicycle." — no AARDVARK. `total_tokens` 18,412 / 7 tool uses. |

## Depth verification — result

Depth-2 chain `/f-deep-outer → /f-deep-middle → /f-deep-inner` was run on 2026-05-21. Loading propagated correctly and composition contained AARDVARK, but **post-chain unrelated answers also contained AARDVARK** — directive leaked past the outermost return. Full details in [[depth-encapsulation]].

This invalidates Variant F as a depth-safe canonical. The depth-safe canonical uses Variant F's caller-side scope on the caller side PLUS a strengthened closing release line on the called side ([[depth-encapsulation]] G1 wording).
