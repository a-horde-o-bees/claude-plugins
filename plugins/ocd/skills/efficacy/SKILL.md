---
name: ocd-efficacy
description: Documentation efficacy testing; evaluates whether documentation enables correct task execution via holistic or per-scenario examination
argument-hint: "--target </skill-name | natural language scenario> [--auto] [--delegate]"
---

# /ocd-efficacy

Evaluate whether documentation enables correct task execution. Agents spawn with no conversation history to truthfully evaluate instructions without prior context influencing assessment. Holistic examination reviews raw document as single target. Per-scenario examination delegates to coordinating agent that spawns parallel evaluators per execution path. Both modes evaluate, triage findings, and fix Defects directly — Observations requiring judgment are reported for user review. `--auto` wraps selected workflow in convergence loop per skill-md convention. `--delegate` runs workflow in background.

## Trigger

User runs `/ocd-efficacy`

## Route

1. If not --target: Exit to user — respond with skill description and argument-hint
2. If ({target} starts with `/` and contains no spaces) or ({target} ends with `/SKILL.md`):
    1. If {target} starts with `/`:
        1. {skill-path} = resolve skill path — run navigator CLI `resolve-skill` with skill name (strip leading `/` from {target})
            ```
            python3 ${CLAUDE_PLUGIN_ROOT}/run.py skills.navigator.scripts.navigator_cli resolve-skill <name>
            ```
        2. If exit code 1: Exit to user — report skill not found
    2. Else:
        1. {skill-path} = {target}
    3. {target} = contents of {skill-path}
    4. If --auto:
        1. {scenario} = {target}
        2. {selected-workflow} = Holistic
        3. Go to step 4. Dispatch
    5. Present mode choice to user via AskUserQuestion with options:
        1. Holistic — raw document, single agent examination
        2. Per-scenario — coordinating agent spawns parallel evaluators per execution path
    6. If holistic:
        1. {scenario} = {target}
        2. {selected-workflow} = Holistic
    7. Else if per-scenario:
        1. Identify scenarios — read target skill's Route section
            1. Each unique path through Route that leads to different Workflow constitutes a scenario; skip Exit to user routes reached by argument validation
            2. Construct one scenario per route:
                1. {scenario-arguments} = description of arguments that exercise route path
        2. Safeguard — if scenario count exceeds 10, report count and suggest consolidating
        3. Present scenarios to user for confirmation via AskUserQuestion
        4. {scenarios} = list of scenario prefaces paired with {target}
            - Preface format — see `_scenario-preface.md`
        5. {selected-workflow} = Per-Scenario
    8. Else: Exit to user — re-invoke with intended target or mode
3. Else:
    1. If --auto: Exit to user — --auto requires file target (/skill-name or SKILL.md path)
    2. If {target} implies multiple test paths, common testing patterns, or meaningfully different contexts:
        1. Suggest scenarios with rationale; present for user confirmation via AskUserQuestion before proceeding
        2. {scenarios} = list of scenario prefaces paired with {target}
            - Preface format — see `_scenario-preface.md`
        3. {selected-workflow} = Per-Scenario
    3. Else if {target} is single clear evaluation subject:
        1. {scenario} = {target}
        2. {selected-workflow} = Holistic
    4. Else:
        1. Ask user for clarification — explain interpretation and propose options
        2. Assign {scenario} or {scenarios} and {selected-workflow} based on clarified input
4. Dispatch {selected-workflow}
    - If --auto: wrap in convergence loop per skill-md convention
    - If --delegate: agent spawn runs in background

## Workflow: Holistic

1. Spawn agent with holistic evaluation({scenario}):
    1. Read `_evaluation-protocol.md` and `_problem-list.md`
    2. Follow evaluation protocol against {scenario}
    3. Evaluation complete — triage phase begins
    4. Read `_triage-criteria.md`
    5. Triage findings — map Defect/Observation classifications per triage criteria
    6. Apply Defect fixes directly to target file; reject fixes that change control flow in loops or Exit to user paths (reclassify as Observation)
    7. Return:
        - Changes applied with rationale
        - Observations requiring user judgment
        - Overall assessment
2. Present agent report

### Report

- Changes applied: Defect fixes with rationale and intent preserved
- Observations: findings requiring user judgment, with descriptions and recommended actions
- Assessment: overall evaluation of document efficacy

## Workflow: Per-Scenario

1. Spawn agent with scenario coordination({scenarios}):
    1. For each {scenario} in {scenarios}:
        1. Spawn agent with scenario evaluation({scenario}):
            1. Read `_evaluation-protocol.md` and `_problem-list.md`
            2. Follow evaluation protocol against {scenario}
            3. Return:
                - Scenario findings
        - async agent per scenario
    2. Collect agent reports
    3. Produce cross-cutting analysis — findings recurring across 2+ scenarios
    4. Read `_triage-criteria.md`
    5. Triage consolidated findings — map Defect/Observation classifications per triage criteria
    6. Apply Defect fixes directly to target files; reject fixes that change control flow in loops or Exit to user paths (reclassify as Observation)
    7. Return:
        - Per-scenario findings
        - Cross-cutting analysis
        - Changes applied
        - Observations requiring user judgment
2. Present coordinating agent report

### Report

- Per-scenario findings from sub-agents
- Cross-cutting analysis — do not promote single-scenario observations
- Changes applied: Defect fixes with rationale
- Observations: findings requiring user judgment

## Rules

- Agents spawn with no conversation history — project rules and CLAUDE.md load automatically; only Workflow instructions and scenario content are passed explicitly
- Evaluation protocol constraints ("Do NOT execute any changes") govern evaluation steps; triage and fix are post-evaluation workflow steps executed by same or coordinating agent
- Coordinating agent in Per-Scenario spawns sub-agents with evaluation file references; sub-agents evaluate only, coordinator does triage and fix after consolidation
- Cross-cutting findings require 2+ scenario recurrence — do not promote single-scenario observations
- Route always runs in main conversation; --delegate applies only to Workflow agent spawns
- Scenario description is agent-determined, no prescribed format
- Natural language {target} routing is inherently non-deterministic — agent judgment determines whether target warrants multiple scenarios
- User always confirms proposed scenarios before per-scenario evaluation proceeds
- --auto defaults to Holistic for file targets — simpler iteration with single agent per pass
- --auto requires file target (/skill-name or SKILL.md path) and clean working tree
- --auto wraps selected workflow in convergence loop per skill-md convention; each iteration spawns fresh agent
