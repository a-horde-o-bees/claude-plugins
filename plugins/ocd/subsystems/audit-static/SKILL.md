---
name: audit-static
description: Audit any path against its governance, best practices, and prior art through holistic static analysis. Produces findings classified as auto-applicable defects or observations requiring user judgment.
argument-hint: "--target <path | /plugin:skill>"
allowed-tools:
  - Read
  - Edit
  - Bash
  - mcp__plugin_ocd_navigator__*
---

# /audit-static

Audit any path against its governance, best practices, and prior art through holistic static analysis. Produces findings classified as auto-applicable defects or observations requiring user judgment.

## Process Model

A single agent reads the target file set holding four concerns simultaneously — conformity against matched governance, execution correctness from cold, structural quality against domain best practices, and alignment with established patterns. All feed the same finding list per `_audit-workflow.md`. Splitting into independent passes creates convergence loops where each pass's fixes invalidate the next; the holistic reading eliminates that spiral.

The skill executor's role is mechanical: discover the target's file set and matched governance, dispatch the audit agent, then classify returned findings as Defects (auto-applied) or Observations (surfaced to user). The skill executor does not audit content — it dispatches and triages.

## Scope

Target is a single path — a file, a directory, or a skill reference (slash-form like `/ocd:navigator` or direct path to a SKILL.md). scope_analyze follows cross-references from the target to build the complete file set with governance metadata.

Accepted arguments:

- `--target` — required; path to a file or directory, or a skill reference

## Rules

- Do not audit content directly — dispatch the audit agent and triage returned findings
- scope_analyze provides the full file set with governance per file — no separate governance discovery step
- Read triage criteria before dispatching the agent — never pass triage criteria to the agent
- Classify findings as Defect or Observation per triage criteria
- Apply defects directly to disk
- Present observations with the agent's proposed fix intact — do not summarize or omit
- Exit to user when observations need user judgment

## Route

1. If not --target: Exit to user: skill description and argument-hint
2. If {target} starts with `/`:
    1. {resolved} = bash: `python3 ${CLAUDE_PLUGIN_ROOT}/run.py subsystems.navigator resolve-skill {target}`
    2. If exit code 1: Exit to user: skill not found
    3. {audit-paths} = [{resolved}]
3. Else if {target} is an existing file or directory path:
    1. {audit-paths} = [{target}]
4. Else: Exit to user: {target} not recognized as a skill reference or filesystem path
5. Dispatch Workflow

## Workflow

### Setup

> Gather inputs for agent dispatch — triage criteria and file scope.

1. Read `.claude/conventions/ocd/audit-triage.md`
2. Discover scope — scope_analyze: paths={audit-paths}
3. {scope} = scope_analyze result; structure: `{files: [{path, governance: [convention paths], references: [paths], referenced_by: [paths]}], governance_index: {convention path: [files governed]}, total_files}`
4. If {scope}.total_files is 0: Exit to user: {target} resolved but produced an empty file set; the path or skill may not exist or contain auditable content

### Dispatch

> A single agent holds all four concerns in one read pass.

5. Spawn:
    1. Call: `${CLAUDE_PLUGIN_ROOT}/subsystems/audit-static/_audit-workflow.md` ({scope} = {scope})
    2. Return to caller:
        - Findings in the audit workflow's prescribed format
6. {findings} = returned findings

### Triage

> Defects are deterministic and intent-preserving — safe to auto-apply without changing what the target communicates or how it controls execution. Observations require user judgment before proceeding.

7. Classify each finding in {findings} as Defect or Observation per `audit-triage.md`
8. For each Defect: apply its proposed fix directly to disk
9. {applied-defects} = list of applied defects
10. Present Report
11. If any Observations exist in {findings}:
    1. Exit to user: Observations need user judgment. Apply or reject each, then re-invoke `/ocd:audit-static` to verify.

### Report

- **Scope** — files audited and the governance loaded for each
- **Defects applied** — fixes the skill executor applied directly, preserving enough detail to audit
- **Observations** — findings needing user judgment, with the agent's proposed fix intact
- **Status** — terminal outcome (clean, defects applied, or observations outstanding)
