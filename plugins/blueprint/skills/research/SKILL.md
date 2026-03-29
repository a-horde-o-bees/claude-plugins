---
name: blueprint-research
description: |
  Structured competitive research and implementation planning. Studies comparable examples through four phases: scoping, deep research, analysis, and implementation blueprint. Uses emergent schema with unified entity model and SQLite database.
argument-hint: "[scope description]"
---

# /blueprint-research

Structured competitive research and implementation planning. Bootstraps new projects by studying comparable examples: defines scope with integrated entity assessment, deep researches highest-relevance entities with atomic notes in SQLite, synthesizes cross-entity patterns, and produces actionable implementation blueprint.

Reads `docs/blueprint.md` to detect current state. If absent, initializes from template and starts Phase 1. Otherwise, finds next incomplete phase and proposes working on it.

## File Map

### Dependencies

```
${CLAUDE_PLUGIN_ROOT}/references/phase-1-scoping.md
${CLAUDE_PLUGIN_ROOT}/references/phase-2-research.md
${CLAUDE_PLUGIN_ROOT}/references/phase-3-analysis.md
${CLAUDE_PLUGIN_ROOT}/references/phase-4-implementation.md
${CLAUDE_PLUGIN_ROOT}/references/reconcile-entity.md
${CLAUDE_PLUGIN_ROOT}/references/resolve-duplicates.md
${CLAUDE_PLUGIN_ROOT}/references/reassess-relevance.md
${CLAUDE_PLUGIN_ROOT}/references/directory-traversal.md
${CLAUDE_PLUGIN_ROOT}/references/source-templates.db
${CLAUDE_PLUGIN_ROOT}/run.py skills.research
${CLAUDE_PLUGIN_ROOT}/templates/blueprint.md
```

### Created

```
docs/blueprint.md
docs/overview.md
docs/1-scope.md
docs/2-assessment-criteria.md
docs/3-goals.md
docs/4-effectiveness-criteria.md
docs/5-constraints.md
docs/6-domain-knowledge.md
docs/history.md
docs/implementation-progress.md
docs/progress.db
references/research.db
references/analysis-findings.md
references/analysis-interpretation.md
references/crawl-scripts/
```

## Process Model

### Phase Structure

| Phase | Name | Type | Reference | Key Output |
|-------|------|------|-----------|------------|
| 1 | Scoping | Design | `references/phase-1-scoping.md` | Project definition files, database initialized, entities with relevance |
| 2 | Deep Research | Execution | `references/phase-2-research.md` | Research DB populated with notes, relationships, capabilities |
| 3 | Analysis | Execution | `references/phase-3-analysis.md` | `references/analysis-findings.md`, `references/analysis-interpretation.md`, measures |
| 4 | Implementation Blueprint | Design | `references/phase-4-implementation.md` | `docs/implementation-progress.md`, `docs/progress.db` |

Design phases (1, 4) include refinement loops — user iterates until satisfied. Execution phases (2, 3) run sequential agent work with checkpointing. All reference file paths relative to `${CLAUDE_PLUGIN_ROOT}`.

### Definition File Usage

Which project definition files agents read at each phase:

| File | P1 | P2 | P3 | P4 |
|------|----|----|----|----|
| `docs/1-scope.md` | R | R | — | — |
| `docs/2-assessment-criteria.md` | R | R | — | — |
| `docs/3-goals.md` | — | — | R | R |
| `docs/4-effectiveness-criteria.md` | — | R | R | — |
| `docs/5-constraints.md` | — | — | — | R |
| `docs/6-domain-knowledge.md` | R | R | R | R |

Files 1-5 populated during Phase 1 scope approval. File 6 updated after context research waves and when deep research reveals new platforms, tools, or business models.

Domain knowledge guard: `6-domain-knowledge.md` documents what exists (platforms, tools, patterns) and what to look for. Must not contain frequency analysis, adoption rates, or absence observations — those belong in Phase 3 output.

## Trigger

User runs `/blueprint-research`. Optional `$ARGUMENTS` passed as initial scope input for Phase 1.

## Route

1. If `docs/blueprint.md` does not exist:
    1. Verify project root is empty or near-empty — only standard init files at top level (`.claude/`, `.gitmodules`, `CLAUDE.md`, `.claudeignore`, `.gitattributes`, `.env.example`, `.gitignore`)
    2. If other files or directories exist:
        1. Exit to user — report what was found; skill bootstraps new projects and should not run in populated projects
    3. Create `docs/` directory and copy `${CLAUDE_PLUGIN_ROOT}/templates/blueprint.md` to `docs/blueprint.md`
    4. Mark Phase 1 as `[-]`; use `$ARGUMENTS` as initial scope input if provided
    5. Go to step 3. Determine active phase
2. Read `docs/blueprint.md`
3. Determine active phase:
    1. If `docs/history.md` exists: read last 5 lines for current stride and next steps
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
    - `references/analysis-findings.md`
    - `references/analysis-interpretation.md`
    - `docs/implementation-progress.md` (if exists)
2. Run `research_cli clear measures`
3. Update `docs/blueprint.md`: Phase 1 `[-]`, Phases 2-4 `[ ]`
4. Read Phase 1 reference file — re-entry detects existing domain knowledge and entities

Database preserved. New entities accumulate during scoping; Phase 2 processes only entities not yet at `researched` stage.

## Workflow

1. Mark {active-phase} status `[-]` in `docs/blueprint.md`
2. Read `${CLAUDE_PLUGIN_ROOT}/references/phase-{active-phase}-{name}.md`
3. Present what current phase will do to user
4. Execute phase per reference file instructions:
    1. Spawn autonomous agents for research/analysis — one per discrete research unit
    2. Present findings to user
    3. If design phase: user approves or refines (loop until satisfied)
    4. Write outputs
5. Append history entry to `docs/history.md` — one line: ISO 8601 datetime, phase, action, result stats, next step
6. Mark {active-phase} status `[x]` in `docs/blueprint.md`
7. Propose next phase

Interactive checkpoints in main conversation between agent calls. Sub-agents run autonomously — user-facing decisions at orchestration level only.

### Report

After each phase: summary of outputs produced, entities affected, and recommended next phase.

## Project Infrastructure

State detection creates `docs/blueprint.md` on first run. Phase 1 creates remaining structure:

```
docs/
  blueprint.md              — master plan (from template)
  history.md                — completed strides; read last lines for current position
  overview.md               — index pointing to numbered definition files
  1-scope.md                — parent concept, in-scope and excluded
  2-assessment-criteria.md  — scoring rubric (hardline filters, gradient criteria, relevance guide)
  3-goals.md                — project goals and priority order
  4-effectiveness-criteria.md — criteria for evaluating patterns
  5-constraints.md          — implementation realities
  6-domain-knowledge.md     — landscape structure and distilled findings
references/
  research.db               — SQLite research database
```

Status markers in `docs/blueprint.md`: `[ ]` pending, `[-]` in progress, `[x]` complete.

## Database

SQLite database at `references/research.db`.

### CLI

```
python3 ${CLAUDE_PLUGIN_ROOT}/run.py skills.research <command> [--db PATH]
```

Default `--db`: `references/research.db`. All commands accept `--db` override.

#### Read Commands

| Command | Description |
|---------|-------------|
| `get entity <id>` | Entity detail with URLs, provenance, relevance, description, measures, notes |
| `get entities [--role R] [--stage S] [--modified-before T]` | All entities sorted by relevance, optionally filtered |
| `get provenance [--entity-id ID]` | Per-entity source URLs or all sources ranked by entity count |
| `get reach [--min N]` | Entities ranked by provenance source count |
| `get stats` | Summary: stage distribution, relevance, provenance counts |
| `get measures` | Measure distributions across entities |
| `get source-data [--source-type T] [--key K] [--entity-id ID]` | Structured source data |
| `search notes --pattern P [--stage S] [--min-relevance N]` | Search notes by keyword across entities |
| `export [--format json\|csv]` | Full database export |
| `normalize-url <url>` | Compute normalized URL for dedup |

#### Write Commands

| Command | Description |
|---------|-------------|
| `init` | Create database with schema |
| `register --name N [--url U] [--source-url U] [--relevance N] [--description D] [--role R]` | Register entity with URL dedup; returns prefixed ID (e.g., `e1`) |
| `register-batch --json '[...]' [--source-url U]` | Register multiple entities from JSON array; notes only for new entities; already-registered listed for reconciliation |
| `update entities (--ids I\|--all) [--stage S] [--relevance N] [--description D] [--name N] [--role R]` | Update entity properties |
| `upsert notes --entity-id ID --notes "fact1" "fact2"` | Add notes (skips duplicates, returns note IDs) |
| `upsert provenance --entity-id ID --source-url U` | Record provenance |
| `upsert url --entity-id ID --url U` | Add URL to existing entity |
| `upsert measures --entity-id ID --measures "key=value" ...` | Add or update measures |
| `upsert source-data --entity-id ID --source-type T --data "k=v" ...` | Upsert structured source data |
| `update note --note-id ID --note "text"` | Replace single note by ID |
| `remove notes --entity-id ID --note-ids n1,n2` | Remove specific notes by ID |
| `touch entities (--ids I\|--all)` | Update modified timestamp |
| `clear measures` | Clear all measures (for re-analysis) |
| `find-duplicates [--templates-db PATH]` | Detect duplicates by URL overlap and source-data matches |
| `merge entities --ids I1,I2,...` | Merge into lowest-ID survivor; appends descriptions; sets stage `merged` |

#### Template Commands

Source templates define structured data schemas for external sources. Templates DB ships at `${CLAUDE_PLUGIN_ROOT}/references/source-templates.db`.

| Command | Description |
|---------|-------------|
| `get template --source-type T [--templates-db PATH]` | Full template for source type |
| `get templates [--templates-db PATH]` | List all source types |
| `match template --url U [--templates-db PATH]` | Match URL against source type patterns |
| `upsert template-key --source-type T --key K [--format F] [--description D] [--templates-db PATH]` | Add or update key definition |
| `update template --type T [--url-pattern P] [--dedup-key K] [--notes N] [--templates-db PATH]` | Update source type metadata |
| `autofill source-data [--source-type T] [--entity-id ID] [--dry-run] --db PATH --templates-db PATH` | Autofill structured data from entity URLs |

### ID Convention

Single-letter prefixes: `e` (entity), `n` (note). IDs are stored, displayed, and accepted identically — `e7` in output is `e7` in input.

### Data Model

Unified entity model — everything is an entity (organizations, platforms, programs). Core fields:

- `id` — prefixed TEXT (e.g., `e7`), stable, never changes
- `name` — display name
- `role` — `example` (comparable sites to study), `directory` (crawlable listings yielding examples), `context` (knowledge/advice sources)
- `stage` — `new` → `rejected` | `researched` | `merged`
- `relevance` — integer or NULL; higher = more relevant; scale from `docs/2-assessment-criteria.md`; NULL = not yet assessed
- `description` — one-sentence identity statement; notes hold specifics, description never lists features or counts

**Notes**: atomic, self-explanatory facts. Primary knowledge store. Begin accumulating from first contact — not deferred to deep research. Deep research produces comprehensive notes; discovery produces initial notes from whatever information is consumed.

**Measures**: universal key/value pairs produced by analysis (Phase 3). Not produced during research. Re-running analysis clears and regenerates all measures.

**URLs**: separate `entity_urls` table; multiple normalized URLs per entity. URL normalization strips scheme, www, trailing slash, lowercases, keeps path. Dedup during registration checks normalized URLs.

**Provenance**: `url_provenance` table links source URL → entity ID. Many-to-many: same entity found via multiple sources.

**Source data**: `entity_source_data` table stores structured key/value pairs per source type. Keys defined by source templates.

### Tagged Notes

`[TAG]:` prefix convention for machine-parseable markers:

| Tag | Used On | Purpose |
|-----|---------|---------|
| `[ACCESSIBILITY]:` | Directory entities | Content access: `static`, `js-rendered`, `auth-gated`, `api-available` |
| `[CRAWL METHOD]:` | Directory entities | Technical extraction approach |
| `[CRAWL SCRIPT]:` | Directory entities | Path to script in `references/crawl-scripts/` |
| `[CRAWL PROGRESS]:` | Directory entities | Mutable crawl position and resumption point |

New tags may emerge per project. Convention: bracketed uppercase, descriptive, unique per entity (replace, not duplicate).

### Concurrency

WAL mode for concurrent reads. Write operations use retry with random 50-200ms jitter, retrying indefinitely on lock. Agents write simultaneously — reads never block, writes queue.

### Ad-Hoc Queries

CLI covers most queries. Before writing raw SQL, check if CLI handles need. When raw queries are necessary (main conversation only, never agents):

```python
python3 -c "
import sqlite3
conn = sqlite3.connect('references/research.db')
conn.row_factory = sqlite3.Row
rows = conn.execute('SELECT ...').fetchall()
for r in rows: print(r)
conn.close()
"
```

Key tables: `entities`, `entity_urls`, `url_provenance`, `entity_notes`, `entity_measures`, `entity_source_data`. No `sqlite3` binary — use `python3 -c`.

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
- Sub-agents inherit parent tools and permissions from settings.json

### Agent Database Access

- Agents access database exclusively through CLI — no raw SQL, no sqlite3 imports, no `python3 -c` commands
- Agents push notes directly to database via CLI — no intermediate JSON files for knowledge storage; files only for artifacts (templates, PDFs, source documents)
- Agent Bash commands: single-line, starting with recognized program name; no comments, line continuations, shell loops, or variable assignments before command
- Agent database errors: report in output text, do not diagnose or fix schema issues

### Agent Write Discipline

- Scoping agents register entities with `register` during landscape exploration, then capture observations with `upsert notes`; entities failing hardline criteria: register with relevance 0, update to stage `rejected`
- Deep research agents receive entity IDs from orchestrator — never create entities
- Notes accumulate from first contact — capture important observations immediately, not deferred to deep research
- Append (`upsert notes`) for new observations; correct (`update note` or `remove notes` + `upsert notes`) for wrong or outdated notes
- Deep research agents complete all research before writing — read existing notes, apply reconciliation (`${CLAUDE_PLUGIN_ROOT}/references/reconcile-entity.md`), then advance stage with `update entities --stage researched`
- Agent final output must report notes written (e.g., "Wrote 14 notes to entity e7") — self-reported count is completion signal; emphasize in agent prompts
- Stage transitions always explicit via `update entities --stage` — data commands never change stage
- Reconcile-on-touch — any time entity is revisited, apply reconciliation procedure

### Agent Verification

- After agent completion, orchestrator checks `get entity <id>` for expected stage
- If stage not advanced after completion, agent failed to write — re-spawn
- If task interrupted, re-spawn — agent reconciles from current note state

### Entity Integrity

- URL-grounded identity — surviving entities must have at least one URL; name-only entities are temporary placeholders during lead harvesting; resolve to URL or reject
- All deduplication is agent-administered — orchestrator proposes spawning resolve-duplicates agent (`${CLAUDE_PLUGIN_ROOT}/references/resolve-duplicates.md`) and waits for user confirmation; merges are hard to reverse

### Research Methodology

- Notes name tools, platforms, and external dependencies explicitly — analysis identifies cross-entity patterns from notes
- Skill infrastructure remains domain-agnostic — taxonomy, notes, measures, and sources are project-specific data produced by execution, not embedded in skill; prompt templates use placeholders filled from project context, never hardcoded domain-specific language
- Do not skip phases — each phase output feeds the next
- Browser tools operate on single active page — browser work runs sequentially unless parallel-capable MCP configured

### State Management

- `docs/blueprint.md` is the single source of truth for phase-level state
- `docs/history.md` is the sequential stride log — entries: ISO 8601 datetime, phase, action, result stats, next step; describe activity type (context wave, directory traversal, research batch); do not include entity IDs
- Mark `[-]` when starting phase, `[x]` when phase gate passed
- Project outputs to project paths (`docs/`, `references/`), not `.claude/` paths
- User can re-invoke completed phase — ask before overwriting
- During execution, load only active phase reference file; pre-reading all for planning is acceptable
- Present proposed work before executing — user approves at every phase gate
- Phase 4 hands off to `/progress` skill after user approves implementation plan
