# Phase 4: Implementation Blueprint

## File Map

### Dependencies
```
.claude/skills/blueprint/blueprint_cli.py
references/analysis-findings.md
references/analysis-interpretation.md
references/research.db
docs/blueprint.md
docs/3-goals.md
docs/5-constraints.md
```

### Created
```
docs/implementation-progress.md
docs/progress.db
```

Design phase — includes refinement loop.

## Input

- Analytical findings from `references/analysis-findings.md`
- Goal-aligned interpretation from `references/analysis-interpretation.md`
- Confirmed findings from `docs/blueprint.md` Phase 3 section
- Project goals and priority order from `docs/3-goals.md`
- Implementation constraints from `docs/5-constraints.md`
- Database for detailed entity queries and source-level notes: `./cli.py claude blueprint get entity {id} --db references/research.db`

## Draft Blueprint

1. Extract from research: every tool, platform, integration, dependency, requirement, and process user needs to implement
2. Use decision cascades from analysis to inform dependency ordering — relationships that unlock multiple needs get priority positioning
3. Organize into dependency-ordered implementation topics
4. For each topic, document:
  - What it is and why it matters
  - Cost estimates where available
  - Dependencies — what must come first
  - Recommended sequence position
  - Supporting evidence from research (which entities use it, how)
5. Build phased timeline based on dependencies and priorities
  - Distinguish between foundational items (needed regardless of scale) and progressive items (adopted as project matures)
  - Where analysis identified relationship target tiers, align implementation phases: table-stakes first, differentiators next, emerging last
6. Present draft implementation plan

## Refine Blueprint

7. User reviews and provides feedback:
  - Reprioritize topics based on specific constraints (budget, timeline, skills)
  - Remove items that do not apply to their situation
  - Add items research surfaced but did not explicitly recommend
  - Adjust dependency ordering based on operational reality
8. Revise and present refined plan
9. Repeat until user approves

## Re-Entry

When Phase 4 resumes with existing implementation work, present re-entry dashboard:

1. If `docs/implementation-progress.md` exists: present existing draft plan
2. `references/analysis-findings.md` — analytical findings
3. `references/analysis-interpretation.md` — goal-aligned interpretation driving implementation decisions
4. `docs/blueprint.md` Phase 3 section — confirmed findings from analysis
5. `docs/3-goals.md` — project goals and priority order
6. `docs/5-constraints.md` — implementation constraints

User directs next action: revise existing plan, restart draft from analysis findings, or proceed to handoff.

## Output

`docs/implementation-progress.md` — actionable checklist with:

- Status tracking per item (checkbox format)
- Dependency ordering (items grouped by phase/priority)
- Decision rationale as sub-bullets on relevant items
- Cost estimates where available
- Phased timeline with logical groupings

## Handoff to Progress Tracking

After user approves implementation plan, invoke `/progress`. Progress skill detects that no database exists, initializes it, and imports `docs/implementation-progress.md` automatically.

Progress skill owns `docs/implementation-progress.md` and `docs/progress.db` from this point forward. Blueprint's job is complete. Future updates to plan happen through `/progress`, not `/blueprint`.

## Gate

User approves final implementation plan and progress database is initialized.
