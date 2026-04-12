---
name: evaluate-skill
description: |
  Evaluate a skill's files in a single holistic pass. A spawned agent reads the skill and all referenced files against domain-specific evaluation criteria and reports findings; the orchestrator classifies each finding against the shared triage criteria, auto-applies defects, and exits to user when observations need judgment.
argument-hint: "--target </skill-name | path/to/SKILL.md>"
allowed-tools:
  - Read
  - Edit
  - Bash
  - mcp__plugin_ocd_navigator__*
---

# /evaluate-skill

Evaluate a skill's SKILL.md and all referenced files in a single holistic pass. A spawned agent reads the full file set holding conformity, efficacy, quality, and prior art concerns simultaneously — not as separate passes. The orchestrator classifies returned findings against the shared triage criteria, auto-applies defects to disk, and exits to user when observations need judgment.

## Lenses

This skill does not apply evaluation concerns as separate passes. A single agent reads the skill's file set and evaluates each file against every concern simultaneously per `_evaluation-criteria.md`: conformity against matched governance, execution correctness from cold, structural quality against domain best practices, and alignment with established patterns. Splitting these into independent passes creates convergence loops where each pass's fixes invalidate the next; the holistic reading eliminates that spiral.

## Scope

Target is a single skill — its SKILL.md plus all files it references (component `_*.md` files, `references/` files, CLI scripts invoked by steps). scope_analyze follows cross-references to build the complete file set with governance metadata.

Accepted arguments:

- `--target` — required; skill name (`/navigator`) or path to SKILL.md

## Protocol

The orchestrator receives the scoped file set from `scope_analyze` and dispatches a single spawned agent over the whole set. The agent reads `_evaluation-criteria.md`, then reads every file while holding all concerns simultaneously, and returns findings in report-only form.

After the agent returns:

1. The orchestrator classifies each finding against `evaluation-triage.md`
2. Defects are auto-applied directly to disk
3. If any Observations exist, the orchestrator exits to user with applied Defects and outstanding Observations surfaced — the user applies or rejects each Observation, then re-invokes to verify
4. If no Observations, the orchestrator presents a final report

## Inputs

- **Triage criteria** — `.claude/conventions/ocd/evaluation-triage.md`. Read by the orchestrator once at the start of Workflow; the spawned agent never reads this file. Governs the Defect / Observation classification the orchestrator applies to every returned finding.
- **Evaluation criteria** — `${CLAUDE_PLUGIN_ROOT}/skills/evaluate-skill/_evaluation-criteria.md`. Read by the spawned agent at the start of its execution. Defines the reading disposition, what to surface, and the finding return format.

## Trigger

User runs `/evaluate-skill`

## Route

1. If not --target: Exit to user — respond with skill description and argument-hint
2. If ({target} starts with `/` and contains no spaces) or ({target} is a path ending with `/SKILL.md`):
    1. If {target} starts with `/`:
        1. Resolve skill path — skills_resolve: name={target} (strip leading `/`)
        2. If error: Exit to user — report skill not found
    2. {skill-path} = resolved path or {target}
3. Else: Exit to user — target must be /skill-name or path to SKILL.md
4. {target-directory} = parent of {skill-path}
5. Verify working tree is clean — bash: `git status --porcelain`
    1. If output is non-empty: Exit to user — working tree must be clean before evaluation; run `/commit` first so applied changes have a clean diff
6. Dispatch Workflow

## Workflow

1. Read `.claude/conventions/ocd/evaluation-triage.md`
2. Discover scope — scope_analyze: paths=[{skill-path}]
3. {scope} = scope_analyze result (files with sizes, governance, references)
4. Spawn agent with skill evaluation({skill-path}, {scope}):
    1. Read `${CLAUDE_PLUGIN_ROOT}/skills/evaluate-skill/_evaluation-criteria.md`
    2. For each {file} in {scope}.files (starting with {skill-path}):
        1. If {file} has governance entries in {scope}: read each governance file not already in context
        2. Read {file}
        3. Evaluate {file} per `_evaluation-criteria.md` against everything already in context
    3. Return — findings in the criteria's format
5. {findings} = returned findings
6. Classify each finding in {findings} as Defect or Observation per `evaluation-triage.md`
7. For each Defect: apply its proposed fix directly to disk
8. {applied-defects} = list of applied defects
9. If any Observations exist in {findings}:
    1. Present applied Defects and outstanding Observations to the user, grouped by file. Present each Observation as-is from the agent's finding — location, what is wrong, why, and proposed fix. Do not summarize or strip content; the user needs the full finding to make a judgment call
    2. Exit to user — "Observations need user judgment. Apply or reject each, then re-invoke `/evaluate-skill` to verify."
10. Present Report

### Report

1. **Scope** — files evaluated
2. **Applied Defects** — grouped by file; each entry shows location, the fix applied, and the source finding
3. **Status** — one of:
    - `clean` — all files processed, no findings
    - `defects applied` — all files processed, Defects applied, no Observations outstanding
    - `observations outstanding` — evaluation exited pending user judgment (report is surfaced mid-workflow, not in this final block)

## Rules

- The spawned agent is report-only. It does not triage findings, classify them, or apply fixes. The orchestrator owns all three concerns.
- The orchestrator reads `evaluation-triage.md` at the start of Workflow. The spawned agent never reads the triage file — classification is the orchestrator's job.
- Defects are deterministic and intent-preserving by definition. Auto-applying them does not change what the skill communicates or how it controls execution.
- Observations may require user judgment. The orchestrator exits to user whenever Observations appear so the user can evaluate each one.
- scope_analyze provides the full file set with governance — the agent does not need separate governance discovery.
- Conformity evaluates each file against its dynamically matched governance, not hardcoded convention names.
- Efficacy traces execution flow; does not actually execute steps or spawn subagents.
- Quality criteria are domain-specific to skills — see `_evaluation-criteria.md`.
- Prior Art draws on the agent's training knowledge of standard patterns.
- Single sequential agent — conformity findings inform efficacy evaluation (shared context matters).
- `/commit` precondition gives each evaluation a clean diff so the user can audit exactly what was changed.
