---
description: Evaluate the rules and conventions governance chain foundations-first, one level at a time. A spawned agent evaluates each level; the skill executor classifies findings, applies defects, and exits to caller when observations need judgment. Convergence across waves is user-driven.
argument-hint: "--target project"
allowed-tools:
  - Read
  - Edit
  - Bash
  - mcp__plugin_ocd_navigator__*
---

# /evaluate-governance

Evaluate the governance dependency chain foundations-first, one level at a time. A spawned agent evaluates each level; the skill executor classifies findings per the triage criteria, applies defects, and exits to caller when observations need judgment. Convergence across waves is user-driven.

## Process Model

The skill walks the governance chain in dependency order, one level at a time. Per-level gating stabilizes each level's fixes before deeper levels build on them. The agent's context accumulates across levels via `Continue:` so coherence checks can reference prior levels.

## Scope

Full governance chain discovered via navigator's order command. Rules and conventions form a closed set with declared `governed_by` dependencies that navigator topologically sorts into levels.

Accepted arguments:

- `--target` — required; must be `project`

## Rules

- `/commit` precondition gives each wave a clean before/after diff for auditing
- Convergence across waves is user-driven — the skill is invoked in fresh sessions until a pass produces no governance-file changes

## Route

1. If not --target: Exit to caller — respond with skill description and argument-hint
2. If {target} is not `project`: Exit to caller — target must be `project`
3. Verify working tree is clean — bash: `git status --porcelain`
    1. If output is non-empty: Exit to caller — run `/commit` first so each wave has a clean before/after diff
4. Discover governance levels — bash: `CLAUDE_PROJECT_DIR=$(pwd) python3 ${CLAUDE_PLUGIN_ROOT}/run.py lib.governance.cli order --json`
5. If result has dangling references:
    1. Present dangling references to user — which file declares each missing governor
    2. Exit to caller — fix offending `governed_by` frontmatter and re-invoke
6. {levels} = levels array from the result
7. Present the plan — levels count, files per level — confirm with user
8. Dispatch Workflow

## Workflow

1. Read `.claude/conventions/ocd/evaluation-triage.md`
2. {current-level} = 0
3. Spawn:
    1. Call: `${CLAUDE_PLUGIN_ROOT}/skills/evaluate-governance/_evaluation-workflow.md` ({level-files} = {levels}[{current-level}])
    2. Return:
        - Findings for this level
4. {agent-ref} = the spawned agent

### Process Level Response

> Defects are intent-preserving — the agent's cached context from prior levels remains valid after defect application. Observations may change what governance prescribes, so a fresh session is required before re-evaluation.

5. {response} = latest return from {agent-ref}
6. Classify each finding in {response} per `evaluation-triage.md`
7. For each Defect: apply its proposed fix directly to disk
8. Present Report
9. If any Observations exist:
    1. Exit to caller — "Observations at level {current-level} need user judgment. Apply or reject each, then re-invoke `/evaluate-governance` in a fresh session."
10. {current-level} = {current-level} + 1
11. If {current-level} >= count of {levels}: Break loop — all levels complete
12. Continue {agent-ref}:
    1. Call: `${CLAUDE_PLUGIN_ROOT}/skills/evaluate-governance/_evaluation-workflow.md` ({level-files} = {levels}[{current-level}])
    2. Return:
        - Findings for this level
13. Go to step 5. Process Level Response

### Report

- **Scope** — levels traversed with file counts per level
- **Defects applied** — grouped by file; each showing location, fix applied, and source finding
- **Observations** — each agent's proposed fix intact when present
- **Status** — `clean`, `defects applied`, `observations outstanding at level N`, or `restarted after anomaly`

## Error Handling

- If governance order command fails: surface the error and the command to the user for manual debugging
