---
name: ocd-conventions
description: Manage and enforce project conventions; --check reformats files to conform using deterministic pattern matching and single sequential agent
argument-hint: "--check [path | /skill-name | project | self] [--pattern \"*.py\"] [--focus \"specific instruction\"] [--all] [--delegate]"
---

# /ocd-conventions

Manage and enforce project conventions. Convention CLI deterministically discovers applicable conventions per target, then single agent applies them across all targets sequentially. Deterministic discovery + non-deterministic application.

## Trigger

User runs `/ocd-conventions`

## Route

1. If `--check` not in `$ARGUMENTS`:
  1. Respond with skill description and argument-hint, then stop
2. Strip flags — extract `--check`, `--delegate`, `--all`, `--focus "..."`, and `--pattern "..."` from `$ARGUMENTS`; collect `--pattern` values and `--focus` text
3. Resolve target — validate remaining arguments, resolve paths
  1. If remaining arguments empty:
    1. EXIT — respond with skill description and argument-hint
  2. If `self`:
    1. If `--delegate`:
      1. EXIT — self-evaluation is interactive and cannot be delegated
    2. Select Workflow: Self-Evaluation; proceed to step 7
  3. Else if `project`:
    1. Set target directory to `.` (project root)
  4. Else if starts with `/`:
    1. Resolve skill path — run navigator CLI `resolve-skill` with skill name (strip leading `/`)
      ```
      python3 ${CLAUDE_PLUGIN_ROOT}/skills/navigator/scripts/navigator_cli.py resolve-skill <name>
      ```
    2. If exit code 1: EXIT — report skill not found
    3. Set target directory to parent of resolved SKILL.md path
  5. Else if path:
    1. If file named `SKILL.md`: set target directory to parent directory (treat as skill target)
    2. Else if file: set single file as sole target; skip to step 5
    3. If directory: set target directory to path
  6. Else:
    1. EXIT — unrecognized argument
4. Enumerate targets — run navigator CLI to get filtered file list
  ```bash
  python3 ${CLAUDE_PLUGIN_ROOT}/skills/navigator/scripts/navigator_cli.py list <directory> [--pattern "..."] [--exclude "..."]
  ```
  - Pass through `--pattern` values from step 2
  - If `--all` not present, apply boundary rule via `--exclude ".claude/*"`
  - Explicit file paths bypass boundary rule — passing `.claude/` path as target in step 3.5 checks that path without exclusion
5. Deduplicate target list
6. Discover criteria — run conventions CLI
  ```
  python3 ${CLAUDE_PLUGIN_ROOT}/skills/conventions/scripts/conventions_cli.py list-matching <target-paths>
  ```
  - Output: `Criteria:` header with deduplicated convention paths, then per-file groups with line count tags
  - If no criteria match: report "no criteria apply" and stop
  - Files tagged `[fail: N lines]` auto-fail — report to user, remove from target list
  - Files tagged `[warn: N lines]` proceed with warning noted
7. Dispatch
  1. If `--delegate`:
    1. Resolve all prompt template placeholders in selected Workflow
    2. Spawn background agent with resolved Workflow and Rules
    3. Present agent report as-is
  2. Else:
    1. Proceed to selected Workflow (default: Workflow: Conformity)

## Workflow: Conformity

1. Extract focus — if `--focus` present, use focus text from Route
2. Build conformity reformat prompt — resolve all placeholders:
  - `{criteria_section}` — `Criteria:` block from `list-matching` output (deduplicated convention paths)
  - `{per_file_criteria}` — per-file groups from `list-matching` output (each target with its matching conventions)
  - `{focus_instruction}` — focus text if present, omit block otherwise
3. Spawn single agent with resolved prompt
4. Review changes — run `git diff` after agent completes; review for correctness before presenting
5. Present results — per-target summary of changes applied, criteria used, and issues requiring user judgment

### File Roles

Every file referenced during reformatting falls into one of two roles:

- Target is file being reformatted
- Criteria are convention and rule files listed in `Criteria:` header — agent reads each once, then applies per-file based on grouping

### Conformity Reformat Prompt

Orchestrator resolves all placeholders before passing to agent. Agent receives fully resolved prompt with no template variables.

```
You are reformatting files to conform with project conventions. Process each target file sequentially.

{if focus_instruction}
Focus: {focus_instruction}
Evaluate and fix only aspects related to this focus. Skip unrelated conventions.
{end if}

Criteria files to read (rules and conventions — your evaluation criteria):
{criteria_section}

Target files to reformat, each with applicable criteria:
{per_file_criteria}

For EACH target file:

1. Read target file
2. Evaluate target file against its listed criteria
3. For each applicable convention or rule:
  1. Assess conformity with specific rule citations
  2. Apply fixes for any non-conformities found
4. After convention conformity, evaluate and fix internal consistency:
  1. Terminology — ensure same concepts use same terms throughout
  2. Cross-references — ensure internal references (section names, step numbers) match their targets
  3. Completeness — ensure no references to concepts, steps, or sections that do not exist
5. Apply all fixes directly to target file using Edit tool. Preserve semantic meaning — reformat and rephrase, never change what file communicates.

After processing ALL targets, provide consolidated report:
1. Per-target: changes applied with brief rationale
2. Per-target: issues NOT fixed because they require user judgment (semantic ambiguity, structural decisions)
3. All criteria files used (conventions and rules, once, not per-target)
```

### Interpreting Results

- Agent applied fixes consistently → Conventions are clear and actionable
- Agent misapplied fixes → Convention definitions are ambiguous
- Convention CLI returned no matches → Pattern definitions need broader coverage
- Agent couldn't determine applicability → Convention scope needs refinement

### Report

- Per-target: changes applied with brief rationale
- Per-target: issues not fixed because they require user judgment (semantic ambiguity, structural decisions)
- All criteria files used (conventions and rules, once, not per-target)

### Running

```
Agent(
  subagent_type="general-purpose",
  prompt="<fully resolved conformity reformat prompt>",
  description="Conformity: <target summary>"
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
3. If `--focus` present:
  1. Note focus scope — evaluation narrows to focus-related aspects; if focus applicability is ambiguous for self-evaluation context, ask user for clarification before proceeding
4. Initialize criteria set — empty list
5. For each level (starting at Level 0):
  1. If criteria set is empty (Level 0):
    1. Evaluate files for internal consistency only — terminology, cross-references, completeness
  2. Else:
    1. Evaluate each file against all criteria in criteria set
    2. For each criterion, assess conformity with specific citations
    3. Evaluate internal consistency — terminology, cross-references, completeness
  3. If `--focus` present:
    1. Skip evaluation of aspects unrelated to focus
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
- Single agent processes all targets sequentially — never spawn parallel agents per target
- Agent applies fixes directly in Conformity workflow — reformatting, not just reporting
- Self-evaluation is report-only — present findings, do not apply fixes; user directs any changes after reviewing
- Agent preserves semantic meaning — changes are stylistic and structural, never altering what file communicates
- Files tagged `[fail: N lines]` in `list-matching` output auto-fail without processing — reported to user with line count
- Files tagged `[warn: N lines]` proceed with size noted — agent may need to use targeted reads for large files
- Line count thresholds are configurable in manifest.yaml `settings` section (`lines_warn_threshold`, `lines_fail_threshold`)
- All convention rules are required by default. Rules described as "recommended" or "optional" in convention text are reported but do not block.
- `--focus` is accepted in all routes — Conformity agent evaluates only focus-related aspects; Self-Evaluation narrows scope to focus; orchestrator asks user for clarification when focus applicability is ambiguous
- `--delegate` spawns background agent with fully resolved Workflow and Rules — orchestration (Route) always runs in main conversation
- Self-evaluation does not support `--delegate` — interactive review between levels is structurally required
- Orchestrator resolves all prompt template placeholders before agent handoff — agents receive fully resolved prompts with no template variables
