---
name: blueprint-research
description: |
  Structured solution research and implementation planning. Studies existing tools, proven approaches, and established patterns through iterative cycles: initialization, expand/consolidate/present cycles, directions, and implementation blueprint. Uses emergent schema with unified entity model and SQLite database.
argument-hint: "[scope description]"
allowed-tools:
  - Read
  - Write
  - Edit
  - AskUserQuestion
  - WebFetch
  - WebSearch
  - Bash(python3 *)
  - Bash(mkdir *)
  - Bash(cp *)
  - mcp__plugin_blueprint_blueprint-research__*
---

# /blueprint-research

Structured solution research and implementation planning. Studies existing tools, proven approaches, and established patterns to fulfill a defined purpose: defines scope with integrated entity assessment, iterates expand/consolidate/present cycles to build and refine the research landscape, synthesizes cross-entity patterns, and produces actionable implementation blueprint.

Reads `blueprint/data/state.md` to detect current state. If absent, initializes from template and starts Initialization. Otherwise, detects active stage and proposes resuming or advancing.

## Process Model

### Cycle Architecture

Research proceeds through initialization, repeatable cycles, and post-cycling deliverables. Initialization establishes foundations using the same expand and present building blocks that cycles use. Each cycle autonomously expands and consolidates the research landscape, then presents findings for user steering.

| Stage | Name | Type | Key Output |
|-------|------|------|------------|
| Initialization | Initialization | Design | Project definition files, database initialized, entities with relevance, initial landscape |
| Cycle N | Expand/Consolidate/Present | Execution | Research DB populated with notes, relationships, capabilities, measures, findings |
| Directions | Directions | Design | `blueprint/9-directions.md` |
| Blueprint | Implementation Blueprint | Design | `blueprint/10-blueprint.md` |

Initialization and post-cycling stages include refinement loops -- user iterates until satisfied. Cycles run autonomous agent work with user decision points between cycles. All reference file paths relative to `${CLAUDE_PLUGIN_ROOT}`.

### Phase Building Blocks

Cycles and initialization share three building blocks:

**Expand** -- discover and research context sources:
1. Targeted web searches informed by scope and domain knowledge
2. Deep research all entities marked as `context`
3. Register directories and entities discovered -- do not deep research non-context entities
4. Update domain knowledge from context research

**Consolidate** -- crawl, assess, research, analyze:
5. Crawl all known directory entities using current criteria
6. Assess and register entities discovered during crawls
7. Deep research entities from highest relevance down within per-cycle limit
8. New directories discovered this cycle postponed to next cycle
9. Resolve duplicates
10. Run analysis across all researched entities
11. Extract measures from entity notes
12. Compile findings and recommendations

**Present** -- surface metrics and findings:
13. Compute coverage: `get_coverage()`
14. Compute criteria effectiveness: `get_criteria_effectiveness()`
15. Present consolidated picture
16. User decides: another cycle (with adjustments) or produce blueprint

### Definition File Usage

Which project definition files agents read at each stage:

| File | Init | Expand | Consolidate | Present | Directions | Blueprint |
|------|------|--------|-------------|---------|------------|-----------|
| `blueprint/1-scope.md` | R | R | -- | -- | -- | -- |
| `blueprint/2-goals.md` | R | -- | -- | R | R | R |
| `blueprint/3-assessment-criteria.md` | R | R | R | -- | -- | -- |
| `blueprint/4-effectiveness-criteria.md` | -- | -- | R | -- | -- | -- |
| `blueprint/5-constraints.md` | -- | -- | -- | -- | -- | R |
| `blueprint/6-domain-knowledge.md` | R | R | R | R | R | R |

Files 1-5 populated during Initialization scope approval. File 6 updated after context research and when deep research reveals new platforms, tools, or business models.

Domain knowledge guard: `6-domain-knowledge.md` documents what exists (platforms, tools, patterns) and what to look for. Must not contain frequency analysis, adoption rates, or absence observations -- those belong in consolidate phase output.

## Trigger

User runs `/blueprint-research`. Optional `$ARGUMENTS` passed as initial scope input for Initialization.

## Route

1. If `blueprint/data/state.md` does not exist:
    1. If `blueprint/` directory exists:
        1. Exit to user -- report existing blueprint folder; skill initializes this directory and cannot run over existing content
    2. Create `blueprint/data/` directory and copy `${CLAUDE_PLUGIN_ROOT}/templates/blueprint.md` to `blueprint/data/state.md`
    3. Mark Initialization as `[-]`; use `$ARGUMENTS` as initial scope input if provided
    4. Go to step 3. Determine active stage
2. Read `blueprint/data/state.md`
3. Determine active stage:
    1. If `blueprint/data/history.md` exists: read last 5 lines for current stride and next steps
    2. Parse state file:
        1. If Initialization is `[-]` or `[ ]`: propose starting or resuming Initialization
        2. Else if latest Cycle N is `[-]`: propose resuming Cycle N
        3. Else if latest Cycle N is `[x]` and Directions is `[ ]`: propose starting next cycle or advancing to Directions
        4. Else if Directions is `[-]` or `[ ]`: propose starting or resuming Directions
        5. Else if Blueprint is `[-]` or `[ ]`: propose starting or resuming Blueprint
        6. Else if all `[x]`: report complete; offer re-invocation of any stage
4. User confirms stage or requests adjustment
5. {active-stage} = confirmed stage
6. Dispatch Workflow

## Workflow

1. Mark {active-stage} status `[-]` in `blueprint/data/state.md`
2. If {active-stage} is Initialization:
    1. Read `${CLAUDE_PLUGIN_ROOT}/references/phase-1-scoping.md`
    2. Execute scoping per reference file -- user approves scope definition files
    3. Run Expand phase -- targeted searches, discover context/directory entities, deep research context sources
    4. Run Present phase -- show landscape, directories found, domain knowledge
    5. User reviews foundations:
        1. If refinement needed: repeat from step 2.3 -- re-expand with refined scope
        2. If foundations approved: continue
    6. Mark Initialization `[x]` in `blueprint/data/state.md`
    7. Add Cycle 1 entry as `[ ]` in `blueprint/data/state.md`
    8. Propose starting Cycle 1
3. Else if {active-stage} is Cycle N:
    1. Check for unclassified entities: `get_unclassified()`
    2. If count > 0: propose spawning assess-entity agent (`${CLAUDE_PLUGIN_ROOT}/references/assess-entity.md`) before proceeding; wait for user confirmation
    3. Run Expand phase:
        1. Targeted web searches informed by scope and domain knowledge
        2. Deep research all entities with `context` mode not yet at `researched` stage
        3. Register directories and entities discovered -- do not deep research non-context entities
        4. Update `blueprint/6-domain-knowledge.md` from context research
    4. Run Consolidate phase:
        1. Crawl all known directory entities using current criteria
        2. Assess and register entities discovered during crawls via assess-entity agent (`${CLAUDE_PLUGIN_ROOT}/references/assess-entity.md`)
        3. Deep research entities from highest relevance down within per-cycle limit -- one agent per entity
        4. New directories discovered this cycle: register but postpone crawling to next cycle
        5. Propose spawning resolve-duplicates agent (`${CLAUDE_PLUGIN_ROOT}/references/resolve-duplicates.md`); wait for user confirmation
        6. Read `${CLAUDE_PLUGIN_ROOT}/references/phase-3-analysis.md`
        7. Run analysis across all researched entities
        8. Extract measures from entity notes
        9. Compile findings to `blueprint/7-findings.md` and recommendations to `blueprint/8-interpretation.md`
    5. Run Present phase:
        1. Compute coverage: `get_coverage()`
        2. Save coverage output to `blueprint/data/coverage-cycle-{N}.md`
        3. If prior cycle snapshot exists (`blueprint/data/coverage-cycle-{N-1}.md`): compare per-domain entity counts and note averages to compute density shift and diminishing returns signal
        4. Compute criteria effectiveness: `get_criteria_effectiveness()`
        5. Present consolidated picture -- coverage metrics, density shift from prior cycle, effectiveness, findings summary, recommendations
        6. Read `blueprint/2-goals.md` -- present progress toward goals
    6. Mark Cycle N `[x]` in `blueprint/data/state.md`
    7. Append history entry to `blueprint/data/history.md`
    8. User decides:
        1. If another cycle: add Cycle N+1 entry as `[ ]` in `blueprint/data/state.md`; user may adjust scope, criteria, or per-cycle limit; propose starting Cycle N+1
        2. If advance to Directions: propose starting Directions
4. Else if {active-stage} is Directions:
    1. Read `blueprint/8-interpretation.md` -- source of recommendations
    2. Read `blueprint/2-goals.md` -- context for directional choices
    3. For each recommendation in interpretation:
        1. Present recommendation to user
        2. User marks: pursue, defer, or reject -- with reasoning
    4. User may add directions not in interpretation
    5. Write decisions to `blueprint/9-directions.md` using template from `${CLAUDE_PLUGIN_ROOT}/templates/9-directions.md`
    6. Mark Directions `[x]` in `blueprint/data/state.md`
    7. Propose starting Blueprint
5. Else if {active-stage} is Blueprint:
    1. Read `${CLAUDE_PLUGIN_ROOT}/references/phase-4-implementation.md`
    2. Read `blueprint/9-directions.md` -- only approved directions
    3. Read `blueprint/5-constraints.md` -- implementation realities
    4. Read `blueprint/6-domain-knowledge.md` -- landscape context
    5. Execute blueprint per reference file -- user approves implementation plan
    6. Write to `blueprint/10-blueprint.md` using template from `${CLAUDE_PLUGIN_ROOT}/templates/10-blueprint.md`
    7. Mark Blueprint `[x]` in `blueprint/data/state.md`
6. Append history entry to `blueprint/data/history.md` -- one line: ISO 8601 datetime, stage, action, result stats, next step

Interactive checkpoints in main conversation between agent calls. Subagents run autonomously -- user-facing decisions at orchestration level only.

### Report

After each stage: summary of outputs produced, entities affected, coverage metrics (when available), and recommended next stage.

## Project Infrastructure

State detection creates `blueprint/data/state.md` on first run. Initialization creates remaining structure. All output files follow templates in `${CLAUDE_PLUGIN_ROOT}/templates/` -- see `templates/overview.md` for the complete deliverable index.

```
blueprint/
  data/
    state.md                — stage progress tracker (from templates/blueprint.md)
    history.md              — sequential stride log with timestamps
    research.db             — SQLite research database
    friction.md             — process friction observations captured during research
    coverage-cycle-{N}.md   — coverage snapshot at each cycle boundary for density shift comparison
  overview.md               — complete deliverable index (from templates/overview.md)
  1-scope.md through 6-domain-knowledge.md  — project definition (Initialization)
  7-findings.md             — cross-entity analysis (Consolidate)
  8-interpretation.md       — actionable conclusions (Consolidate)
  9-directions.md           — user directional choices (Directions)
  10-blueprint.md           — implementation plan; final deliverable (Blueprint)
  scripts/                  — crawl scripts for directory traversal
```

Status markers in `blueprint/data/state.md`: `[ ]` pending, `[-]` in progress, `[x]` complete. Cycle entries added dynamically as cycles are initiated.

## Database

SQLite database at `blueprint/data/research.db`.

### MCP Tools

The `blueprint-research` MCP server exposes domain tools grouped by function. The server starts automatically when the plugin is installed. Database path configured via `DB_PATH` environment variable (default: `blueprint/data/research.db`).

#### Entity Registration

| Tool | Parameters | Description |
|------|-----------|-------------|
| `register_entity` | `name`, `url?`, `source_url?`, `modes?`, `relevance?`, `description?`, `purpose?` | Register single entity; URL normalization, dedup, provenance |
| `register_entities` | `entities` (array), `source_url?` | Batch register entities from a single source |

#### Entity Field Updates

| Tool | Parameters | Description |
|------|-----------|-------------|
| `set_stage` | `entity_id`, `stage` | Advance entity stage; validates transitions (`new` → `rejected` \| `researched` \| `merged`) |
| `set_relevance` | `entity_id`, `relevance` | Set entity relevance score |
| `set_description` | `entity_id`, `description` | Set entity description |
| `set_modes` | `entity_id`, `modes` (array) | Replace entity modes |
| `add_modes` | `entity_id`, `modes` (array) | Add modes to entity (preserves existing) |
| `remove_modes` | `entity_id`, `modes` (array) | Remove specific modes from entity |
| `reject_entity` | `entity_id`, `reason` | Reject entity -- sets stage to rejected, relevance to -1, adds reason as note |

#### Notes

| Tool | Parameters | Description |
|------|-----------|-------------|
| `add_notes` | `entity_id`, `notes` (array of strings) | Add one or more notes to an entity |
| `set_note` | `note_id`, `text` | Update existing note text |
| `remove_notes` | `entity_id`, `note_ids` (array) | Delete specific notes from an entity |

#### Measures

| Tool | Parameters | Description |
|------|-----------|-------------|
| `set_measures` | `entity_id`, `measures` (array of `{measure, value}`) | Set key/value measures on an entity |
| `clear_measures` | `entity_id` | Clear all measures from one entity |
| `clear_all_measures` | (none) | Clear all measures across all entities |

#### Retrieval

| Tool | Parameters | Description |
|------|-----------|-------------|
| `get_entity` | `entity_id` | Get entity with all related data (notes, measures, URLs) |
| `list_entities` | `mode?`, `stage?`, `min_relevance?` | List entities with optional filters |
| `get_unclassified` | (none) | Get entities with `unclassified` mode |
| `get_dashboard` | (none) | Overview of entity counts by stage, mode, and relevance |
| `get_research_queue` | (none) | Entities ready for deep research, ordered by relevance |
| `get_measure_summary` | (none) | Summary of measures across entities |
| `find_duplicates` | (none) | Detect potential duplicate entities by URL or name similarity |

#### Criteria

| Tool | Parameters | Description |
|------|-----------|-------------|
| `set_criteria` | `criteria` (array of {type, name, gate}) | Replace ALL criteria definitions; cascade deletes old links |
| `add_criterion` | `type`, `name`, `gate` | Add single criterion definition |
| `remove_criterion` | `criterion_id` | Remove criterion and cascade-delete its note links |
| `get_criteria` | (none) | List all criteria with type, name, gate |
| `link_criterion_note` | `criterion_id`, `note_id`, `quality` | Link criterion to note with quality (pass/fail) |
| `unlink_criterion_note` | `criterion_id`, `note_id` | Remove specific criterion-note link |
| `clear_criterion_links` | `criterion_id` | Remove all note links for a criterion |
| `get_assessment` | `entity_id` | Computed per-entity: criterion quality, hardline result, relevancy count |
| `compute_relevance` | `entity_id` | Recompute cached relevance from criterion-note links |

#### Domains

| Tool | Parameters | Description |
|------|-----------|-------------|
| `set_domains` | `domains` (array of {name, description?}) | Replace ALL domain definitions; cascade deletes old junction links |
| `add_domain` | `name`, `description?` | Add single domain definition |
| `remove_domain` | `domain_id` | Remove domain and cascade-delete junction links |
| `get_domains` | (none) | List all domains with linked criteria counts |
| `link_domain_criterion` | `domain_id`, `criterion_id` | Link domain to criterion; many-to-many |
| `unlink_domain_criterion` | `domain_id`, `criterion_id` | Remove domain-criterion link |

#### Goals

| Tool | Parameters | Description |
|------|-----------|-------------|
| `set_goals` | `goals` (array of {name, description?}) | Replace ALL goal definitions; cascade deletes old junction links |
| `add_goal` | `name`, `description?` | Add single goal definition |
| `remove_goal` | `goal_id` | Remove goal and cascade-delete junction links |
| `get_goals` | (none) | List all goals with linked domain counts |
| `link_goal_domain` | `goal_id`, `domain_id` | Link goal to domain; many-to-many |
| `unlink_goal_domain` | `goal_id`, `domain_id` | Remove goal-domain link |

#### Coverage and Effectiveness

| Tool | Parameters | Description |
|------|-----------|-------------|
| `get_coverage` | (none) | Per-domain: researched entity count, criteria count, avg notes/entity; entity pool trajectory |
| `get_criteria_effectiveness` | (none) | Per-criterion: pass/fail/not-assessed counts, hit rate, discrimination, hardline rejection distribution, untriggered criteria |

#### Schema, Merge, and Query

| Tool | Parameters | Description |
|------|-----------|-------------|
| `describe_schema` | `table?` | Schema discovery — tables, columns, types, FK relationships |
| `merge_entities` | `entity_ids` (array) | Merge entities into lowest-ID survivor; preserves all related data |
| `init_database` | (none) | Initialize database schema; idempotent |

#### Examples

```json
// Register entity with URL dedup and provenance
register_entity({name: "Semgrep", url: "https://github.com/semgrep/semgrep", source_url: "https://directory.com", modes: ["context"], relevance: 5})

// Batch register entities from a directory source
register_entities([{name: "Tool A", url: "https://tool-a.dev"}, {name: "Tool B", url: "https://tool-b.dev"}], source_url: "https://directory.com")

// Add notes to an entity
add_notes({entity_id: "e1", notes: ["First observation", "Second observation"]})

// Get entity with all related data
get_entity({entity_id: "e1"})

// List researched entities with minimum relevance
list_entities({stage: "researched", min_relevance: 7})

// Set entity stage after research complete
set_stage({entity_id: "e1", stage: "researched"})

// Reject entity with reason
reject_entity({entity_id: "e3", reason: "Does not meet open-source hardline criterion"})

// Set relevance (count of criteria met)
set_relevance({entity_id: "e1", relevance: 5})

// Update a note
set_note({note_id: "n14", text: "Corrected observation"})

// Remove notes
remove_notes({entity_id: "e1", note_ids: ["n14"]})

// Clear all measures before re-analysis
clear_all_measures()

// Set measures on an entity
set_measures({entity_id: "e1", measures: [{measure: "adoption", value: "high"}, {measure: "maturity", value: "stable"}]})

// Register domains and link to criteria
set_domains([{name: "Static Analysis", description: "Code scanning tools"}, {name: "Runtime Security", description: "Live monitoring"}])
link_domain_criterion({domain_id: "d1", criterion_id: "c1"})

// Register goals and link to domains
set_goals([{name: "Reduce false positives", description: "Minimize noise in scan results"}])
link_goal_domain({goal_id: "g1", domain_id: "d1"})

// Coverage and effectiveness
get_coverage()
get_criteria_effectiveness()

// Complex query (only when no domain tool covers the need)
query({sql: "SELECT e.name, COUNT(n.id) as note_count FROM entities e LEFT JOIN entity_notes n ON n.entity_id = e.id GROUP BY e.id"})
```

### ID Convention

Single-letter prefixes: `e` (entity), `n` (note), `c` (criterion), `d` (domain), `g` (goal). IDs are stored, displayed, and accepted identically — `e7` in output is `e7` in input.

### Data Model

Unified entity model — everything is an entity (organizations, platforms, programs). Core fields:

- `id` — prefixed TEXT (e.g., `e7`), stable, never changes
- `name` — display name
- `stage` — `new` → `rejected` | `researched` | `merged`; enforced by CHECK constraint
- `relevance` — integer; count of binary assessment criteria met from `blueprint/3-assessment-criteria.md`; higher = more criteria satisfied; -1 = rejected; 0 = none met or not yet assessed
- `description` — one-sentence identity statement; notes hold specifics, description never lists features or counts
- `purpose` — why this entity matters to the research; summarizes relevance outside of notes for intelligent navigation

**Modes** (`entity_modes` table): interaction modes that determine what kind of agent work an entity receives. An entity may have multiple modes. Default mode is `unclassified`. Enforced by CHECK constraint.

- `example` — comparable tool, project, or system to study; receives deep research during Consolidate
- `directory` — crawlable listing that yields other entities; receives directory crawl agents during Consolidate
- `context` — knowledge, advice, or data source; receives context research during Expand
- `unclassified` — marker indicating assessment pass needed; coexists with other modes; removed by assess-entity agent (`${CLAUDE_PLUGIN_ROOT}/references/assess-entity.md`)

If an entity has two modes, it needs two different kinds of agent work — crawl it AND deep-research it. These are separate activities that happen in different phases of a cycle.

**Notes**: atomic, self-explanatory facts. Primary knowledge store. Begin accumulating from first contact — not deferred to deep research. Deep research produces comprehensive notes; discovery produces initial notes from whatever information is consumed.

**Criteria** (`criteria` table): assessment definitions loaded from `blueprint/3-assessment-criteria.md`. Two types: `hardline` (reject on fail) and `relevancy` (count toward relevance score). Each criterion has a `gate` — an explicit pass/fail description with concrete thresholds. Populated via `set_criteria()` during Initialization infrastructure setup.

**Criteria-Note Links** (`criteria_notes` junction): many-to-many between criteria and entity_notes with quality (`pass`/`fail`). Links are the evidence trail — trace any relevance score to specific notes. Resolution: any "pass" link for a criterion-entity pair means passed (supersedes fail). Only "fail" links means failed. No links means not assessed. ON DELETE CASCADE from both criteria and entity_notes.

**Domains** (`domains` table): research domains that organize criteria into functional areas. Each domain has `id`, `name`, and `description`. Linked to criteria via `domain_criteria` junction table (many-to-many). Coverage metrics are computed per domain.

**Goals** (`goals` table): project goals that define what success looks like. Each goal has `id`, `name`, and `description`. Linked to domains via `goal_domains` junction table (many-to-many). Goals form the top of the relationship chain: goals → goal_domains → domains → domain_criteria → criteria → criteria_notes → entity_notes → entities.

**Measures**: universal key/value pairs produced by analysis (Consolidate phase). Not produced during Expand. Measures are cleared at the point of change — when assessment criteria or effectiveness criteria are modified, the modifying workflow step clears measures immediately. Adding new entities does not invalidate existing measures.

**URLs**: separate `entity_urls` table; multiple normalized URLs per entity. URL normalization strips scheme, www, trailing slash, lowercases, keeps path. Dedup during registration checks normalized URLs.

**Provenance**: `url_provenance` table links source URL → entity ID. Many-to-many: same entity found via multiple sources.

**Source data**: `entity_source_data` table stores structured key/value pairs per source type. Keys defined by source templates.

### Tagged Notes

`[TAG]:` prefix convention for machine-parseable markers:

| Tag | Used On | Purpose |
|-----|---------|---------|
| `[ACCESSIBILITY]:` | Directory entities | Content access: `static`, `js-rendered`, `auth-gated`, `api-available` |
| `[CRAWL METHOD]:` | Directory entities | Technical extraction approach |
| `[CRAWL SCRIPT]:` | Directory entities | Path to script in `blueprint/scripts/` |
| `[CRAWL PROGRESS]:` | Directory entities | Mutable crawl position and resumption point |

New tags may emerge per project. Convention: bracketed uppercase, descriptive, unique per entity (replace, not duplicate).

### Concurrency

WAL mode for concurrent reads. Write operations use retry with random 50-200ms jitter, retrying indefinitely on lock. Agents write simultaneously — reads never block, writes queue.

### Complex Queries

Use domain retrieval tools (`get_entity`, `list_entities`, `get_dashboard`, `get_research_queue`, `get_unclassified`, `find_duplicates`, `get_measure_summary`, `get_coverage`, `get_criteria_effectiveness`) for most reads. For complex joins, aggregations, or subqueries that no domain tool covers, use the `query` tool with read-only SQL. The `query` tool enforces SELECT-only — write operations are rejected.

Key tables: `entities`, `entity_urls`, `url_provenance`, `entity_notes`, `entity_measures`, `entity_source_data`, `domains`, `goals`, `goal_domains`, `domain_criteria`.

## Recommended MCP Servers

Optional servers that enhance capabilities when configured:

| Server | Package | Purpose |
|--------|---------|---------|
| Playwright | `@playwright/mcp` | Browser automation for JS-rendered pages, forms, dynamic content |
| Playwright Parallel | `playwright-parallel-mcp` | Concurrent browser sessions with process-level isolation via `sessionId` |

Setup:

```
claude mcp add playwright -- npx @playwright/mcp@latest
claude mcp add playwright-parallel -- npx playwright-parallel-mcp
```

`playwright-parallel-mcp` env vars: `MAX_SESSIONS` (default 10), `SESSION_TIMEOUT_MS` (default 3600000), `PLAYWRIGHT_PARALLEL_MODE` (`lite` | `full`).

Orchestrator selects server based on directory accessibility notes and concurrent browser agent needs. Single browser agent: either server. Parallel browser agents: `playwright-parallel-mcp`.

## Rules

### Agent Spawning

- Spawn autonomous agents — one per discrete research unit
- One agent per entity for deep research, single pass — relevance ordering determines priority
- Sequential by default — parallel only when explicitly approved by user
- Subagents inherit parent tools and permissions from settings.json

### Agent Database Access

- Agents access database exclusively through MCP domain tools (`register_entity`, `register_entities`, `add_notes`, `set_note`, `remove_notes`, `set_measures`, `set_stage`, `set_relevance`, `set_description`, `set_modes`, `add_modes`, `remove_modes`, `reject_entity`, `get_entity`, `list_entities`, `get_unclassified`, `get_dashboard`, `get_research_queue`, `find_duplicates`, `get_measure_summary`, `get_coverage`, `get_criteria_effectiveness`, `describe_schema`, `merge_entities`, `query`, `set_domains`, `add_domain`, `remove_domain`, `get_domains`, `link_domain_criterion`, `unlink_domain_criterion`, `set_goals`, `add_goal`, `remove_goal`, `get_goals`, `link_goal_domain`, `unlink_goal_domain`, `set_criteria`, `add_criterion`, `remove_criterion`, `get_criteria`, `link_criterion_note`, `unlink_criterion_note`, `clear_criterion_links`, `get_assessment`, `compute_relevance`)
- Agents push notes directly to database via `add_notes` — no intermediate JSON files for knowledge storage; files only for artifacts (templates, PDFs, source documents)
- Agent database errors: report in output text, do not diagnose or fix schema issues

### Agent Write Discipline

- Scoping and crawl agents register entities with `register_entity`/`register_entities` during landscape exploration, then capture observations with `add_notes`; crawl agents set relevance=0 on newly discovered entities; formal assessment via assess-entity afterward
- Entities failing hardline criteria: register with relevance -1 via `reject_entity`, which sets stage to `rejected`, relevance to -1, and adds rejection reason as note
- Deep research agents receive entity IDs from orchestrator — never register entities
- Notes accumulate from first contact — capture important observations immediately, not deferred to deep research
- Create notes with `add_notes`; update via `set_note` for corrections; delete via `remove_notes` for stale notes
- Deep research agents complete all research before writing — read existing data with `get_entity`, apply reconciliation (`${CLAUDE_PLUGIN_ROOT}/references/reconcile-entity.md`), then advance stage with `set_stage`
- Agent final output must report notes written (e.g., "Wrote 14 notes to entity e7") — self-reported count is completion signal; emphasize in agent prompts
- Stage transitions always explicit via `set_stage` — other tool calls never change stage
- Reconcile-on-touch — any time entity is revisited, apply reconciliation procedure

### Agent Verification

- After agent completion, orchestrator checks `get_entity({entity_id: ID})` for expected stage
- If stage not advanced after completion, agent failed to write — re-spawn
- If task interrupted, re-spawn — agent reconciles from current note state

### Entity Integrity

- URL-grounded identity — surviving entities must have at least one URL; name-only entities are temporary placeholders during lead harvesting; resolve to URL or reject
- All deduplication is agent-administered — orchestrator proposes spawning resolve-duplicates agent (`${CLAUDE_PLUGIN_ROOT}/references/resolve-duplicates.md`) and waits for user confirmation; merges are hard to reverse
- Duplicate resolution belongs in deep research — agents with entity context loaded are best positioned to make dedup decisions; duplicate detection via `find_duplicates` is exclusively for use within the resolve-duplicates agent workflow, not standalone; do not suggest duplicate detection outside of deep research or post-research phases

### Research Methodology

- Prefer existing solutions over custom builds — if a well-adopted tool or pattern fulfills the purpose, recommend adoption or mirroring over building from scratch; well-exercised tools have resolved problems not yet encountered; high adoption is a strong signal of maturity and completeness
- Notes name tools, platforms, and external dependencies explicitly — analysis identifies cross-entity patterns from notes
- Skill infrastructure remains domain-agnostic — taxonomy, notes, measures, and sources are project-specific data produced by execution, not embedded in skill; prompt templates use placeholders filled from project context, never hardcoded domain-specific language
- Do not skip stages — each stage output feeds the next
- Browser tools operate on single active page — browser work runs sequentially unless parallel-capable MCP configured

### State Management

- `blueprint/data/state.md` is the single source of truth for stage-level state
- `blueprint/data/history.md` is the sequential stride log — entries: ISO 8601 datetime, stage, action, result stats, next step; describe activity type (context wave, directory traversal, research batch); do not include entity IDs
- Mark `[-]` when starting stage, `[x]` when stage complete
- Project outputs to `blueprint/` directory at project root, not `.claude/` paths
- User can re-invoke completed stage — ask before overwriting
- During execution, load only active stage reference file; pre-reading all for planning is acceptable
- Present proposed work before executing — user approves at every stage gate
- Blueprint stage produces `blueprint/10-blueprint.md` as its final deliverable

### Friction Log

- Agents append process friction observations to `blueprint/data/friction.md` — tool gaps, workflow bottlenecks, unexpected constraints encountered during research
- Friction observations are meta-process notes, never redirect or interrupt the current cycle
- Review friction log between cycles to inform process adjustments
