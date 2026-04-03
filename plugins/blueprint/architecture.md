# Research Database Architecture

MCP server providing deterministic operations for agent-facing instructions where supporting data is relational. Agents interact exclusively through domain tools — no generic CRUD, no query building, no raw SQL.

## Purpose

The research database supports the `/blueprint-research` skill across its cycle-based workflow: initialization, repeating expand/consolidate/present cycles, directions, and implementation blueprint. It stores entities (tools, projects, sources being studied), their notes (atomic facts), assessment criteria, coverage domains, goals, and analysis outputs. Every write operation enforces business rules (URL dedup, stage validation, criteria constraints) so agent instructions focus on research decisions, not data manipulation.

## Layers

```
Agent instructions (SKILL.md, phase references)
    ↓ MCP tool calls
MCP server (servers/research_db.py)
    ↓ function calls
Business logic modules (skills/research/_*.py)
    ↓ SQL
SQLite database (blueprint/data/research.db)
```

**Agent instructions** reference tools by name. They never construct SQL or manage database state directly.

**MCP server** is a thin routing layer. Each `@mcp.tool()` function validates input, calls the business logic function, and wraps the result. Error handling (CHECK constraint violations, missing entities) returns structured messages agents can act on.

**Business logic modules** contain all domain rules: URL normalization, dedup detection, stage transition validation, criteria assessment resolution. Each module owns one domain concept.

**SQLite database** enforces structural constraints (CHECK, UNIQUE, FK) as the last line of defense. WAL mode enables concurrent reads during writes. The `retry_write` decorator handles lock contention with random jitter.

## Schema

### Entity (core)

```
entities
├── id TEXT PK                    — prefixed: e1, e2, ...
├── name TEXT NOT NULL
├── stage TEXT NOT NULL            — CHECK: new, rejected, researched, merged
├── relevance INTEGER DEFAULT 0   — cached count of passed relevancy criteria
├── description TEXT               — one-sentence identity
├── purpose TEXT                   — why it matters to this research
└── last_modified TEXT
```

### Entity Properties (satellite tables)

```
entity_modes      (entity_id, mode)         — interaction modes: example, directory, context, unclassified
entity_urls       (entity_id, url)          — normalized URLs for dedup
entity_notes      (id, entity_id, note)     — atomic facts; primary knowledge store
entity_measures   (entity_id, measure, value) — analysis output key-value pairs
entity_source_data (entity_id, source_type, key, value) — structured metadata from external sources
url_provenance    (source_url, entity_id)   — discovery path tracking
```

### Assessment (criteria system)

```
criteria          (id, type, name, gate)    — definitions from assessment file
criteria_notes    (criterion_id, note_id, quality) — evidence links: pass or fail
```

### Coverage (domain/goal system)

```
domains           (id, name, description)   — research focus areas
goals             (id, name, description)   — project goals
goal_domains      (goal_id, domain_id)      — many-to-many: goals ↔ domains
domain_criteria   (domain_id, criterion_id) — many-to-many: domains ↔ criteria
```

Creates a queryable chain for coverage computation:
```
goals → goal_domains → domains → domain_criteria → criteria → criteria_notes → entity_notes → entities
```

Coverage at any level is a join query using DISTINCT entity counts to avoid inflation from many-to-many paths.

### Relationships

```
entities ←──── entity_modes        (entity_id FK)
entities ←──── entity_urls         (entity_id FK)
entities ←──── entity_notes        (entity_id FK)
entities ←──── entity_measures     (entity_id FK)
entities ←──── entity_source_data  (entity_id FK)
entities ←──── url_provenance      (entity_id FK)

criteria ←──── criteria_notes      (criterion_id FK, ON DELETE CASCADE)
entity_notes ←─ criteria_notes     (note_id FK, ON DELETE CASCADE)

domains ←──── domain_criteria      (domain_id FK, ON DELETE CASCADE)
criteria ←──── domain_criteria     (criterion_id FK, ON DELETE CASCADE)
goals ←──── goal_domains           (goal_id FK, ON DELETE CASCADE)
domains ←──── goal_domains         (domain_id FK, ON DELETE CASCADE)
```

All junction tables use ON DELETE CASCADE on both foreign keys. This ensures links never orphan when parent records are deleted.

### Constraints

| Table | Constraint | Purpose |
|-------|-----------|---------|
| `entities.stage` | CHECK IN (new, rejected, researched, merged) | Invalid stages rejected at SQL level |
| `entity_modes.mode` | CHECK IN (example, directory, context, unclassified) | Invalid modes rejected at SQL level |
| `criteria.type` | CHECK IN (hardline, relevancy) | Invalid types rejected at SQL level |
| `criteria_notes.quality` | CHECK IN (pass, fail) | Invalid quality rejected at SQL level |
| `entity_urls` | UNIQUE(entity_id, url) | No duplicate URLs per entity |
| `entity_notes` | UNIQUE(entity_id, note) | No duplicate note text per entity |

CHECK constraint violations return the constraint expression in the error message dynamically — no per-field hardcoding in the server.

## Tool Design

### Verb Convention

Four verbs for mutations, consistent across all entity properties:

| Verb | Meaning | Example |
|------|---------|---------|
| `set` | Replace value | `set_relevance(entity_id, relevance)` |
| `add` | Append to collection | `add_notes(entity_id, notes)` |
| `remove` | Remove specific items | `remove_notes(entity_id, note_ids)` |
| `clear` | Reset to null/empty | `clear_relevance(entity_id)` |

Registration creates entities: `register_entity(data)`, `register_entities(entities, source_url)`.

Queries use descriptive names: `get_entity`, `list_entities`, `get_assessment`, `get_dashboard`.

### Parameter Pattern

Every tool takes a JSON object. Entity ID is the anchor for mutations. Only pass what's changing — no required fields beyond the ID.

### ID Convention

Single-letter prefixes generated by `_next_id`: `e` (entity), `n` (note), `c` (criterion), `d` (domain), `g` (goal). IDs are stable, never reused, and identical in input and output.

## Assessment Model

### Criteria Definitions

Loaded from `blueprint/3-assessment-criteria.md` into the `criteria` table via `set_criteria()`. Two types:

- **Hardline**: entity fails any → rejected (stage=rejected, relevance=-1)
- **Relevancy**: each criterion met = 1 point; relevance = count of passed relevancy criteria

Each criterion has a `gate` — an explicit pass/fail description with concrete thresholds. No judgment calls.

### Evidence Linking

The `criteria_notes` junction links criteria to entity notes with quality (pass/fail):

- **pass**: this note provides evidence the criterion IS met
- **fail**: this note provides evidence the criterion is NOT met
- **No link**: insufficient evidence (implicit — absence, not stored)

Entity relationship is implicit: `criteria_notes.note_id` → `entity_notes.entity_id` → `entities`.

### Resolution Logic

For a given criterion-entity pair:
1. Collect all `criteria_notes` rows where `note_id` belongs to the entity
2. If any link has quality "pass" → criterion passed (pass supersedes fail)
3. If all links have quality "fail" → criterion failed
4. If no links exist → not assessed

### Surgical Updates

When a criterion definition changes:
1. `clear_criterion_links(criterion_id)` removes only that criterion's links
2. All other criteria retain their links and assessments
3. Only the changed criterion needs re-evaluation

When a note is deleted (including during stage downgrade):
- ON DELETE CASCADE removes all criteria_notes rows for that note
- Assessment results update automatically on next `compute_relevance` call

### Cached Relevance

`entities.relevance` is a cached value for efficient sorting in `list_entities`. The source of truth is the criteria_notes junction. `compute_relevance(entity_id)` recomputes and caches from the links.

## Modes

Interaction modes determine what kind of agent work an entity receives. Stored in the `entity_modes` satellite table — an entity may have multiple modes.

| Mode | Agent work | Cycle phase |
|------|-----------|-------------|
| `example` | Deep research as comparable tool | Consolidate |
| `directory` | Directory crawl for entity listings | Consolidate |
| `context` | Context research for domain knowledge | Expand |
| `unclassified` | Marker — needs assessment pass | Resolved by assess-entity |

Default mode for new entities is `unclassified`, requiring classification via the assess-entity agent before receiving phase-appropriate work. If an entity has two modes, it needs two different kinds of agent work in different cycle phases.

## Stage Transitions

```
new → rejected     (fails hardline criteria)
new → researched   (deep research complete)
new → merged       (duplicate merge target)
merged → new       (post-reconciliation; only valid transition from merged)
```

Downgrading from `researched` to a lower stage deletes all notes and measures for that entity (and cascades to criteria_notes via ON DELETE CASCADE).

Merge preserves the highest relevance from all merging entities and retains measures on the survivor. The `merged` stage serves as a crash-recovery marker — the resolve-duplicates workflow transitions `merged → new` after reconciliation.

## Business Logic Modules

| Module | Domain | Key functions |
|--------|--------|--------------|
| `_db.py` | Schema, connection, utilities | `init_db`, `normalize_url`, `_next_id`, `_enforce_stage`, `retry_write` |
| `_entities.py` | Entity lifecycle | `register_entity`, `update_entity`, `get_entity`, `list_entities`, `register_batch` |
| `_notes.py` | Knowledge accumulation | `upsert_notes`, `update_note`, `remove_notes`, `clear_notes` |
| `_criteria.py` | Assessment definitions and links | `register_criteria`, `link_criterion_note`, `get_assessment`, `compute_relevance` |
| `_measures.py` | Analysis output | `upsert_measures`, `clear_measures` |
| `_merge.py` | Duplicate resolution | `find_duplicates`, `merge_entities` |
| `_provenance.py` | Discovery path tracking | `upsert_provenance`, `upsert_url` |
| `_source_data.py` | Structured external metadata | `upsert_source_data`, `list_source_data` |
| `_coverage.py` | Domain/goal management and coverage computation | `register_domains`, `get_coverage`, `link_domain_criterion` |
| `_effectiveness.py` | Criteria effectiveness metrics | `get_criteria_effectiveness` |
| `_search.py` | Note search and export | `search_notes`, `export_db` |
| `_templates.py` | Source type definitions | Template DB for structured data collection |
| `_init.py` | Plugin lifecycle | `init`, `status` |
| `__init__.py` | Public facade | Re-exports all modules |

## Concurrency

WAL mode enables concurrent reads. Write operations use the `@retry_write` decorator — catches "database is locked" errors and retries with random 50-200ms jitter. Multiple agents can read simultaneously; writes queue.

## Transport

MCP server runs via stdio transport, launched by the `.mcp.json` configuration:

```json
{
  "command": "${CLAUDE_PLUGIN_DATA}/venv/bin/python3",
  "args": ["${CLAUDE_PLUGIN_ROOT}/servers/research_db.py"],
  "env": { "DB_PATH": "blueprint/data/research.db" }
}
```

Python dependencies installed into a persistent venv at `${CLAUDE_PLUGIN_DATA}/venv/` by a `SessionStart` hook that diffs `requirements.txt` against a cached copy.
