# Runner key — what we can measure and how

The findings key for skill-architecture assertions: the pivotal signals a `claude -p` run exposes, the [`runner.py`](./runner.py) call that surfaces each, and the caveat that makes it trustworthy. Assertion `## Procedure` sections call the runner instead of re-deriving parsing or spilling raw streams into context.

## Quick start

```bash
# Run and summarize (compact JSON only — model, skill_calls, tool_calls, volume, cost):
uv run runner.py run "Invoke /foo via the Skill tool." --add-dir /tmp --registry-check foo

# Summarize a stream you already captured:
uv run runner.py parse run.jsonl --registry-check process-flow-notation
```

```python
import runner
p = runner.run("Invoke /foo 5 times via the Skill tool.", add_dir="/tmp", capture="run.jsonl")
p.skill_calls_matching("foo")   # ground-truth invocation count
p.volume()                      # cache-invariant token cost
p.registry_has("foo")           # was /foo even loadable?
```

## The key — how to get X

| Want | Call | Source | Caveat |
|---|---|---|---|
| Times skill X was invoked | `skill_calls_matching("X")` | `tool_use` blocks, deduped by id | suffix-aware — plugin skills are namespaced (`writing:X`); self-report is cross-check only |
| All skill invocations | `skill_calls()` | `tool_use` | — |
| All tool invocations | `tool_calls()` | `tool_use` | — |
| One tool's count (Bash, Skill…) | `tool_call_count("Bash")` | `tool_use` | — |
| Efficiency / marginal cost | `volume()`, then baseline-subtract | `result` event usage sum | **cache-invariant** — the only metric safe for cross-phase comparison; single-turn clean, multi-turn needs sample-averaging (see below) |
| Real billed dollars | `cost()` | `result.total_cost_usd` | warmth-dependent **and** client-derived — never use cross-phase |
| Raw token breakdown | `usage()` | `result` event | server-reported, authoritative |
| Is skill/command X loadable | `registry_has("X")` | `init` event `skills`+`slash_commands` | ground truth, emitted pre-turn — replaces self-report |
| Which model ran | `model()` | `init` event | confirms `--model` took effect |
| Which tools were available | `tools()` | `init` event | confirms `--tools` took effect |
| Writable scratch for the run | `run(add_dir="/tmp")` | `--add-dir` flag | `/tmp` is blocked by default; grant explicitly |

## Invariants this rests on (verified this session)

- **Token volume is cache-invariant across identical calls** — split and cost are not. → [`test-harness/token-volume-invariance.md`](./test-harness/token-volume-invariance.md)
- **The Skill tool re-injects the full body every call; no harness cache.** Token volume scales with call count. → [`skill-runtime/skill-caching.md`](./skill-runtime/skill-caching.md)
- **Usage is server-reported and aggregates in the `result` event.** Never sum per-turn `usage` blocks — consecutive stream events repeat a turn's snapshot.
- **`tool_use` ids are unique per call.** Dedup-by-id is a no-op today, kept as insurance against stream replay.
- **`--add-dir` and `--tools` are variadic** — they swallow a positional prompt as another value. `runner.py` passes the prompt via stdin to sidestep this; don't append the prompt as an arg after a variadic flag.

## Multi-turn caveat

`volume()` is invariant to cache warmth but **not** to turn count. A multi-turn workflow accumulates `cache_read` across turns, so its volume grows with however many turns the model took — and turn count varies run-to-run from model nondeterminism. For multi-turn probes, sample-average the volume, or isolate the mechanism under test in a single-turn call. Call counts (`skill_calls`) are unaffected — they are exact regardless of turn count.

## Adding a measurement

When a new assertion needs a signal not in the table, add the extraction to `runner.py` as a `Probe` method, validate it against a captured stream, then add a row here. The runner is the single place parsing lives; this key is the single place "how to get X" lives.
