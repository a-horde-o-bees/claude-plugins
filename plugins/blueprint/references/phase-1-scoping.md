# Phase 1: Scoping

## File Map

### Dependencies
```
.claude/skills/blueprint/blueprint_cli.py
references/reconcile-entity.md
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

Design phase — iterative exploration with integrated entity assessment.

## Seed Data

When database contains entities at Phase 1 start (from initialization arguments, prior sessions, or external import), treat them as unverified leads. Phase 1 landscape exploration and direct relevance assessment are required regardless of pre-existing data. Seeded entities are verified during exploration alongside new discoveries — not assumed correct. Discovery agents encountering a seeded entity's URL will hit registration dedup and skip it, but orchestrator must ensure every seeded entity gets directly assessed before Phase 1 gate: verify URL is live, confirm recency criterion, validate description against actual content, and reconcile notes.

## Input

User description, examples, or goals. Available as `$ARGUMENTS` if passed with `/blueprint`, or discussed interactively.

## Initial Scope

1. Parse user input into parent concept
2. Surface-level research — fetch examples, check what exists, identify landscape
  - Use web searches to gauge breadth of space
  - Note meta-sources encountered (directories, associations, aggregators)
3. Present findings:
  - Summarize parent concept as understood
  - Suggest related/adjacent concepts with brief evidence of what exists in each
  - Include concepts that might reveal user's true core intent — initial description is sometimes adjacent to what they actually need
4. User confirms which concepts belong in scope and which do not

## Refine Scope

5. For concepts user is uncertain about, do targeted surface research to help decide
6. Ask clarifying questions about goals — tailor to subject type discovered in Initial Scope:
  - Target audience or user base
  - Scale ambitions and success metrics
  - Key constraints (budget, timeline, skills, platform)
  - Differentiators — what should set this apart from existing examples
7. Offer to surface additional related concepts if user feels initial suggestions did not fully cover space
8. Present refined scope summary for approval
9. User may iterate (adjust concepts, request more suggestions, change focus) until scope feels right

## After Scope Approval

Complete project infrastructure (`docs/blueprint.md` already exists from initialization):

10. Write project definition files in `docs/`:
  - `overview.md` — lightweight index pointing to all numbered files with one-line purpose descriptions
  - `1-scope.md` — parent concept, confirmed in-scope concepts, excluded concepts (with brief rationale)
  - `2-assessment-criteria.md` — hardline filters, gradient criteria, relevance guide
  - `3-goals.md` — goals and priority order from refinement
  - `4-effectiveness-criteria.md` — criteria for judging whether patterns/approaches are effective
  - `5-constraints.md` — implementation realities (budget, timeline, skills, platform)
  - `6-domain-knowledge.md` — landscape structure and distilled context research findings (updated after each context wave)
11. Create `references/` directory
12. Initialize research database: `./cli.py claude blueprint init --db references/research.db`

## Domain Knowledge Development

Codify observations into domain knowledge that will guide discovery and deep research. Sources are registered as entities with `directory` or `context` roles.

13. Propose sources — directories (crawlable listings) and context sources (advice, data, guides). Register confirmed sources as entities:
    `./cli.py claude blueprint register --name "Source Name" --url "https://source-url.com" --description "What it contains and why it matters" --role directory --relevance 0 --db references/research.db`
    `./cli.py claude blueprint register --name "Source Name" --url "https://source-url.com" --description "What it contains and why it matters" --role context --relevance 0 --db references/research.db`

    For directory entities, add an accessibility note after registration:
    `./cli.py claude blueprint upsert notes --entity-id ID --notes "[ACCESSIBILITY]: {static|js-rendered|auth-gated|api-available} — {brief description of access method}" --db references/research.db`
    Accessibility classification guides orchestrator tool selection: `static` directories use web fetch agents; `js-rendered` and `auth-gated` directories require browser automation agents (sequential).

14. Present sources for user review:
    `./cli.py claude blueprint get entities --role directory --db references/research.db`
    `./cli.py claude blueprint get entities --role context --db references/research.db`

15. User refines — add, remove, or adjust sources

## Context Research Waves

Context entities (role: `context`) are knowledge sources researched in waves to build domain knowledge before landscape exploration. Each wave's findings update `docs/6-domain-knowledge.md`, enriching context for subsequent waves and discovery.

16. Order context entities by relevance (highest first). Low-relevance context entities may be deferred — document the cutoff decision in history.
17. For each wave (batch of context entities at similar relevance):
  1. Spawn context research agents — one agent per context entity, sequential by default
  2. After wave completes, review findings across all researched context entities in the wave
  3. Update `docs/6-domain-knowledge.md` with distilled insights from this wave
  4. Append history entry: wave number, entities researched count, key insights gained, next step
  5. If remaining unresearched context entities exist: reassess whether updated domain knowledge changes their value or suggests additional sources
18. When domain knowledge is sufficiently developed for informed landscape exploration: user confirms, proceed to directory traversal and targeted search

### Context Research Agent Prompt Template

```
Research context entity to extract domain knowledge relevant to the project.

Entity: `{entity_id}`

Read scope and domain knowledge:
- `docs/1-scope.md`
- `docs/6-domain-knowledge.md`

1. Resolve entity from database:
  `./cli.py claude blueprint get entity {entity_id} --db references/research.db`
2. Research entity's content thoroughly — focus on extracting knowledge, frameworks, data, and insights relevant to the project scope
3. After completing ALL research, read existing notes and apply Entity Reconciliation Procedure (see below):
  `./cli.py claude blueprint get entity {entity_id} --db references/research.db`
4. Set stage to researched:
  `./cli.py claude blueprint update entities --ids {entity_id} --stage researched --db references/research.db`

Rules:
- Complete ALL research before writing anything to database
- Final output text MUST state number of notes written, e.g.: "Wrote 14 notes to entity `{entity_id}`"
- Do NOT repeat entity details, notes, or research findings in output text — report only note count, entity ID, and errors encountered
- Do NOT create files — write only to database via CLI
- NEVER access database directly — CLI is only interface
- Every Bash call must be a single-line command starting with a recognized program name — no comments, no line continuations, no shell loops, no variable assignments before command
- Use `./cli.py claude blueprint` — never absolute paths
- When entity content uses JavaScript rendering, use browser automation tools if available. Fall back to web search when pages cannot be rendered.

--- Entity Reconciliation Procedure ---
`{content of references/reconcile-entity.md}`
```

Orchestrator appends content of `references/reconcile-entity.md` to this prompt before spawning agent.

## Landscape Exploration

Explore domain to understand structure and discover entities. Entities are assessed during discovery — not registered as stubs for later scoring. Two exploration modes:

- **Targeted search** — web searches with focused queries, following results to discover examples. Use discovery agent prompt template.
- **Directory crawl** — systematic traversal of directory entities (role: `directory`). Use directory crawl agent prompt template. Directory crawl agents track progress via notes on the directory entity so interrupted crawls can resume. Check directory entity's accessibility notes before spawning agent — `js-rendered` or `auth-gated` directories require browser automation tools.

19. For each directory entity: spawn directory crawl agent to systematically extract examples
20. For targeted searches: spawn discovery agents with focused queries to find examples not covered by directories
21. As entities are encountered, assess against scope criteria before registering:
  1. If entity fails hardline criterion (e.g., predates scope-defined recency cutoff):
    1. Register as rejected with description, notes, and reason
      `./cli.py claude blueprint register --name "Entity Name" --url "https://entity-url.com" --source-url "https://source.com" --description "One sentence: what entity is and its primary approach" --relevance 0 --db references/research.db`
      `./cli.py claude blueprint update entities --ids ID --stage rejected --db references/research.db`
      `./cli.py claude blueprint upsert notes --entity-id ID --notes "Rejected: reason" --db references/research.db`
  2. Else:
    1. Register with relevance assessment, description, role, and initial notes
      `./cli.py claude blueprint register --name "Entity Name" --url "https://entity-url.com" --source-url "https://source.com" --description "One sentence: what entity is and its primary approach" --relevance N [--role example|directory|context] --db references/research.db`
      `./cli.py claude blueprint upsert notes --entity-id ID --notes "observation 1" "observation 2" --db references/research.db`
22. Observe patterns across what is found:
  - What types of structured public data exist for this type of entity?
  - What differentiates entities in this space?
  - Which entities address core concerns from scope?
23. Present accumulated entities and observations to user

### Entity Roles

Entities have three roles:
- `example` (default) — comparable sites to study and emulate
- `directory` — crawlable listings that yield examples (e.g., member directories, curated lists)
- `context` — knowledge/advice sources whose content informs the project (e.g., SEO guides, marketing data)

All roles share the same table, notes, URLs, and provenance. Role determines how agents interact with the entity and what notes capture.

### Discovery Agent Prompt Template

```
Explore `{source_description}` to discover entities relevant to this project scope.

Read scope and domain knowledge:
- `docs/1-scope.md`
- `docs/6-domain-knowledge.md`

Entities have three roles:
- `example` (default) — comparable sites to study and emulate
- `directory` — crawlable listings that yield examples
- `context` — knowledge/advice sources whose content informs the project

For each entity you encounter:
1. Assess against assessment criteria (from `docs/2-assessment-criteria.md`)
2. Register with appropriate role — `register` returns either new ID or "Already registered" with existing ID:
  `./cli.py claude blueprint register --name "Entity Name" --url "https://entity-url.com" --source-url "https://source-where-found.com" --description "One sentence: what entity is and its primary approach" --relevance N [--role example|directory|context] --db references/research.db`
3. If new entity:
  1. Add notes capturing whatever you already know:
    `./cli.py claude blueprint upsert notes --entity-id ID --notes "observation 1" "observation 2" --db references/research.db`
  2. If entity fails hardline criterion: update stage to rejected with reason:
    `./cli.py claude blueprint update entities --ids ID --stage rejected --db references/research.db`
    `./cli.py claude blueprint upsert notes --entity-id ID --notes "Rejected: reason" --db references/research.db`
4. If already registered (reconcile-on-touch): read existing entity, apply Entity Reconciliation Procedure (see below):
  1. `./cli.py claude blueprint get entity ID --db references/research.db`
  2. Apply Entity Reconciliation Procedure to notes, description, and relevance

Relevance guide (scale is project-specific, defined by criteria count):
  Read `docs/2-assessment-criteria.md` for relevance guide.

Rules:
- Assess each entity as you encounter it — do not register stubs for later evaluation
- Register even rejected entities (with relevance 0) so they are not re-discovered
- NEVER access database directly — CLI is only interface
- Every Bash call must be a single-line command starting with a recognized program name — no comments, no line continuations, no shell loops, no variable assignments before the command
- Use `./cli.py claude blueprint` — never absolute paths
- When pages use JavaScript rendering or require interaction, use browser automation tools if available. Fall back to web search when pages cannot be rendered.
- Final output: report entities registered, rejected, and top relevance entities found

--- Entity Reconciliation Procedure ---
`{content of references/reconcile-entity.md}`
```

Orchestrator appends content of `references/reconcile-entity.md` to this prompt before spawning agent.

### Directory Crawl Agent Prompt Template

```
Crawl directory entity `{directory_name}` (ID: `{directory_id}`) to discover example entities.

Read scope, domain knowledge, and traversal patterns:
- `docs/1-scope.md`
- `docs/6-domain-knowledge.md`
- `.claude/skills/blueprint/references/directory-traversal.md`

First, check the directory entity for existing notes:
  `./cli.py claude blueprint get entity {directory_id} --db references/research.db`

Look for tagged crawl notes:
- `[CRAWL METHOD]:` — technical approach. If present, follow it. If absent, follow the Approach Discovery Workflow in `directory-traversal.md` to develop one.
- `[CRAWL SCRIPT]:` — file path to saved extraction script. If present, read the file and use it (adjust START_PAGE from progress note). If absent, develop script during approach discovery and save it.
- `[CRAWL PROGRESS]:` — current position. If present, resume from where indicated. If absent, start from the beginning.

For batch extraction results (multiple entities per extraction call), use `register-batch`:
  `./cli.py claude blueprint register-batch --json '[{"name": "...", "url": "...", "description": "...", "relevance": N, "notes": ["fact1", "fact2"]}, ...]' --source-url "https://directory-url.com" --db references/research.db`
Notes are only written for new entities. Already-registered entities are listed in output for manual reconciliation — read their existing notes and apply Entity Reconciliation Procedure.

For individual entities (small directories, one-off discoveries):
1. Assess against assessment criteria (from `docs/2-assessment-criteria.md`)
2. Register:
  `./cli.py claude blueprint register --name "Entity Name" --url "https://entity-url.com" --source-url "https://directory-page-url.com" --description "One sentence: what entity is and its primary approach" --relevance N --db references/research.db`
3. If new entity:
  1. Add notes: `./cli.py claude blueprint upsert notes --entity-id ID --notes "observation 1" "observation 2" --db references/research.db`
  2. If entity fails hardline criterion: update stage to rejected:
    `./cli.py claude blueprint update entities --ids ID --stage rejected --db references/research.db`
4. If already registered (reconcile-on-touch):
  1. `./cli.py claude blueprint get entity ID --db references/research.db`
  2. Apply Entity Reconciliation Procedure to notes, description, and relevance

CRITICAL — Directory crawl notes:

Tagged notes on directory entity track method, script, and progress:

`[CRAWL METHOD]:` — Record the technical approach before starting (or on first session). Only update if approach changes.

1. Add method note (once, before first crawl):
  `./cli.py claude blueprint upsert notes --entity-id {directory_id} --notes "[CRAWL METHOD]: [base URL, extraction technique, pagination, filtering logic, directory-specific details]" --db references/research.db`

`[CRAWL SCRIPT]:` — Save extraction script to file and record pointer. Enables session resumption without reconstructing the script.

1. Save script to `references/crawl-scripts/{directory_id}-{short_name}.js`
2. Add pointer note:
  `./cli.py claude blueprint upsert notes --entity-id {directory_id} --notes "[CRAWL SCRIPT]: references/crawl-scripts/{directory_id}-{short_name}.js" --db references/research.db`

`[CRAWL PROGRESS]:` — Update after completing each page, section, or logical segment. Remove previous progress note and replace with current position.

1. Remove the previous progress note (if one exists):
  `./cli.py claude blueprint remove notes --entity-id {directory_id} --note-ids N_ID --db references/research.db`
2. Add updated progress note:
  `./cli.py claude blueprint upsert notes --entity-id {directory_id} --notes "[CRAWL PROGRESS]: [describe what was processed and where to resume, e.g., 'Processed pages 1-47 of 136, resume on page 48, 23 entities registered' or 'Processed developmental editing filter results 1-40 of 120, resume at result 41']" --db references/research.db`
3. Touch the directory entity to update its timestamp:
  `./cli.py claude blueprint touch entities --ids {directory_id} --db references/research.db`

Write both notes in whatever terms make sense for this directory's structure. The goal is that a new agent reading these notes for the first time can unambiguously understand the approach and find the resumption point.

Relevance guide (scale is project-specific, defined by criteria count):
  Read `docs/2-assessment-criteria.md` for relevance guide.

Rules:
- Assess each entity as you encounter it — do not register stubs for later evaluation
- Register even rejected entities (with relevance 0) so they are not re-discovered
- NEVER access database directly — CLI is only interface
- Every Bash call must be a single-line command starting with a recognized program name — no comments, no line continuations, no shell loops, no variable assignments before the command
- Use `./cli.py claude blueprint` — never absolute paths
- Use browser automation tools when directory content requires JavaScript rendering or interaction (filters, pagination, search forms). Fall back to web fetch for static content. Check directory entity's accessibility notes before choosing approach.
- Final output: report entities registered, rejected, directory progress, and top relevance entities found

--- Entity Reconciliation Procedure ---
`{content of references/reconcile-entity.md}`
```

Orchestrator appends content of `references/reconcile-entity.md` to this prompt before spawning agent. Orchestrator uses directory crawl template when source is a directory entity, discovery template for targeted web searches.

## Scope Refinement and Relevance Adjustment

23. User reviews accumulated entities and domain knowledge, directs next steps:
  - "Look at more entities in [region/category]"
  - "What do the [sources] say about this space?"
  - "Check [specific directory or aggregator]"
  - "That category is more important than I thought — boost those entities"
  - "Remove source [X] — not relevant"
24. Execute directed exploration, register new entities
25. When scope criteria change, spawn reassess-relevance agent (`references/reassess-relevance.md`) to rescore all researched entities against updated criteria using existing notes. No new research needed unless notes are insufficient for a specific criterion.
26. Repeat until user considers landscape adequately mapped and entity relevance ordering reflects priorities

## Re-Entry

When Phase 1 resumes with existing data, present re-entry dashboard:

1. `./cli.py claude blueprint get stats --db references/research.db` — entity counts by role and stage
2. `./cli.py claude blueprint get entities --role example --db references/research.db` — examples sorted by relevance
3. `./cli.py claude blueprint get entities --role directory --db references/research.db` — directories (check progress notes)
4. `./cli.py claude blueprint get entities --role context --db references/research.db` — context/knowledge sources
5. `./cli.py claude blueprint get provenance --db references/research.db` — provenance sources with entity counts
6. `./cli.py claude blueprint get reach --min 2 --db references/research.db` — multi-source entities
7. `docs/overview.md` for file index, `docs/1-scope.md` for scope context

User directs next action: explore more, crawl directories, refine relevance, or proceed to deep research.

## Output

- `docs/overview.md` — index pointing to numbered project definition files
- `docs/1-scope.md` through `docs/6-domain-knowledge.md` — project definition files
- `references/research.db` — entities with relevance, descriptions, and notes; provenance
- Entity list ordered by relevance — ready for Phase 2 deep research starting from top

## Gate

User approves:
1. Scope definition and assessment criteria
2. Domain knowledge file (`docs/6-domain-knowledge.md`) reflects context research
3. Directory and context entities identified
4. Entity relevance ordering reflects priorities for deep research
