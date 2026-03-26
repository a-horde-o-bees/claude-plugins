# Phase 3: Analysis

## File Map

### Dependencies
```
.claude/skills/blueprint/blueprint_cli.py
docs/3-goals.md
docs/4-effectiveness-criteria.md
docs/6-domain-knowledge.md
```

### Created
```
references/research.db
references/analysis-findings.md
references/analysis-interpretation.md
```

Execution phase — sequential batch agents with rolling analysis and orchestrator-driven measure extraction.

## Input

- Populated database from Phase 2 (`references/research.db`)
- `docs/3-goals.md` for project goals and priority order
- `docs/4-effectiveness-criteria.md` for evaluating patterns
- `docs/6-domain-knowledge.md` for Domain Knowledge

## Pre-Analysis

1. Query database for analysis inputs:
  - `./cli.py claude blueprint get stats --db references/research.db` — overall summary
  - `./cli.py claude blueprint get entities --stage researched --db references/research.db` — researched entities with relevance
2. Build ordered entity list — researched entities sorted by relevance (highest first), with entity IDs
3. Present analysis plan to user — entity count, analytical questions to examine, dynamic loading approach (agents self-regulate batch size based on accumulated note content)
4. User confirms to proceed

## Analysis

Sequential agents consume entity batches and build a rolling analysis. Each agent reads a batch of entity notes via CLI, answers all analytical questions from the data it sees, and produces a consolidated analysis. The next agent receives the prior analysis plus a new batch, refining and extending findings. Analysis compounds across agents — later agents confirm, adjust, or overturn earlier findings.

### Analytical Questions

All agents answer all questions from whatever entities they consume:

1. Cross-cutting patterns — "What do high-relevance entities share?" Compare note themes across entities with highest relevance scores. Identify common approaches, tools, strategies.
2. Adoption frequency — "How many entities use X?" Scan notes for mentions of specific tools, platforms, approaches. Count distinct entities referencing each.
3. Purpose and value — "Why do they use X?" Extract context from notes about why entities adopted specific approaches. Capture stated benefits and outcomes.
4. Gap analysis — "What are top performers using that others aren't?" Compare note content between high-relevance and lower-relevance entities. Identify differentiating factors.
5. Cautionary patterns — "What do underperformers share?" Identify patterns associated with low relevance, abandonment, or poor adoption signals.
6. Decision cascades — "Adopting X also gives you Y and Z." Identify co-occurring patterns in notes — approaches that come bundled, single decisions with outsized impact.

### Execution

5. Clear any existing measures from prior analysis runs:
  `./cli.py claude blueprint clear measures --db references/research.db`

6. Spawn sequential agents with dynamic loading:
  1. Spawn agent (`subagent_type=general-purpose`) with Analysis Agent Prompt Template
    - Provide full ordered entity list (all researched entity IDs by relevance descending)
    - First agent: no prior analysis, start from first entity
    - Subsequent agents: prior agent's analysis + resume from next unconsumed entity
  2. Agent dynamically loads entities one at a time via CLI, tracking accumulated content size. Stops consuming when approaching context budget and produces analysis of entities consumed so far. Returns: analysis + last entity consumed + next entity to resume from.
  3. Orchestrator reviews agent output — checks for completeness, flags issues
  4. If agent reports all entities consumed (`complete: true`):
    1. Analysis is terminal; proceed to step 7
  5. Else: spawn next agent with prior analysis + resumption point

7. Domain knowledge refinement — orchestrator reviews terminal analysis against current Domain Knowledge in `docs/6-domain-knowledge.md`:
  - Do current categories reflect the functional areas that emerged from cross-entity analysis?
  - Are there areas with enough entities to warrant a new category?
  - Are there categories that no longer have meaningful entity populations?
  - Update Domain Knowledge in `docs/6-domain-knowledge.md` if warranted — present changes to user before writing

8. Derive measures per entity from notes and terminal analysis:
  - Measures are universal key/value pairs discovered during analysis — whatever quantifiable attributes the analysis reveals as meaningful across entities (not predefined)
  - Measures are extracted from existing notes — facts already captured during research
  - Orchestrator identifies the measure schema from terminal analysis, then spawns agent(s) to extract measures from entity notes via CLI

9. Compile analytical findings into `references/analysis-findings.md`:
  - Every section and subsection must include a description explaining what it measures, why items are grouped together, and how to interpret the data — a reader encountering the document without context should understand the grouping logic
  - Pattern tiers (table-stakes, differentiators, emerging, absent) are based on adoption count across the cohort, not effectiveness recommendation; tier descriptions must state this
  - Cautionary patterns note correlation with weaker presences, not causal claims
  - Decision cascades explain the co-occurrence logic that led to grouping
  - Measure distributions and co-occurrence data (from `get measures` command)
  - Decision cascades with specific entity evidence
  - Cautionary patterns with specific entity evidence
  - Domain knowledge updates (if any)
  - This is templated, data-driven output — no project-specific interpretation

10. Compile goal-aligned interpretation into `references/analysis-interpretation.md`:
  - Read `docs/3-goals.md` — frame every finding through these goals
  - Read `docs/4-effectiveness-criteria.md` — evaluate patterns against these criteria
  - For each significant finding: what does this mean for our goals? What should we learn from it? What practices should we model in our workflow?
  - Practices to adopt, organized by effectiveness evidence — what the best entities do, why it works, and how to model it
  - This is project-specific output — rewritten when goals change without re-running analysis agents

11. Present both documents to user

### Analysis Agent Prompt Template

```
Analyze entity notes and produce consolidated cross-entity analysis.

Analytical questions to answer from the entities you examine:
1. Cross-cutting patterns — what do high-relevance entities share?
2. Adoption frequency — how many entities use each tool, platform, or approach?
3. Purpose and value — why do entities adopt specific approaches? What benefits do they report?
4. Gap analysis — what are top performers using that others aren't?
5. Cautionary patterns — what do underperformers share?
6. Decision cascades — which adoptions bundle together or create outsized impact?

Ordered entity list (by relevance descending): `{ordered_entity_ids}`
Start from: `{start_entity_id}`

`{if prior_analysis}`
Prior analysis from previous batches (refine, confirm, adjust, or overturn with evidence from new entities):

`{prior_analysis_text}`
`{end if}`

Procedure:
1. Read entities one at a time in the provided order, starting from `{start_entity_id}`:
  `./cli.py claude blueprint get entity {entity_id} --db references/research.db`
2. After reading each entity, assess whether you have room to consume more. Stop consuming new entities when you judge that adding another entity's notes would leave insufficient room for producing a thorough analysis. Always consume at least one entity.
3. Analyze notes across all consumed entities
4. `{if prior_analysis}` Integrate with prior analysis — update counts, strengthen or weaken patterns, add new findings `{end if}`
5. Produce consolidated analysis

Output format — consolidated analysis document containing:
- For each analytical question: findings with specific entity IDs and note evidence
- Quantified where possible: entity counts per pattern, frequency rankings
- Confidence indicators: patterns seen in 2 entities vs 20
- Entities consumed this batch: count and ID list
- Cumulative entities examined (including prior batches): count and ID list
- Next entity to resume from (or "complete" if all entities consumed)

Rules:
- Do NOT write to the database — this is read-only analysis
- Do NOT create files
- Do NOT repeat full entity details or note lists — cite entity IDs and summarize relevant note content
- NEVER access database directly — no raw SQL, no `sqlite3` imports, no `python -c` database commands; CLI is only interface
- Every Bash call must be a single-line command starting with a recognized program name — no comments, no line continuations, no shell loops, no variable assignments before command
- Use `./cli.py claude blueprint` — never absolute paths
```

## Post-Analysis Goal Refinement

After presenting findings, review whether the project definition files produced the right analysis framing:

12. Orchestrator and user review:
  - Did `docs/3-goals.md` produce interpretation that reflects the project's actual intent?
  - Did `docs/4-effectiveness-criteria.md` filter for the right qualities in patterns?
  - Are there findings that don't map to any goal, suggesting a missing goal?
  - Are there goals that produced no findings, suggesting scope or criteria misalignment?
13. If refinement needed: update the relevant project definition file(s), then rewrite `references/analysis-interpretation.md` through updated goals — no need to re-run analysis agents or regenerate `references/analysis-findings.md`
14. User confirms interpretation is aligned

## Re-Entry

When Phase 3 resumes with existing analysis data, present re-entry dashboard:

1. `./cli.py claude blueprint get stats --db references/research.db` — entity counts including measure counts
2. If `references/analysis-findings.md` exists: present existing analytical findings
3. If `references/analysis-interpretation.md` exists: present existing interpretation
4. User directs next action: re-run analysis (clears measures first), re-interpret with updated goals (rewrites interpretation only), refine existing analysis, or proceed to Phase 4

## Output

- `references/analysis-findings.md` — measure distributions, pattern tiers, decision cascades, cautionary patterns, taxonomy changes
- `references/analysis-interpretation.md` — goal-aligned interpretation of findings, practices to adopt with effectiveness evidence
- `references/research.db` — measures derived per entity from notes and terminal analysis

## Gate

User reviews findings and confirms which practices to pursue. May request:
- Re-interpret findings through refined goals (updates interpretation only)
- Add more entities (reverts to Phase 1 — see Phase Reversion in SKILL.md)

Record confirmed findings in `docs/blueprint.md` under Phase 3 section — these drive Phase 4 implementation planning.
