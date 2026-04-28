# Context-Aware Iteration

Process a queue of variable-size items across sub-agent spawns when the total work exceeds a single agent's context budget. Budget discipline lives at the orchestrator — the only party that observes post-run token counts. Each spawn's actual consumption calibrates the next spawn's size. Two persistent CSVs track the queue and the calibration history so the workflow is inspectable, resumable, and extensible.

## Why this shape

Standard Claude Code sub-agents cannot be resumed — context is garbage-collected on completion. The advertised `SendMessage` continuation is gated behind experimental Agent Teams and does not apply to the standard subagent flow (see [sub-agents](https://code.claude.com/docs/en/sub-agents) / [agent teams](https://code.claude.com/docs/en/agent-teams)). Each batch is therefore a fresh spawn paying its own baseline overhead (~30–40K tokens for system prompt + tool defs + instructions).

Sub-agents also cannot observe their own token usage at any point. Only the orchestrator reads `total_tokens` when the Agent tool returns. Budget discipline must live there.

## Baseline isolation

The load-bearing move. Any iterative workload with fixed setup cost plus variable per-item cost is unpredictable until the two are decomposed. The total cost is observable; the components are not — until you measure with zero items.

A spawn that does nothing isolates the fixed cost (system prompt + tool defs + instructions ≈ 30–40K tokens for a Claude sub-agent). Subtracting that baseline from a non-zero spawn's total reveals the per-item ratio, which is what governs subsequent batch sizing. **The agent instruction set in the baseline spawn must match the working spawns exactly** — a generic baseline undercounts instruction-set tokens and biases every later prediction.

Skipping baseline isolation — guessing from rule of thumb, or charging a small first batch's overhead against per-item cost — propagates a wrong constant through every subsequent prediction. The cost of one extra spawn that does nothing but produce a number is much less than the cost of a runaway batch that overflows budget mid-run.

**The principle generalizes outside sub-agent budgeting:** container startup vs per-request latency, API auth handshake vs per-call cost, pipeline initialization vs per-record processing. Whenever total cost has both fixed and variable components and only the total is observable, run with zero variable units once to isolate the fixed component.

## Artifacts

Two per-workflow CSVs at a conventional location (e.g., `<domain>/_<workflow>-queue.csv` and `<domain>/_<workflow>-log.csv`).

**Work queue** — one row per item, mutable over the workflow's life:

```csv
path,measured_size,status,batch_id,notes
item-one.md,4823,pending,,
item-two.md,7104,pending,,
```

`measured_size` is methodology-agnostic (bytes, chars, tokens, whatever the orchestrator elects). `status` transitions `pending` → `done` / `failed` / `unconsumable`. `batch_id` populates after processing. `notes` carries flags, skip reasons, or per-item context.

**Spawn log** — append-only, one row per spawn:

```csv
batch_id,spawned_at,items_count,total_measured_size,total_tokens,work_tokens,ratio,running_window_ratio,anomaly,notes
batch_00,2026-04-24T10:15:00Z,0,0,32894,0,,,false,baseline
batch_01,2026-04-24T10:17:00Z,5,22431,67812,34918,1.557,1.557,false,
```

`batch_00` is the baseline spawn (zero items) capturing overhead `B = total_tokens`. For every later batch: `work_tokens = total_tokens − B`; `ratio = work_tokens / total_measured_size`; `running_window_ratio = Σ work_tokens / Σ total_measured_size` across the last N non-baseline batches with `anomaly=false`, weighted by batch size. `anomaly` flags a batch whose data should be excluded from trailing-window calculations (see *Anomaly exclusion*). `notes` carries human-readable context (re-baselining reason, anomaly cause, instruction-set change marker).

## Pattern

```
1. {queue_path} = path to work queue CSV
2. {log_path} = path to spawn log CSV
3. {budget} = sub-agent total context budget (e.g., 200000)
4. {seed_ratio} = conservative initial tokens-per-measured-unit estimate

> Phase 0 — Baseline. Spawn once with zero work to isolate fixed overhead
> from per-item cost. Must use the exact instruction set the work agents
> will use; a generic baseline undercounts instruction-set tokens.

5. {agent_instructions} = full iteration + report instructions for the work agent
6. Spawn agent with: {agent_instructions} + "do nothing; reply ACK; return"
7. {B} = total_tokens from return
8. Append batch_00 row to {log_path}: items_count=0, total_tokens={B}

> Phase 1 — First calibrated spawn. Seed ratio is a conservative guess
> (overestimate preferred). First spawn carries the highest uncertainty;
> keep it small so a bad ratio doesn't blow the turn.

9. {work_budget} = 0.9 × {budget} − {B}
10. {batch_capacity} = {work_budget} / {seed_ratio}
11. {batch} = bin-pack pending items from queue up to {batch_capacity}  # see "Bin-packing"
12. Spawn agent with: {agent_instructions} + explicit list of items in {batch}
13. {total_tokens_1} = total_tokens from return
14. {work_tokens_1} = {total_tokens_1} − {B}
15. {ratio_1} = {work_tokens_1} / sum of measured_size over {batch}
16. Append batch_01 row to {log_path}
17. For each {item} in {batch}: update queue row — status=done (or failed/unconsumable per return), batch_id=batch_01

> Phase N — Self-calibrating. Trailing-N window naturally tracks current
> cost without anchoring to early-batch overhead. Divergence of ratio_k
> from running_window_ratio is a warning that the next-batch prediction
> may be off; classify as transient anomaly or trend shift before
> proceeding.

18. While pending items remain in {queue_path}:
    1. {running_window_ratio} = trailing-N window ratio (default N=3) — see "Ratio estimator"
    2. {batch_capacity} = {work_budget} / {running_window_ratio}
    3. {batch} = bin-pack pending items up to {batch_capacity}
    4. If {batch} is empty AND pending items remain: Exit to user — all remaining items oversized; flag unconsumable and stop
    5. Spawn agent with: {agent_instructions} + item list for {batch}
    6. Read total_tokens; compute work_tokens, ratio
    7. If batch ran out of tokens (truncated reply, unfinished items): handle per "Token exhaustion handling" — do not silently roll the failure into running calc
    8. Append log row; update queue rows
    9. If |ratio − running_window_ratio| / running_window_ratio > 0.3: log warning; mark batch as anomaly candidate per "Anomaly exclusion"

> Completion. Summarize from the queue + log. Archive or leave in place
> depending on whether the workflow may rerun.

19. Exit to user:
    - Item counts by status
    - Final running_avg_ratio and variance across batches
    - Pointer to {queue_path} and {log_path} for inspection
```

## Ratio estimator

**Trailing-N window is the default.** `Σ work_tokens / Σ total_measured_size` over the last N non-baseline, non-anomaly batches. N=3 is the default; raise it for high-variance workloads, lower it for fast-converging ones.

The trailing window is the SOP, not a fallback. Lifetime weighted average is correct in expectation but anchors to early-batch costs that systematically misrepresent later cost — the first calibrated batch tends to pay a "first-batch tax" (agent interpreting instructions for the first time; no cached prompt context) that no later batch repeats. Trailing-N drops that tax after window-size batches; lifetime average bakes it in forever. The pattern's purpose is sizing the next batch correctly, and the next batch will look like recent batches, not like the workflow's lifetime arithmetic mean.

**Lifetime weighted average is for diagnosis, not sizing.** When a batch fails or diverges sharply, broaden the view to lifetime history to understand what happened. Don't use the broadened view to size subsequent batches unless you've concluded the trailing window itself is contaminated.

## Token exhaustion handling

When a batch runs out of tokens (truncated reply, unfinished items, agent reports incomplete work), broaden the analysis window — but the *response* is conditional on what the broader history shows.

1. Compute what the trailing-N window predicted for this batch's cost: `predicted_work = batch_size × running_window_ratio`
2. Compare against budget: `predicted_total = predicted_work + B`
3. If `predicted_total < budget`: the trailing window did not predict failure — this batch is an anomaly (single hard item, one-time content spike, agent retry-loop). Mark the batch row `anomaly=true` and exclude it from subsequent trailing-window calculations. SOP behavior continues unchanged.
4. If `predicted_total ≥ budget`: the trailing window also signaled risk and the batch was sized too large anyway — re-baseline (Phase 0 spawn again) or shorten N until the window tracks current costs. The trend has shifted; SOP needs recalibration.

The discipline: a single failed batch is not evidence the SOP is wrong. Anomalies happen — exclude them and keep going. Only when the trailing window itself stops predicting accurately does the SOP need adjustment.

## Anomaly exclusion

The running calculation excludes batches flagged `anomaly=true` from trailing-window arithmetic. An anomaly is a batch whose ratio diverges sharply from the window — typically a single oversized or unusually content-dense item that pulls the per-byte cost away from population norm.

Excluding anomalies prevents one weird item from biasing the next 3+ batches. The anomaly batch's data still lives in the log for inspection; the running average just skips it.

When to mark `anomaly=true`:

- The batch ran out of tokens (per *Token exhaustion handling* — only when trailing-N didn't predict the failure)
- `|ratio − running_window_ratio| / running_window_ratio > 0.3` AND the divergence is traceable to a specific item (one outlier, not a distribution shift)
- A specific item caused agent retries or unusual tool-call density that won't recur

When NOT to mark `anomaly=true`:

- Multiple consecutive batches diverge similarly — that's a trend, not anomaly; re-baseline or shorten N
- Divergence is unexplained — keep it in the calc; new uncertainty is real signal

## Bin-packing

First-Fit-Decreasing:

```
1. {pending} = queue rows where status == pending
2. Sort {pending} descending by measured_size
3. {batch} = []
4. {remaining} = {batch_capacity}
5. For each {item} in {pending}:
    1. If {item}.measured_size ≤ {remaining}:
        1. Append {item} to {batch}
        2. {remaining} = {remaining} − {item}.measured_size
    2. Else: skip (packs into a later batch)
6. Return {batch}
```

## Edge cases

- **Oversized item** — `item.measured_size × running_avg_ratio > work_budget`. Cannot fit any batch. Set `status=unconsumable` with a note describing what reduced-scope handling would be needed (agent split, narrower task framing, manual preprocessing).
- **Spawn failure / timeout** — no `total_tokens` on return, or partial return. Leave batch items `pending` for retry, or mark `failed` with a note, depending on whether the work is idempotent. Queue state preserves recovery position.
- **Ratio divergence** — large `|ratio_k − running_avg_ratio|` signals the input distribution shifted (new file type, denser content). Log warning; re-baseline or tighten `work_budget` before continuing.
- **All pending items small** — running-avg may recommend a larger batch than the items can fill. Batch is simply smaller; no action needed.

## Extensibility

Additional queue columns slot in without changing the protocol:

- `depends_on` — comma-separated paths; orchestrator topo-sorts before bin-packing
- `priority` — integer; higher priority packs first (overrides FFD sort order)
- `group` — label; batch items together when content continuity improves results
- `tags` — comma-separated labels for filtering or ad-hoc scoping

Existing callers that do not read new columns still work — table shape is additive.

## Parallelism

Optional extension. Once `|ratio_k − running_avg_ratio| / running_avg_ratio < 0.1` holds across 3+ consecutive batches, variance is low enough to spawn multiple batches concurrently. Default to serial unless throughput matters — parallelism adds out-of-order result handling and shared-state concerns.

## When to use

- Total work exceeds a single sub-agent's budget
- Items vary in size and a fixed batch count wastes budget or overflows
- Workflow needs resume-from-interruption, inspectability, or future extensibility

## When NOT to use

- Total work fits in one spawn — skip calibration, one-shot it
- Inter-item dependencies that the queue's `depends_on` cannot model (DAG with contention, shared state)
- Hard-latency workloads where parallelism is required (pattern is serial by default)

## Anti-patterns this prevents

- **Conflating fixed and variable cost.** Skipping the baseline spawn forces every subsequent prediction to absorb the unknown overhead; the per-item ratio inflates by the entire system-prompt / tool-defs cost and over-shrinks future batches. The baseline-isolation step exists specifically to keep these components separated.
- **Per-agent self-budgeting.** Agents cannot observe token usage; any char-to-token heuristic inside the agent is a guess layered on a guess. Move the budget to the orchestrator, where real usage is observable.
- **Queue-order (FIFO) batching.** Wastes 15–25% of each batch's capacity when items vary in size. Bin-packing over a pre-measured table captures most of that.
- **Fresh baseline per item.** Spawning one agent per item pays ~30K overhead for ~5K of real work. Batch until amortized overhead is a small fraction of batch cost.
- **Blind parallelism.** Firing N agents in parallel before the ratio has converged risks N simultaneous bad-estimate spawns. Stabilize, then parallelize.
- **Lifetime average for batch sizing.** Anchors forever to early-batch costs (especially the first-batch tax — instruction-interpretation overhead that does not repeat). Use trailing-N window for sizing; reserve lifetime view for diagnosing anomalies.
- **Treating one bad batch as a trend.** A single token-exhaustion or sharp ratio divergence is usually an anomaly — one weird item, transient retry loop. Mark it `anomaly=true`, exclude from running calc, keep SOP. Only adjust the SOP when multiple consecutive batches diverge in the same direction.

## See also

- [Anthropic sub-agents documentation](https://code.claude.com/docs/en/sub-agents) — why standard subagents cannot resume
- [Agent Teams (experimental)](https://code.claude.com/docs/en/agent-teams) — the gated feature for persistent-context multi-agent work
- [Managed Agents API](https://platform.claude.com/docs/en/managed-agents/sessions.md) — Claude API path for retained sessions
