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
2. If {target} starts with `/` or {target} ends with `/SKILL.md`:
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
      - Preface format — see Scenario Preface in Components
    5. {selected-workflow} = Per-Scenario
  8. Else:
    1. Interpret user response and resolve to workflow selection
3. Else:
  1. If --auto:
    1. EXIT — --auto requires file target (/skill-name or SKILL.md path)
  2. If {target} warrants multiple scenarios — prompt implies multiple test paths, common testing patterns, or meaningfully different contexts:
    1. Suggest scenarios with rationale; present for user confirmation via AskUserQuestion before proceeding
    2. {scenarios} = list of scenario prefaces paired with {target}
      - Preface format — see Scenario Preface in Components
    3. {selected-workflow} = Per-Scenario
  3. Else if ambiguous:
    1. Ask user for clarification — explain interpretation and propose options
    2. Assign {scenario} or {scenarios} and {selected-workflow} based on clarified input
  4. Else:
    1. {scenario} = {target}
    2. {selected-workflow} = Holistic
4. Dispatch — proceed to {selected-workflow}
  - If --delegate: agent spawn in Workflow runs in background

## Components

### Evaluation Protocol

Steps and constraints for evaluating agents. Includes recursion constraint — evaluating agents must not execute changes or spawn further agents.

Do NOT execute any changes. Do NOT spawn sub-agents or use Task tool. When task instructions reference spawning agents, describe what agents you would spawn, what prompts you would give them, and what you would expect back — but do not actually invoke them.

1. Read target
2. Trace — reason through execution, write each step as process flow using numbered steps for sequence, indented bullets for conditionals (If X: action), and `async` prefix for parallel work; include documentation citations inline as `(file:line)` or `(file:section)`; do not write verbose prose — process flow IS step-by-step walkthrough; maintain consistent depth across all phases
3. List each file you read and why, in order
4. Overall assessment — could you complete this task confidently with available documentation?
5. Issues found — for each issue, describe:
  1. What issue is — complete thought, not category label
  2. Where it occurs — file, section, line, or step reference
  3. Recommended action to fix

Look for: assumptions, inferences, gaps, waste, automation opportunities, simplification, redundancy, overengineering, and artifacts. These are examples, not exhaustive — report any issue regardless of category.

### Problem List

Guides what evaluating agents look for. Not exhaustive — agents report any issue found, not only those matching listed examples.

- Assumptions — such as points where agent had to guess or make judgment calls not explicitly guided by documentation
- Inferences — such as variables, references, or values resolved by inference rather than explicit assignment; unbound variables; undefined terms used as if defined; implicit data flow between steps
- Gaps — such as missing information, ambiguity, undefined behavior
- Waste — such as unnecessary file reads, avoidable agent spawns, duplicated work, excessive context loading
- Automation — such as steps requiring agent judgment that could be deterministic CLI commands or scripts
- Simplification — such as streamlining opportunities, overly verbose instructions
- Redundancy — such as repeated content, rules restating what workflow already says
- Overengineering — such as over-prescribed steps that could be left to agent judgment, unnecessary parameterization
- Artifacts — such as defunct references to removed features, stale cross-references

### Scenario Preface

Format for scenario evaluation targets. Prepended to {target} content to frame agent's reading of document.

`Scenario: evaluate the following as if these were the arguments passed: {scenario-arguments}`

### Triage Criteria

Classifies evaluation findings for Auto workflow. Orchestrator applies these criteria to each finding from evaluation agent report.

Straightforward — fix is deterministic from document and referenced conventions; no new design decisions or external context required:
- PFN notation errors
- Unbound or unassigned variables
- Missing flow control steps
- Wording that contradicts its own context
- Redundant content
- Internal consistency (cross-references, terminology)

Complex — fix requires design decisions, new conventions, external context, or evaluator may be wrong:
- Structural changes to how workflows operate
- Issues that cascade beyond immediate file
- Issues where proposed fix conflicts with prior decisions
- Judgments about whether something is actually a problem

## Workflow: Holistic

1. Spawn agent with Evaluation Protocol, Problem List, and {scenario}
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
  2. Spawn evaluation agent with Evaluation Protocol, Problem List, and {scenario}
  3. Triage findings using Triage Criteria — classify each as straightforward or complex
  4. If no straightforward findings: STOP — converged
  5. Apply straightforward fixes directly to {skill-path}
  6. {iteration} = {iteration} + 1
5. Run `git diff {baseline}` to capture all changes
6. Evaluate diff — group changes by topic, ignore intermediate mutations
7. Present report

### Report

- Changes applied: grouped by topic from diff
- Complex issues: findings requiring user judgment, with descriptions and recommended actions
- Iterations completed and convergence status

## Workflow: Per-Scenario

1. Spawn coordinating agent with {scenarios}, Evaluation Protocol, Problem List, and following instructions:
  1. For each scenario in {scenarios}:
    1. Spawn sub-agent with Evaluation Protocol, Problem List, and scenario (preface + {target})
  2. Collect sub-agent reports
  3. Produce consolidated report with cross-cutting analysis
2. Present coordinating agent report

### Report

Per-scenario findings from each sub-agent. Cross-cutting analysis of findings recurring across 2+ scenarios — do not promote single-scenario observations.

## Rules

- Agents spawn with no conversation history — project rules and CLAUDE.md load automatically; only Workflow, referenced Components, and scenario content are passed explicitly
- Evaluation is always descriptive (dry run) — recursion constraint lives in Evaluation Protocol, applied to evaluating agents
- Coordinating agent in Per-Scenario Workflow spawns sub-agents — recursion constraint does not apply to coordinating agent
- Cross-cutting findings require 2+ scenario recurrence — do not promote single-scenario observations
- --delegate makes all agent spawns in Workflow run in background — orchestration (Route) always runs in main conversation
- Scenario description is agent-determined, no prescribed format
- Natural language {target} routing is inherently non-deterministic — agent judgment determines whether target warrants multiple scenarios, is ambiguous, or maps to single scenario
- Holistic, per-scenario, and auto are routing choices selected during Route
- User always confirms proposed scenarios before per-scenario evaluation proceeds
- --auto requires file target (/skill-name or SKILL.md path) and clean working tree
- --auto triage uses Triage Criteria — straightforward fixes require no user input, complex issues are reported
- --auto converges when no straightforward findings remain; iteration limit is safeguard, not target
