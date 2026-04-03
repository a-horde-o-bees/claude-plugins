# Phase 4: Implementation Blueprint

Design phase — includes refinement loop.

## Workflow

### Input

- Analytical findings from `blueprint/7-findings.md`
- Goal-aligned interpretation from `blueprint/8-interpretation.md`
- Project goals and priority order from `blueprint/2-goals.md`
- Implementation constraints from `blueprint/5-constraints.md`
- Approved directions from `blueprint/9-directions.md` — only approved directions are implemented in the blueprint
- Database for detailed entity queries: `python3 ${CLAUDE_PLUGIN_ROOT}/run.py skills.research get entity {id} --db blueprint/data/research.db`

### Draft Blueprint

1. Extract from research: every tool, platform, integration, dependency, requirement, and process the user needs to implement
2. Use decision cascades from analysis to inform dependency ordering — relationships unlocking multiple needs get priority positioning
3. Organize into dependency-ordered implementation topics
4. For each {topic} in {implementation-topics}:
    - What it is and why it matters
    - Cost estimates where available
    - Dependencies — what must come first
    - Recommended sequence position
    - Supporting evidence from research (which entities use it, how)
5. Build phased timeline based on dependencies and priorities:
    - Distinguish foundational items (needed regardless of scale) from progressive items (adopted as project matures)
    - Where analysis identified relationship target tiers, align phases: table-stakes first, differentiators next, emerging last
6. Present draft implementation plan

### Refine Blueprint

7. User reviews and provides feedback:
    - Reprioritize topics based on specific constraints (budget, timeline, skills)
    - Remove items that do not apply
    - Add items research surfaced but did not explicitly recommend
    - Adjust dependency ordering based on operational reality
8. Revise and present refined plan
9. Repeat until user approves

### Finalize

10. Write approved plan to `blueprint/10-blueprint.md`

## Re-Entry

When Phase 4 resumes with existing implementation work, present dashboard:

1. If `blueprint/10-blueprint.md` exists: present existing draft plan
2. `blueprint/7-findings.md` — analytical findings
3. `blueprint/8-interpretation.md` — interpretation driving decisions
4. `blueprint/2-goals.md` — project goals
5. `blueprint/5-constraints.md` — implementation constraints

User directs: revise existing plan, restart draft from analysis findings, or approve.

## Output

`blueprint/10-blueprint.md` — an actionable implementation blueprint with:

- Dependency ordering (items grouped by phase/priority)
- Decision rationale as sub-bullets on relevant items
- Cost estimates where available
- Phased timeline with logical groupings

## Gate

User approves final implementation blueprint.
