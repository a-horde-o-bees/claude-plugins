# Context-Aware Iteration

Process a queue of variable-size items within an agent's context budget. Self-regulating — adapts to item size, always makes progress, and provides an exact resumption checkpoint.

## Pattern

```
1. Load queue (ordered list of items to process)
2. {checkpoint} = starting position (from previous agent or beginning)
3. For each {item} in {queue} starting from {checkpoint}:
    1. Estimate item size (read metadata or first pass)
    2. If consumed context + estimated size exceeds budget AND at least one item processed:
        1. Return to caller:
            - Completed items and their results
            - Next item ID as resumption checkpoint
            - "incomplete" status
    3. Process {item} fully
    4. Record result
    5. Update {checkpoint} to next item
4. Return to caller:
    - All completed items and their results
    - "complete" status
```

## Properties

- **Always progresses** — processes at least one item regardless of budget (guard: check `at least one item processed` before stopping)
- **Monotonic checkpoint** — everything before the checkpoint is done; everything after is pending
- **Self-regulating** — items of varying size naturally adjust batch size; dense items = fewer per batch; sparse items = more
- **Resumable** — next agent receives checkpoint, reads current state, continues from where the previous agent stopped
- **Idempotent** — if an agent crashes after processing but before returning, the next agent reads persisted state and skips completed work

## Orchestrator Workflow

```
1. Spawn agent with queue and starting checkpoint
2. Agent returns results + status
3. If status is "incomplete":
    1. Record results
    2. Spawn next agent with returned checkpoint
4. If status is "complete":
    1. Record final results
```

## Budget Estimation

Context budget depends on the agent's model and the overhead of instructions + tool calls. Practical heuristics:

- Track accumulated token count or character count of tool results consumed
- Leave room for the agent's output and final tool calls (write operations)
- Conservative: stop at 60-70% of estimated available context
- The exact threshold is less important than always processing at least one item

## Checkpoint Persistence

For workflows where the skill executor is also context-limited:

- Persist checkpoint to a file or database after each agent completes
- On skill executor restart, read checkpoint and continue
- Example: `blueprint/data/history.md` entries with "resume from entity e14" or database stage markers where `stage = 'researched'` implicitly marks completion

## When to Use

- Processing a list of entities (research, assessment, analysis)
- Crawling paginated directories
- Any sequential operation over items of unpredictable size
- Any workflow where the total work may exceed a single agent's context
