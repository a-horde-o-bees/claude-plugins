---
name: ocd-conventions
description: Manage and enforce project conventions; --check reformats files to conform using deterministic pattern matching and single sequential agent
argument-hint: "--check [path | /skill-name | project] [--pattern \"*.py\"] [--focus \"specific instruction\"] [--all] [--delegate]"
---

# /ocd-conventions

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

1. Strip `--delegate`, `--all`, `--focus "..."`, and `--pattern "..."` from `$ARGUMENTS` if present; collect all `--pattern` values
2. If remaining arguments empty:
  1. Respond with skill description and argument-hint, then stop
3. Else if `project`:
  1. Treat as `.` — project root directory
4. Else if starts with `/`:
  1. Target directory is `.claude/skills/{name}/` (replace hyphens with underscores for directory name)
5. Else if path:
  1. If file — single file is sole target; ignore `--pattern` if present; skip to step 7
  2. If directory — target directory is path
6. Enumerate directory targets — run navigator CLI to get filtered file list
  ```bash
  python3 ${CLAUDE_PLUGIN_ROOT}/skills/navigator/scripts/navigator_cli.py list <directory> [--pattern "..."] [--exclude "..."]
  ```
  - Pass through any `--pattern` values collected in step 1
  - If `--all` not present, apply boundary rule via `--exclude ".claude/*"`
  - Output is one file path per line, pre-filtered by navigator exclude rules, pattern filters, and exclude filters
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
5. Discover criteria — run conventions CLI to get all applicable rules and conventions
  ```
  python3 ${CLAUDE_PLUGIN_ROOT}/skills/conventions/scripts/conventions_cli.py get <target-paths>
  ```
  1. Output is one file path per line (rules first, then matched conventions)
  2. If no output:
    1. Report "no criteria apply" and stop
6. Spawn single agent — one agent processes all targets sequentially with conformity reformat prompt; pass criteria file paths for agent to read directly
7. Review changes — run `git diff` after agent completes, review for correctness before presenting
8. Present results — per-target summary of changes applied, criteria used, and any issues requiring user judgment

### File Roles

Every file referenced during reformatting falls into one of two roles:

- Target is file being reformatted
- Criteria are file paths returned by conventions CLI (rules and matched conventions) — passed to agent for direct reading

### Boundary Rule

Files under `.claude/` are excluded from target list by default — convention definitions, rule definitions, and project instructions live there. Use `--all` to include `.claude/` files in target list, or pass a `.claude/` path as explicit target to check specific files.

### Conformity Reformat Prompt

```
You are reformatting files to conform with project conventions. Process each target file sequentially.

`{if focus_instruction}`
Focus: `{focus_instruction}`
Evaluate and fix only aspects related to this focus. Skip unrelated conventions.
`{end if}`

Criteria files to read (rules and conventions — your evaluation criteria):
`{criteria_paths}`

Target files to reformat (process in order):
`{target_list}`

For EACH target file:

1. Read target file
2. Evaluate target file against all criteria read above
3. For each convention or rule:
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

## Rules

- Use Agent tool with `subagent_type="general-purpose"` for agent spawn
- Do not pass conversation context to spawned agent — agent inherits CLAUDE.md automatically but receives no other context beyond conformity reformat prompt
- Single agent processes all targets sequentially — never spawn parallel agents per target
- Agent applies fixes directly — reformatting, not just reporting
- Agent preserves semantic meaning — changes are stylistic and structural, never altering what file communicates
- Target files exceeding 500 lines auto-fail without processing — file needs to be divided before conformity reformatting is meaningful
- All convention rules are required by default. Rules described as "recommended" or "optional" in convention text are reported but do not block.
- When `--focus` is provided, agent evaluates and fixes only aspects related to focus instruction — skip unrelated conventions entirely

## Report

- Per-target: changes applied with brief rationale
- Per-target: issues not fixed because they require user judgment (semantic ambiguity, structural decisions)
- All criteria files used (conventions and rules, once, not per-target)

## Running

```
Agent(
  subagent_type="general-purpose",
  prompt="<filled conformity reformat prompt with convention content, target list, and optional focus>",
  description="Conformity: <target summary>"
)
```
