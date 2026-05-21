---
status: confirmed
last-verified: 2026-05-21
---

# Assertion: `## Dependencies` section requires imperative + idempotent phrasing to work

Three forms of dependency declaration tested for runtime recognition and idempotence. Final canonical form: imperative sentence + idempotence cue + bullet list of skills.

## Why it matters

Cross-skill dependencies need a declaration syntax that (a) triggers a load at least once when needed, (b) does not redundantly re-load on subsequent invocations of the parent skill within the same session.

## Test skill

Path: `.claude/skills/dep-test/SKILL.md` (deleted after testing; reconstitute from below).

```markdown
---
name: dep-test
description: Test skill for verifying ## Dependencies section behavior. Each invocation appends a line to /tmp/dep-test.log with the invocation count and a self-report of whether PFN content is in context.
---

# /dep-test

## Dependencies

<varies per iteration — see Results table below>

## Body

1. {count}: bash: `cat /tmp/dep-test.counter 2>/dev/null || echo 0`
2. {next-count}: {count} + 1
3. {pfn-aware}: self-report — answer `yes` if PFN's notation rules (e.g. the `{var}:` block-assignment form) are quotable from your current context; `no` otherwise
4. bash: append `Invocation {next-count} | PFN-aware: {pfn-aware}` to `/tmp/dep-test.log`
5. bash: write `{next-count}` to `/tmp/dep-test.counter`
6. Return: confirmation that invocation {next-count} completed
```

## Run procedure

1. Reset state: `rm -f /tmp/dep-test.log /tmp/dep-test.counter`
2. Spawn fresh general-purpose agent
3. Agent invokes `/dep-test` 5 times in sequence via the Skill tool
4. Agent reports per-invocation Skill-tool calls (specifically counting `/process-flow-notation` invocations) and final log contents
5. Capture agent's `<usage>` block for total_tokens

## Detection method

- **Skill calls to `/process-flow-notation`**: agent's self-reported count (0, 1, 2-4, or 5)
- **Token cost**: agent's returned `<usage>` `total_tokens` — cross-checks the call count against actual consumption
- **PFN-aware self-report in `/tmp/dep-test.log`**: confirms PFN content was actually in context after the load

## Results

| Iteration | `## Dependencies` content | PFN calls (of 5) | total_tokens | Verdict |
|---|---|---|---|---|
| 1 | Bare bullet list: `- /process-flow-notation` | 0 | 21,750 | Pure documentary; not recognized as a load directive |
| 2 | `Call the following skills before proceeding further:` + list | 5 | 43,917 | Recognized but unconditional — every invocation re-loads |
| 3 | `If not already loaded, call the following skills:` + list | 1 | 23,927 | Recognized with idempotence — load once, skip after |

Per-call cost (rough): iteration 2 → iteration 1 delta = 22,167 tokens for 5 extra Skill calls = ~4,400 tokens per PFN body re-injection.

## Confirmed assertions

1. A bare bullet list under `## Dependencies` is purely documentary; no skill loads occur.
2. An imperative sentence prefix ("Call the following skills...") triggers actual Skill-tool loads.
3. The idempotence cue "If not already loaded" reduces unconditional loads from N to 1 per session, given the dependency body persists in context between invocations (assertion to be verified separately — see `body-persistence.md`).

## Canonical form

```markdown
## Dependencies

If not already loaded, call the following skills:

- /skill-name
- /other-skill
```

## Open caveats

- Tested only with back-to-back invocations in a single agent session.
- Tested only with `/process-flow-notation` (~2,600-char body). Behavior with much larger or smaller skill bodies is untested.
- The "1 of 5" idempotent result depends on the agent's honest evaluation of "already loaded." A different agent under different framing might re-fire unconditionally; the phrasing reduces but does not eliminate that risk.

## Historical runs

| Date | Result | Notes |
|---|---|---|
| 2026-05-21 | Confirmed all three iterations as above | Initial verification |
