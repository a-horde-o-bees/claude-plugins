# Convention-gate re-delivery measurement via total token exposure

A token-based test that detects whether the convention gate hook re-delivers convention context per-file (instead of caching once per agent session) needs a different token methodology than the one we tried. The attempt is documented here so a future implementation can skip the dead end and aim at the real signal.

## What we were trying to catch

The convention gate hook fires on PreToolUse for Edit/Write. Each fire resolves `governance_match` and returns `additionalContext` containing the matching convention's text. If the hook naively delivers this text every fire, a 10-file batch edit sees the same convention in context 10 times. The agent's behavior may be fine (it reads the convention once semantically), but token cost, cache pressure, and latency all scale with redundant deliveries. A regression test should catch the shift from "delivered once" to "delivered per file."

## Methodology we tried

Four agent invocations, module-scoped fixtures:

- **baseline_single** — 1 edit against `no_match0.txt` (matches no convention glob)
- **baseline_batch** — 10 edits against `no_match{0..9}.txt`
- **single_python** — 1 edit against `file0.py` (python.md matches)
- **batch_python** — 10 edits against `file{0..9}.py`

The test subtracted baselines to isolate convention-driven cost:

```
single_marginal = single_python.input_tokens - baseline_single.input_tokens
batch_marginal  = batch_python.input_tokens  - baseline_batch.input_tokens
ratio = batch_marginal / single_marginal    # expect ~1.0 cached, ~10 per-file
```

## Observed numbers (2026-04-22)

Against a session with the convention correctly cached (hook delivers additionalContext each fire, but prompt cache collapses duplicates):

```
Baseline single:         7 tokens  $0.2866
Baseline batch:          8 tokens  $0.3971
Single +convention:     18 tokens  $0.3623  (+11 marginal)
Batch +convention:      72 tokens  $0.9663  (+64 marginal)
Raw ratio (batch/single):    4.00x
Marginal ratio:              5.82x
```

## Why the methodology failed

The `input_tokens` field in `claude -p --output-format json` reports **non-cached input tokens only**. With prompt caching enabled (default in Claude Code), the first convention delivery writes to the cache (`cache_creation_input_tokens`) and subsequent identical deliveries read from cache (`cache_read_input_tokens`). Neither shows up in `input_tokens`. So:

- If the hook delivers additionalContext 10 times with identical text: 1x `cache_creation` + 9x `cache_read`, ~0 difference in `input_tokens`
- If the hook delivers once: 1x `cache_creation`, 0x `cache_read`, ~0 difference in `input_tokens`

**Both cases look similar through `input_tokens`.** The signal we're trying to detect lives in the cache-hit path, not the new-input path. Our measurement was looking at the wrong layer.

The residual `input_tokens` we did see (11 / 64 marginal) mostly reflects per-tool-call overhead — tool result payloads, tool argument echoes, small per-turn noise — scaling with the number of Edit operations, not with convention delivery.

## What a working methodology looks like

Read the full usage envelope, not just `input_tokens`:

```python
usage = data["usage"]
total_exposure = (
    usage.get("input_tokens", 0)
    + usage.get("cache_read_input_tokens", 0)
    + usage.get("cache_creation_input_tokens", 0)
)
```

`total_exposure` represents the total context volume the model processed for the session. Per-file re-delivery would roughly multiply this by N (since each fire adds another copy to the conversation stream; cache collapses cost but not logical volume).

Compare marginals on `total_exposure` rather than `input_tokens`:

```
single_marginal_total = single_python.total_exposure - baseline_single.total_exposure
batch_marginal_total  = batch_python.total_exposure  - baseline_batch.total_exposure
ratio_total = batch_marginal_total / single_marginal_total
```

If the hook delivers once: `ratio_total ≈ 1.0` (convention appears once in total exposure regardless of file count).
If the hook delivers per-file: `ratio_total ≈ N` (convention appears N times, so marginal exposure scales).

## Alternative: assert on delivery count directly

Instead of measuring via token proxies, intercept what the hook emits. The convention gate hook's `additionalContext` responses are observable — a test harness could record hook invocations and count how many times a given convention's text appears across a session. That's a direct behavioral assertion, not a token-volume proxy.

This requires test infrastructure that captures hook output during an agent run, which we don't currently have.

## Why this matters

- Token re-delivery waste is invisible in the agent's conventions_read report (the existing `test_batch_reads_not_multiplied` test). The agent could see the same convention delivered 10 times in context and still only file-Read it once; conventions_read length stays at 1.
- Prompt-cache interactions mean cost differences are subtle but real over thousands of Edit/Write operations.
- Without a measurement, a regression to per-file delivery ships silently.

## When to pick this up

Not release-blocking. The existing `test_batch_reads_not_multiplied` and `test_batch_no_duplicate_reads` catch the agent-visible regression (convention read multiple times). What's missing is the hook-level regression (convention delivered multiple times even if agent reads once).

Consider when:
- Usage-cost regressions show up in production and we want a measurement-backed guard
- Hook instrumentation infrastructure exists that can observe additionalContext output directly
- The convention gate hook is being refactored and we want a proof-carrying test during the change

## Related

- `plugins/ocd/hooks/convention_gate.py` — the hook implementation whose caching behavior we wanted to measure
- `tests/plugins/ocd/systems/navigator/integration/test_convention_agent.py` — the agent-spawning test file that would host the measurement if revisited
- `logs/idea/Sandbox run — markdown-driven agent tests.md` — the broader markdown-driven test framework that would standardize this kind of measurement across agent tests
