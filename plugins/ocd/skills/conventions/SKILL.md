---
name: ocd-conventions
description: Manage and enforce project conventions; --check reformats files to conform using deterministic pattern matching and a single sequential agent
argument-hint: "--check [path | /skill-name | project] [--focus \"specific instruction\"] [--all] [--delegate]"
---

# /ocd-conventions

## File Map

### Dependencies
```
CLAUDE.md
.claude/ocd/conventions/ (convention definitions)
```

Manage and enforce project conventions. Convention CLI deterministically discovers applicable conventions per target, then single agent applies them across all targets sequentially. Deterministic discovery + non-deterministic application.

## Trigger

User runs `/ocd-conventions`

## Route

1. If `--check` not in `$ARGUMENTS`:
  1. Respond with skill description and argument-hint, then stop
2. Else:
  1. Strip `--check` from `$ARGUMENTS`
  2. Proceed to Resolve Arguments

## Resolve Arguments

1. Strip `--delegate`, `--all`, and `--focus "..."` from `$ARGUMENTS` if present
2. If remaining arguments empty:
  1. Respond with skill description and argument-hint, then stop
3. Else if `project`:
  1. Treat as `.` — project root directory
4. Else if starts with `/`:
  1. All files in `.claude/skills/{name}/` directory (replace hyphens with underscores for directory name)
5. Else if path:
  1. If file — single file is sole target
  2. If directory — all files in directory recursively
6. If `--all` not present:
  1. Apply boundary rule — remove matching files from target list
7. Deduplicate target list

## Delegate Execution

1. When `--delegate` is in `$ARGUMENTS`:
  1. Route
  2. Resolve Arguments
  3. Spawn single background agent with Workflow section, Rules section, Report section, and resolved arguments
  4. Present agent's report as-is

## Workflow

1. Route
2. Resolve Arguments
3. Extract focus — if `--focus "..."` present, extract quoted text as focus instruction
4. Check line counts — count lines in each target file
  1. If any target exceeds 500 lines:
    1. Report auto-fail for that target, remove from target list
5. Discover conventions — run convention CLI to find applicable conventions for all targets
  ```bash
  python3 ${CLAUDE_PLUGIN_ROOT}/skills/conventions/scripts/convention_cli.py get <target-paths>
  ```
  1. If no conventions match any target:
    1. Report "no conventions apply" and stop
  2. Collect convention content output — pass to agent as pre-discovered criteria
6. Spawn single agent — one agent processes all targets sequentially with conformity reformat prompt, including discovered convention content
7. Review changes — run `git diff` after agent completes, review for correctness before presenting
8. Present results — per-target summary of changes applied, criteria used, and any issues requiring user judgment

### File Roles

Every file referenced during reformatting falls into one of two roles:

- Target is file being reformatted
- Criteria are convention files matched by convention CLI — passed to agent as pre-discovered context

### Boundary Rule

Convention architecture files are excluded from target list by default:

- `.claude/ocd/conventions/**` — Convention definitions
- `.claude/rules/ocd-*` — Rule definitions
- Root `CLAUDE.md` — Project instructions

Use `--all` to include these files in the target list.

### Conformity Reformat Prompt

```
You are reformatting files to conform with project conventions. Process each target file sequentially.

`{if focus_instruction}`
Focus: `{focus_instruction}`
Evaluate and fix only aspects related to this focus. Skip unrelated conventions.
`{end if}`

Applicable conventions (pre-discovered — these are your evaluation criteria):
`{convention_content}`

Target files to reformat (process in order):
`{target_list}`

For EACH target file:

1. Read target file
2. Evaluate target file against all applicable conventions from above
3. For each convention:
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
3. All convention files used as evaluation criteria (once, not per-target)
```

### Interpreting Results

- Agent applied fixes consistently → Conventions are clear and actionable
- Agent misapplied fixes → Convention definitions are ambiguous
- Convention CLI returned no matches → Pattern definitions need broader coverage
- Agent couldn't determine applicability → Convention scope needs refinement

## Report

- Per-target: changes applied with brief rationale
- Per-target: issues not fixed because they require user judgment (semantic ambiguity, structural decisions)
- All convention files used as evaluation criteria (once, not per-target)

## Rules

- Use Agent tool with `subagent_type="general-purpose"` for agent spawn
- Do not pass conversation context to spawned agent — agent inherits CLAUDE.md automatically but receives no other context beyond the conformity reformat prompt
- Single agent processes all targets sequentially — never spawn parallel agents per target
- Agent applies fixes directly — reformatting, not just reporting
- Agent preserves semantic meaning — changes are stylistic and structural, never altering what file communicates
- Target files exceeding 500 lines auto-fail without processing — file needs to be divided before conformity reformatting is meaningful
- All convention rules are required by default. Rules described as "recommended" or "optional" in convention text are reported but do not block.
- When `--focus` is provided, agent evaluates and fixes only aspects related to focus instruction — skip unrelated conventions entirely

## Running

```
Agent(
  subagent_type="general-purpose",
  prompt="<filled conformity reformat prompt with convention content, target list, and optional focus>",
  description="Conformity: <target summary>"
)
```
