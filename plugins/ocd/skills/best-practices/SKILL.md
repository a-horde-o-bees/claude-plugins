---
name: ocd-best-practices
description: Convention and best-practice review; evaluates project against standard patterns, flags unconventional decisions with trade-off analysis and recommendations
argument-hint: "--target <project | directory-path> [--delegate]"
---

# /ocd-best-practices

Evaluate project conventions and architectural decisions against standard practices. Spawns agent that performs judgment-based analysis across focus areas. Deterministic checks (type checking, linting, reference validation) belong in separate tooling. Agent inherits project rules and CLAUDE.md automatically — ability to discover and follow project conventions is part of evaluation.

Core question agent answers: does this follow standard practices, or is something unconventional creating friction?

## Trigger

User runs `/ocd-best-practices`

## Route

1. If not --target: Exit to user — respond with skill description and argument-hint
2. If {target} is `project`:
    1. {scope} = `.` (project root)
    2. {scope-type} = project
3. Else if {target} is directory path:
    1. {scope} = {target}
    2. {scope-type} = directory
4. Else: Exit to user — target must be `project` or directory path
5. Dispatch
    - If --delegate: Workflow agent spawns in background

## Workflow

1. Spawn agent with evaluation({scope}, {scope-type}):
    1. Read `_evaluation-instructions.md` and `_criteria.md`
    2. Evaluate {scope} against criteria following focus area instructions
    3. If {scope-type} is `project`: include Architecture focus area
    4. Return:
        - Findings grouped by focus area
2. Present agent report

### Report

Agent findings grouped by focus area with per-finding trade-off analysis and recommendations. Overall assessment classifies scope as conventional, unconventional-but-justified, or unconventional-with-friction.

## Interpreting Results

- Agent found no issues — scope follows conventions well
- Agent flagged findings with justified trade-offs — unconventional but acceptable; document rationale
- Agent flagged findings with friction — structural decisions creating ongoing cost; consider addressing
- Same finding across multiple focus areas — strong signal; prioritize
- Agent missed obvious issues — criteria catalog has gaps; update `_criteria.md`

## Rules

- Single agent evaluates all focus areas sequentially across entire scope
- Architecture focus area included only for `project` scope — directory-scoped audits do not need it
- No deterministic checks — type checking, linting, reference validation belong in separate tooling
- Agent reports findings; does not apply fixes — best-practice review is diagnostic, not corrective
- Findings must include specific file paths and line references — no vague category-level observations
- Criteria catalog lives in `_criteria.md` — update when new anti-patterns are discovered
