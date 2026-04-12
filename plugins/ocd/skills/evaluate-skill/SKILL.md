---
name: evaluate-skill
description: Evaluate a skill through static analysis of its files against governance and runtime exercise of its pathways in isolated worktrees. Produces findings classified as auto-applicable defects or observations requiring user judgment.
argument-hint: "--target </skill-name | path/to/SKILL.md>"
allowed-tools:
  - Read
  - Edit
  - Bash
  - mcp__plugin_ocd_navigator__*
---

# /evaluate-skill

Evaluate a skill through static analysis of its files against governance and runtime exercise of its pathways in isolated worktrees. Produces findings classified as auto-applicable defects or observations requiring user judgment.

## Process Model

Two complementary phases — static analysis followed by runtime verification — feed the same finding list before triage.

**Static.** A single agent reads the skill's file set holding four concerns simultaneously — conformity against matched governance, execution correctness from cold, structural quality against domain best practices, and alignment with established patterns. All feed the same finding list per `_evaluation-workflow.md`. Splitting into independent passes creates convergence loops where each pass's fixes invalidate the next; the holistic reading eliminates that spiral.

**Runtime.** The orchestrator traces the skill's routes to identify exercisable pathways — routes with verifiable outcomes (CLI commands, file modifications, observable output). For each exercisable route, a worktree-isolated agent invokes the skill with the arguments for that path and compares actual behavior against documented claims per `_runtime-evaluation.md`. Worktree isolation ensures state-modifying skills execute safely — branch isolation, push blocking, and automatic cleanup.

The orchestrator reads triage criteria once, dispatches both phases, then classifies all returned findings as Defects (auto-applied) or Observations (surfaced to user). No agent sees the triage criteria — separation of evaluation from classification is load-bearing.

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
4. Else: Exit to user — respond with skill description and argument-hint
5. Verify working tree is clean — bash: `git status --porcelain`
    1. If output is non-empty: Exit to user — working tree must be clean before evaluation; run `/commit` first so applied changes have a clean diff
6. Dispatch Workflow

## Workflow

### Static Phase

> Catches governance conformity, PFN correctness, structural quality, and prior art alignment through file reading alone — cheap and comprehensive for text-level issues.

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
5. {static-findings} = returned findings

### Runtime Phase

> Exercises actual skill pathways in isolated worktrees — catches gaps between what documentation claims and what actually happens at runtime.

6. Read {skill-path} to trace the skill's Route and Workflow sections
7. Identify exercisable routes — routes with CLI commands, file modifications, or verifiable output
    1. For each route, determine the arguments needed to trigger that path
    2. Determine preconditions each route requires (e.g., uncommitted changes, specific file state)
    3. Skip routes that only exit to user with static messages — no runtime verification value
    4. If no exercisable routes: skip to step 11
8. For each {route} in exercisable routes:
    1. Spawn agent with runtime evaluation({route}, {skill-path}) and isolation: "worktree":
        1. Read `${CLAUDE_PLUGIN_ROOT}/skills/evaluate-skill/_runtime-evaluation.md`
        2. Exercise skill {route}.name with arguments {route}.arguments against {skill-path} per the runtime evaluation workflow
        3. Return:
            - Runtime findings
    - async agent per route
9. Collect runtime findings from all route agents
10. {runtime-findings} = collected findings

### Triage

> Defects are deterministic and intent-preserving — safe to auto-apply without changing what the skill communicates or how it controls execution. Observations require user judgment before proceeding.

11. {findings} = {static-findings} + {runtime-findings}
12. Classify each finding in {findings} as Defect or Observation per `evaluation-triage.md`
13. For each Defect: apply its proposed fix directly to disk
14. {applied-defects} = list of applied defects
15. If any Observations exist in {findings}:
    1. Present applied Defects grouped by file
    2. Present each Observation as-is from the agent's finding — file path, location, what is wrong, why, and proposed fix
    3. Exit to user — "Observations need user judgment. Apply or reject each, then re-invoke `/evaluate-skill` to verify."
16. Present Report

### Report

1. **Scope** — files evaluated (static) and routes exercised (runtime)
2. **Applied Defects** — grouped by file; each entry shows location, the fix applied, and the source finding
3. **Observations** — presented as-is from agent findings when present; surfaced interactively before this report (see step 15)
4. **Status** — one of:
    - `clean` — all files processed, all exercisable routes verified, no findings
    - `defects applied` — all files processed, Defects applied, no Observations outstanding
    - `observations outstanding` — evaluation exited pending user judgment (report is surfaced mid-workflow, not in this final block)

## Rules

- All spawned agents are report-only — they do not triage findings, classify them, or apply fixes
- The orchestrator reads `evaluation-triage.md` at the start of Workflow; no spawned agent reads the triage file
- scope_analyze provides the full file set with governance — the static agent does not need separate governance discovery
- Conformity evaluates each file against its dynamically matched governance, not hardcoded convention names
- Efficacy traces execution flow; does not actually execute steps or spawn subagents
- Single sequential static agent — conformity findings inform efficacy evaluation (shared context matters)
- Runtime agents invoke the skill via the Skill tool — not by manually executing workflow steps
- Runtime agents block git push as their first step; push failures are expected safety behavior
- Runtime agents execute `Spawn agent with:` steps themselves — Agent tool is unavailable in worktrees
- Observations presented to the user include the agent's proposed fix verbatim — the proposed fix is the actionable recommendation the user evaluates; do not summarize or omit it
- `/commit` precondition gives each evaluation a clean diff so the user can audit exactly what was changed
