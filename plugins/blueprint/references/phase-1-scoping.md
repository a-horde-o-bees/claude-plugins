# Phase 1: Scoping

Design phase — iterative exploration with integrated entity assessment.

## File Map

### Dependencies

```
${CLAUDE_PLUGIN_ROOT}/references/reconcile-entity.md
${CLAUDE_PLUGIN_ROOT}/references/directory-traversal.md
${CLAUDE_PLUGIN_ROOT}/skills/research/scripts/research_cli.py
docs/blueprint.md
```

### Created

```
docs/overview.md
docs/1-scope.md
docs/2-assessment-criteria.md
docs/3-goals.md
docs/4-effectiveness-criteria.md
docs/5-constraints.md
docs/6-domain-knowledge.md
references/research.db
```

## Seed Data

When database contains entities at Phase 1 start (from initialization arguments, prior sessions, or external import), treat as unverified leads. Landscape exploration and relevance assessment required regardless. Seeded entities verified during exploration alongside new discoveries — not assumed correct. Discovery agents encountering seeded entity URL hit registration dedup and skip, but orchestrator must ensure every seeded entity gets directly assessed before Phase 1 gate: verify URL is live, confirm recency criterion, validate description against actual content, reconcile notes.

## Workflow

### Input

1. Parse user input into parent concept; available as `$ARGUMENTS` if passed with `/blueprint-research`, or discussed interactively
2. Surface-level research — fetch examples, check what exists, identify landscape
    - Web searches to gauge breadth of space
    - Note meta-sources encountered (directories, associations, aggregators)
3. Present findings:
    - Summarize parent concept as understood
    - Suggest related/adjacent concepts with evidence of what exists
    - Include concepts that might reveal user's true core intent — initial description is sometimes adjacent to actual need
4. User confirms which concepts belong in scope and which do not

### Scope Refinement

5. For concepts user is uncertain about: targeted surface research to help decide
6. Ask clarifying questions about goals — tailor to subject type from step 2:
    - Target audience or user base
    - Scale ambitions and success metrics
    - Key constraints (budget, timeline, skills, platform)
    - Differentiators — what should set this apart from existing examples
7. If user feels initial suggestions did not fully cover space: surface additional related concepts
8. Present refined scope summary for approval
9. User may iterate (adjust concepts, request suggestions, change focus) until scope feels right

### Project Infrastructure

10. Write project definition files in `docs/`:
    - `overview.md` — lightweight index pointing to all numbered files with one-line purpose descriptions
    - `1-scope.md` — parent concept, confirmed in-scope concepts, excluded concepts with brief rationale
    - `2-assessment-criteria.md` — hardline filters, gradient criteria, relevance guide
    - `3-goals.md` — goals and priority order from refinement
    - `4-effectiveness-criteria.md` — criteria for judging pattern and approach effectiveness
    - `5-constraints.md` — implementation realities (budget, timeline, skills, platform)
    - `6-domain-knowledge.md` — landscape structure and distilled context research findings
11. Create `references/` directory
12. Initialize research database: `research_cli.py init`

### Domain Knowledge Development

Codify observations into domain knowledge guiding discovery and deep research. Sources registered as entities with `directory` or `context` roles.

13. Propose sources — directories (crawlable listings) and context sources (advice, data, guides)
14. Register confirmed sources as entities:
    - `research_cli.py register --name "Source Name" --url "https://source-url.com" --description "What it contains and why it matters" --role directory --relevance 0`
    - `research_cli.py register --name "Source Name" --url "https://source-url.com" --description "What it contains and why it matters" --role context --relevance 0`
15. For directory entities, add accessibility note after registration:
    - `research_cli.py upsert notes --entity-id ID --notes "[ACCESSIBILITY]: {static|js-rendered|auth-gated|api-available} — {brief access method}"`
    - Accessibility guides tool selection: `static` uses web fetch; `js-rendered` and `auth-gated` require browser automation (sequential)
16. Present sources for user review:
    - `research_cli.py get entities --role directory`
    - `research_cli.py get entities --role context`
17. User refines — add, remove, or adjust sources

### Context Research Waves

Context entities (role: `context`) researched in waves to build domain knowledge before landscape exploration. Each wave's findings update `docs/6-domain-knowledge.md`.

18. Order context entities by relevance (highest first); low-relevance context entities may be deferred — document cutoff in history
19. For each {wave} in {context-waves}:
    1. Spawn context research agents — one per entity, sequential by default; use Context Research Agent template
    2. After wave completes, review findings across all researched entities in wave
    3. Update `docs/6-domain-knowledge.md` with distilled insights
    4. Append history entry: wave number, entities researched, key insights, next step
    5. If remaining unresearched context entities: reassess whether updated knowledge changes their value or suggests additional sources
20. When domain knowledge sufficiently developed for informed landscape exploration: user confirms, proceed to directory traversal and targeted search

### Landscape Exploration

Explore domain to discover entities. Two modes:

- **Targeted search** — web searches with focused queries, following results; use Discovery Agent template
- **Directory crawl** — systematic traversal of directory entities; use Directory Crawl Agent template; check accessibility notes before spawning — `js-rendered` or `auth-gated` require browser automation

21. For each {directory} in {directory-entities}: spawn directory crawl agent
22. For targeted searches: spawn discovery agents with focused queries for examples not covered by directories
23. As entities are encountered, assess against scope criteria before registering:
    1. If entity fails hardline criterion:
        1. Register as rejected with description, notes, and reason (relevance 0, stage `rejected`)
    2. Else:
        1. Register with relevance assessment, description, role, and initial notes
24. Observe patterns:
    - What types of structured public data exist for this entity type?
    - What differentiates entities in this space?
    - Which entities address core scope concerns?
25. Present accumulated entities and observations to user

### Scope Refinement and Relevance Adjustment

26. User reviews entities and domain knowledge, directs next steps:
    - "Look at more entities in [region/category]"
    - "What do the [sources] say about this space?"
    - "Check [specific directory or aggregator]"
    - "That category is more important — boost those entities"
    - "Remove source [X] — not relevant"
27. Execute directed exploration, register new entities
28. When scope criteria change: spawn reassess-relevance agent (`${CLAUDE_PLUGIN_ROOT}/references/reassess-relevance.md`) to rescore all entities against updated criteria using existing notes
29. Repeat until user considers landscape adequately mapped and relevance ordering reflects priorities

## Re-Entry

When Phase 1 resumes with existing data, present dashboard:

1. `research_cli.py get stats` — entity counts by role and stage
2. `research_cli.py get entities --role example` — examples sorted by relevance
3. `research_cli.py get entities --role directory` — directories (check progress notes)
4. `research_cli.py get entities --role context` — context sources
5. `research_cli.py get provenance` — provenance sources with entity counts
6. `research_cli.py get reach --min 2` — multi-source entities
7. `docs/overview.md` for file index, `docs/1-scope.md` for scope context

User directs next action: explore more, crawl directories, refine relevance, or proceed to deep research.

## Agent Prompt Templates

Orchestrator appends content of `${CLAUDE_PLUGIN_ROOT}/references/reconcile-entity.md` to each template before spawning agent. Use directory crawl template for directory entities; discovery template for targeted web searches.

### Context Research Agent

```
Research context entity to extract domain knowledge relevant to project.

Entity: `{entity_id}`

Database CLI — all commands use this prefix:
  python3 ${CLAUDE_PLUGIN_ROOT}/skills/research/scripts/research_cli.py

Read scope and domain knowledge:
- `docs/1-scope.md`
- `docs/6-domain-knowledge.md`

1. Resolve entity:
    python3 ${CLAUDE_PLUGIN_ROOT}/skills/research/scripts/research_cli.py get entity {entity_id} --db references/research.db
2. Research entity content thoroughly — focus on knowledge, frameworks, data, and insights relevant to project scope
3. After completing ALL research, read existing notes and apply Entity Reconciliation Procedure (below):
    python3 ${CLAUDE_PLUGIN_ROOT}/skills/research/scripts/research_cli.py get entity {entity_id} --db references/research.db
4. Set stage to researched:
    python3 ${CLAUDE_PLUGIN_ROOT}/skills/research/scripts/research_cli.py update entities --ids {entity_id} --stage researched --db references/research.db

Rules:
- Complete ALL research before writing to database
- Final output MUST state notes written, e.g.: "Wrote 14 notes to entity `{entity_id}`"
- Do NOT repeat entity details, notes, or research findings in output — report only note count, entity ID, and errors
- Do NOT create files — write only to database via CLI
- NEVER access database directly — CLI is only interface
- Every Bash call: single-line command starting with recognized program name; no comments, line continuations, shell loops, or variable assignments
- When entity content uses JavaScript rendering, use browser automation if available; fall back to web search

--- Entity Reconciliation Procedure ---
{content of ${CLAUDE_PLUGIN_ROOT}/references/reconcile-entity.md}
```

### Discovery Agent

```
Explore `{source_description}` to discover entities relevant to project scope.

Database CLI — all commands use this prefix:
  python3 ${CLAUDE_PLUGIN_ROOT}/skills/research/scripts/research_cli.py

Read scope and domain knowledge:
- `docs/1-scope.md`
- `docs/6-domain-knowledge.md`

Entity roles:
- `example` (default) — comparable sites to study and emulate
- `directory` — crawlable listings that yield examples
- `context` — knowledge/advice sources informing project

For each entity encountered:
1. Assess against criteria from `docs/2-assessment-criteria.md`
2. Register with appropriate role — `register` returns new ID or "Already registered" with existing ID:
    python3 ${CLAUDE_PLUGIN_ROOT}/skills/research/scripts/research_cli.py register --name "Entity Name" --url "https://entity-url.com" --source-url "https://source-url.com" --description "One sentence: what entity is and primary approach" --relevance N [--role example|directory|context] --db references/research.db
3. If new entity:
    1. Add notes capturing current knowledge:
        python3 ${CLAUDE_PLUGIN_ROOT}/skills/research/scripts/research_cli.py upsert notes --entity-id ID --notes "observation 1" "observation 2" --db references/research.db
    2. If entity fails hardline criterion:
        python3 ${CLAUDE_PLUGIN_ROOT}/skills/research/scripts/research_cli.py update entities --ids ID --stage rejected --db references/research.db
        python3 ${CLAUDE_PLUGIN_ROOT}/skills/research/scripts/research_cli.py upsert notes --entity-id ID --notes "Rejected: reason" --db references/research.db
4. If already registered (reconcile-on-touch):
    1. Read existing entity:
        python3 ${CLAUDE_PLUGIN_ROOT}/skills/research/scripts/research_cli.py get entity ID --db references/research.db
    2. Apply Entity Reconciliation Procedure to notes, description, and relevance

Relevance guide: read `docs/2-assessment-criteria.md` for project-specific scale.

Rules:
- Assess each entity on encounter — do not register stubs for later evaluation
- Register even rejected entities (relevance 0) so they are not re-discovered
- NEVER access database directly — CLI is only interface
- Every Bash call: single-line command starting with recognized program name; no comments, line continuations, shell loops, or variable assignments
- When pages use JavaScript rendering or require interaction, use browser automation if available; fall back to web search
- Final output: report entities registered, rejected, and top relevance entities found

--- Entity Reconciliation Procedure ---
{content of ${CLAUDE_PLUGIN_ROOT}/references/reconcile-entity.md}
```

### Directory Crawl Agent

```
Crawl directory entity `{directory_name}` (ID: `{directory_id}`) to discover example entities.

Database CLI — all commands use this prefix:
  python3 ${CLAUDE_PLUGIN_ROOT}/skills/research/scripts/research_cli.py

Read scope, domain knowledge, and traversal patterns:
- `docs/1-scope.md`
- `docs/6-domain-knowledge.md`
- `${CLAUDE_PLUGIN_ROOT}/references/directory-traversal.md`

Check directory entity for existing notes:
    python3 ${CLAUDE_PLUGIN_ROOT}/skills/research/scripts/research_cli.py get entity {directory_id} --db references/research.db

Look for tagged crawl notes:
- `[CRAWL METHOD]:` — technical approach; if present, follow it; if absent, follow Approach Discovery Workflow in directory-traversal.md
- `[CRAWL SCRIPT]:` — file path to extraction script; if present, read and use (adjust START_PAGE from progress); if absent, develop during approach discovery and save
- `[CRAWL PROGRESS]:` — current position; if present, resume from indicated position; if absent, start from beginning

For batch results (multiple entities per extraction):
    python3 ${CLAUDE_PLUGIN_ROOT}/skills/research/scripts/research_cli.py register-batch --json '[{"name": "...", "url": "...", "description": "...", "relevance": N, "notes": ["fact1", "fact2"]}, ...]' --source-url "https://directory-url.com" --db references/research.db
Notes only written for new entities. Already-registered listed in output for reconciliation — read existing notes and apply Entity Reconciliation Procedure.

For individual entities:
1. Assess against criteria from `docs/2-assessment-criteria.md`
2. Register:
    python3 ${CLAUDE_PLUGIN_ROOT}/skills/research/scripts/research_cli.py register --name "Entity Name" --url "https://entity-url.com" --source-url "https://directory-page-url.com" --description "One sentence: what entity is and primary approach" --relevance N --db references/research.db
3. If new entity:
    1. Add notes:
        python3 ${CLAUDE_PLUGIN_ROOT}/skills/research/scripts/research_cli.py upsert notes --entity-id ID --notes "observation 1" "observation 2" --db references/research.db
    2. If entity fails hardline criterion:
        python3 ${CLAUDE_PLUGIN_ROOT}/skills/research/scripts/research_cli.py update entities --ids ID --stage rejected --db references/research.db
4. If already registered (reconcile-on-touch):
    1. Read entity and apply reconciliation:
        python3 ${CLAUDE_PLUGIN_ROOT}/skills/research/scripts/research_cli.py get entity ID --db references/research.db

Directory crawl notes — tagged notes on directory entity track method, script, and progress:

`[CRAWL METHOD]:` — record technical approach before starting (or on first session); update only if approach changes:
    python3 ${CLAUDE_PLUGIN_ROOT}/skills/research/scripts/research_cli.py upsert notes --entity-id {directory_id} --notes "[CRAWL METHOD]: [base URL, extraction technique, pagination, filtering, directory-specific details]" --db references/research.db

`[CRAWL SCRIPT]:` — save extraction script and record pointer:
1. Save script to `references/crawl-scripts/{directory_id}-{short_name}.js`
2. Add pointer note:
    python3 ${CLAUDE_PLUGIN_ROOT}/skills/research/scripts/research_cli.py upsert notes --entity-id {directory_id} --notes "[CRAWL SCRIPT]: references/crawl-scripts/{directory_id}-{short_name}.js" --db references/research.db

`[CRAWL PROGRESS]:` — update after each page, section, or logical segment; remove previous and replace:
1. If previous progress note exists, remove it:
    python3 ${CLAUDE_PLUGIN_ROOT}/skills/research/scripts/research_cli.py remove notes --entity-id {directory_id} --note-ids N_ID --db references/research.db
2. Add updated progress:
    python3 ${CLAUDE_PLUGIN_ROOT}/skills/research/scripts/research_cli.py upsert notes --entity-id {directory_id} --notes "[CRAWL PROGRESS]: [what was processed and where to resume]" --db references/research.db
3. Touch directory entity:
    python3 ${CLAUDE_PLUGIN_ROOT}/skills/research/scripts/research_cli.py touch entities --ids {directory_id} --db references/research.db

Write notes in terms that make sense for directory structure. Goal: new agent reading notes for first time can unambiguously understand approach and find resumption point.

Relevance guide: read `docs/2-assessment-criteria.md` for project-specific scale.

Rules:
- Assess each entity on encounter — do not register stubs for later evaluation
- Register even rejected entities (relevance 0) so they are not re-discovered
- NEVER access database directly — CLI is only interface
- Every Bash call: single-line command starting with recognized program name; no comments, line continuations, shell loops, or variable assignments
- Use browser automation when directory requires JavaScript rendering or interaction (filters, pagination, search forms); fall back to web fetch for static content; check accessibility notes
- Final output: report entities registered, rejected, directory progress, and top relevance entities

--- Entity Reconciliation Procedure ---
{content of ${CLAUDE_PLUGIN_ROOT}/references/reconcile-entity.md}
```

## Entity Roles

- `example` (default) — comparable sites to study and emulate
- `directory` — crawlable listings that yield examples (member directories, curated lists)
- `context` — knowledge/advice sources informing project (guides, data, advice)

All roles share the same table, notes, URLs, and provenance. Role determines how agents interact with the entity and what notes capture.

## Output

- `docs/overview.md` — index pointing to numbered project definition files
- `docs/1-scope.md` through `docs/6-domain-knowledge.md` — project definition files
- `references/research.db` — entities with relevance, descriptions, notes, provenance
- Entity list ordered by relevance — ready for Phase 2 deep research starting from top

## Gate

User approves:

1. Scope definition and assessment criteria
2. Domain knowledge (`docs/6-domain-knowledge.md`) reflects context research
3. Directory and context entities are identified
4. Entity relevance ordering reflects priorities for deep research
