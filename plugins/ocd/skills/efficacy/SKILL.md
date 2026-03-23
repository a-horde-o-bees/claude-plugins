---
name: ocd-efficacy
description: Documentation efficacy testing; --check spawns blank-context agent to verify documentation enables correct task execution
argument-hint: "--check [/skill-name | scenario description] [--multi]"
---

# /ocd-efficacy

Test whether documentation enables blank-context agent to describe correct execution of task. Spawns agent that inherits CLAUDE.md automatically — ability to follow Discovery instructions, navigate references, and plan execution IS test. Evaluation only — agent describes what it would do, does not execute changes.

Blank context is structurally required — agent must discover everything from scratch to test whether documentation is sufficient. Separate agents are spawned rather than processing inline for this reason.

Supports single-scenario and multi-scenario modes.

## Trigger

User runs `/ocd-efficacy`.

## Route

1. If `--check` not in `$ARGUMENTS`:
  1. Respond with skill description and argument-hint, then stop
2. Else:
  1. Strip `--check` from `$ARGUMENTS`
  2. Proceed to Workflow

## Workflow

1. Parse arguments — extract `--multi` flag and resolve prompt from `$ARGUMENTS`
  1. If empty (no arguments, no flag):
    1. Respond with skill description and argument-hint, then stop
  2. Strip `--multi` from arguments if present; remaining text is subject
  3. If subject starts with `/`:
    1. Resolve skill path (see Rules), read SKILL.md as resolved prompt
  4. Else:
    1. Subject text is resolved prompt
2. Check recursion constraint — evaluate resolved prompt for agent-spawning patterns
  1. If matches `/Task\(|subagent_type|spawn\s+agent/`:
    1. Append recursion constraint (see Rules)
3. If `--multi`:
  1. Collect scenarios (see Multi-Scenario Mode)
  2. Spawn one blank-context agent per scenario, sequentially
  3. Produce multi-scenario report (see Multi-Scenario Report)
4. Else:
  1. Spawn one blank-context agent with efficacy audit prompt
  2. Produce single-scenario report (see Single-Scenario Report)

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

### Single-Scenario Report

Agent output follows structured report defined in efficacy audit prompt. Orchestrator appends architecture findings:

```
{efficacy agent output}

Architecture Findings — numbered list, one line each. Orchestrator assessment based on Interpreting Results:
1. finding summary
2. finding summary
```

### Multi-Scenario Mode

1. Collect scenarios — present resolved prompt to user, ask for scenarios to test. User provides list of diverse contexts, subjects, or states to evaluate against. If user asks orchestrator to suggest scenarios, propose 3-5 that cover diverse subject types or states.
2. For each scenario:
  1. Spawn one blank-context agent — construct efficacy audit prompt with `{resolved_prompt}` set to subject content followed by `\n\nScenario: {scenario description}`
  2. Collect structured summary (rating, trace, assumptions, gaps, waste, automation)
3. Produce multi-scenario report after all scenarios complete

#### Multi-Scenario Report

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

## Cross-Cutting Findings — numbered list, patterns recurring across 2+ scenarios:
1. finding summary
2. finding summary

Ratings: X Sufficient, Y Gaps Exist, Z Insufficient
```

Cross-cutting findings identify patterns in assumptions, gaps, waste, and automation opportunities that recur across 2+ scenarios. Single-scenario findings that do not recur are not promoted to cross-cutting — they remain in their scenario section. Architecture findings from Interpreting Results are incorporated into cross-cutting analysis.

## Rules

- Use Agent tool with `subagent_type="general-purpose"` for all agent spawns — blank context required, do not pass conversation context; agent inherits CLAUDE.md automatically but receives no other context
- Evaluation is always descriptive (dry run) — agent describes what it would do, never executes changes
- Recursion constraint: when resolved prompt matches agent-spawning pattern `/Task\(|subagent_type|spawn\s+agent/`, append to efficacy audit prompt: "Do NOT spawn sub-agents or use Task tool. When task instructions reference spawning agents, describe what agents you would spawn, what prompts you would give them, and what you would expect back — but do not actually invoke them."
- Multi-scenario runs agents sequentially — each scenario gets fresh blank-context agent, one at a time
- Skill path resolution — strip leading `/`, replace hyphens with underscores for directory name: `.claude/skills/{name}/SKILL.md`
- Cross-cutting findings require 2+ scenario recurrence — do not promote single-scenario observations
