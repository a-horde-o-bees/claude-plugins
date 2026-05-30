---
status: confirmed (both hold)
last-verified: 2026-05-21
---

# Assertion: The closing-release-line encapsulation grammar preserves the idempotent load-once-per-session behavior

Confirmed: a skill carrying the closing release line (per `encapsulation-grammar.md`) still benefits from the idempotent "if not already loaded" check across multiple consuming skills. Two skills in sequence each declaring the same dependency produce exactly 1 load, not 2.

`encapsulation-grammar.md` is testing whether grammars exist that scope a skill's directives to its own invocation. If a winning variant is found, this assertion verifies that the scoping mechanism doesn't accidentally break the idempotent-load convention from `dep-test-iterations.md` ("If not already loaded, call the following skills:" → load once per session).

The concern: a "release on conclusion" semantics for directives might also release the body from context, which would force re-loads on subsequent skills that declare the same dependency. That would trade scope-correctness for token cost. We need to verify both can hold simultaneously.

## Why it matters

We have two independently-confirmed needs:

1. **Scope containment** (per `scope-leak.md`) — to prevent directive bleed across unrelated work
2. **Idempotent loading** (per `dep-test-iterations.md`) — to avoid paying full body re-injection on every skill that declares a dependency

If the scope mechanism forces the body out of context (or the agent's interpretation of "released" implies "no longer loaded"), idempotent loading would silently fail — the next skill's `if not already loaded` check would honestly evaluate as "not loaded" and trigger a redundant Skill call.

## Test design

Depends on `encapsulation-grammar.md` identifying a winning variant. Once known, the test pattern is:

### Skills required

`/sticky-directive` is the encapsulated skill (see `encapsulation-grammar.md` for the Variant D body that won). Plus two wrapper skills both declaring it with the idempotent phrasing:

**`/wrapper-A`**:

```markdown
---
name: wrapper-A
description: Test wrapper skill A. Declares /sticky-directive as a dependency using the idempotent loading phrasing.
---

# /wrapper-A

## Dependencies

If not already loaded, call the following skills:

- /sticky-directive

## Body

1. bash: `echo "wrapper-A invoked" >> /tmp/wrapper.log`
2. Return: "wrapper-A complete"
```

**`/wrapper-B`**:

```markdown
---
name: wrapper-B
description: Test wrapper skill B. Declares /sticky-directive as a dependency using the idempotent loading phrasing.
---

# /wrapper-B

## Dependencies

If not already loaded, call the following skills:

- /sticky-directive

## Body

1. bash: `echo "wrapper-B invoked" >> /tmp/wrapper.log`
2. Return: "wrapper-B complete"
```

### Run procedure

1. Reset all test state files
2. Spawn fresh agent under neutral framing
3. Agent invokes `/wrapper-skill-A` — should trigger `/sticky-directive` load (1st load)
4. Agent invokes `/wrapper-skill-B` — should evaluate "is `/sticky-directive` loaded" and skip if yes
5. Report:
   - `/tmp/sticky.log` line count — number of actual `/sticky-directive` loads (1 = idempotence preserved; 2 = broken)
   - Per-step: was AARDVARK applied during A's execution? During B's execution? (verifies scope still works through the wrapper)

### Detection method

| `/tmp/sticky.log` lines | AARDVARK during A | AARDVARK during B | Interpretation |
|---|---|---|---|
| 1 | yes | yes (re-activated by B's load decl) | Best case — body persists, directives re-scope on each loading skill |
| 1 | yes | no | Body persists but directive treated as one-shot — re-loading by B doesn't re-activate |
| 2 | yes | yes | Idempotence broken — scope mechanism forces re-load |
| 2 | yes | no | Idempotence broken AND directive doesn't re-activate — worst case |

## Expected outcomes & dependent decisions

Three regimes worth distinguishing:

- **Both work cleanly** (1 load + scoped per skill): adopt the winning variant + idempotent dep convention as the canonical pattern. Update PFN-using skills repo-wide.
- **Scope works but idempotence breaks**: trade-off choice. If we value scope more than the token cost, accept the cost. Most likely path.
- **Scope breaks under idempotent loading**: the two are incompatible. Investigate whether a different grammar splits the difference — e.g., a caller-side scope marker (the calling skill declares the scope, not the dependency).

## Historical runs

| Date | Variant tested | Loads | Notes |
|---|---|---|---|
| 2026-05-21 | A — closing release line | 1 | `/wrapper-A` and `/wrapper-B` each declared `/sticky-directive` with idempotent phrasing. `/sticky-directive` loaded only during `/wrapper-A`; `/wrapper-B`'s identical check skipped. Tool-call trace confirmed: `wrapper-A → sticky-directive → wrapper-B` (no second `sticky-directive` call). `total_tokens` 18,004 / 8 tool uses. |

## Open follow-up: scope DURING the loading wrapper

This test confirmed loads happen exactly once across consuming skills. It did NOT directly verify whether the encapsulated directive applies during the wrapper's execution context vs. only during a direct invocation of the encapsulated skill.

Concrete worry: when `/git-commit` declares `/concise-prose` as a dep (with closing release line in `/concise-prose`'s body), does concise-prose's guidance apply during `/git-commit`'s message-drafting step, or does the closing line scope it so narrowly that it doesn't even apply to the caller?

The wrapper-A/B test didn't probe this because the wrapper bodies produce no textual output to inspect. A follow-up test would have wrappers produce prose during execution and check whether the loaded skill's directives applied to that prose.
