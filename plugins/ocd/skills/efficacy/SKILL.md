---
name: ocd-efficacy
description: Documentation efficacy testing; evaluates whether documentation enables correct task execution via holistic or per-scenario examination
argument-hint: "--target </skill-name | natural language scenario> [--delegate]"
---

# /ocd-efficacy

Evaluate whether documentation enables correct task execution. Holistic examination reviews raw document as single target. Per-scenario examination delegates to coordinating agent that spawns parallel evaluators per execution path. Mode is routing choice — evaluation protocol is shared.

## Trigger

User runs `/ocd-efficacy`

## Route

1. If not --target:
  1. EXIT — respond with skill description and argument-hint
2. If {target} starts with `/` or file named `SKILL.md`:
  1. If {target} starts with `/`:
    1. {skill-path} = resolve skill path — run navigator CLI `resolve-skill` with skill name (strip leading `/` from {target})
      ```
      python3 ${CLAUDE_PLUGIN_ROOT}/skills/navigator/scripts/navigator_cli.py resolve-skill <name>
      ```
    2. If exit code 1: EXIT — report skill not found
  2. Else:
    1. {skill-path} = {target}
  3. {target} = contents of {skill-path}
  4. Present mode choice to user:
    - Holistic — raw document, single agent examination
    - Per-scenario — coordinating agent spawns parallel evaluators per execution path
  5. If holistic:
    1. {scenario} = {target}
  6. If per-scenario:
    1. Identify scenarios — read target skill's Route section
      1. Each unique path through Route that leads to different Workflow constitutes scenario; skip EXIT routes reached by argument validation
      2. Construct one scenario per route — describe arguments that exercise that path
    2. Safeguard — if scenario count exceeds 10, report count and suggest consolidating
    3. Present scenarios to user for confirmation or modification
    4. {scenarios} = list of scenario prefaces paired with {target}
      - Preface format: `Scenario: evaluate the following as if these were the arguments passed: {scenario-arguments}`
3. Else:
  1. If {target} warrants multiple scenarios — prompt implies multiple test paths, common testing patterns, or meaningfully different contexts:
    1. Suggest scenarios with rationale; present for confirmation
    2. {scenarios} = list of scenario prefaces paired with {target}
  2. Else if ambiguous:
    1. Ask user for clarification — explain interpretation and propose options
  3. Else:
    1. {scenario} = {target}
4. Dispatch
  1. If --delegate:
    1. Spawn background agent with selected Workflow, referenced Components, and Rules
    2. Present agent report as-is
  2. Else:
    1. Proceed to selected Workflow

## Components

### Evaluation Protocol

Steps and constraints for leaf evaluating agents. Passed to agents as execution instructions. Includes recursion constraint — evaluating agents must not execute changes or spawn further agents.

Do NOT execute any changes. Do NOT spawn sub-agents or use Task tool. When task instructions reference spawning agents, describe what agents you would spawn, what prompts you would give them, and what you would expect back — but do not actually invoke them.

1. Read full document
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

## Workflow: Holistic

1. Spawn blank-context agent with Evaluation Protocol, Problem List, and {scenario}
2. Present agent report

### Report

Agent findings with trace, assessment, and per-issue descriptions with recommended actions.

## Workflow: Per-Scenario

1. Spawn blank-context coordinating agent with {scenarios}, Evaluation Protocol, and Problem List
  - Coordinating agent spawns one sub-agent per scenario — each sub-agent receives Evaluation Protocol, Problem List, and one scenario (preface + {target})
  - Coordinating agent collects sub-agent reports
  - Coordinating agent produces consolidated report with cross-cutting analysis
2. Present coordinating agent report

### Report

Per-scenario findings from each sub-agent. Cross-cutting analysis of findings recurring across 2+ scenarios — do not promote single-scenario observations.

## Rules

- Use Agent tool with `subagent_type="general-purpose"` for all agent spawns — blank context required; agent inherits CLAUDE.md automatically but receives no other context
- Evaluation is always descriptive (dry run) — recursion constraint lives in Evaluation Protocol, applied to leaf evaluating agents
- Coordinating agent in Per-Scenario Workflow spawns sub-agents — recursion constraint does not apply to coordinating agent
- Cross-cutting findings require 2+ scenario recurrence — do not promote single-scenario observations
- --delegate spawns background agent with selected Workflow, referenced Components, and Rules — mode selection and scenario resolution (Route) always run in main conversation
- Scenario description is agent-determined, no prescribed format
- Deterministic {target} values (`/skill-name`, SKILL.md paths) reassign {target} to file contents; all other {target} values pass through as literal text
- Holistic and per-scenario are routing choices selected during Route
