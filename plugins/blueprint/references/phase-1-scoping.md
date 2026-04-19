# Phase 1: Scoping

Design phase — iterative exploration with integrated entity assessment.

## Seed Data

When database contains entities at Phase 1 start (from initialization arguments, prior sessions, or external import), treat as unverified leads. Landscape exploration and relevance assessment required regardless. Seeded entities verified during exploration alongside new discoveries — not assumed correct. Discovery agents encountering seeded entity URL hit registration dedup and skip, but orchestrator must ensure every seeded entity gets directly assessed before Phase 1 gate: verify URL is live, confirm recency criterion, validate description against actual content, reconcile notes.

## Workflow

### Input

1. Parse user input into parent concept; available as `$ARGUMENTS` if passed with `/research`, or discussed interactively
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

10. Write project definition files in `blueprint/`, following templates in `${CLAUDE_PLUGIN_ROOT}/templates/`:
    - `overview.md` from `templates/overview.md`
    - `1-scope.md` from `templates/1-scope.md`
    - `2-goals.md` from `templates/2-goals.md`
    - `3-assessment-criteria.md` from `templates/3-assessment-criteria.md`
    - `4-effectiveness-criteria.md` from `templates/4-effectiveness-criteria.md`
    - `5-constraints.md` from `templates/5-constraints.md`
    - `6-domain-knowledge.md` from `templates/6-domain-knowledge.md`
11. Create `blueprint/data/` directory
12. Initialize research database: `init_database()`
13. Populate criteria in database: `set_criteria([{type, name, gate}, ...])`
    - Read criteria from `blueprint/3-assessment-criteria.md`
    - Each hardline criterion must define a concrete pass/fail gate with no judgment required
    - Each relevancy criterion must include thresholds or enumerated conditions (e.g., ">=50 GitHub stars OR >=10 forks OR active community channel")
    - Review criteria and flag any that require agent judgment rather than evaluation — rewrite until all are deterministic

### Domain Knowledge Development

Codify observations into domain knowledge guiding discovery and deep research. Sources registered as entities with `directory` or `context` modes.

13. Propose sources — directories (crawlable listings) and context sources (advice, data, guides)
14. Register confirmed sources as entities:
    - `register_entity({name: "Source Name", url: "https://source-url.com", description: "What it contains and why it matters", modes: ["directory"], relevance: 0})`
    - `register_entity({name: "Source Name", url: "https://source-url.com", description: "What it contains and why it matters", modes: ["context"], relevance: 0})`
15. For directory entities, add accessibility note after registration:
    - `add_notes({entity_id: "ID", notes: ["[ACCESSIBILITY]: {static|js-rendered|auth-gated|api-available} — {brief access method}"]})`
    - Accessibility guides tool selection: `static` uses web fetch; `js-rendered` and `auth-gated` require browser automation (sequential)
16. Present sources for user review:
    - `list_entities({mode: "directory"})`
    - `list_entities({mode: "context"})`
17. User refines — add, remove, or adjust sources

### Context Research Waves

Context entities (mode: `context`) researched in waves to build domain knowledge before landscape exploration. Each wave's findings update `blueprint/6-domain-knowledge.md`.

18. Order context entities by relevance (highest first); low-relevance context entities may be deferred — document cutoff in history
19. For each {wave} in {context-waves}:
    1. Spawn context research agents — one per entity, sequential by default; use Context Research Agent template
    2. After wave completes, review findings across all researched entities in wave
    3. Update `blueprint/6-domain-knowledge.md` with distilled insights
    4. Append history entry: wave number, entities researched, key insights, next step
    5. If remaining unresearched context entities: reassess whether updated knowledge changes their value or suggests additional sources
20. When domain knowledge sufficiently developed for informed landscape exploration: user confirms, proceed to directory traversal and targeted search

### Landscape Exploration

Explore domain to discover entities. Two modes:

- **Targeted search** — web searches with focused queries, following results; use Discovery Agent template
- **Directory crawl** — systematic traversal of directory entities; use Directory Crawl Agent template; check accessibility notes before spawning — `js-rendered` or `auth-gated` require browser automation

21. For each {directory} in {directory-entities}: spawn directory crawl agent
22. For targeted searches: spawn discovery agents with focused queries for examples not covered by directories
23. Crawl and discovery agents register entities with relevance 0 — no criteria assessment during crawl; hardline rejections still applied on encounter
24. Observe patterns:
    - What types of structured public data exist for this entity type?
    - What differentiates entities in this space?
    - Which entities address core scope concerns?
25. Present accumulated entities and observations to user
26. Update `blueprint/6-domain-knowledge.md` — distill landscape exploration findings into domain knowledge; present changes to user before writing
27. If unclassified entities exist: propose spawning assess-entity agent (`${CLAUDE_PLUGIN_ROOT}/references/assess-entity.md`); wait for user confirmation

### Scope Refinement and Relevance Adjustment

27. User reviews entities and domain knowledge, directs next steps:
    - "Look at more entities in [region/category]"
    - "What do the [sources] say about this space?"
    - "Check [specific directory or aggregator]"
    - "That category is more important — boost those entities"
    - "Remove source [X] — not relevant"
28. Execute directed exploration, register new entities
29. When scope criteria change:
    1. Spawn assess-entity agent (`${CLAUDE_PLUGIN_ROOT}/references/assess-entity.md`) with scope: all researched entities; reassesses criteria against updated definitions
    2. Apply hardline filters retroactively — check existing entities against new/modified hardline criteria; reject entities that no longer pass
    3. Clear measures — criteria change invalidates prior analysis measures: `clear_all_measures()`
30. Repeat until user considers landscape adequately mapped and relevance ordering reflects priorities

## Re-Entry

When Phase 1 resumes with existing data, present dashboard:

1. `get_dashboard()` — entity counts by stage and mode
2. `list_entities({mode: "example"})` — examples by relevance
3. `list_entities({mode: "directory"})` — directories (check progress notes)
4. `list_entities({mode: "context"})` — context sources
5. `query({sql: "SELECT source_url, COUNT(entity_id) as entity_count FROM url_provenance GROUP BY source_url ORDER BY entity_count DESC"})` — provenance sources with entity counts
6. `query({sql: "SELECT entity_id, COUNT(source_url) as source_count FROM url_provenance GROUP BY entity_id HAVING source_count >= :min", params: {min: 2}})` — multi-source entities
7. `blueprint/overview.md` for file index, `blueprint/1-scope.md` for scope context

User directs next action: explore more, crawl directories, refine relevance, or proceed to deep research.

## Agent Prompt Templates

Orchestrator appends content of `${CLAUDE_PLUGIN_ROOT}/references/reconcile-entity.md` to each template before spawning agent. Use directory crawl template for directory entities; discovery template for targeted web searches.

### Context Research Agent

```
Research context entity to extract domain knowledge relevant to project.

Entity: `{entity_id}`

Read scope and domain knowledge:
- `blueprint/1-scope.md`
- `blueprint/6-domain-knowledge.md`

1. Resolve entity:
    get_entity({entity_id: "{entity_id}"})
2. Research entity content thoroughly — focus on knowledge, frameworks, data, and insights relevant to project scope
3. After completing ALL research, read existing notes and apply Entity Reconciliation Procedure (below):
    get_entity({entity_id: "{entity_id}"})
4. Set stage to researched:
    set_stage({entity_id: "{entity_id}", stage: "researched"})

Rules:
- Complete ALL research before writing to database
- Final output MUST state notes written, e.g.: "Wrote 14 notes to entity `{entity_id}`"
- Do NOT repeat entity details, notes, or research findings in output — report only note count, entity ID, and errors
- Do NOT create files — write only to database via MCP tool calls
- NEVER access database directly — MCP tool calls are the only interface
- When entity content uses JavaScript rendering, use browser automation if available; fall back to web search

--- Entity Reconciliation Procedure ---
{content of ${CLAUDE_PLUGIN_ROOT}/references/reconcile-entity.md}
```

### Discovery Agent

```
Explore `{source_description}` to discover entities relevant to project scope.

Read scope and domain knowledge:
- `blueprint/1-scope.md`
- `blueprint/6-domain-knowledge.md`

Entity modes (database enforces these values via CHECK constraint):
- `example` (default) — comparable sites to study and emulate
- `directory` — crawlable listings that yield examples
- `context` — knowledge/advice sources informing project
- `unclassified` — discovered adjacently, pending mode classification

For each entity encountered:
1. Register with appropriate modes — `register_entity` returns new ID or "Already registered" with existing ID:
    register_entity({name: "Entity Name", url: "https://entity-url.com", source_url: "https://source-url.com", description: "One sentence: what entity is and primary approach", relevance: 0, modes: ["example"]})
2. If new entity:
    1. Add notes capturing current knowledge:
        add_notes({entity_id: "ID", notes: ["observation 1", "observation 2"]})
    2. If entity fails hardline criterion:
        set_stage({entity_id: "ID", stage: "rejected"})
        add_notes({entity_id: "ID", notes: ["Rejected: reason"]})
3. If already registered (reconcile-on-touch):
    1. Read existing entity:
        get_entity({entity_id: "ID"})
    2. Apply Entity Reconciliation Procedure to notes and description

Relevance: always 0 during discovery. Do NOT assess criteria during crawl. Formal assessment happens via assess-entity agent afterward.

Rules:
- Do not assess criteria — register entities with relevance 0; assessment is a separate step
- Register even rejected entities (relevance 0) so they are not re-discovered
- NEVER access database directly — MCP tool calls are the only interface
- When pages use JavaScript rendering or require interaction, use browser automation if available; fall back to web search
- Final output: report entities registered, rejected, and entities found

--- Entity Reconciliation Procedure ---
{content of ${CLAUDE_PLUGIN_ROOT}/references/reconcile-entity.md}
```

### Directory Crawl Agent

```
Crawl directory entity `{directory_name}` (ID: `{directory_id}`) to discover example entities.

Read scope, domain knowledge, and traversal patterns:
- `blueprint/1-scope.md`
- `blueprint/6-domain-knowledge.md`
- `${CLAUDE_PLUGIN_ROOT}/references/directory-traversal.md`

Check directory entity for existing notes:
    get_entity({entity_id: "{directory_id}"})

Look for tagged crawl notes:
- `[CRAWL METHOD]:` — technical approach; if present, follow it; if absent, follow Approach Discovery Workflow in directory-traversal.md
- `[CRAWL SCRIPT]:` — file path to extraction script; if present, read and use (adjust START_PAGE from progress); if absent, develop during approach discovery and save
- `[CRAWL PROGRESS]:` — current position; if present, resume from indicated position; if absent, start from beginning

For batch results (multiple entities per extraction):
    register_entity({name: "...", url: "...", source_url: "https://directory-url.com", description: "...", relevance: 0, notes: ["fact1", "fact2"]})
Notes only written for new entities. Already-registered listed in output for reconciliation — read existing notes and apply Entity Reconciliation Procedure.

For individual entities:
1. Register:
    register_entity({name: "Entity Name", url: "https://entity-url.com", source_url: "https://directory-page-url.com", description: "One sentence: what entity is and primary approach", relevance: 0})
2. If new entity:
    1. Add notes:
        add_notes({entity_id: "ID", notes: ["observation 1", "observation 2"]})
    2. If entity fails hardline criterion:
        set_stage({entity_id: "ID", stage: "rejected"})
3. If already registered (reconcile-on-touch):
    1. Read entity and apply reconciliation:
        get_entity({entity_id: "ID"})

Directory crawl notes — tagged notes on directory entity track method, script, and progress:

`[CRAWL METHOD]:` — record technical approach before starting (or on first session); update only if approach changes:
    add_notes({entity_id: "{directory_id}", notes: ["[CRAWL METHOD]: [base URL, extraction technique, pagination, filtering, directory-specific details]"]})

`[CRAWL SCRIPT]:` — save extraction script and record pointer:
1. Save script to `blueprint/scripts/{directory_id}-{short_name}.js`
2. Add pointer note:
    add_notes({entity_id: "{directory_id}", notes: ["[CRAWL SCRIPT]: blueprint/scripts/{directory_id}-{short_name}.js"]})

`[CRAWL PROGRESS]:` — update after each page, section, or logical segment; remove previous and replace:
1. If previous progress note exists, remove it:
    remove_notes({entity_id: "{directory_id}", note_ids: ["N_ID"]})
2. Add updated progress:
    add_notes({entity_id: "{directory_id}", notes: ["[CRAWL PROGRESS]: [what was processed and where to resume]"]})

Write notes in terms that make sense for directory structure. Goal: new agent reading notes for first time can unambiguously understand approach and find resumption point.

Relevance: always 0 during crawl. Do NOT assess criteria during crawl. Formal assessment happens via assess-entity agent afterward.

Rules:
- Do not assess criteria — register entities with relevance 0; assessment is a separate step
- Register even rejected entities (relevance 0) so they are not re-discovered
- NEVER access database directly — MCP tool calls are the only interface
- Use browser automation when directory requires JavaScript rendering or interaction (filters, pagination, search forms); fall back to web fetch for static content; check accessibility notes
- Final output: report entities registered, rejected, directory progress, and top relevance entities

--- Entity Reconciliation Procedure ---
{content of ${CLAUDE_PLUGIN_ROOT}/references/reconcile-entity.md}
```

## Entity Modes

Interaction modes determine what kind of agent work an entity receives. Stored in `entity_modes` satellite table — an entity may have multiple modes. Database enforces valid values via CHECK constraint.

- `example` (default) — comparable sites to study and emulate; deep researched in Phase 2
- `directory` — crawlable listings that yield examples (member directories, curated lists); crawled in Phase 1
- `context` — knowledge/advice sources informing project (guides, data, advice); researched for domain knowledge in Phase 1
- `unclassified` — marker indicating assessment pass needed; coexists with other modes; removed by assess-entity agent

If an entity has two modes, it needs two different kinds of agent work. All modes share the same entity table, notes, URLs, and provenance.

## Output

- `blueprint/overview.md` — index pointing to numbered project definition files
- `blueprint/1-scope.md` through `blueprint/6-domain-knowledge.md` — project definition files
- `blueprint/data/research.db` — entities with relevance, descriptions, notes, provenance
- Entity list ordered by relevance — ready for Phase 2 deep research starting from top

## Gate

User approves:

1. Scope definition and assessment criteria
2. Domain knowledge (`blueprint/6-domain-knowledge.md`) reflects context research
3. Directory and context entities are identified
4. Entity relevance ordering reflects priorities for deep research
