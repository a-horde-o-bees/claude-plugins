# Phase 2: Deep Research

Execution phase — sequential agent work with checkpointing.

## Workflow

### Input

- Entities sorted by relevance: `python3 ${CLAUDE_PLUGIN_ROOT}/run.py skills.research get entities --role example --stage new --db blueprint/data/research.db`
- `blueprint/1-scope.md` for scope context, `blueprint/2-assessment-criteria.md` for relevance reassessment
- `blueprint/4-effectiveness-criteria.md` for evaluating patterns, `blueprint/6-domain-knowledge.md` for landscape context

### Pre-Research

1. Present research plan to user:
    - Entity count and relevance-sorted list (highest relevance first)
    - Emergent schema approach: agents capture everything observed as atomic notes — self-explanatory facts that each stand alone
    - One agent per entity, sequential processing, starting from highest relevance
    - User may set relevance cutoff (e.g., "research entities with relevance 5+") or entity count limit
2. User confirms to proceed

### Research Waves

Research proceeds in waves by relevance tier. After each wave, orchestrator and user review findings and update domain knowledge with newly observed platforms, tools, and business models before next wave begins — later agents get richer context.

3. For each {tier} in {relevance-tiers}:
    1. Identify entities at this relevance level with stage `new`
    2. For each {entity} in {tier}: dispatch Research Loop
    3. After wave completes: review findings, update `blueprint/6-domain-knowledge.md` with new platforms, tools, models observed; document existence only — no frequency analysis per domain knowledge guard
    4. User decides whether to continue to next tier or proceed to Phase 3

### Research Loop

4. Record current note count for entity:
    - `python3 ${CLAUDE_PLUGIN_ROOT}/run.py skills.research get entity {entity_id} --db blueprint/data/research.db` — note "Notes:" count
5. Spawn agent with Research Agent template
6. After agent completes, verify:
    1. If task interrupted or errored: re-spawn
    2. Check stage: `python3 ${CLAUDE_PLUGIN_ROOT}/run.py skills.research get entity {entity_id} --db blueprint/data/research.db`
    3. If stage is not `researched`: re-spawn — agent failed to write

### Post-Research

7. Propose spawning resolve-duplicates agent (`${CLAUDE_PLUGIN_ROOT}/references/resolve-duplicates.md`) — present to user for confirmation before executing; merges are hard to reverse
    1. If user confirms: spawn agent
8. Present summary: `python3 ${CLAUDE_PLUGIN_ROOT}/run.py skills.research get stats --db blueprint/data/research.db`

## Re-Entry

When Phase 2 resumes with existing research, present dashboard:

1. `python3 ${CLAUDE_PLUGIN_ROOT}/run.py skills.research get stats --db blueprint/data/research.db` — entity counts by stage
2. `python3 ${CLAUDE_PLUGIN_ROOT}/run.py skills.research get entities --db blueprint/data/research.db` — entities sorted by relevance with stage
3. Identify entities at stage `new` (pending) vs `researched` (complete)

Resume with next entity at stage `new` in relevance order (highest first). Entities at `researched` have completed deep research — skip them.

## Checkpointing

- Database is checkpoint — agent writes notes then explicitly sets stage to `researched`
- If session breaks, `python3 ${CLAUDE_PLUGIN_ROOT}/run.py skills.research get entities --db blueprint/data/research.db` shows stage for each entity
- Resume by continuing with next `new` entity in relevance order
- Writes are transactional with retry — database is always consistent

## Agent Prompt Template

Orchestrator appends content of `${CLAUDE_PLUGIN_ROOT}/references/reconcile-entity.md` before spawning agent.

### Research Agent

```
Research entity's public presence thoroughly.

Entity: `{entity_id}`

Database CLI — all commands use this prefix:
  python3 ${CLAUDE_PLUGIN_ROOT}/run.py skills.research

Read domain knowledge and effectiveness criteria:
- `blueprint/6-domain-knowledge.md`
- `blueprint/4-effectiveness-criteria.md`

1. Resolve entity:
    python3 ${CLAUDE_PLUGIN_ROOT}/run.py skills.research get entity {entity_id} --db blueprint/data/research.db
2. Research entity web presence — start with primary URL, then explore thoroughly
3. After completing ALL research, read existing notes and apply Entity Reconciliation Procedure (below):
    python3 ${CLAUDE_PLUGIN_ROOT}/run.py skills.research get entity {entity_id} --db blueprint/data/research.db
4. Set stage to researched:
    python3 ${CLAUDE_PLUGIN_ROOT}/run.py skills.research update entities --ids {entity_id} --stage researched --db blueprint/data/research.db

Rules:
- Complete ALL research before writing to database
- Final output MUST state notes written, e.g.: "Wrote 14 notes to entity `{entity_id}`"
- Do NOT repeat entity details, notes, or research findings in output — all data lives in database; report only note count, entity ID, and errors
- Do NOT create files — write only to database via CLI
- NEVER access database directly — no raw SQL, no sqlite3 imports, no python3 -c database commands; CLI is only interface; report database errors in output, do not diagnose or fix
- Every Bash call: single-line command starting with recognized program name; no comments, line continuations, shell loops, or variable assignments
- When entity web presence uses JavaScript rendering (SPAs, dynamic content), use browser automation if available; fall back to web search when pages cannot be rendered

--- Entity Reconciliation Procedure ---
{content of ${CLAUDE_PLUGIN_ROOT}/references/reconcile-entity.md}
```

## Output

`blueprint/data/research.db` — populated SQLite database with entities and notes.

## Gate

User reviews entity landscape and stats. May request:

1. Re-research of specific entities (re-spawn agent)
2. Add more entities (reverts to Phase 1 — see Phase Reversion in SKILL.md)
