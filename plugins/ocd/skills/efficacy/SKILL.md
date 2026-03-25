---
name: ocd-efficacy
description: Documentation efficacy testing; iterates between holistic review and per-scenario evaluation to identify issues in documentation
argument-hint: "--target </skill-name | natural language scenario> [--delegate]"
---

# /ocd-efficacy

Test whether documentation enables correct task execution. Two-phase iterative evaluation: holistic review catches structural issues across full document, per-scenario evaluation catches issues that surface when walking specific execution paths. Phases alternate until user stops.

## Trigger

User runs `/ocd-efficacy`

## Route

1. If not --target:
  1. EXIT — respond with skill description and argument-hint
2. If {target} starts with `/` or file named `SKILL.md`:
  1. If {target} starts with `/`:
    1. Resolve skill path — run navigator CLI `resolve-skill` with skill name (strip leading `/` from {target})
      ```
      python3 ${CLAUDE_PLUGIN_ROOT}/skills/navigator/scripts/navigator_cli.py resolve-skill <name>
      ```
    2. If exit code 1: EXIT — report skill not found
  2. {target} = contents of resolved SKILL.md
  3. Resolve scenarios — read target skill's Route section
    1. Identify distinct routes — each unique path through Route that leads to different Workflow constitutes scenario; skip EXIT routes reached by argument validation (missing flags, empty arguments, unrecognized input)
    2. Construct one scenario per route — describe arguments that exercise that path
3. Else:
  1. {target} = {target}
  2. Evaluate whether {target} warrants multiple scenarios — consider whether prompt implies multiple test paths, common testing patterns, or meaningfully different contexts
    1. If multiple scenarios fit:
      1. Suggest scenarios with rationale
    2. Else if ambiguous:
      1. Ask user for clarification — explain interpretation and propose options
    3. Else:
      1. Single scenario — {target} as-is
4. Safeguard — if scenario count exceeds 10, report count and suggest consolidating
5. Present scenarios to user for confirmation or modification before executing
6. Dispatch
  1. If --delegate:
    1. Spawn background agent with resolved Workflow and Rules
    2. Present agent report as-is
  2. Else:
    1. Proceed to Workflow

## Workflow

### Phase 1: Holistic Review

1. Spawn single agent with Holistic Audit Prompt using {target}
2. Present findings to user
3. Wait for user — user reviews findings, resolves issues, or directs next steps
4. If user resolves issues:
  1. {target} = updated document contents
  2. User chooses: run Phase 2, repeat Phase 1, or stop

### Phase 2: Per-Scenario Evaluation

5. For each scenario:
  1. {scenario-target} = {target}
  2. If multiple scenarios:
    1. Append `\n\nScenario: {scenario-description}` to {scenario-target}
6. Spawn parallel agents — one blank-context agent per scenario with Per-Scenario Audit Prompt using {scenario-target}
  - async Scenario A agent
  - async Scenario B agent
  - async (one per additional scenario)
7. Collect agent reports and present results — for multiple scenarios, add cross-cutting analysis of findings recurring across 2+ scenarios
8. Wait for user — user reviews findings, resolves issues, or directs next steps
9. If user resolves issues:
  1. {target} = updated document contents
  2. User chooses: run Phase 1, repeat Phase 2, or stop

### Problem List

Guides what agents look for during both phases. Not exhaustive — agents report any issue found, not only those matching listed examples.

- Assumptions — points where agent had to guess or make judgment calls not explicitly guided by documentation
- Inferences — variables, references, or values resolved by inference rather than explicit assignment; unbound variables; undefined terms used as if defined; implicit data flow between steps
- Gaps — missing information, ambiguity, undefined behavior
- Waste — unnecessary file reads, avoidable agent spawns, duplicated work, excessive context loading
- Automation — steps requiring agent judgment that could be deterministic CLI commands or scripts
- Simplification — streamlining opportunities, overly verbose instructions
- Redundancy — repeated content, rules restating what workflow already says
- Overengineering — over-prescribed steps that could be left to agent judgment, unnecessary parameterization
- Artifacts — defunct references to removed features, stale cross-references

### Holistic Audit Prompt

```
You are reviewing documentation for structural issues. Read the full document, then report every issue you find. Do NOT execute any changes. Do NOT spawn sub-agents or use Task tool. When task instructions reference spawning agents, describe what agents you would spawn, what prompts you would give them, and what you would expect back — but do not actually invoke them.

Document:
`{target}`

For each issue found, describe:
1. What the issue is — complete thought, not a category label
2. Where it occurs — file, section, line, or step reference
3. Recommended action to fix

Look for: assumptions, inferences, gaps, waste, automation opportunities, simplification, redundancy, overengineering, and artifacts. These are examples, not an exhaustive list — report any issue regardless of category.
```

### Per-Scenario Audit Prompt

```
You are testing whether project documentation enables you to perform task. Follow your Discovery instructions, then describe IN DETAIL what you would do to accomplish task — but do NOT execute any changes. Do NOT spawn sub-agents or use Task tool. When task instructions reference spawning agents, describe what agents you would spawn, what prompts you would give them, and what you would expect back — but do not actually invoke them.

Task:
`{scenario-target}`

Report:
1. List each file you read and why, in order
2. Trace — as you reason through execution, write each step as process flow using numbered steps for sequence, indented bullets for conditionals (If X: action), and `async` prefix for parallel work. Include documentation citations inline as `(file:line)` or `(file:section)`. Do not write verbose prose — process flow IS step-by-step walkthrough. Maintain consistent depth across all phases.
3. Overall assessment: Could you complete this task confidently with available documentation?
4. Issues found — for each issue, describe:
  1. What the issue is — complete thought, not a category label
  2. Where it occurs — file, section, line, or step reference
  3. Recommended action to fix

Look for: assumptions, inferences, gaps, waste, automation opportunities, simplification, redundancy, overengineering, and artifacts. These are examples, not an exhaustive list — report any issue regardless of category.
```

### Report

Holistic — agent findings with per-issue descriptions and recommended actions.

Per-scenario — per-scenario agent output with trace, rating, and issues. Multiple scenarios include cross-cutting analysis of findings recurring across 2+ scenarios.

## Rules

- Use Agent tool with `subagent_type="general-purpose"` for all agent spawns — blank context required; agent inherits CLAUDE.md automatically but receives no other context
- Evaluation is always descriptive (dry run) — recursion prevention embedded in audit prompts as permanent directive
- Per-scenario agents spawn in parallel — each scenario gets independent blank-context agent; no shared state between scenarios
- Cross-cutting findings require 2+ scenario recurrence — do not promote single-scenario observations
- --delegate spawns background agent with resolved Workflow and Rules — scenario resolution (Route) always runs in main conversation
- Scenario description is agent-determined, no prescribed format
- Deterministic {target} values (`/skill-name`, SKILL.md paths) reassign {target} to file contents; all other {target} values pass through as literal text
- Phases alternate at user direction — orchestrator does not auto-advance between phases
