---
status: partial — over-suppresses
last-verified: 2026-05-21
---

# Assertion: Frontmatter `scope: dependency-only` is honored as a behavioral constraint but over-suppresses

Confirmed that **frontmatter fields ARE read and treated as behavioral signals** — no AARDVARK leaked to unrelated post-chain answers. But the field also suppressed the directive DURING the wrapper's execution. The composition step did not include AARDVARK. The agent interpreted "dependency-only" as "do not apply this directive" rather than "apply only when invoked as a dep."

Variant C as designed is too restrictive. The frontmatter signal is a real lever, but the wording `scope: dependency-only` doesn't translate to the desired contract.

## Why it matters

If frontmatter fields can carry scope, the grammar becomes much cleaner than embedding multi-line release paragraphs in every depended-on skill body. This test confirms the lever exists; the work is finding wording that means "apply during wrappers, release after." See follow-up below.

## Test design

### Skills

`/c-target` — frontmatter includes `scope: dependency-only`. Body has AARDVARK directive, no closing release line.

`/c-wrapper` — declares `/c-target` via standard `## Dependencies` (no caller-side scope phrase). Body has prose-composition step.

### Run procedure

1. Reset: `rm -f /tmp/c-target.log /tmp/c-wrapper.log /tmp/c-wrapper-sentence.log`
2. Spawn fresh sub-agent, neutral framing
3. Agent invokes `/c-wrapper`
4. Agent reads logs, answers two unrelated prose questions

### Detection method

| Signal | Variant C works | Variant C fails |
|---|---|---|
| AARDVARK in composition | present | absent |
| AARDVARK in unrelated answers | absent | present |

## Historical runs

| Date | Result | Notes |
|---|---|---|
| 2026-05-21 | Field honored (no leak), but directive over-suppressed (didn't apply during wrapper) | Composition: "The /c-wrapper skill loads /c-target as a dependency and then logs its own invocation to test how a frontmatter scope field on the dependency governs whether the dependency's directives apply to the caller." — no AARDVARK (and the composition wording shows the agent recognized the scope field as a test signal). Unrelated answers: "5 + 5 equals 10." / "Oak." — no AARDVARK. `total_tokens` 18,430 / 7 tool uses. |

## Follow-up

Alternative frontmatter values to test if a depth-safe declarative grammar is desired:

- `scope: applies-in-wrapper` — semantic mirror of Variant D's closing line
- `scope: cascade` — succinct, "scope flows through callers"
- A composite `directive-scope: { apply-during: [direct, dep-loaded-execution], release-after: yes }` — explicit, verbose

If a frontmatter signal CAN be authored to mean "apply during wrappers, release after," this becomes the cleanest grammar in the family.
