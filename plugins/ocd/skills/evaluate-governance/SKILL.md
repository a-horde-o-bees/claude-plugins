---
name: evaluate-governance
description: |
  Evaluate the rules and conventions governance chain level-by-level. A spawned agent walks foundations-first and reports findings with proposed fixes; the orchestrator classifies each finding against the shared triage criteria, auto-applies defects, and exits to user when observations need judgment. Convergence across waves is user-driven.
argument-hint: "--target project"
allowed-tools:
  - Read
  - Edit
  - Bash
  - mcp__plugin_ocd_navigator__*
---

# /evaluate-governance

Evaluate the governance dependency chain in a single holistic pass, gated by the orchestrator between levels. A spawned agent walks the chain foundations-first and reports findings after each level. The orchestrator classifies findings against the shared triage criteria, auto-applies defects to disk, and exits to user when any observation at the current level needs judgment — so foundation changes are picked up in a fresh session before the next wave.

## Lenses

This skill does not apply evaluation lenses as separate passes. A single agent reads the chain in dependency order with three concerns held simultaneously per `_evaluation-criteria.md`: active conformance against loaded governors, cold-reader friction, and coherence with what prior levels established. Splitting these into independent passes creates convergence loops where each pass's fixes invalidate the next; the holistic reading eliminates that spiral.

## Scope

Full governance chain discovered via `governance_order`. Rules and conventions are a known, closed set — navigator maps every entry with its declared `governed_by` dependencies and produces topologically grouped levels. No file-path targeting.

Accepted arguments:

- `--target` — required; must be `project`

## Protocol

The orchestrator receives the level-grouped governance ordering from `governance_order` and dispatches a single long-running spawned agent that processes the chain one level at a time. After each level:

1. The agent returns findings for that level in report-only form — no classification, no fixes
2. The orchestrator reads `evaluation-triage.md` once and classifies each finding as Defect or Observation
3. Defects are auto-applied directly to disk; because Defects are deterministic and intent-preserving by definition, the spawned agent's cached content from prior levels remains semantically valid for the next level's evaluation
4. If any Observations exist at the current level, the orchestrator exits to user with the observations surfaced. The user applies or rejects them, then re-invokes the skill in a fresh session so Claude Code's session-loaded governance reflects the corrected chain
5. Otherwise the orchestrator sends the agent a continuation message for the next level and repeats

This per-level gating prevents the agent from spending tokens on later levels against a foundation that is about to change. On a clean traversal of all levels, the orchestrator presents a summary of applied Defects and exits normally.

## Inputs

- **Triage criteria** — `.claude/conventions/ocd/evaluation-triage.md`. Read by the orchestrator once at the start of Workflow; the spawned agent never reads this file. Governs the Defect / Observation classification the orchestrator applies to every returned finding.
- **Evaluation criteria** — `${CLAUDE_PLUGIN_ROOT}/skills/evaluate-governance/_evaluation-criteria.md`. Read by the spawned agent at the start of its execution. Defines the reading disposition, what to surface, graph-anomaly semantics, and the finding return format.

## Trigger

User runs `/evaluate-governance --target project`.

## Route

1. If not --target: Exit to user — respond with skill description and argument-hint
2. If {target} is not `project`: Exit to user — target must be `project`
3. Verify working tree is clean — bash: `git status --porcelain`
    1. If output is non-empty: Exit to user — working tree must be clean before evaluation; run `/commit` first so each convergence wave has a clean before/after diff
4. Discover governance levels — bash: `CLAUDE_PROJECT_DIR=$(pwd) python3 ${CLAUDE_PLUGIN_ROOT}/run.py lib.governance.cli order --json`
5. If result has any dangling references:
    1. Present the dangling references to the user — which file declares each missing governor
    2. Exit to user — fix the offending `governed_by` frontmatter and re-invoke; the evaluation cannot proceed against a graph with unresolved references
6. {levels} = levels array from the result
7. Present the plan to user — levels count, total files per level, prompt to confirm
8. Dispatch Workflow

## Workflow

1. Read `.claude/conventions/ocd/evaluation-triage.md`
2. {current-level} = 0
3. {applied-defects} = empty list
4. {level-files} = paths from {levels}[{current-level}]
5. Spawn agent with governance evaluation({current-level}, {level-files}):
    1. Read `${CLAUDE_PLUGIN_ROOT}/skills/evaluate-governance/_evaluation-criteria.md`
    2. For each {file} in the files handed in the current message:
        1. Read {file}
        2. Evaluate {file} per `_evaluation-criteria.md` against everything already in context
        3. If a graph anomaly surfaces: Return — anomaly description and findings accumulated so far
    3. Return — findings for the processed level in the criteria's format
    4. Await continuation. On each resume, the orchestrator hands a new level number and file list; repeat from step 2
6. {agent-ref} = reference to the spawned agent for later continuation
7. Process level response. Label:
    1. {response} = latest return from {agent-ref}
    2. If {response} describes a graph anomaly:
        1. Present the anomaly and any partial findings to the user
        2. Work with the user to fix the offending `governed_by` frontmatter
        3. Re-query governance levels — bash: `CLAUDE_PROJECT_DIR=$(pwd) python3 ${CLAUDE_PLUGIN_ROOT}/run.py lib.governance.cli order --json`; verify the correction is reflected
        4. Go to step 2. Reset state and restart with the corrected {levels}
    3. Classify each finding in {response} as Defect or Observation per `evaluation-triage.md`
    4. For each Defect: apply its proposed fix directly to disk
    5. {applied-defects} = {applied-defects} + newly applied defects
    6. If any Observations exist in {response}:
        1. Present applied Defects and outstanding Observations to the user, grouped by file, each with full context from the finding
        2. Exit to user — "Observations at level {current-level} need user judgment. Apply or reject each, then re-invoke `/evaluate-governance` in a fresh session so the corrected governance loads before the next wave."
    7. {current-level} = {current-level} + 1
    8. If {current-level} >= count of {levels}:
        1. Break loop — all levels complete
    9. {level-files} = paths from {levels}[{current-level}]
    10. Continue {agent-ref} with the next level — send a message carrying the new level number and file list; await the new return
    11. Go to step 7. Process level response — read the new response and repeat
8. Present Report

### Report

1. **Scope** — levels traversed with file counts per level
2. **Applied Defects** — grouped by file; each entry shows location, the fix applied, and the source finding
3. **Status** — one of:
    - `clean` — all levels processed, no findings
    - `defects applied` — all levels processed, Defects applied, no Observations outstanding
    - `observations outstanding at level N` — evaluation exited at level N pending user judgment (report is surfaced mid-workflow, not in this final block)
    - `restarted after anomaly` — one or more graph-anomaly restarts occurred before the successful run; applied Defects are from the final run only

## Rules

- The spawned agent is report-only. It does not triage findings, classify them, or apply fixes. The orchestrator owns all three concerns.
- The orchestrator reads `evaluation-triage.md` at the start of Workflow. The spawned agent never reads the triage file — classification is the orchestrator's job.
- Defects are deterministic and intent-preserving by definition. Auto-applying them cannot invalidate findings on deeper levels, so the spawned agent's cached content from prior levels remains semantically valid for the next level's evaluation after the orchestrator applies fixes.
- Observations may change what governance files prescribe. After any Observation is applied to a governance file, Claude Code's session-cached rules are stale — a fresh session is required before re-evaluation can see the corrected chain. The orchestrator exits to user whenever Observations appear at the current level to enforce this.
- Graph anomalies stop traversal immediately. The orchestrator handles them inline with the user, corrects the frontmatter, re-queries `governance_order` to verify, and restarts the workflow from Level 0. Partial findings accumulated before the anomaly are presented for user reference but not auto-applied — the frontmatter correction may have changed what counts as a valid finding.
- `/commit` precondition gives each wave a clean before/after diff so the user can audit exactly what each convergence pass changed.
- Convergence across multiple waves is user-driven. The skill is invoked repeatedly in fresh sessions until a pass produces no governance-file changes.
