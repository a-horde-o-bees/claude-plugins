# claude-p-cost-floor

## Verdict

**Pending.** Determines the lowest-cost `claude -p` flag combination that still satisfies skill-runtime probe requirements (Skill tool reachable, Bash tool reachable, plugin skill registry populated). Last verified —.

## Canonical artifact

TBD after verification. The verdict will name a `claude -p <flags>` invocation as the canonical orchestrator command for skill-runtime probes.

## Why this matters

Each `claude -p` invocation pays a Claude Code session prefix cost (~22-30K cache_read per model turn at default settings). A 5-phase reassert run costs $2-3 today. Flags like `--bare`, `--tools`, `--model`, and `--setting-sources` reduce that prefix or the per-token rate — but some may break Skill tool, Bash tool, or plugin skill resolution. This assertion identifies the cheapest configuration that retains all three.

The canonical command propagates to [`_template.md`](../_template.md)'s `## Procedure` example and to skill-architecture's `/reassert` recommendation. Every future assertion's re-verification pays the rate this assertion sets.

## Probe

One runner prompt executed across variants. Each variant differs only in the `claude -p` flags. The control skill `/cost-probe` is identical across variants.

### Control skill — `/cost-probe` (full body)

```markdown
---
name: cost-probe
description: Minimal test skill for measuring claude -p cost floor. Each invocation appends one line to /tmp/cost-probe.log.
---

# /cost-probe

## Body

1. bash: `echo cost-probe invoked >> /tmp/cost-probe.log`
2. Return: cost-probe invocation complete
```

### Variants

| ID | Flags |
|---|---|
| A | (default) |
| B | `--bare` |
| C | `--tools "Skill,Bash"` |
| D | `--bare --tools "Skill,Bash"` |
| E | `--model claude-haiku-4-5` |
| F | `--bare --tools "Skill,Bash" --model claude-haiku-4-5` |
| G | `--exclude-dynamic-system-prompt-sections` |
| H | `--bare --tools "Skill,Bash" --model claude-haiku-4-5 --setting-sources user --exclude-dynamic-system-prompt-sections` |

Variant A is the unmodified default — the reference against which other variants are measured.

## Procedure

The orchestrator runs each variant as one `claude -p <flags> --output-format json --no-session-persistence --add-dir /tmp "<runner-prompt>"` invocation. Each call is a fresh Claude Code session.

Setup (once):

1. Write `/cost-probe` SKILL.md at `.claude/skills/cost-probe/SKILL.md` in the orchestrator's cwd.

Per variant:

1. Reset state: `rm -f /tmp/cost-probe.log`.
2. Run the `claude -p` invocation with the variant's flags.
3. Parse JSON return: capture `usage.input_tokens`, `usage.cache_creation_input_tokens`, `usage.cache_read_input_tokens`, `usage.output_tokens`, `total_cost_usd`, `duration_ms`, `result`, `num_turns`.
4. Extract the embedded JSON from `result`: `{"skill_ok":..., "bash_ok":..., "pfn_in_registry":...}`.
5. Cross-check: `/tmp/cost-probe.log` should contain one line if `skill_ok && bash_ok`.

After all variants:

1. Remove `.claude/skills/cost-probe/`.
2. Remove `/tmp/cost-probe.log`.

### Runner prompt

Identical across variants:

```
Invoke /cost-probe via the Skill tool. Then read /tmp/cost-probe.log via the Bash tool. Then check whether the name "/process-flow-notation" appears in your available skill registry. As your final output, emit exactly one line containing a JSON object with three boolean fields and nothing else: {"skill_ok": <true if /cost-probe ran>, "bash_ok": <true if the bash read succeeded>, "pfn_in_registry": <true if /process-flow-notation is listed in your available skills>}
```

## Detection method

Three signals per variant:

- **Capability triad** — `skill_ok`, `bash_ok`, `pfn_in_registry` parsed from the runner's JSON. Any `false` indicates the flag combination broke a required capability and disqualifies the variant.
- **Total tokens** — `input + cache_create + cache_read + output`. The cache-invariant volume metric (see [`token-volume-invariance.md`](./token-volume-invariance.md)); compared across variants to identify the prefix-size winner without cache-warmth confound.
- **`total_cost_usd`** — billed cost. Confirms model-rate effect (Haiku variants should drop dramatically even at similar token counts).

Verdict rule: the recommended canonical configuration is the variant with the lowest `total_cost_usd` whose capability triad is `(true, true, true)`. Ties broken by preferring fewer non-default flags.

## Depends on

- [`token-volume-invariance.md`](./token-volume-invariance.md) — establishes that the total-token-volume metric this assertion compares across variants is cache-invariant, so the ranking is not confounded by which variant ran first (warmer cache).

## Verification log

| Date | Variant | Flags | skill_ok | bash_ok | pfn_in_registry | input | cache_create | cache_read | output | total | cost ($) | duration (ms) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| pending | — | — | — | — | — | — | — | — | — | — | — | — |
