# Classify Modes

Agent subprocess — resolves all entities carrying the `unclassified` mode marker. Modes are interaction modes that determine what kind of agent work an entity receives. If an entity has two modes, it needs two different kinds of agent work — crawl it AND deep-research it. These are separate activities that happen in different phases.

## Valid Modes

Database enforces these values via CHECK constraint:

- `example` — comparable tool, project, or system to study; receives deep research in Phase 2
- `directory` — crawlable listing that yields other entities; receives directory crawl agents in Phase 1
- `context` — knowledge, advice, or data source informing the project; receives context research in Phase 1
- `unclassified` — marker indicating classification pass needed; removed by this subprocess

An entity may have multiple modes simultaneously (e.g., both `directory` and `example`). `unclassified` coexists with other modes — it signals that the current mode assignments have not been verified.

## Input

Orchestrator provides:
- Research database (accessed via MCP tool calls)
- `blueprint/1-scope.md` for scope context
- `blueprint/3-assessment-criteria.md` for assessment reference

## Agent Workflow

### Discover Unclassified

1. Find entities needing classification:
    ```
    get_unclassified()
    ```
2. If no results: Return — report "No unclassified entities"
3. Read scope and assessment criteria for classification context

### Classify Each Entity

4. For each {entity} in {unclassified-entities}:
    1. Read entity with existing data:
        ```
        get_entity({entity_id: "{entity_id}"})
        ```
    2. Evaluate existing notes, description, and URLs to determine applicable modes:
        - Does it list or aggregate other entities? → `directory`
        - Is it a tool, project, or system comparable to the research target? → `example`
        - Is it a knowledge source, guide, dataset, or advice resource? → `context`
        - Multiple modes may apply — assign all that fit
    3. If existing information is insufficient for confident classification:
        1. Fetch primary URL (one web request) for surface-level understanding
        2. Classify based on combined knowledge
    4. Replace modes — remove all current modes and set correct ones:
        ```
        set_modes({entity_id: "{entity_id}", modes: ["example", "directory"]})
        ```
        `set_modes` replaces all existing modes. Do not include `unclassified` — its removal signals classification is complete.
    5. If classification reveals the entity fails hardline criteria from `blueprint/3-assessment-criteria.md`:
        ```
        set_stage({entity_id: "{entity_id}", stage: "rejected"})
        add_notes({entity_id: "{entity_id}", notes: ["Rejected: {reason}"]})
        ```

### Report

5. Report for each entity:
    - Entity ID and name
    - Previous modes → new modes assigned
    - If rejected: reason
6. Summary: total classified, mode distribution, any rejections

## When to Invoke

Orchestrator proposes spawning this agent at these points:

- **Phase 1**: after each discovery or crawl wave, if `unclassified` entities exist
- **Phase 2**: after each research wave, if adjacent discoveries added `unclassified` entities
- **Before Phase 3**: all entities should be properly classified before analysis begins
- **After migration**: database migration marks all entities `unclassified` for verification

## Rules

- Shallow classification only — read existing notes and at most one web fetch per entity; do not perform deep research
- Assign all applicable modes — an entity can be both `directory` and `example`
- Always remove `unclassified` — every entity processed by this agent exits with only substantive modes
- Process sequentially — one entity at a time
- Agent uses only MCP tool calls, never raw SQL
- Do not modify notes or description unless classification reveals clearly stale information — this is a classification pass, not a research pass
