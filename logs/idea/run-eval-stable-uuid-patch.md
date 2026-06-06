# Patch run_eval.py for stable uuid per batch

A one-line script change in Anthropic's upstream `skill-creator/scripts/run_eval.py` would unlock ~6× cost reduction on the cacheable portion of each subprocess call.

## The issue

`run_single_query()` generates a fresh `uuid.uuid4().hex[:8]` per call:

```python
unique_id = uuid.uuid4().hex[:8]
clean_name = f"{skill_name}-skill-{unique_id}"
command_file = project_commands_dir / f"{clean_name}.md"
```

The unique-named command file appears in the agent's visible skills list. Different filename per call → different prompt prefix at the skills/commands block → cache miss for that block on every call.

Measured per-call:

- `cache_read_input_tokens` ≈ 24,696 (stable base — CLAUDE.md + base system prompt + tool defs)
- `cache_creation_input_tokens` ≈ 9,576 (skills/commands list, invalidated by the uuid)
- Fresh: ~10 input + ~328 output

The 9,576-token slice gets re-cached every call at 125% input price (cache write premium) instead of read at 10% (cache read).

## The patch

Make the uuid stable within a batch. One generation per `run_eval` invocation, reused across all queries:

```python
# At top of main() or in the eval runner
batch_uuid = uuid.uuid4().hex[:8]

# In run_single_query, take batch_uuid as a param instead of generating:
def run_single_query(query, skill_name, skill_description, ..., batch_uuid):
    clean_name = f"{skill_name}-skill-{batch_uuid}"
    ...
```

Trade-off: file-write race condition under ProcessPoolExecutor parallelism. Mitigation: write the file once *before* the parallel pool spawns, and only delete after all workers complete. Adds two lines of synchronization, removes per-worker file creation.

## Cost impact (Opus pricing as proxy for quota burn)

| Approach | Cost per 60-call batch | Cost per skill (5 iterations × 60) |
|---|---|---|
| As-is (per-call uuid) | $10.80 just for Block 4 | $72 total |
| Stable uuid per batch | $1.01 for Block 4 (first call creates, rest read) | $20 total |

Across 22 skills (full project refinement loop): ~$1,600 → ~$450. Substantially better for full eval coverage.

## Status

Proposed, not implemented. Patch lives in user's project, not in upstream `anthropics/skills` — easier to maintain a local fork until we know the patched version produces equivalent results.

## When to apply

- Before running `run_loop.py` (with default 5 iterations) on more than one or two skills
- Defer if doing dry-tests only — single-query runs are cheap regardless

## Related

- [logs/decision/rules-to-skills-pivot.md](../decision/rules-to-skills-pivot.md) — set up the conditions where we need to refine many descriptions
- [logs/patterns/description-refinement-two-phase-loop.md](../patterns/description-refinement-two-phase-loop.md) — uses run_eval as the Phase 2 tool
