---
name: blueprint-research
description: |
  Structured solution research and implementation planning. Studies existing tools, proven approaches, and established patterns through four phases: scoping, deep research, analysis, and implementation blueprint. Uses emergent schema with unified entity model and SQLite database.
argument-hint: "[scope description]"
---

# /blueprint-research

Structured solution research and implementation planning. Studies existing tools, proven approaches, and established patterns to fulfill a defined purpose: defines scope with integrated entity assessment, deep researches highest-relevance entities with atomic notes in SQLite, synthesizes cross-entity patterns, and produces actionable implementation blueprint.

Reads `blueprint/data/state.md` to detect current state. If absent, initializes from template and starts Phase 1. Otherwise, finds next incomplete phase and proposes working on it.

## Process Model

### Phase Structure

| Phase | Name | Type | Reference | Key Output |
|-------|------|------|-----------|------------|
| 1 | Scoping | Design | `references/phase-1-scoping.md` | Project definition files, database initialized, entities with relevance |
| 2 | Deep Research | Execution | `references/phase-2-research.md` | Research DB populated with notes, relationships, capabilities |
| 3 | Analysis | Execution | `references/phase-3-analysis.md` | `blueprint/7-findings.md`, `blueprint/8-interpretation.md`, measures |
| 4 | Implementation Blueprint | Design | `references/phase-4-implementation.md` | `blueprint/9-blueprint.md` |

Design phases (1, 4) include refinement loops — user iterates until satisfied. Execution phases (2, 3) run sequential agent work with checkpointing. All reference file paths relative to `${CLAUDE_PLUGIN_ROOT}`.

### Definition File Usage

Which project definition files agents read at each phase:

| File | P1 | P2 | P3 | P4 |
|------|----|----|----|----|
| `blueprint/1-scope.md` | R | R | — | — |
| `blueprint/2-assessment-criteria.md` | R | R | — | — |
| `blueprint/3-goals.md` | — | — | R | R |
| `blueprint/4-effectiveness-criteria.md` | — | R | R | — |
| `blueprint/5-constraints.md` | — | — | — | R |
| `blueprint/6-domain-knowledge.md` | R | R | R | R |

Files 1-5 populated during Phase 1 scope approval. File 6 updated after context research waves and when deep research reveals new platforms, tools, or business models.

Domain knowledge guard: `6-domain-knowledge.md` documents what exists (platforms, tools, patterns) and what to look for. Must not contain frequency analysis, adoption rates, or absence observations — those belong in Phase 3 output.

## Trigger

User runs `/blueprint-research`. Optional `$ARGUMENTS` passed as initial scope input for Phase 1.

## Route

1. If `blueprint/data/state.md` does not exist:
    1. If `blueprint/` directory exists:
        1. Exit to user — report existing blueprint folder; skill initializes this directory and cannot run over existing content
    2. Create `blueprint/data/` directory and copy `${CLAUDE_PLUGIN_ROOT}/templates/blueprint.md` to `blueprint/data/state.md`
    3. Mark Phase 1 as `[-]`; use `$ARGUMENTS` as initial scope input if provided
    4. Go to step 3. Determine active phase
2. Read `blueprint/data/state.md`
3. Determine active phase:
    1. If `blueprint/data/history.md` exists: read last 5 lines for current stride and next steps
    2. Find first phase with status `[-]` or `[ ]`
        1. If `[-]` found: propose resuming; history log indicates last stride; for execution phases check database for completed work; for design phases check for phase output files
        2. Else if `[ ]` found: propose starting that phase
        3. Else if all `[x]`: report complete; offer re-invocation of any phase — ask before overwriting existing outputs
4. User confirms phase, chooses different phase, or requests reversion
    1. If reversion requested: dispatch Phase Reversion
5. {active-phase} = confirmed phase number
6. Dispatch Workflow

### Phase Reversion

When user requests "add more entities" at any phase gate:

1. Delete downstream outputs:
    - `blueprint/7-findings.md`
    - `blueprint/8-interpretation.md`
    - `blueprint/9-blueprint.md` (if exists)
2. Clear measures: `delete_records({table: "entity_measures", all: true})`
3. Update `blueprint/data/state.md`: Phase 1 `[-]`, Phases 2-4 `[ ]`
4. Read Phase 1 reference file — re-entry detects existing domain knowledge and entities

Database preserved. New entities accumulate during scoping; Phase 2 processes only entities not yet at `researched` stage.

## Workflow

1. Mark {active-phase} status `[-]` in `blueprint/data/state.md`
2. Read `${CLAUDE_PLUGIN_ROOT}/references/phase-{active-phase}-{name}.md`
3. Present what current phase will do to user
4. Execute phase per reference file instructions:
    1. Spawn autonomous agents for research/analysis — one per discrete research unit
    2. Present findings to user
    3. If design phase: user approves or refines (loop until satisfied)
    4. Write outputs
5. Append history entry to `blueprint/data/history.md` — one line: ISO 8601 datetime, phase, action, result stats, next step
6. Mark {active-phase} status `[x]` in `blueprint/data/state.md`
7. Propose next phase

Interactive checkpoints in main conversation between agent calls. Subagents run autonomously — user-facing decisions at orchestration level only.

### Report

After each phase: summary of outputs produced, entities affected, and recommended next phase.

## Project Infrastructure

State detection creates `blueprint/data/state.md` on first run. Phase 1 creates remaining structure:

```
blueprint/
  data/
    state.md                — master plan (from template)
    history.md              — completed strides; read last lines for current position
    research.db             — SQLite research database
  overview.md               — index pointing to numbered definition files
  1-scope.md                — parent concept, in-scope and excluded
  2-assessment-criteria.md  — scoring rubric (hardline filters, gradient criteria, relevance guide)
  3-goals.md                — project goals and priority order
  4-effectiveness-criteria.md — criteria for evaluating patterns
  5-constraints.md          — implementation realities
  6-domain-knowledge.md     — landscape structure and distilled findings
  scripts/                  — crawl scripts for directory traversal
```

Status markers in `blueprint/data/state.md`: `[ ]` pending, `[-]` in progress, `[x]` complete.

## Database

SQLite database at `blueprint/data/research.db`.

### MCP Tools

The `blueprint-research` MCP server exposes 7 tools. The server starts automatically when the plugin is installed. Database path configured via `DB_PATH` environment variable (default: `blueprint/data/research.db`).

#### CRUD Tools

| Tool | Parameters | Description |
|------|-----------|-------------|
| `create_records` | `table`, `data` (object or array), `source_url?` | Insert one or many rows; entities table: URL normalization, dedup, provenance; other tables: straight insert |
| `read_records` | `table`, `conditions?`, `include?`, `limit?` | Select with Django `__operator` conditions and FK-resolved joins |
| `update_records` | `table`, `id`, `data` | Update fields by ID; entities table: validates stage transitions |
| `delete_records` | `table`, `id?`, `all?` | Delete by ID or clear all (requires explicit `all: true`) |

#### Query and Schema Tools

| Tool | Parameters | Description |
|------|-----------|-------------|
| `query` | `sql`, `params?` | Read-only SQL (SELECT only enforced); for complex joins, aggregations, subqueries |
| `describe_entities` | `table?` | Schema discovery — tables, columns, types, FK relationships |
| `merge_entities` | `ids` (array) | Merge entities into lowest-ID survivor; preserves all related data |
| `init_database` | (none) | Initialize database schema; idempotent |

#### Conditions Syntax

`read_records` conditions use Django `__operator` suffix convention:

| Condition | Operator |
|-----------|----------|
| `{field: value}` | `=` (equality) |
| `{field__gte: N}` | `>=` |
| `{field__gt: N}` | `>` |
| `{field__lte: N}` | `<=` |
| `{field__lt: N}` | `<` |
| `{field__ne: value}` | `!=` |
| `{field__like: pattern}` | `LIKE` |
| `{field__null: true}` | `IS NULL` |
| `{field__null: false}` | `IS NOT NULL` |

Multiple conditions combine with AND logic.

#### Star-Schema Joins

`read_records` `include` parameter resolves FK joins:

```json
read_records({table: "entities", conditions: {id: "e1"}, include: ["entity_notes", "entity_measures"]})
```

Returns entity with nested related data. Error if no FK relationship exists between tables.

#### Examples

```json
// Create entity with URL dedup and provenance
create_records({table: "entities", data: {name: "Semgrep", url: "https://github.com/semgrep/semgrep", source_url: "https://directory.com", role: "context", relevance: 8}})

// Batch create notes
create_records({table: "entity_notes", data: [{entity_id: "e1", note: "First observation"}, {entity_id: "e1", note: "Second observation"}]})

// Read with conditions
read_records({table: "entities", conditions: {stage: "researched", relevance__gte: 7}})

// Read entity with all related data
read_records({table: "entities", conditions: {id: "e1"}, include: ["entity_notes", "entity_measures", "entity_urls"]})

// Update entity
update_records({table: "entities", id: "e1", data: {stage: "researched", relevance: 9}})

// Delete note
delete_records({table: "entity_notes", id: "n14"})

// Clear all measures
delete_records({table: "entity_measures", all: true})

// Complex query
query({sql: "SELECT e.name, COUNT(n.id) as note_count FROM entities e LEFT JOIN entity_notes n ON n.entity_id = e.id GROUP BY e.id", params: {stage: "researched"}})
```

### ID Convention

Single-letter prefixes: `e` (entity), `n` (note). IDs are stored, displayed, and accepted identically — `e7` in output is `e7` in input.

### Data Model

Unified entity model — everything is an entity (organizations, platforms, programs). Core fields:

- `id` — prefixed TEXT (e.g., `e7`), stable, never changes
- `name` — display name
- `role` — `example` (comparable sites to study), `directory` (crawlable listings yielding examples), `context` (knowledge/advice sources)
- `stage` — `new` → `rejected` | `researched` | `merged`
- `relevance` — integer or NULL; higher = more relevant; scale from `blueprint/2-assessment-criteria.md`; NULL = not yet assessed
- `description` — one-sentence identity statement; notes hold specifics, description never lists features or counts

**Notes**: atomic, self-explanatory facts. Primary knowledge store. Begin accumulating from first contact — not deferred to deep research. Deep research produces comprehensive notes; discovery produces initial notes from whatever information is consumed.

**Measures**: universal key/value pairs produced by analysis (Phase 3). Not produced during research. Measures are cleared at the point of change — when assessment criteria or effectiveness criteria are modified, the modifying workflow step clears measures immediately. Adding new entities does not invalidate existing measures.

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

Use `read_records` with conditions and include for most reads. For complex joins, aggregations, or subqueries that `read_records` cannot express, use the `query` tool with read-only SQL. The `query` tool enforces SELECT-only — write operations are rejected.

Key tables: `entities`, `entity_urls`, `url_provenance`, `entity_notes`, `entity_measures`, `entity_source_data`.

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

- Agents access database exclusively through MCP tools (`create_records`, `read_records`, `update_records`, `delete_records`, `query`, `describe_entities`, `merge_entities`)
- Agents push notes directly to database via `create_records` — no intermediate JSON files for knowledge storage; files only for artifacts (templates, PDFs, source documents)
- Agent database errors: report in output text, do not diagnose or fix schema issues

### Agent Write Discipline

- Scoping agents create entities with `create_records` during landscape exploration, then capture observations with `create_records` on `entity_notes`; entities failing hardline criteria: create with relevance 0, update stage to `rejected`
- Deep research agents receive entity IDs from orchestrator — never create entities
- Notes accumulate from first contact — capture important observations immediately, not deferred to deep research
- Create notes for new observations; update via `update_records` for corrections; delete via `delete_records` for stale notes
- Deep research agents complete all research before writing — read existing notes with `read_records` including `entity_notes`, apply reconciliation (`${CLAUDE_PLUGIN_ROOT}/references/reconcile-entity.md`), then advance stage with `update_records`
- Agent final output must report notes written (e.g., "Wrote 14 notes to entity e7") — self-reported count is completion signal; emphasize in agent prompts
- Stage transitions always explicit via `update_records` on entities — other tool calls never change stage
- Reconcile-on-touch — any time entity is revisited, apply reconciliation procedure

### Agent Verification

- After agent completion, orchestrator checks `read_records({table: "entities", conditions: {id: ID}})` for expected stage
- If stage not advanced after completion, agent failed to write — re-spawn
- If task interrupted, re-spawn — agent reconciles from current note state

### Entity Integrity

- URL-grounded identity — surviving entities must have at least one URL; name-only entities are temporary placeholders during lead harvesting; resolve to URL or reject
- All deduplication is agent-administered — orchestrator proposes spawning resolve-duplicates agent (`${CLAUDE_PLUGIN_ROOT}/references/resolve-duplicates.md`) and waits for user confirmation; merges are hard to reverse
- Duplicate resolution belongs in deep research — agents with entity context loaded are best positioned to make dedup decisions; duplicate detection via `query` tool is exclusively for use within the resolve-duplicates agent workflow, not standalone; do not suggest duplicate detection outside of deep research or post-research phases

### Research Methodology

- Prefer existing solutions over custom builds — if a well-adopted tool or pattern fulfills the purpose, recommend adoption or mirroring over building from scratch; well-exercised tools have resolved problems not yet encountered; high adoption is a strong signal of maturity and completeness
- Notes name tools, platforms, and external dependencies explicitly — analysis identifies cross-entity patterns from notes
- Skill infrastructure remains domain-agnostic — taxonomy, notes, measures, and sources are project-specific data produced by execution, not embedded in skill; prompt templates use placeholders filled from project context, never hardcoded domain-specific language
- Do not skip phases — each phase output feeds the next
- Browser tools operate on single active page — browser work runs sequentially unless parallel-capable MCP configured

### State Management

- `blueprint/data/state.md` is the single source of truth for phase-level state
- `blueprint/data/history.md` is the sequential stride log — entries: ISO 8601 datetime, phase, action, result stats, next step; describe activity type (context wave, directory traversal, research batch); do not include entity IDs
- Mark `[-]` when starting phase, `[x]` when phase gate passed
- Project outputs to `blueprint/` directory at project root, not `.claude/` paths
- User can re-invoke completed phase — ask before overwriting
- During execution, load only active phase reference file; pre-reading all for planning is acceptable
- Present proposed work before executing — user approves at every phase gate
- Phase 4 produces `blueprint/9-blueprint.md` as its final deliverable
