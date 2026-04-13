---
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

Two complementary phases — static analysis and runtime verification — run concurrently, feeding the same finding list before triage.

**Static.** A single agent reads the skill's file set holding four concerns simultaneously — conformity against matched governance, execution correctness from cold, structural quality against domain best practices, and alignment with established patterns. All feed the same finding list per `_evaluation-workflow.md`. Splitting into independent passes creates convergence loops where each pass's fixes invalidate the next; the holistic reading eliminates that spiral.

**Runtime.** Per-route agents invoke the skill with specific argument combinations in worktree-isolated environments, comparing actual behavior against documented claims per `_runtime-evaluation.md`. Worktree isolation ensures state-modifying skills execute safely — branch isolation, push blocking, and automatic cleanup.

The skill executor's role is mechanical: extract exercisable argument combinations from the skill's Route section, dispatch all agents concurrently, then classify returned findings as Defects (auto-applied) or Observations (surfaced to user). The skill executor does not evaluate skill content. No agent sees the triage criteria — separation of evaluation from classification is load-bearing.

## Scope

Target is a single skill — its SKILL.md plus all files it references (component `_*.md` files, `references/` files, CLI scripts invoked by steps). scope_analyze follows cross-references to build the complete file set with governance metadata.

Accepted arguments:

- `--target` — required; skill name (`/navigator`) or path to SKILL.md

## Trigger

User runs `/evaluate-skill`

## Route

1. If not --target: Exit to user — respond with skill description and argument-hint
2. If {target} is a path ending with `/SKILL.md`:
    1. {skill-path} = {target}
3. Else if {target} starts with `/` and contains no spaces:
    1. Resolve skill path — skills_resolve: name={target} (strip leading `/`)
    2. If result contains error: Exit to user — report skill not found
    3. {skill-path} = resolved path
4. Else: Exit to user — respond with skill description and argument-hint
5. Verify working tree is clean — bash: `git status --porcelain`
    1. If output is non-empty: Exit to user — working tree must be clean before evaluation; run `/commit` first so applied changes have a clean diff
6. Dispatch Workflow

## Workflow

### Setup

> Gather inputs for agent dispatch — triage criteria, file scope, and exercisable argument combinations.

1. Read `.claude/conventions/ocd/evaluation-triage.md`
2. Discover scope — scope_analyze: paths=[{skill-path}]
3. {scope} = scope_analyze result
4. Read {skill-path} Route section to extract exercisable argument combinations
    1. For each branch in Route, determine the arguments that would reach it
    2. Skip branches that only exit to user with static messages — no runtime verification value
    3. For each remaining branch, note preconditions it requires (e.g., uncommitted changes, specific file state)
5. {arg-combinations} = extracted list; may be empty if all routes are no-ops

### Dispatch

> Static and runtime agents launch concurrently. Push blocking wraps all agents as a safety boundary for worktree-isolated runtime agents.

6. Block git push — bash: `git config remote.origin.pushurl "file:///dev/null"`
7. Dispatch agents:
    1. async Spawn agent with static evaluation({skill-path}, {scope}):
        1. Read `${CLAUDE_PLUGIN_ROOT}/skills/evaluate-skill/_evaluation-workflow.md`
        2. For each {file} in {scope} files (starting with {skill-path}):
            1. If {file} has governance entries in {scope}: read each governance file not already in context
            2. Read {file}
            3. Evaluate {file} per the evaluation workflow against its matched governance and all target files already in context
        3. Return:
            - Findings in the evaluation workflow's prescribed format
    2. For each {combo} in {arg-combinations}:
        1. async Spawn agent with runtime evaluation({combo}, {skill-path}) and isolation: "worktree":
            1. Read `${CLAUDE_PLUGIN_ROOT}/skills/evaluate-skill/_runtime-evaluation.md`
            2. Exercise skill with {combo} arguments per the runtime evaluation workflow
            3. Return:
                - Runtime findings in the runtime evaluation's prescribed format
8. {static-findings} = static agent return
9. {runtime-findings} = collected runtime agent returns; empty if {arg-combinations} was empty
10. Unblock git push — bash: `git config --unset remote.origin.pushurl`

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

Review all agent findings and present unified recommendations to the user. Cover what scope was evaluated (files and routes), what defects were applied, what observations need user judgment, and overall status. Preserve finding detail — the user needs specifics to act — but present as actionable recommendations, not a reformatted dump of agent output.

## Rules

- Do not evaluate skill content — extract argument combinations mechanically, dispatch agents, and triage returned findings
- scope_analyze provides the full file set with governance — no separate governance discovery step needed
- Single sequential static agent — conformity findings inform efficacy evaluation (shared context matters)
- Block push before agents spawn and unblock after all return
- Present observations with the agent's proposed fix verbatim — do not summarize or omit
- `/commit` precondition gives each evaluation a clean diff for auditing

## Error Handling

- If workflow errors between push block (step 6) and unblock (step 10): run `git config --unset remote.origin.pushurl` before surfacing the error
- If the unblock command itself fails: warn user that `remote.origin.pushurl` may still be set and provide the corrective command `git config --unset remote.origin.pushurl`
