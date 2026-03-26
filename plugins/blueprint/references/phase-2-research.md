# Phase 2: Deep Research

## File Map

### Dependencies
```
.claude/skills/blueprint/blueprint_cli.py
docs/1-scope.md
docs/2-assessment-criteria.md
docs/4-effectiveness-criteria.md
docs/6-domain-knowledge.md
```

### Created
```
references/research.db
```

Execution phase — sequential agent work with checkpointing.

## Input

- Entities sorted by relevance: `./cli.py claude blueprint get entities --role example --stage new --db references/research.db`
- `docs/1-scope.md` for scope context, `docs/2-assessment-criteria.md` for relevance reassessment
- `docs/4-effectiveness-criteria.md` for evaluating patterns, `docs/6-domain-knowledge.md` for landscape context

## Pre-Research

1. Present research plan to user:
  - Entity count and relevance-sorted list (highest relevance first)
  - Explain emergent schema approach: agents capture everything they observe as atomic notes — self-explanatory facts that each stand alone
  - Estimated approach: one agent per entity, sequential processing, starting from highest relevance
  - User may set a relevance cutoff (e.g., "research entities with relevance 5+") or entity count limit
2. User confirms to proceed — confirmation covers research plan

## Research Waves

Research proceeds in waves by relevance tier. After each wave, orchestrator and user review findings and update domain knowledge with newly observed platforms, tools, and business models before the next wave begins. This ensures later research agents have richer context.

3. For each relevance tier (highest first):
  1. Identify entities at this relevance level with stage `new`
  2. Research all entities in the tier sequentially (see Research Loop below)
  3. After wave completes: review findings, update `docs/6-domain-knowledge.md` with new platforms/tools/models observed (document existence only — no frequency analysis per domain knowledge guard)
  4. User decides whether to continue to next tier or proceed to Phase 3

## Research Loop

4. For each entity at stage `new` in relevance order (highest first, sequential, one at a time):
  1. Record current note count for this entity (for completion verification):
    `./cli.py claude blueprint get entity {entity_id} --db references/research.db` — note "Notes:" count
  2. Spawn agent (`subagent_type=general-purpose`) with Research Agent Prompt Template
  3. After agent completes, verify:
    1. If task interrupted or errored:
      1. Re-spawn
    2. Check stage: `./cli.py claude blueprint get entity {entity_id} --db references/research.db`
    3. If stage is not `researched`:
      1. Re-spawn — agent failed to write

### Research Agent Prompt Template

```
Research entity's public presence thoroughly.

Entity: `{entity_id}`

Read domain knowledge and effectiveness criteria:
- `docs/6-domain-knowledge.md`
- `docs/4-effectiveness-criteria.md`

1. Resolve entity from database:
  `./cli.py claude blueprint get entity {entity_id} --db references/research.db`
2. Research entity's web presence — start with primary URL, then explore thoroughly
3. After completing ALL research, read existing notes and apply Entity Reconciliation Procedure (see below):
  `./cli.py claude blueprint get entity {entity_id} --db references/research.db`
4. Set stage to researched:
  `./cli.py claude blueprint update entities --ids {entity_id} --stage researched --db references/research.db`

Rules:
- Complete ALL research before writing anything to database
- Final output text MUST state number of notes written, e.g.: "Wrote 14 notes to entity `{entity_id}`"
- Do NOT repeat entity details, notes, or research findings in output text — all data lives in database; report only note count, entity ID, and errors encountered
- Do NOT create files — write only to database via CLI
- NEVER access database directly — no raw SQL, no `sqlite3` imports, no `python -c` database commands; CLI is only interface; report database errors in output, do not diagnose or fix schema issues
- Every Bash call must be a single-line command starting with a recognized program name — no comments, no line continuations, no shell loops, no variable assignments before command
- Use `./cli.py claude blueprint` — never absolute paths
- When entity's web presence uses JavaScript rendering (SPAs, dynamic content), use browser automation tools if available. Fall back to web search for supplementary information when pages cannot be rendered.

--- Entity Reconciliation Procedure ---
`{content of references/reconcile-entity.md}`
```

Orchestrator appends content of `references/reconcile-entity.md` to this prompt before spawning agent.

## After All Entities Processed

6. Run deduplication:
  1. Propose spawning resolve-duplicates agent (`references/resolve-duplicates.md`) — present to user for confirmation before executing (merges are hard to reverse)
  2. If user confirms: spawn agent
7. Run `./cli.py claude blueprint get stats --db references/research.db` — present summary

## Re-Entry

When Phase 2 resumes with existing research, present re-entry dashboard:

1. `./cli.py claude blueprint get stats --db references/research.db` — entity counts by stage
2. `./cli.py claude blueprint get entities --db references/research.db` — entities sorted by relevance with stage
3. Identify entities at stage `new` (research pending) vs `researched` (complete)

Resume by continuing with next entity at stage `new` in relevance order (highest first). Entities at stage `researched` have completed deep research — skip them.

## Checkpointing

- Database is checkpoint — agent writes notes then explicitly sets stage to `researched`
- If session breaks, `get entities` shows stage for each entity
- Resume by continuing with next entity at stage `new` in relevance order
- Entities at stage `researched` have completed research — skip them
- Database is always consistent (writes are transactional with retry)

## Output

`references/research.db` — populated SQLite database with entities and notes

## Gate

User reviews entity landscape and stats. May request:
- Re-research of specific entities (re-spawn agent)
- Add more entities (reverts to Phase 1 — see Phase Reversion in SKILL.md)
