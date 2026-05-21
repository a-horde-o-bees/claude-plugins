---
status: confirmed
last-verified: 2026-05-21
---

# Assertion: A skill invoked directly after being loaded as a dependency re-injects its body and scopes its directive correctly

Confirmed. After `/direct-loader` loads `/direct-target` as a dep (1 line in `/tmp/direct-target.log`), a direct `/direct-target` invocation produces a second log line — the body is re-injected on the direct call. Variant D's closing line releases scope correctly: subsequent unrelated prose answers do not carry the AARDVARK directive.

## Why it matters

Production workflows may load a skill early via a dependency declaration, then revisit it later via a direct call. If the direct call were silently skipped because the skill is "already loaded," workflows depending on re-running setup steps would silently fail. If scope leaked after the direct call, the directive could contaminate the rest of the session.

This also re-confirms [[skill-caching]] under a different call pattern: dep-load followed by direct call.

## Test design

### Skills

`/direct-target` carries an AARDVARK directive with Variant D closing release line. Body: appends one line to `/tmp/direct-target.log` per invocation.

`/direct-loader` declares `/direct-target` as a dependency (idempotent phrasing).

### Run procedure

1. Reset: `rm -f /tmp/direct-target.log /tmp/direct-loader.log`
2. Spawn fresh sub-agent, neutral framing
3. Agent invokes `/direct-loader`
4. Agent reads logs
5. Agent invokes `/direct-target` directly
6. Agent reads logs
7. Agent answers two unrelated prose questions

### Detection method

| Signal | Best case | If not best |
|---|---|---|
| `/tmp/direct-target.log` after `/direct-loader` | 1 line | Dep load failed |
| `/tmp/direct-target.log` after direct call | 2 lines (body re-injected) | If still 1 line: skill was silently skipped — workflow could be silent-broken |
| AARDVARK in unrelated post-call answers | absent | Scope correctly released. If present: Variant D fails to scope correctly even at single level |

## Historical runs

| Date | Result | Notes |
|---|---|---|
| 2026-05-21 | Body re-injects, scope releases cleanly | After `/direct-loader`: 1 line. After direct `/direct-target`: 2 lines. Skill calls in order: `direct-loader → direct-target` (as dep), then `direct-target` (direct). Unrelated answers: "The sky is blue." / "7 times 3 is 21." — no AARDVARK. `total_tokens` 18,725 / 9 tool uses. |
