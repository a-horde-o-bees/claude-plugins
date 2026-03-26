# Reassess Relevance

## File Map

### Dependencies
```
.claude/skills/blueprint/blueprint_cli.py
docs/2-assessment-criteria.md
```

Agent subprocess reference — rescores entity relevance against current assessment criteria using existing notes. No URL visits or new research unless notes are insufficient to evaluate a criterion.

## Input

Orchestrator provides:
- Database path (e.g., `references/research.db`)
- Entity scope: `--stage researched` (default), or specific entity IDs

## Agent Workflow

### Load Criteria

1. Read `docs/2-assessment-criteria.md` — load all gradient criteria with definitions
2. Count total criteria (determines maximum relevance score)

### Dynamic Entity Loading

3. Get entity list: `./cli.py claude blueprint get entities --stage researched --db PATH`
4. Read entities one at a time in relevance order (highest first):
  `./cli.py claude blueprint get entity {entity_id} --db PATH`
5. After reading each entity, assess whether room remains to consume more. Stop consuming when approaching context budget. Always consume at least one entity.
6. For each consumed entity, evaluate every gradient criterion against entity notes:
  1. For each criterion: determine met or not met based on note evidence
  2. Sum met criteria to produce new relevance score
  3. If new score differs from current: record the change
7. After evaluating all consumed entities, apply updates:
  1. For each entity with changed relevance:
    `./cli.py claude blueprint update entities --ids {entity_id} --relevance {new_score} --db PATH`

### Output

8. Report:
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
- When notes are insufficient to determine whether a criterion is met, score it as not met — do not visit URLs or conduct new research
- If notes clearly contradict a criterion previously scored as met, correct the score downward
- If notes support a criterion previously scored as not met, correct the score upward
- Report both gains and losses — reassessment is bidirectional
- NEVER access database directly — CLI is only interface
- Every Bash call must be a single-line command starting with a recognized program name
- Use `./cli.py claude blueprint` — never absolute paths
