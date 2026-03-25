---
name: ocd-efficacy
description: Documentation efficacy testing; evaluates whether documentation enables correct task execution via holistic or per-scenario examination
argument-hint: "--target </skill-name | natural language scenario> [--auto] [--delegate]"
---

# /ocd-efficacy

Evaluate whether documentation enables correct task execution. Agents spawn with no conversation history to truthfully evaluate instructions without prior context influencing assessment. Holistic examination reviews raw document as single target. Per-scenario examination delegates to coordinating agent that spawns parallel evaluators per execution path. Auto mode iteratively evaluates and fixes straightforward issues until convergence, reporting complex issues for user review. Mode is routing choice — evaluation protocol is shared.

## Trigger

User runs `/ocd-efficacy`

## Route

1. If not --target:
  1. EXIT — respond with skill description and argument-hint
2. If {target} starts with `/` or {target} is a path ending with `/SKILL.md`:
  1. If {target} starts with `/`:
    1. {skill-path} = resolve skill path — run navigator CLI `resolve-skill` with skill name (strip leading `/` from {target})
      ```
      python3 ${CLAUDE_PLUGIN_ROOT}/skills/navigator/scripts/navigator_cli.py resolve-skill <name>
      ```
    2. If exit code 1: EXIT — report skill not found
  2. Else:
    1. {skill-path} = {target}
  3. {target} = contents of {skill-path}
  4. If --auto:
    1. {selected-workflow} = Auto
    2. Go to step 4. Dispatch
  5. Present mode choice to user via AskUserQuestion with options:
    1. Holistic — raw document, single agent examination
    2. Per-scenario — coordinating agent spawns parallel evaluators per execution path
  6. If holistic:
    1. {scenario} = {target}
    2. {selected-workflow} = Holistic
  7. Else if per-scenario:
    1. Identify scenarios — read target skill's Route section
      1. Each unique path through Route that leads to different Workflow constitutes scenario; skip EXIT routes reached by argument validation
      2. Construct one scenario per route:
        1. {scenario-arguments} = description of arguments that exercise route path
    2. Safeguard — if scenario count exceeds 10, report count and suggest consolidating
    3. Present scenarios to user for confirmation via AskUserQuestion
    4. {scenarios} = list of scenario prefaces paired with {target}
      - Preface format — see `_scenario-preface.md`
    5. {selected-workflow} = Per-Scenario
  8. Else:
    1. EXIT — re-invoke with intended target or mode
3. Else:
  1. If --auto:
    1. EXIT — --auto requires file target (/skill-name or SKILL.md path)
  2. If {target} warrants multiple scenarios — prompt implies multiple test paths, common testing patterns, or meaningfully different contexts:
    1. Suggest scenarios with rationale; present for user confirmation via AskUserQuestion before proceeding
    2. {scenarios} = list of scenario prefaces paired with {target}
      - Preface format — see `_scenario-preface.md`
    3. {selected-workflow} = Per-Scenario
  3. Else if ambiguous:
    1. Ask user for clarification — explain interpretation and propose options
    2. Assign {scenario} or {scenarios} and {selected-workflow} based on clarified input
  4. Else:
    1. {scenario} = {target}
    2. {selected-workflow} = Holistic
4. Dispatch
  - If --delegate: agent spawn in Workflow runs in background

## Workflow: Holistic

1. Spawn agent with {scenario} and instructions:
  1. Read `_evaluation-protocol.md` and `_problem-list.md`
  2. Follow evaluation protocol against {scenario}
2. Present agent report

### Report

Agent findings with trace, assessment, and per-issue descriptions with recommended actions.

## Workflow: Auto

Iterative fix-and-verify loop. Orchestrator evaluates, triages findings, fixes straightforward issues, and re-evaluates until convergence.

1. Check precondition — working tree must be clean
  1. Run `git status --porcelain`
  2. If output is non-empty: EXIT — commit pending changes before running --auto
2. {baseline} = `git rev-parse HEAD`
3. {iteration} = 0
4. While {iteration} < 5:
  1. {scenario} = re-read {skill-path} from disk
  2. Spawn evaluation agent with {scenario} and instructions:
    1. Read `_evaluation-protocol.md` and `_problem-list.md`
    2. Follow evaluation protocol against {scenario}
  3. Read `_triage-criteria.md`
  4. Triage findings — classify each as straightforward or complex
  5. If no straightforward findings: STOP — converged
  6. Apply straightforward fixes directly to {skill-path}
  7. {iteration} = {iteration} + 1
5. Run `git diff {baseline}` to capture all changes
6. Evaluate diff — group changes by topic, ignore intermediate mutations
7. Present report

### Report

- Changes applied: grouped by topic from diff
- Complex issues: findings requiring user judgment, with descriptions and recommended actions
- Iterations completed and convergence status

## Workflow: Per-Scenario

1. Spawn coordinating agent with {scenarios} and instructions:
  1. For each scenario in {scenarios}:
    1. Spawn sub-agent with scenario and instructions:
      1. Read `_evaluation-protocol.md` and `_problem-list.md`
      2. Follow evaluation protocol against scenario
  2. Collect sub-agent reports
  3. Produce consolidated report with cross-cutting analysis
2. Present coordinating agent report

### Report

Per-scenario findings from each sub-agent. Cross-cutting analysis of findings recurring across 2+ scenarios — do not promote single-scenario observations.

## Rules

- Agents spawn with no conversation history — project rules and CLAUDE.md load automatically; only Workflow instructions and scenario content are passed explicitly
- Evaluation is always descriptive (dry run) — recursion constraint lives in `_evaluation-protocol.md`, applied to evaluating agents; coordinating agents never read evaluation files
- Coordinating agent in Per-Scenario Workflow spawns sub-agents — passes evaluation file references to sub-agents without reading them
- Cross-cutting findings require 2+ scenario recurrence — do not promote single-scenario observations
- --delegate makes all agent spawns in Workflow run in background — orchestration (Route) always runs in main conversation
- Scenario description is agent-determined, no prescribed format
- Natural language {target} routing is inherently non-deterministic — agent judgment determines whether target warrants multiple scenarios, is ambiguous, or maps to single scenario
- Holistic, per-scenario, and auto are routing choices selected during Route
- User always confirms proposed scenarios before per-scenario evaluation proceeds
- --auto requires file target (/skill-name or SKILL.md path) and clean working tree
- --auto triage uses `_triage-criteria.md` — straightforward fixes require no user input, complex issues are reported
- --auto converges when no straightforward findings remain; iteration limit is safeguard, not target
