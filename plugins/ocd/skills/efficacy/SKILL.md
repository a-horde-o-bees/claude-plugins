---
name: ocd-efficacy
description: Documentation efficacy testing; --check spawns blank-context agent to verify documentation enables correct task execution
argument-hint: "--check [/skill-name | scenario description] [--delegate]"
---

# /ocd-efficacy

Test whether documentation enables blank-context agent to describe correct execution of task. Spawns agent that inherits CLAUDE.md automatically — ability to follow Discovery instructions, navigate references, and plan execution IS test. Evaluation only — agent describes what it would do, does not execute changes.

Blank context is structurally required — agent must discover everything from scratch to test whether documentation is sufficient. Separate agents are spawned rather than processing inline for this reason.

## Trigger

User runs `/ocd-efficacy`

## Route

1. If `--check` not in `$ARGUMENTS`:
  1. Respond with skill description and argument-hint, then stop
2. Strip flags — extract `--check` and `--delegate` from `$ARGUMENTS`
3. Resolve subject — validate remaining arguments, resolve paths
  1. If remaining arguments empty:
    1. EXIT — respond with skill description and argument-hint
  2. If subject starts with `/`:
    1. Resolve skill path — run navigator CLI `resolve-skill` with skill name (strip leading `/`)
      ```
      python3 ${CLAUDE_PLUGIN_ROOT}/skills/navigator/scripts/navigator_cli.py resolve-skill <name>
      ```
    2. If exit code 1: EXIT — report skill not found
    3. Read resolved SKILL.md as resolved prompt
  3. Else if subject is path to SKILL.md file:
    1. Read file as resolved prompt
  4. Else:
    1. Subject text is resolved prompt
4. Check recursion constraint — evaluate resolved prompt for agent-spawning patterns
  1. If matches `/Task\(|subagent_type|spawn\s+agent/`:
    1. Append recursion constraint (see Rules)
5. Resolve scenarios
  1. If subject is skill path:
    1. Read target skill's Route section
    2. Identify distinct routes — each unique path through Route that leads to a different Workflow or EXIT constitutes a scenario
    3. Construct one scenario per route — describe arguments that exercise that path
  2. Else:
    1. Evaluate whether subject warrants multiple scenarios — consider whether prompt implies multiple test paths, whether common testing patterns apply, or whether different contexts would produce meaningfully different results
    2. If multiple scenarios fit:
      1. Suggest scenarios with rationale
    3. Else if ambiguous:
      1. Ask user for clarification — explain interpretation and propose options
    4. Else:
      1. Single scenario — resolved prompt as-is
6. Present scenarios to user for confirmation or modification before executing
7. Dispatch
  1. If `--delegate`:
    1. Resolve all prompt template placeholders in Workflow
    2. Spawn background agent with resolved Workflow, subsections, and Rules
    3. Present agent report as-is
  2. Else:
    1. Proceed to Workflow with resolved scenarios

## Workflow

1. Spawn agents — one blank-context agent per scenario; construct Efficacy Audit Prompt with resolved prompt; for multiple scenarios, append `\n\nScenario: {scenario description}` to resolved prompt
  - async Scenario A agent
  - async Scenario B agent
  - async (one per additional scenario)
2. Collect structured output per agent (rating, trace, assumptions, gaps, waste, automation)
3. Evaluate results using Interpreting Results
4. If single scenario:
  1. Append architecture findings to agent output
5. Else:
  1. Produce cross-cutting analysis across scenarios
  2. Incorporate architecture findings from Interpreting Results into cross-cutting analysis

### Report

Single scenario — agent output with architecture findings appended:

```
{efficacy agent output}

Architecture Findings — numbered list, one line each. Orchestrator assessment based on Interpreting Results:
1. finding summary
2. finding summary
```

Multiple scenarios — per-scenario sections followed by cross-cutting analysis:

```
## Scenario 1: {scenario description}

Rating: {rating}

Trace:
{process flow from agent}

Assumptions:
{numbered one-liners from agent}

Gaps:
{numbered one-liners from agent}

Waste:
{numbered one-liners from agent}

Automation:
{numbered one-liners from agent}

## Scenario 2: {scenario description}
...

## Cross-Cutting Findings — numbered list, patterns recurring across 2+ scenarios:
1. finding summary
2. finding summary

Ratings: X Sufficient, Y Gaps Exist, Z Insufficient
```

Cross-cutting findings identify patterns in assumptions, gaps, waste, and automation opportunities that recur across 2+ scenarios. Single-scenario findings that do not recur are not promoted to cross-cutting — they remain in their scenario section.

### Efficacy Audit Prompt

```
You are testing whether project documentation enables you to perform task. Follow your Discovery instructions, then describe IN DETAIL what you would do to accomplish task — but do NOT execute any changes.

Task:
`{resolved_prompt}`

Report:
1. List each file you read and why, in order
2. Trace — as you reason through execution, write each step as process flow using numbered steps for sequence, indented bullets for conditionals (If X: action), and `async` prefix for parallel work. Include documentation citations inline as `(file:line)` or `(file:section)`. Do not write verbose prose — process flow IS step-by-step walkthrough. Maintain consistent depth across all phases — do not front-load detail on early steps and compress later ones. Each phase or major section should show same level of substep granularity, including domain-specific examples where task context makes them available (e.g., specific candidates, dimensions, or categories that would emerge).
3. Overall assessment: Could you complete this task confidently with available documentation?
4. Rate documentation efficacy: Sufficient / Gaps exist / Insufficient
5. Assumptions — numbered list, one line each. Every point where you had to guess, assume, or make judgment call not explicitly guided by documentation:
  1. assumption summary
  2. assumption summary
6. Gaps — numbered list, one line each. Every documentation gap, ambiguity, missing information, or suggested improvement encountered:
  1. gap summary
  2. gap summary
7. Waste — numbered list, one line each. Steps that read unnecessary files, spawn avoidable agents, duplicate work already done, or load more context than needed:
  1. waste summary
  2. waste summary
8. Automation — numbered list, one line each. Steps that require agent judgment but could be converted to deterministic CLI commands or scripts:
  1. automation summary
  2. automation summary
```

### Interpreting Results

- Agent described correct steps → Skill definition is clear and actionable
- Agent got stuck or guessed → Documentation has gaps at that step, needs specificity
- Agent found patterns and made sound judgments → Architecture works for this case
- Agent missed patterns → Reference chain has gaps (missing links between files)

## Rules

- Use Agent tool with `subagent_type="general-purpose"` for all agent spawns — blank context required, do not pass conversation context; agent inherits CLAUDE.md automatically but receives no other context
- Evaluation is always descriptive (dry run) — agent describes what it would do, never executes changes
- Recursion constraint: when resolved prompt matches agent-spawning pattern `/Task\(|subagent_type|spawn\s+agent/`, append to efficacy audit prompt: "Do NOT spawn sub-agents or use Task tool. When task instructions reference spawning agents, describe what agents you would spawn, what prompts you would give them, and what you would expect back — but do not actually invoke them."
- Agents spawn in parallel — each scenario gets independent blank-context agent; no shared state or dependencies between scenarios
- Skill path resolution via navigator `resolve-skill` — searches personal, project, plugin-dir, marketplace in Claude Code priority order
- Cross-cutting findings require 2+ scenario recurrence — do not promote single-scenario observations
- Route discovery for skill paths identifies distinct routes through Route section — each unique path that leads to a different Workflow or EXIT is a scenario
- Scenarios are always presented to user for confirmation before execution — orchestrator does not proceed without user approval of scenario list
- `--delegate` spawns background agent with resolved Workflow and Rules — scenario resolution (Route) always runs in main conversation; only workflow execution is delegated
