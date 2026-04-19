# Assess Entity

Agent subprocess — classifies modes and evaluates criteria for entities in a single pass. Replaces separate mode classification and relevance reassessment with one unified operation per entity.

Uses context-aware iteration pattern: processes entities until approaching context budget, reports resumption checkpoint. Orchestrator spawns next agent to continue from checkpoint.

## Input

Orchestrator provides:
- Research database (accessed via MCP tool calls)
- `blueprint/1-scope.md` for scope context
- `blueprint/3-assessment-criteria.md` for assessment reference
- Entity scope: all entities with `unclassified` mode (default), or specific entity IDs, or all researched entities (for reassessment after criteria change)

## Agent Workflow

### Load Context

1. Read `blueprint/1-scope.md` and `blueprint/3-assessment-criteria.md`
2. Load criteria definitions: `get_criteria()`
3. Get entity queue:
    - Default: `get_unclassified()` — entities with unclassified marker
    - Reassessment: `list_entities({stage: "researched"})` — all researched entities
    - Specific: orchestrator provides entity IDs

### Assess Each Entity

4. For each {entity} in {queue}:
    1. Check context budget — if approaching limit AND at least one entity processed:
        1. Return to caller:
            - Completed entity IDs and changes
            - Next entity ID as resumption checkpoint
            - "incomplete" status
    2. Read entity: `get_entity({entity_id: "{entity_id}"})`
    3. **Classify modes** — evaluate notes, description, and URLs:
        - Is it a tool, project, or system comparable to the research target? → `example`
        - Does it list or aggregate other entities? → `directory`
        - Is it a knowledge source, guide, dataset, or advice resource? → `context`
        - Multiple modes may apply — assign all that fit
        - If existing information is insufficient: fetch primary URL (one web request)
        - Set modes: `set_modes({entity_id: "{entity_id}", modes: ["example", "directory"]})`
        - Do not include `unclassified` — its removal signals classification is complete
    4. **Evaluate criteria** — for each criterion from `get_criteria()`:
        1. Find notes that provide evidence for or against this criterion
        2. For each relevant note, link with quality:
            `link_criterion_note({criterion_id: "{cid}", note_id: "{nid}", quality: "pass"})`
        3. If no notes address the criterion: skip (absence = not assessed)
    5. **Compute relevance**: `compute_relevance({entity_id: "{entity_id}"})`
    6. **Check hardline criteria** — if any hardline criterion has only "fail" links:
        `reject_entity({entity_id: "{entity_id}", reason: "Fails hardline: {criterion_name}"})`

### Report

5. For each entity processed:
    - Entity ID and name
    - Previous modes → new modes
    - Criteria linked: count of pass, fail, not assessed
    - Relevance: old → new
    - If rejected: reason
6. Summary: total processed, mode changes, relevance changes, rejections
7. If incomplete: next entity ID for resumption

## When to Invoke

Orchestrator proposes spawning this agent at these points:

- **Phase 1**: after each discovery or crawl wave, if unclassified entities exist
- **Phase 2**: after each research wave, if adjacent discoveries added unclassified entities
- **Before Phase 3**: all entities should be assessed before analysis begins
- **After criteria change**: reassess all researched entities against updated criteria
- **After migration**: database migration marks entities needing verification

## Rules

- Shallow mode classification only — read existing notes, at most one web fetch per entity
- Assign all applicable modes — entities can have multiple modes
- Always remove `unclassified` — every entity exits with only substantive modes
- Link criteria to notes with evidence quality — do not link without evidence
- "pass" means the note provides evidence the criterion is met
- "fail" means the note provides evidence the criterion is NOT met
- No link means insufficient evidence — distinct from failure
- Process sequentially — one entity at a time
- Write as you go — do not batch all writes to the end
- Agent uses only MCP tool calls
- Do not modify notes or descriptions — this is an assessment pass, not a research pass
