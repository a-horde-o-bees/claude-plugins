---
name: ocd-conventions
description: Manage and enforce project conventions; reformats files to conform using deterministic pattern matching and per-file parallel agents
argument-hint: "--target <path | /skill-name | project | self | natural language goal> [--pattern <glob> ...] [--delegate]"
---

# /ocd-conventions

Manage and enforce project conventions. Convention CLI deterministically discovers applicable conventions per target, then parallel agents apply them with one agent per file. Deterministic discovery + non-deterministic application.

## Trigger

User runs `/ocd-conventions`

## Route

1. If not --target:
  1. EXIT — respond with skill description and argument-hint
2. If {target} is `self`:
  1. If --delegate:
    1. EXIT — self-evaluation is interactive and cannot be delegated
  2. {selected-workflow} = Self-Evaluation
  3. Go to step 12. Dispatch
3. Else if {target} is `project`:
  1. {target-directory} = `.` (project root)
4. Else if ({target} starts with `/` and contains no spaces) or ({target} is a path ending with `/SKILL.md`):
  1. If {target} starts with `/`:
    1. Resolve skill path — run navigator CLI `resolve-skill` with skill name (strip leading `/` from {target})
      ```
      python3 ${CLAUDE_PLUGIN_ROOT}/skills/navigator/scripts/navigator_cli.py resolve-skill <name>
      ```
    2. If exit code 1: EXIT — report skill not found
    3. {target-directory} = parent of resolved skill path
  2. Else:
    1. {target-directory} = parent directory of {target}
5. Else if {target} is file path:
  1. {target-file} = {target}
  2. Go to step 9. Deduplicate target list
6. Else if {target} is directory path:
  1. {target-directory} = {target}
7. Else:
  1. Interpret {target} as natural language goal — evaluate against available pipeline controls: target resolution (directory, skill, project), file enumeration (--pattern)
  2. Derive adjustments — translate into one or more execution passes; each pass is a set of resolved variables ({target-directory}, --pattern values) that exercises part of goal
  3. If adjustments conflict with other provided flags:
    1. Surface conflict and work with user to resolve
  4. Present proposed passes and ask user for confirmation via AskUserQuestion before proceeding
  5. For each confirmed pass:
    1. Assign derived variables ({target-directory}) for pass
    2. Execute steps 8-12 with assigned variables
8. Enumerate targets — run navigator CLI to get filtered file list
  ```bash
  python3 ${CLAUDE_PLUGIN_ROOT}/skills/navigator/scripts/navigator_cli.py list {target-directory} --exclude ".claude/*" [--pattern "..."]
  ```
  - If --pattern: For each --pattern, pass {pattern} to navigator CLI
  - {target-file} bypasses enumeration — file target from step 5 checks that path without exclusion
9. Deduplicate target list
10. {selected-workflow} = Conformity
11. Safeguard — check target count
  1. If target count exceeds 20:
    1. Report count and suggest narrowing via AskUserQuestion with options: proceed, narrow with --pattern, or specify more specific path
12. Dispatch {selected-workflow}
  - If --delegate: Workflow agent spawns in background

## Workflow: Conformity

1. Spawn coordinating agent with target file list and instructions:
  1. For each target file, spawn agent with {target-path} and instructions:
    1. Read `_conformity-instructions.md`
    2. Apply to {target-path}
    - async agent per target file
  2. Review changes — run `git diff` after all agents complete; review for correctness
  3. Report results — per-target summary of changes applied, criteria used, issues requiring user judgment; deduplicate criteria files across agents
2. Present coordinating agent report

### Report

- Agent reports follow format defined in `_conformity-instructions.md`
- Coordinating agent deduplicates criteria files across agents

## Workflow: Self-Evaluation

Evaluate rules and conventions against each other in dependency order. Report-only — present findings per level for user review, do not apply fixes. Files at each level are evaluated against criteria from all prior validated levels.

1. Get evaluation order — run conventions CLI `list-self` command
  ```
  python3 ${CLAUDE_PLUGIN_ROOT}/skills/conventions/scripts/conventions_cli.py list-self
  ```
  1. If error (cycle detected or missing dependency):
    1. Report error to user and stop
  - Output is levels (Level 0, Level 1, ...) with file paths
2. Present DAG overview to user via AskUserQuestion — show levels with file names, confirm before starting
3. Initialize criteria set — empty list
4. For each level (starting at Level 0):
  1. If criteria set is empty (Level 0):
    1. Evaluate files for internal consistency only — terminology, cross-references, completeness
  2. Else:
    1. Evaluate each file against all criteria in criteria set
    2. For each criterion, assess conformity with specific citations
    3. Evaluate internal consistency — terminology, cross-references, completeness
  3. Present findings for current level — per-file summary of conformity issues found
  4. Wait for user via AskUserQuestion with options: approve level, request changes
  5. When user approves level:
    1. Add all files from current level to criteria set
    2. Proceed to next level
5. After all levels complete — present summary of full evaluation

### Report

- Per-level: files evaluated, criteria used, issues found
- Per-file: conformity issues with specific rule/convention citations
- Summary: total levels, total files, total issues found

## Rules

- Do not pass conversation context to spawned agent — agent inherits CLAUDE.md automatically but receives no other context beyond workflow instructions
- One agent per target file — parallel execution gives each file full attention; agent reads `_conformity-instructions.md` and discovers its own criteria via conventions CLI
- Agent applies fixes directly in Conformity workflow — reformatting, not just reporting
- Orchestrator safeguards target count — reports and suggests narrowing when exceeding 20 files; waits for user confirmation before spawning
- Self-evaluation is report-only — present findings, do not apply fixes; user directs any changes after reviewing
- Agent preserves semantic meaning — changes are stylistic and structural, never altering what file communicates
- Files tagged `[fail: N lines]` in `list-matching` output auto-fail without processing — reported to user with line count
- Files tagged `[warn: N lines]` proceed with size noted — agent may need to use targeted reads for large files
- Line count thresholds are configurable in manifest.yaml `settings` section (`lines_warn_threshold`, `lines_fail_threshold`)
- All convention rules are required by default. Rules described as "recommended" or "optional" in convention text are reported but do not block.
- Natural language {target} evaluation occurs in Route as fallback after deterministic matches — orchestrator interprets goal, derives adjustments, and presents for user confirmation before proceeding
- When natural language adjustments conflict with other provided flags, orchestrator surfaces conflict and works with user to resolve — no implicit precedence
- Deterministic {target} values (`project`, `self`, paths, `/skill-name`) execute without interpretation or confirmation
- --delegate spawns background agent with Workflow and Rules — agents read component files at execution time; orchestration (Route) always runs in main conversation
- Self-evaluation does not support --delegate — interactive review between levels is structurally required
