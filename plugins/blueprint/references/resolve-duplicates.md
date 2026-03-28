# Resolve Duplicates

Agent subprocess — resolves all duplicate groups in research database sequentially.

## File Map

### Dependencies

```
${CLAUDE_PLUGIN_ROOT}/references/reconcile-entity.md
${CLAUDE_PLUGIN_ROOT}/run.py skills.research.scripts.research_cli
```

## Input

Orchestrator provides:
- Database path (e.g., `references/research.db`)

## Agent Workflow

Process all duplicate groups sequentially. For each group, fetch context, make merge decisions, and reconcile combined data.

### Discover Groups

1. Run `find-duplicates --db PATH`
2. Parse output into groups — each group lists entity IDs and detection evidence (URL overlap, source-data key match)
3. If no duplicates found: Exit to user — report "No duplicates detected"
4. For each {group} in {duplicate-groups}: dispatch Evaluate Group through Report Group

### Evaluate Group

5. For each {entity-id} in {group}:
    1. Run `get entity {entity-id} --db PATH`
6. If group members are not true duplicates (e.g., forks with divergent purposes, same tool used differently):
    1. Report recommendation to skip with reasoning
    2. Continue next {group}

### Merge

7. Run `merge entities --ids ID1,ID2,... --db PATH`
    - Lowest ID becomes survivor automatically
    - Moves URLs, provenance, source data, notes to survivor
    - Appends notes and descriptions to survivor
    - Clears relevance to NULL (agent reassesses)
    - Wipes measures on survivor (stale after merge)
    - Sets survivor stage to `merged` (signals unreconciled data)
    - Deletes absorbed entities

`merge entities` is fully mechanical — all data preserved on survivor. `merged` stage signals reconciliation needed. If process interrupted after merge but before reconciliation, `get entities --stage merged --db PATH` finds entities needing cleanup.

### Reconcile

After merge, survivor has combined notes and descriptions from all group members (including duplicates and potential contradictions). Read survivor full state and produce clean, reconciled version.

8. Read survivor: `get entity SURVIVOR --db PATH`
9. Apply Entity Reconciliation Procedure (from `${CLAUDE_PLUGIN_ROOT}/references/reconcile-entity.md`) to notes, description, and relevance
10. When two or more notes address the same fact (e.g., both describe the same feature or record the same metric):
    1. Consolidate into one note — remove redundant, keep or replace with the most complete version; merged entities often have the same fact captured independently by different sources; do not consolidate notes addressing different facts — distinct observations remain as separate notes

### Clear Merged Stage

11. Set survivor stage to `new`: `update entities --ids SURVIVOR --stage new --db PATH`

`merged` → `new` transition preserves all data. Entity is now ready for normal processing.

### Report Group

12. Report for each group:
    - Survivor entity ID and name
    - Number of entities absorbed
    - Number of reconciled notes written
    - Relevance and description set on survivor
    - If skipped: reason for skipping

### Summary

13. After all groups processed, provide summary listing all groups and outcomes.

## Rules

- Agent fetches all context via CLI before writing
- `merge entities` is fully mechanical, preserves all data — no information lost
- Reconciliation happens after merge when full combined picture is visible on survivor
- Agent may skip merge if entities are not true duplicates — report reasoning, continue to next group
- Process groups sequentially — one at a time, complete each before starting next
- Agent uses only CLI commands, never raw SQL
- Every Bash call: single-line command starting with recognized program name; no comments, line continuations, shell loops, or variable assignments

Orchestrator appends content of `${CLAUDE_PLUGIN_ROOT}/references/reconcile-entity.md` to agent prompt before spawning.
