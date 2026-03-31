# Phase 3: Analysis

Execution phase — sequential batch agents with rolling analysis and orchestrator-driven measure extraction.

## Workflow

### Input

- Populated database from Phase 2 (`blueprint/data/research.db`)
- `blueprint/2-goals.md` for project goals and priority order
- `blueprint/4-effectiveness-criteria.md` for evaluating patterns
- `blueprint/6-domain-knowledge.md` for landscape context

### Pre-Analysis

1. Query database for analysis inputs:
    - `get_dashboard()` — overall summary
    - `list_entities({stage: "researched"})` — researched entities with relevance
2. Build ordered entity list — researched entities sorted by relevance (highest first), with entity IDs
3. Present analysis plan to user — entity count, analytical questions, dynamic loading approach (agents self-regulate batch size based on accumulated note content)
4. User confirms to proceed

### Analytical Questions

All agents answer all questions from whatever entities they consume:

1. Cross-cutting patterns — what do high-relevance entities share? Compare note themes across entities with highest relevance. Identify common approaches, tools, strategies.
2. Adoption frequency — how many entities use X? Scan notes for mentions of specific tools, platforms, approaches. Count distinct entities referencing each.
3. Purpose and value — why do they use X? Extract context from notes about why entities adopted specific approaches. Capture stated benefits and outcomes.
4. Gap analysis — what are top performers using that others are not? Compare note content between high-relevance and lower-relevance entities.
5. Cautionary patterns — what do underperformers share? Identify patterns associated with low relevance, abandonment, or poor adoption.
6. Decision cascades — adopting X also gives Y and Z. Identify co-occurring patterns in notes — approaches that come bundled, single decisions with outsized impact.

### Execution

5. Check existing measures: `get_measure_summary()`
    1. If measures exist: existing entity measures remain valid — extract measures for new entities only during step 9
    2. If no measures: full extraction during step 9
7. Spawn sequential agents with dynamic loading:
    1. Spawn agent with Analysis Agent template:
        - Provide full ordered entity list (all researched entity IDs by relevance descending)
        - First agent: no prior analysis, start from first entity
        - Subsequent agents: prior agent's analysis + resume from next unconsumed entity
    2. Agent dynamically loads entities one at a time via MCP tool calls, tracking accumulated content size; stops consuming when approaching context budget; produces analysis of entities consumed so far; returns analysis + last entity consumed + next entity to resume from
    3. Orchestrator reviews agent output — checks for completeness, flags issues
    4. If agent reports all entities consumed (`complete: true`): Go to step 8. Domain Knowledge Refinement
    5. Else: spawn next agent with prior analysis + resumption point

### Domain Knowledge Refinement

8. Review terminal analysis against `blueprint/6-domain-knowledge.md`:
    - Do current categories reflect functional areas from cross-entity analysis?
    - Are there areas with enough entities to warrant a new category?
    - Are there categories with no meaningful entity population?
    - Update if warranted — present changes to user before writing

### Measure Extraction

9. Derive measures per entity from notes and terminal analysis:
    - Measures are universal key/value pairs discovered during analysis — quantifiable attributes revealed as meaningful across entities (not predefined)
    - Extracted from existing notes — facts already captured during research
    - Orchestrator identifies measure schema from terminal analysis, then spawns agent(s) to extract measures from entity notes via MCP tool calls

### Findings

10. Compile analytical findings into `blueprint/7-findings.md`:
    - Every section and subsection must include a description explaining what it measures, why items are grouped, and how to interpret data — a reader without context should understand grouping logic
    - Pattern tiers (table-stakes, differentiators, emerging, absent) based on adoption count across cohort, not effectiveness recommendation; tier descriptions must state this
    - Cautionary patterns note correlation with weaker presences, not causal claims
    - Decision cascades explain co-occurrence logic
    - Measure distributions and co-occurrence data (from `get_measure_summary()`)
    - Decision cascades with specific entity evidence
    - Cautionary patterns with specific entity evidence
    - Domain knowledge updates (if any)
    - Templated, data-driven output — no project-specific interpretation

11. Compile goal-aligned interpretation into `blueprint/8-interpretation.md`:
    - Read `blueprint/2-goals.md` — frame every finding through these goals
    - Read `blueprint/4-effectiveness-criteria.md` — evaluate patterns against these criteria
    - For each significant finding: what does this mean for the goals? What should we learn? What practices to model?
    - Practices to adopt, organized by effectiveness evidence
    - Project-specific output — rewritten when goals change without re-running analysis agents

12. Present both documents to user

### Post-Analysis Goal Refinement

13. Orchestrator and user review:
    - Did `blueprint/2-goals.md` produce an interpretation reflecting the project's actual intent?
    - Did `blueprint/4-effectiveness-criteria.md` filter for the right pattern qualities?
    - Are there findings mapping to no goal, suggesting a missing goal?
    - Are there goals producing no findings, suggesting scope or criteria misalignment?
14. If refinement needed:
    1. Update relevant project definition file(s)
    2. If `blueprint/4-effectiveness-criteria.md` changed: clear measures — criteria change invalidates prior measures: `clear_all_measures()`
    3. Rewrite `blueprint/8-interpretation.md` through updated goals — no need to re-run analysis agents or regenerate findings unless measures were cleared
15. User confirms interpretation is aligned

## Re-Entry

When Phase 3 resumes with existing analysis data, present dashboard:

1. `get_dashboard()` — entity counts including measures
2. If `blueprint/7-findings.md` exists: present existing findings
3. If `blueprint/8-interpretation.md` exists: present existing interpretation
4. User directs: re-run analysis (clears measures first), re-interpret with updated goals (rewrites interpretation only), refine existing analysis, or proceed to Phase 4

## Agent Prompt Template

### Analysis Agent

```
Analyze entity notes and produce consolidated cross-entity analysis.

Analytical questions to answer from entities examined:
1. Cross-cutting patterns — what do high-relevance entities share?
2. Adoption frequency — how many entities use each tool, platform, or approach?
3. Purpose and value — why do entities adopt specific approaches? What benefits?
4. Gap analysis — what are top performers using that others are not?
5. Cautionary patterns — what do underperformers share?
6. Decision cascades — which adoptions bundle together or create outsized impact?

Ordered entity list (by relevance descending): `{ordered_entity_ids}`
Start from: `{start_entity_id}`

{if prior_analysis}
Prior analysis from previous batches (refine, confirm, adjust, or overturn with evidence from new entities):

{prior_analysis_text}
{end if}

Procedure:
1. Read entities one at a time in provided order, starting from `{start_entity_id}`:
    get_entity({entity_id: "{entity_id}"})
2. After reading each entity, assess whether room to consume more; stop when adding another entity's notes would leave insufficient room for thorough analysis; always consume at least one entity
3. Analyze notes across all consumed entities
4. {if prior_analysis} Integrate with prior analysis — update counts, strengthen or weaken patterns, add new findings {end if}
5. Produce consolidated analysis

Output format — consolidated analysis containing:
- For each analytical question: findings with specific entity IDs and note evidence
- Quantified where possible: entity counts per pattern, frequency rankings
- Confidence indicators: patterns seen in 2 entities vs 20
- Entities consumed this batch: count and ID list
- Cumulative entities examined (including prior batches): count and ID list
- Next entity to resume from (or "complete" if all entities consumed)

Rules:
- Do NOT write to database — read-only analysis
- Do NOT create files
- Do NOT repeat full entity details or note lists — cite entity IDs and summarize relevant note content
- NEVER access database directly — MCP tool calls are the only interface
```

## Output

- `blueprint/7-findings.md` — measure distributions, pattern tiers, decision cascades, cautionary patterns, taxonomy changes
- `blueprint/8-interpretation.md` — goal-aligned interpretation, practices to adopt with effectiveness evidence
- `blueprint/data/research.db` — measures derived per entity from notes and terminal analysis

## Gate

User reviews findings and confirms practices to pursue. May request:

1. Re-interpret findings through refined goals (updates interpretation only)
2. Add more entities (reverts to Phase 1 — see Phase Reversion in SKILL.md)

`blueprint/8-interpretation.md` feeds Phase 4 implementation planning directly.
