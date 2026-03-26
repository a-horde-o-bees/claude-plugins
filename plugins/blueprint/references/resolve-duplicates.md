# Resolve Duplicates

## File Map

### Dependencies
```
.claude/skills/blueprint/blueprint_cli.py
.claude/skills/blueprint/references/reconcile-entity.md
```

Agent subprocess reference — resolves all duplicate groups in research database sequentially.

## Input

Orchestrator provides:
- Database path (e.g., `references/research.db`)

## Agent Workflow

Process all duplicate groups sequentially. For each group, fetch context, make merge decisions, and reconcile combined data.

### Discover Groups

1. Run `./cli.py claude blueprint find-duplicates --db PATH`
2. Parse output into groups — each group lists entity IDs and detection evidence (URL overlap, source-data key match)
3. If no duplicates found:
  1. Report "No duplicates detected", EXIT
4. For each group:
  1. Execute Evaluate Group through Summary

### Evaluate Group

5. For each entity ID in group:
  1. Run `./cli.py claude blueprint get entity ID --db PATH`
6. If group members are not true duplicates (e.g., forks with divergent purposes, same tool used differently):
  1. Report recommendation to skip with reasoning, continue to next group

### Merge

7. Run `./cli.py claude blueprint merge entities --ids ID1,ID2,... --db PATH`
  - Lowest ID becomes survivor automatically
  - Moves URLs, provenance, source data, notes to survivor
  - Appends notes and descriptions to survivor
  - Clears relevance to NULL (agent reassesses)
  - Wipes measures on survivor (stale after merge)
  - Sets survivor stage to `merged` (signals unreconciled data)
  - Deletes absorbed entities

`merge entities` is fully mechanical — all data is preserved on survivor. No data is lost. `merged` stage signals that reconciliation is needed. If process is interrupted after merge but before reconciliation, `./cli.py claude blueprint get entities --stage merged --db PATH` finds entities that need cleanup.

### Reconcile

After merge, survivor has combined notes and descriptions from all group members (including duplicates and potential contradictions). Read survivor's full state and produce clean, reconciled versions.

8. Read survivor: `./cli.py claude blueprint get entity SURVIVOR --db PATH`
9. Apply Entity Reconciliation Procedure (from `.claude/skills/blueprint/references/reconcile-entity.md`) to notes, description, and relevance
10. When two or more notes address same fact (e.g., both describe same feature or record same metric):
  1. Consolidate into one note — remove redundant notes and keep (or replace) most complete version; merged entities often have same fact captured independently by different sources; do not consolidate notes that address different facts — distinct observations remain as separate notes regardless of count

### Clear Merged Stage

11. Set survivor stage to `new`: `./cli.py claude blueprint update entities --ids SURVIVOR --stage new --db PATH`

`merged` → `new` transition preserves all data (no enforcement clearing). Entity is now ready for normal processing.

### Report Group

12. Agent output for each group must include:
  - Survivor entity ID and name
  - Number of entities absorbed
  - Number of reconciled notes written
  - Relevance and description set on survivor
  - If skipped: reason for skipping

### Summary

13. After all groups are processed, provide summary listing all groups and their outcomes.

## Rules

- Agent fetches all context via CLI before writing anything
- `merge entities` is fully mechanical and preserves all data — no information lost during merge
- Reconciliation happens after merge when full combined picture is visible on survivor
- Agent may skip a merge if entities are not true duplicates — report reasoning and continue to next group
- Process groups sequentially — one group at a time, complete each before starting next
- Agent uses only CLI commands, never raw SQL
- Every Bash call must be single-line command starting with recognized program name — no comments, no line continuations, no shell loops, no variable assignments before command
- Use `./cli.py claude blueprint` — never absolute paths

Orchestrator appends content of `.claude/skills/blueprint/references/reconcile-entity.md` to agent prompt before spawning.
