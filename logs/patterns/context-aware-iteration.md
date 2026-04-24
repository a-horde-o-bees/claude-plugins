# Context-Aware Iteration

Process a queue of variable-size items across sub-agent spawns when the total work exceeds a single agent's context budget. Budget discipline lives at the orchestrator — the only party that observes post-run token counts. Each spawn's actual consumption calibrates the next spawn's size. Two persistent CSVs track the queue and the calibration history so the workflow is inspectable, resumable, and extensible.

## Why this shape

Standard Claude Code sub-agents cannot be resumed — context is garbage-collected on completion. The advertised `SendMessage` continuation is gated behind experimental Agent Teams and does not apply to the standard subagent flow (see [sub-agents](https://code.claude.com/docs/en/sub-agents) / [agent teams](https://code.claude.com/docs/en/agent-teams)). Each batch is therefore a fresh spawn paying its own baseline overhead (~30–40K tokens for system prompt + tool defs + instructions).

Sub-agents also cannot observe their own token usage at any point. Only the orchestrator reads `total_tokens` when the Agent tool returns. Budget discipline must live there.

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
batch_id,spawned_at,items_count,total_measured_size,total_tokens,work_tokens,ratio,running_avg_ratio
batch_00,2026-04-24T10:15:00Z,0,0,32894,0,,
batch_01,2026-04-24T10:17:00Z,5,22431,67812,34918,1.557,1.557
```

`batch_00` is the baseline spawn (zero items) capturing overhead `B = total_tokens`. For every later batch: `work_tokens = total_tokens − B`; `ratio = work_tokens / total_measured_size`; `running_avg_ratio = Σ work_tokens / Σ total_measured_size` across all non-baseline batches, weighted by batch size.

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

> Phase N — Self-calibrating. Running average naturally weights larger
> batches more (they carry more signal per unit of size). Divergence of
> ratio_k from running_avg_ratio is a warning that input distribution
> shifted; investigate before the next spawn.

18. While pending items remain in {queue_path}:
    1. {running_avg_ratio} = Σ work_tokens / Σ total_measured_size across all non-baseline log rows
    2. {batch_capacity} = {work_budget} / {running_avg_ratio}
    3. {batch} = bin-pack pending items up to {batch_capacity}
    4. If {batch} is empty AND pending items remain: Exit to user — all remaining items oversized; flag unconsumable and stop
    5. Spawn agent with: {agent_instructions} + item list for {batch}
    6. Read total_tokens; compute work_tokens, ratio
    7. Append log row; update queue rows
    8. If |ratio − running_avg_ratio| / running_avg_ratio > 0.3: log warning; consider re-baselining

> Completion. Summarize from the queue + log. Archive or leave in place
> depending on whether the workflow may rerun.

19. Exit to user:
    - Item counts by status
    - Final running_avg_ratio and variance across batches
    - Pointer to {queue_path} and {log_path} for inspection
```

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

- **Per-agent self-budgeting.** Agents cannot observe token usage; any char-to-token heuristic inside the agent is a guess layered on a guess. Move the budget to the orchestrator, where real usage is observable.
- **Queue-order (FIFO) batching.** Wastes 15–25% of each batch's capacity when items vary in size. Bin-packing over a pre-measured table captures most of that.
- **Fresh baseline per item.** Spawning one agent per item pays ~30K overhead for ~5K of real work. Batch until amortized overhead is a small fraction of batch cost.
- **Blind parallelism.** Firing N agents in parallel before the ratio has converged risks N simultaneous bad-estimate spawns. Stabilize, then parallelize.

## See also

- [Anthropic sub-agents documentation](https://code.claude.com/docs/en/sub-agents) — why standard subagents cannot resume
- [Agent Teams (experimental)](https://code.claude.com/docs/en/agent-teams) — the gated feature for persistent-context multi-agent work
- [Managed Agents API](https://platform.claude.com/docs/en/managed-agents/sessions.md) — Claude API path for retained sessions
