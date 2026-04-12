---
name: evaluate-skill
description: Evaluate a skill's files in a single holistic pass. A spawned agent reads the skill and all referenced files against domain-specific evaluation criteria and reports findings; the orchestrator classifies each finding against the shared triage criteria, auto-applies defects, and exits to user when observations need judgment.
argument-hint: "--target </skill-name | path/to/SKILL.md>"
allowed-tools:
  - Read
  - Edit
  - Bash
  - mcp__plugin_ocd_navigator__*
---

# /evaluate-skill

Run against any skill to check conformity with governance conventions, execution correctness, structural quality, and alignment with established patterns. Produces findings classified as auto-applicable defects or observations requiring user judgment.

## Process Model

A single agent reads the skill's file set holding four concerns simultaneously — conformity against matched governance, execution correctness from cold, structural quality against domain best practices, and alignment with established patterns. All feed the same finding list per `_evaluation-workflow.md`. Splitting into independent passes creates convergence loops where each pass's fixes invalidate the next; the holistic reading eliminates that spiral.

The orchestrator reads triage criteria once, dispatches the agent, then classifies returned findings as Defects (auto-applied) or Observations (surfaced to user). The agent never sees the triage criteria — separation of evaluation from classification is load-bearing.

## Scope

Target is a single skill — its SKILL.md plus all files it references (component `_*.md` files, `references/` files, CLI scripts invoked by steps). scope_analyze follows cross-references to build the complete file set with governance metadata.

Accepted arguments:

- `--target` — required; skill name (`/navigator`) or path to SKILL.md

## Trigger

User runs `/evaluate-skill`

## Route

1. If not --target: Exit to user — respond with skill description and argument-hint
2. If {target} starts with `/` and contains no spaces:
    1. Resolve skill path — skills_resolve: name={target} (strip leading `/`)
    2. If result contains error: Exit to user — report skill not found
    3. {skill-path} = resolved path
3. Else if {target} is a path ending with `/SKILL.md`:
    1. {skill-path} = {target}
4. Else: Exit to user — target must be /skill-name or path to SKILL.md
5. Verify working tree is clean — bash: `git status --porcelain`
    1. If output is non-empty: Exit to user — working tree must be clean before evaluation; run `/commit` first so applied changes have a clean diff
6. Dispatch Workflow

## Workflow

1. Read `.claude/conventions/ocd/evaluation-triage.md`
2. Discover scope — scope_analyze: paths=[{skill-path}]
3. {scope} = scope_analyze result
4. Spawn agent with skill evaluation({skill-path}, {scope}):
    1. Read `${CLAUDE_PLUGIN_ROOT}/skills/evaluate-skill/_evaluation-workflow.md`
    2. For each {file} in {scope}.files (starting with {skill-path}):
        1. If {file} has governance entries in {scope}: read each governance file not already in context
        2. Read {file}
        3. Evaluate {file} per `_evaluation-workflow.md` against everything already in context
    3. Return:
        - Findings in the evaluation criteria's format
5. {findings} = returned findings

> Defects are deterministic and intent-preserving — safe to auto-apply without changing what the skill communicates or how it controls execution. Observations require user judgment before proceeding.

6. Classify each finding in {findings} as Defect or Observation per `evaluation-triage.md`
7. For each Defect: apply its proposed fix directly to disk
8. {applied-defects} = list of applied defects
9. If any Observations exist in {findings}:
    1. Present applied Defects grouped by file
    2. Present each Observation as-is from the agent's finding — location, what is wrong, why, and proposed fix
    3. Exit to user — "Observations need user judgment. Apply or reject each, then re-invoke `/evaluate-skill` to verify."
10. Present Report

### Report

1. **Scope** — files evaluated
2. **Applied Defects** — grouped by file; each entry shows location, the fix applied, and the source finding
3. **Observations** — presented as-is from agent findings when present; surfaced interactively before this report (see step 9)
4. **Status** — one of:
    - `clean` — all files processed, no findings
    - `defects applied` — all files processed, Defects applied, no Observations outstanding
    - `observations outstanding` — evaluation exited pending user judgment (report is surfaced mid-workflow, not in this final block)

## Rules

- The spawned agent is report-only — it does not triage findings, classify them, or apply fixes
- The orchestrator reads `evaluation-triage.md` at the start of Workflow; the spawned agent never reads the triage file
- scope_analyze provides the full file set with governance — the agent does not need separate governance discovery
- Conformity evaluates each file against its dynamically matched governance, not hardcoded convention names
- Efficacy traces execution flow; does not actually execute steps or spawn subagents
- Single sequential agent — conformity findings inform efficacy evaluation (shared context matters)
- `/commit` precondition gives each evaluation a clean diff so the user can audit exactly what was changed
