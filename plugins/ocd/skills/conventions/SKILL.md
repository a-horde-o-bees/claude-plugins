---
name: ocd-conventions
description: Manage and enforce project conventions; reformats files to conform using deterministic pattern matching and per-file parallel agents
argument-hint: "--target <path | /skill-name | project | self | natural language goal> [--pattern <glob> ...] [--auto] [--delegate]"
---

# /ocd-conventions

Manage and enforce project conventions. Convention CLI deterministically discovers applicable conventions per target, then parallel agents apply them with one agent per file. Deterministic discovery + non-deterministic application. `--auto` wraps Conformity in convergence loop per skill-md convention.

## Trigger

User runs `/ocd-conventions`

## Route

1. If not --target: Exit to user — respond with skill description and argument-hint
2. If {target} is `self`:
    1. If --auto: Exit to user — self-evaluation does not support --auto
    2. If --delegate: Exit to user — self-evaluation is interactive and cannot be delegated
    3. {selected-workflow} = Self-Evaluation
    4. Go to step 11. Dispatch
3. Else if {target} is `project`:
    1. {target-directory} = `.` (project root)
4. Else if ({target} starts with `/` and contains no spaces) or ({target} is a path ending with `/SKILL.md`):
    1. If {target} starts with `/`:
        1. Resolve skill path — run navigator CLI `resolve-skill` with skill name (strip leading `/` from {target})
            ```
            python3 ${CLAUDE_PLUGIN_ROOT}/skills/navigator/scripts/navigator_cli.py resolve-skill <name>
            ```
        2. If exit code 1: Exit to user — report skill not found
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
    5. For each {pass} in {confirmed-passes}:
        1. Assign derived variables ({target-directory}) for pass
        2. Execute steps 8-10 with assigned variables
8. Enumerate targets — run navigator CLI to get filtered file list
    ```bash
    python3 ${CLAUDE_PLUGIN_ROOT}/skills/navigator/scripts/navigator_cli.py list {target-directory} --exclude ".claude/*" [--pattern "..."]
    ```
    - If --pattern: For each --pattern, pass {pattern} to navigator CLI
    - {target-file} bypasses enumeration — file target from step 5 checks that path without exclusion
9. Deduplicate target list
10. {selected-workflow} = Conformity
    1. Safeguard — if target count exceeds 20: report count and suggest narrowing via AskUserQuestion with options: proceed, narrow with --pattern, or specify more specific path
11. Dispatch {selected-workflow}
    - If --auto: wrap in convergence loop per skill-md convention
    - If --delegate: agent spawn runs in background

## Workflow: Conformity

1. Spawn agent with coordination:
    1. For each {target-file} in {target-files}:
        1. Spawn agent with conformity({target-file}):
            1. Read `_conformity-instructions.md`
            2. Apply to {target-file}
            3. Return:
                - Changes applied
                - Criteria used
                - Issues requiring user judgment
        - async agent per target file
    2. Review changes — run `git diff` after all agents complete; review for correctness
    3. Return:
        - Per-target summary; deduplicate criteria files across agents
2. Present coordinating agent report

### Report

- Agent reports follow format defined in `_conformity-instructions.md`
- Coordinating agent deduplicates criteria files across agents

## Workflow: Self-Evaluation

Evaluate rules and conventions against each other in dependency order. Per level: detect cross-file conflicts for user resolution, then dispatch Conformity with self-evaluation constraints for structural fixes. Rule file changes require session restart between levels.

1. Get evaluation order — run conventions CLI `list-self` command
    ```
    python3 ${CLAUDE_PLUGIN_ROOT}/skills/conventions/scripts/conventions_cli.py list-self
    ```
    1. If error (cycle detected or missing dependency):
        1. Report error to user and stop
    - Output is levels (Level 0, Level 1, ...) with file paths
2. Present DAG overview to user via AskUserQuestion — show levels with file names, confirm before starting
3. For each {level} in {levels}:
    1. Spawn agent with conflict detection:
        1. Read all files at current level and all files from prior levels
        2. Identify semantic conflicts:
            - Horizontal — files at current level make contradictory or incompatible claims about same topic
            - Vertical — files at current level contradict guidance in files from prior levels
            - Scope: semantic content only; structural and formatting differences are handled by Conformity
        3. Return:
            - Conflicts with specific citations from both sides
    2. If conflicts found:
        1. Present conflicts to user
        2. User resolves conflicts with orchestrator assistance
    3. Dispatch Conformity workflow with level's files as target list
        - Agents read `_self-eval-conformity-instructions.md` instead of `_conformity-instructions.md`
        - Scope: structural, notation, and formatting fixes; semantic differences from criteria are observations for user judgment
    4. Present level findings — applied fixes and observations requiring user judgment
    5. Wait for user via AskUserQuestion — approve level or request changes
    6. When user approves level:
        1. If any `.claude/rules/` files modified during this level:
            1. Exit to user — instruct user to restart session (`/exit` then `claude --continue`) and re-invoke `/ocd-conventions --target self`
        2. Else: proceed to next level
4. After all levels complete — present summary of full evaluation

### Report

- Per-level: conflicts detected, conflicts resolved, conformity fixes applied, observations for user judgment
- Per-file: fixes applied with rationale, observations requiring user judgment
- Summary: total levels, total files, conflicts found, fixes applied

## Rules

- Do not pass conversation context to spawned agent — agent inherits CLAUDE.md automatically but receives no other context beyond workflow instructions
- One agent per target file — parallel execution gives each file full attention; agent reads `_conformity-instructions.md` and discovers its own criteria via conventions CLI
- Agent applies fixes directly in Conformity workflow — reformatting, not just reporting
- Orchestrator safeguards target count — reports and suggests narrowing when exceeding 20 files; waits for user confirmation before spawning
- Agent preserves semantic meaning — changes are stylistic and structural, never altering what file communicates
- Files tagged `[fail: N lines]` in `list-matching` output auto-fail without processing — reported to user with line count
- Files tagged `[warn: N lines]` proceed with size noted — agent may need to use targeted reads for large files
- Line count thresholds are configurable in manifest.yaml `settings` section (`lines_warn_threshold`, `lines_fail_threshold`)
- All convention rules are required by default. Rules described as "recommended" or "optional" in convention text are reported but do not block.
- Natural language {target} evaluation occurs in Route as fallback after deterministic matches — orchestrator interprets goal, derives adjustments, and presents for user confirmation before proceeding
- When natural language adjustments conflict with other provided flags, orchestrator surfaces conflict and works with user to resolve — no implicit precedence
- Deterministic {target} values (`project`, `self`, paths, `/skill-name`) execute without interpretation or confirmation
- --delegate spawns background agent with Workflow and Rules — agents read component files at execution time; orchestration (Route) always runs in main conversation
- Self-evaluation does not support --delegate — interactive conflict resolution and level-by-level approval required
- Self-evaluation does not support --auto — interactive conflict resolution and level-by-level approval required
- --auto wraps Conformity workflow in convergence loop per skill-md convention; each iteration spawns fresh agent
- `.claude/rules/` files loaded at session start — in-session changes to rule files not visible to agents until session restart; convention files read explicitly, changes take effect immediately
- Self-evaluation conflict detection precedes Conformity per level — horizontal (within-level) and vertical (against prior levels) semantic conflicts require user resolution before structural fixes
- Self-evaluation Conformity uses `_self-eval-conformity-instructions.md` — structural, notation, and formatting fixes only; semantic differences are observations for user judgment
- Rule-change restart gate: if `.claude/rules/` files modified during self-evaluation level, session must restart; on restart, self-evaluation begins from Level 0 to re-evaluate with updated rules
