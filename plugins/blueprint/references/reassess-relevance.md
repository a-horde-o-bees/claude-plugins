# Reassess Relevance

Agent subprocess — rescores entity relevance against current assessment criteria using existing notes. No URL visits or new research unless notes are insufficient to evaluate a criterion.

## File Map

### Dependencies

```
${CLAUDE_PLUGIN_ROOT}/skills/research/scripts/research_cli.py
docs/2-assessment-criteria.md
```

## Input

Orchestrator provides:
- Database path (e.g., `references/research.db`)
- Entity scope: `--stage researched` (default), or specific entity IDs

## Agent Workflow

### Load Criteria

1. Read `docs/2-assessment-criteria.md` — load all gradient criteria with definitions
2. Count total criteria (determines maximum relevance score)

### Dynamic Entity Loading

3. Get entity list: `get entities --stage researched --db PATH`
4. For each {entity} in {entity-list}:
    1. Read entity: `get entity {entity_id} --db PATH`
    2. Assess whether room remains to consume more; stop when approaching context budget; always consume at least one entity
5. For each {entity} in {consumed-entities}:
    1. For each {criterion} in {gradient-criteria}: determine met or not met based on note evidence
    2. Sum met criteria to produce new relevance score
    3. If new score differs from current: record change
6. After evaluating all consumed entities, apply updates:
    1. For each {entity} in {changed-entities}: `update entities --ids {entity_id} --relevance {new_score} --db PATH`

### Output

7. Report:
    - Entities evaluated this batch: count and ID list
    - Changes: entity ID, old score, new score, criteria gained/lost
    - Unchanged: count
    - Next entity to resume from (or "complete" if all evaluated)

### Resumption

If not all entities evaluated in one agent, orchestrator spawns next agent with:
- Same criteria (re-read from file)
- Resume from next unconsumed entity

## Rules

- Read-only for notes — do not modify notes, descriptions, or stage during reassessment
- Score strictly against criteria definitions in `docs/2-assessment-criteria.md` — do not infer criteria not listed
- When notes are insufficient to determine whether criterion is met, score as not met — do not visit URLs or conduct new research
- If notes clearly contradict criterion previously scored as met, correct score downward
- If notes support criterion previously scored as not met, correct score upward
- Report both gains and losses — reassessment is bidirectional
- NEVER access database directly — CLI is only interface
- Every Bash call: single-line command starting with recognized program name; no comments, line continuations, shell loops, or variable assignments
