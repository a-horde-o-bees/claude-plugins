---
name: audit-governance
description: Audit the rules and conventions governance chain foundations-first, one level at a time. A spawned agent audits each level; the skill executor classifies findings, applies defects, and exits to caller when observations need judgment. User selects which level to start at on each invocation; convergence is user-driven.
argument-hint: "--target project"
allowed-tools:
  - Read
  - Edit
  - Bash
  - mcp__plugin_ocd_navigator__*
---

# /audit-governance

Audit the governance dependency chain foundations-first, one level at a time. A spawned agent audits each level; the skill executor classifies findings per the triage criteria, applies defects, and exits to caller when observations need judgment. User selects which level to start at on each invocation; convergence is user-driven.

## Process Model

The skill walks the governance chain in dependency order starting from a level the user selects (default 0). Per-level gating stabilizes each level's fixes before deeper levels build on them. The agent's context accumulates across levels via `Continue:` so coherence checks can reference prior levels.

Observations at a level pause the run: the skill exits with the agent's findings so the user can apply or reject each. To resume, the user re-invokes the skill and selects the level to restart from — typically the lowest level they modified. Convergence is reached when a pass produces no further observations.

The skill directory carries two audit workflow variants — `_audit-workflow-A.md` (active) and `_audit-workflow-B.md` (alternative). Swap the active workflow by editing the `Call:` target in the Spawn step below.

## Scope

Full governance chain discovered via navigator's order command. Rules and conventions form a closed set with declared `governed_by` dependencies that navigator topologically sorts into levels.

Accepted arguments:

- `--target` — required; must be `project`

## Rules

- Convergence is user-driven — re-invoke after applying or rejecting observations and select the level to resume from; a pass is clean when no further observations surface
- Read triage criteria before dispatching agents — never pass triage criteria to agents
- Classify findings as Defect or Observation per triage criteria
- Apply defects directly to disk
- Present observations with the agent's proposed fix intact — do not summarize or omit
- Exit to caller when observations need user judgment

## Route

1. If not --target: Exit to caller — respond with skill description and argument-hint
2. If {target} is not `project`: Exit to caller — target must be `project`
3. Discover governance levels — bash: `CLAUDE_PROJECT_DIR=$(pwd) python3 ${CLAUDE_PLUGIN_ROOT}/run.py lib.governance order --json`
4. If result has dangling references:
    1. Present dangling references to user — which file declares each missing governor
    2. Exit to caller — fix offending `governed_by` frontmatter and re-invoke
5. {levels} = levels array from the result
6. Present levels to user — for each level, show the level number (0..N-1), the file count, and the full list of file paths at that level
7. Ask user which level to start at — AskUserQuestion with options 0..N-1; first option (level 0) is the default
8. {start-level} = user's selection
9. Dispatch Workflow

## Workflow

1. Read `.claude/conventions/ocd/audit-triage.md`
2. {current-level} = {start-level}
3. Spawn:
    1. Call: `${CLAUDE_PLUGIN_ROOT}/skills/audit-governance/_audit-workflow-A.md` ({level-files} = {levels}[{current-level}])
    2. Return:
        - Findings for this level
4. {agent-ref} = the spawned agent

### Process Level Response

> Defects are intent-preserving — the agent's cached context from prior levels remains valid after defect application. Observations may change what governance prescribes, so the run exits and a re-invocation spawns a fresh agent that reads the updated content.

5. {response} = latest return from {agent-ref}
6. Classify each finding in {response} per `audit-triage.md`
7. For each Defect: apply its proposed fix directly to disk
8. Present Report
9. If any Observations exist:
    1. Exit to caller — "Observations at level {current-level} need user judgment. Apply or reject each, then re-invoke `/ocd:audit-governance` and choose the level to resume from."
10. {current-level} = {current-level} + 1
11. If {current-level} >= count of {levels}: Break loop — all levels complete
12. Continue {agent-ref}:
    1. Call: `${CLAUDE_PLUGIN_ROOT}/skills/audit-governance/_audit-workflow-A.md` ({level-files} = {levels}[{current-level}])
    2. Return:
        - Findings for this level
13. Go to step 5. Process Level Response

### Report

- **Scope** — levels traversed with file counts per level
- **Defects applied** — grouped by file; each showing location, fix applied, and source finding
- **Observations** — each agent's proposed fix intact when present
- **Status** — `clean`, `defects applied`, or `observations outstanding at level N`
