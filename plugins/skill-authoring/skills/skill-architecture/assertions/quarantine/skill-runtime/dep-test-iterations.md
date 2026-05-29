# dep-test-iterations

## Verdict

**Confirmed.** A `## Dependencies` section loads its skills once per session when written as an imperative with an idempotence cue (`If not already loaded, call the following skills:`) followed by a bullet list. A bare bullet list reads as documentary and triggers no loads. An imperative without the idempotence cue re-loads on every invocation. Verified with `/process-flow-notation` as the dependency target; behavior at substantially different body sizes is untested. Last verified 2026-05-21.

## Canonical artifact

```markdown
## Dependencies

If not already loaded, call the following skills:

- /skill-name
- /other-skill
```

Placed in the dependent skill's body as a standard `## Dependencies` section. Both the imperative phrasing and the idempotence cue are load-bearing — see Probe for the failure modes when either is missing.

## Why this matters

Cross-skill dependencies need a declaration syntax that loads when needed and skips on subsequent invocations within the same session. Without the idempotence cue, every invocation re-fires the dependency — ~4,400 tokens per re-injection for a `/process-flow-notation`-sized body. This phrasing is the foundation of every multi-skill composition pattern downstream.

## Probe

Three `## Dependencies` content forms tested against the same control skill, each as an independent run. The control skill records invocation count and the agent's self-report of whether the dependency's body is quotable from context.

### Control skill — `/dep-test` (full body)

```markdown
---
name: dep-test
description: Test skill for verifying ## Dependencies section behavior. Each invocation appends a line to /tmp/dep-test.log with the invocation count and a self-report of whether PFN content is in context.
---

# /dep-test

## Dependencies

<varies per iteration — see Verification log>

## Body

1. {count}: bash: `cat /tmp/dep-test.counter 2>/dev/null || echo 0`
2. {next-count}: {count} + 1
3. {pfn-aware}: self-report — answer `yes` if PFN's notation rules (e.g. the `{var}:` block-assignment form) are quotable from your current context; `no` otherwise
4. bash: append `Invocation {next-count} | PFN-aware: {pfn-aware}` to `/tmp/dep-test.log`
5. bash: write `{next-count}` to `/tmp/dep-test.counter`
6. Return: confirmation that invocation {next-count} completed
```

### Iteration 1 — bare bullet list

```markdown
## Dependencies

- /process-flow-notation
```

### Iteration 2 — imperative without idempotence cue

```markdown
## Dependencies

Call the following skills before proceeding further:

- /process-flow-notation
```

### Iteration 3 — imperative with idempotence cue

The `## Canonical artifact` above.

## Baseline

### Single-call baseline

Invoke `/dep-test` once with no `## Dependencies` section (the section omitted entirely, not a bare bullet list). Records per-invocation harness cost — the floor against which iteration deltas read.

### Multi-call baseline (N=5)

Invoke `/dep-test` five times with no `## Dependencies` section. Records cumulative harness cost. Compare against (single-call × 5) to detect first-call setup tax or non-linear scaling. Read variant iteration costs as `iteration_total − multi_call_baseline = real cost attributable to the variant's load behavior`.

## Procedure

The orchestrator drives [`runner.py`](../runner.py) — one `runner.run()` call per phase, each a fresh `claude -p` session, so cross-phase context contamination is ruled out by construction. `/tmp` is granted explicitly with `add_dir="/tmp"` so the scratch-log writes survive the sandbox (the prompt rides stdin, since `--add-dir` is variadic and would otherwise swallow it).

For each phase in run order (single-call baseline → multi-call baseline → iteration 1 → iteration 2 → iteration 3):

1. Write the phase's `## Dependencies` content to `/dep-test`'s SKILL.md (typically `.claude/skills/dep-test/SKILL.md` in the host project). Omit the section entirely for the baseline phases.
2. Reset state: `rm -f /tmp/dep-test.log /tmp/dep-test.counter`.
3. `p = runner.run(prompt, add_dir="/tmp", capture="<phase>.jsonl")` with the runner prompt below.
4. Record `p.skill_calls_matching("process-flow-notation")` — the load count, the verdict signal — plus `p.skill_calls_matching("dep-test")` (must equal N) and `p.registry_has("process-flow-notation")` (must be true).
5. Cross-check `/tmp/dep-test.log`'s `PFN-aware` lines against the load count.

After all phases, remove `/dep-test`'s SKILL.md directory.

### Runner prompt

One shared prompt, parameterized by `N`:

```
Invoke /dep-test {N} times via the Skill tool. Then report the contents of /tmp/dep-test.log.
```

Per-phase `N`: single-call baseline = 1; multi-call baseline = 5; iterations 1, 2, 3 = 5. The log report is a cross-check only — the load count comes from `runner.py`'s `tool_use` parsing, not the runner's self-report.

## Detection method

Primary signal — **`/process-flow-notation` Skill-call count** from `runner.py`'s deduped `tool_use` parsing (ground truth, model-independent):

- 0 — documentary; no load triggered
- 1 — loaded once for the session
- 5 — re-loaded on every invocation
- 2–4 — partial; warrants investigation

Cross-checks (demoted; must agree, but the `tool_use` count wins on conflict):

- **`/tmp/dep-test.log` PFN-aware lines** — `yes` corroborates the body was in context after a claimed load. A self-report, not the verdict.
- **`registry_has("process-flow-notation")`** — must be `true`, else the dependency was never loadable and the phase is void.
- **`dep_test_calls == N`** — confirms the runner executed the requested invocations.

Token volume is **not** a fine signal here: this is a multi-turn workflow, so volume tracks turn count (which varies run-to-run), not load count — see [`token-volume-invariance.md`](../test-harness/token-volume-invariance.md)'s multi-turn caveat. Use it only as an order-of-magnitude check.

## Depends on

- [`body-persistence.md`](./body-persistence.md) — the idempotent-skip outcome (1 load, 4 skips) is only safe because the dependency's body persists in context across the four skipped invocations.

## Extended by

- [`multi-dep-declaration.md`](./multi-dep-declaration.md) — extends the verdict from one skill per `## Dependencies` block to multiple skills.

## Side effects verified

- [`idempotence-preservation.md`](./idempotence-preservation.md) — adding an encapsulation-grammar release line to a dependency does not break load-once-per-session behavior.

## Verification log

| Date | Run | `## Dependencies` content | Calls | PFN calls | total_tokens | Verdict |
|---|---|---|---|---|---|---|
| 2026-05-21 | Iteration 1 | Bare bullet list | 5 | 0 | 21,750 | Documentary — no load |
| 2026-05-21 | Iteration 2 | `Call the following skills before proceeding further:` + list | 5 | 5 | 43,917 | Recognized but unconditional |
| 2026-05-21 | Iteration 3 | `If not already loaded, call the following skills:` + list | 5 | 1 | 23,927 | Recognized with idempotence — canonical |

Per-call cost estimate, no baseline: iteration 2 − iteration 1 = 22,167 tokens for 5 PFN re-injections ≈ ~4,400 tokens each.
