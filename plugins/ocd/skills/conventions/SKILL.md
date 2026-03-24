---
name: ocd-conventions
description: Manage and enforce project conventions; --check reformats files to conform using deterministic pattern matching and single sequential agent
argument-hint: "--check [path | /skill-name | project | self] [--pattern \"*.py\"] [--intent \"natural language goal\"] [--all] [--delegate]"
---

# /ocd-conventions

Manage and enforce project conventions. Convention CLI deterministically discovers applicable conventions per target, then single agent applies them across all targets sequentially. Deterministic discovery + non-deterministic application.

## Trigger

User runs `/ocd-conventions`

## Route

1. If `--check` not in `$ARGUMENTS`:
  1. Respond with skill description and argument-hint, then stop
2. Strip flags — extract `--check`, `--delegate`, `--all`, `--intent "..."`, and `--pattern "..."` from `$ARGUMENTS`; collect `--pattern` values and `--intent` text
3. If `--intent` present:
  1. Interpret intent — evaluate intent text against available pipeline controls: target resolution (directory, skill, project, self), file enumeration (`--pattern`, `--all`), criteria scoping, workflow selection, and agent scope instruction
  2. Derive adjustments — translate intent into concrete changes to downstream steps; adjustments may include adding patterns, changing target, narrowing criteria, selecting workflow, or adding agent scope instruction
  3. If adjustments conflict with explicit flags:
    1. Surface conflict and work with user to resolve
  4. Present adjustments and ask user for confirmation before proceeding
  5. Apply confirmed adjustments — merge into pipeline state (patterns, target, scope instruction) for downstream steps
4. Resolve target — validate remaining arguments, resolve paths
  1. If remaining arguments empty:
    1. EXIT — respond with skill description and argument-hint
  2. If `self`:
    1. If `--delegate`:
      1. EXIT — self-evaluation is interactive and cannot be delegated
    2. Select Workflow: Self-Evaluation; proceed to step 8
  3. Else if `project`:
    1. Set target directory to `.` (project root)
  4. Else if starts with `/` or file named `SKILL.md`:
    1. If starts with `/`:
      1. Resolve skill path — run navigator CLI `resolve-skill` with skill name (strip leading `/`)
        ```
        python3 ${CLAUDE_PLUGIN_ROOT}/skills/navigator/scripts/navigator_cli.py resolve-skill <name>
        ```
      2. If exit code 1: EXIT — report skill not found
    2. Set target directory to parent of resolved SKILL.md path
  5. Else if file:
    1. Set single file as sole target; skip to step 6
  6. Else if directory:
    1. Set target directory to path
  7. Else:
    1. EXIT — unrecognized argument
5. Enumerate targets — run navigator CLI to get filtered file list
  ```bash
  python3 ${CLAUDE_PLUGIN_ROOT}/skills/navigator/scripts/navigator_cli.py list <directory> [--pattern "..."] [--exclude "..."]
  ```
  - Pass through `--pattern` values from step 2
  - Without `--all`, apply boundary rule via `--exclude ".claude/*"`
  - Explicit file paths bypass boundary rule — passing `.claude/` path as target in step 4.5 or 4.6 checks that path without exclusion
6. Deduplicate target list
7. Safeguard — check target count
  1. If target count exceeds 20:
    1. Report count and suggest narrowing with `--pattern` or more specific path
    2. Wait for user confirmation before proceeding
8. Dispatch
  1. If `--delegate`:
    1. Resolve all prompt template placeholders in selected Workflow
    2. Spawn background agents with resolved Workflow and Rules
    3. Present agent reports as-is
  2. Else:
    1. Proceed to selected Workflow (default: Workflow: Conformity)

## Workflow: Conformity

1. Spawn parallel agents — one per target file
  - async Agent per target file with resolved Conformity Reformat Prompt
2. Review changes — run `git diff` after all agents complete; review for correctness before presenting
3. Present results — per-target summary of changes applied, criteria used, and issues requiring user judgment

### Conformity Reformat Prompt

Orchestrator resolves `{target_path}` and `{scope_instruction}` before passing to agent. Agent discovers its own criteria via conventions CLI.

```
You are reformatting a file to conform with project conventions.

{if scope_instruction}
Scope: {scope_instruction}
Evaluate and fix only aspects related to this scope. Skip unrelated conventions.
{end if}

Target file: {target_path}

1. Discover criteria — run conventions CLI to find applicable conventions and rules
  ```
  python3 ${CLAUDE_PLUGIN_ROOT}/skills/conventions/scripts/conventions_cli.py list-matching {target_path}
  ```
  1. If no criteria match: report "no criteria apply" and stop
  2. If file tagged `[fail: N lines]`: report auto-fail with line count and stop
  3. If file tagged `[warn: N lines]`: note warning, proceed with targeted reads for large file
2. Read all criteria files listed in output
3. Read target file
4. Evaluate target file against its criteria
5. For each applicable convention or rule:
  1. Assess conformity with specific rule citations
  2. Apply fixes for any non-conformities found
6. After convention conformity, evaluate and fix internal consistency:
  1. Terminology — ensure same concepts use same terms throughout
  2. Cross-references — ensure internal references (section names, step numbers) match their targets
  3. Completeness — ensure no references to concepts, steps, or sections that do not exist
7. Apply all fixes directly to target file using Edit tool. Preserve semantic meaning — reformat and rephrase, never change what file communicates.

After processing, provide report:
1. Changes applied with brief rationale
2. Issues NOT fixed because they require user judgment (semantic ambiguity, structural decisions)
3. Criteria files used
```

### Interpreting Results

- Agent applied fixes consistently → Conventions are clear and actionable
- Agent misapplied fixes → Convention definitions are ambiguous
- Convention CLI returned no matches → Pattern definitions need broader coverage
- Agent couldn't determine applicability → Convention scope needs refinement

### Report

- Per-target: changes applied with brief rationale
- Per-target: issues not fixed because they require user judgment (semantic ambiguity, structural decisions)
- All criteria files used (deduplicated across agents)

### Running

```
For each target:
  Agent(
    subagent_type="general-purpose",
    prompt="<resolved conformity reformat prompt>",
    description="Conformity: <target filename>",
    run_in_background=true
  )
```

## Workflow: Self-Evaluation

Evaluate rules and conventions against each other in dependency order. Report-only — present findings per level for user review, do not apply fixes. Files at each level are evaluated against criteria from all prior validated levels.

1. Get evaluation order — run conventions CLI `list-self` command
  ```
  python3 ${CLAUDE_PLUGIN_ROOT}/skills/conventions/scripts/conventions_cli.py list-self
  ```
  1. If error (cycle detected or missing dependency):
    1. Report error to user and stop
  - Output is levels (Level 0, Level 1, ...) with file paths
2. Present DAG overview to user — show levels with file names, confirm before starting
3. If scope instruction present (from intent resolution):
  1. Note scope — evaluation narrows to scope-related aspects
4. Initialize criteria set — empty list
5. For each level (starting at Level 0):
  1. If criteria set is empty (Level 0):
    1. Evaluate files for internal consistency only — terminology, cross-references, completeness
  2. Else:
    1. Evaluate each file against all criteria in criteria set
    2. For each criterion, assess conformity with specific citations
    3. Evaluate internal consistency — terminology, cross-references, completeness
  3. If scope instruction present:
    1. Skip evaluation of aspects unrelated to scope
  4. Present findings for current level — per-file summary of conformity issues found
  5. Wait for user — user reviews findings and either approves, requests changes, or directs next steps
  6. When user approves level:
    1. Add all files from current level to criteria set
    2. Proceed to next level
6. After all levels complete — present summary of full evaluation

### Report

- Per-level: files evaluated, criteria used, issues found
- Per-file: conformity issues with specific rule/convention citations
- Summary: total levels, total files, total issues found

## Rules

- Use Agent tool with `subagent_type="general-purpose"` for agent spawn
- Do not pass conversation context to spawned agent — agent inherits CLAUDE.md automatically but receives no other context beyond resolved prompt
- One agent per target file — parallel execution gives each file full attention; agent discovers its own criteria via conventions CLI
- Agent applies fixes directly in Conformity workflow — reformatting, not just reporting
- Orchestrator safeguards target count — reports and suggests narrowing when exceeding 20 files; waits for user confirmation before spawning
- Self-evaluation is report-only — present findings, do not apply fixes; user directs any changes after reviewing
- Agent preserves semantic meaning — changes are stylistic and structural, never altering what file communicates
- Files tagged `[fail: N lines]` in `list-matching` output auto-fail without processing — reported to user with line count
- Files tagged `[warn: N lines]` proceed with size noted — agent may need to use targeted reads for large files
- Line count thresholds are configurable in manifest.yaml `settings` section (`lines_warn_threshold`, `lines_fail_threshold`)
- All convention rules are required by default. Rules described as "recommended" or "optional" in convention text are reported but do not block.
- `--intent` evaluation occurs in Route before deterministic pipeline steps — orchestrator interprets intent, derives adjustments (target, patterns, criteria scoping, agent scope instruction), and presents for user confirmation before proceeding
- When `--intent` conflicts with explicit flags, orchestrator surfaces conflict and works with user to resolve — no implicit precedence
- Without `--intent`, Route executes deterministically from explicit flags alone — no interpretation step, no confirmation pause
- `--delegate` spawns background agent with fully resolved Workflow and Rules — orchestration (Route) always runs in main conversation
- Self-evaluation does not support `--delegate` — interactive review between levels is structurally required
- Orchestrator resolves all prompt template placeholders before agent handoff — agents receive fully resolved prompts with no template variables
