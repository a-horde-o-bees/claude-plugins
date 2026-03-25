---
type: template
---

# SKILL.md Conventions

SKILL.md defines slash command behavior. Claude Code parses frontmatter for metadata and loads markdown body when skill is invoked. Skills are user-triggered interactive workflows.

## YAML Frontmatter

Frontmatter is optional but recommended. Claude Code falls back to directory name for `name` and first markdown paragraph for `description` when omitted.

```yaml
---
name: skill-name
description: What this skill does and when to use it
---
```

Fields:

| Field | Default | Description |
|-------|---------|-------------|
| `name` | Directory name | Slash command name. Lowercase letters, numbers, hyphens only (max 64 characters). Plugin skills use plugin-name prefix (e.g., `ocd-navigator` not `navigator`) so plugin name surfaces during search. |
| `description` | First markdown paragraph | Claude uses this to decide when skill is relevant. Loaded into context at metadata level before full body. |
| `argument-hint` | None | Autocomplete hint shown after `/command` (e.g., `[issue-number]`, `[filename]`). For skills with argument-type routing, use pipe-separated format: `[type-a \| type-b \| type-c]` |
| `disable-model-invocation` | `false` | Prevents Claude from auto-loading skill |
| `user-invocable` | `true` | Set `false` to hide from `/` menu |
| `allowed-tools` | None | Tools allowed without permission prompts. Supports wildcards (e.g., `Bash(git *)`) |
| `model` | Inherited | Override model for this skill |
| `context` | None | Set `fork` to run in subagent context |
| `agent` | None | Sub-agent type when `context: fork` (e.g., `Explore`, `Plan`, `general-purpose`) |

Multi-line descriptions — use YAML block scalar operator (`|` or `>`) for multi-line values. Bare multi-line descriptions (wrapped by formatters without operator) break parser.

## Body Structure

Markdown body follows skill after frontmatter. Claude loads full body only when skill is invoked.

Standard sections:

| Section | Description |
|---------|-------------|
| `# /skill-name` | Title matching slash command |
| Description paragraph | What skill does (also serves as `description` fallback if no frontmatter) |
| `## Process Model` | Conceptual model of how skill operates and why (optional — for skills with non-obvious mechanics) |
| `## Trigger` | When user invokes this skill |
| `## Route` | Central orchestration section — resolve arguments, validate inputs, select Workflow, dispatch (inline or delegated); handles `--delegate` as dispatch modifier |
| `## Workflow` | Numbered steps using Process Flow Notation; encapsulates everything agent needs to execute, including `### Report` subheading |
| `## Components` | Reusable content blocks shared across multiple workflows; prefer extracted `_{name}.md` files over inline sections (optional — only for multi-path skills with shared content) |
| `## Rules` | Constraints and guardrails |

Not all sections required — simple skills may only need title, description, and rules list.

Process Model is optional — only for skills where workflow correctness depends on mechanics not self-evident from steps themselves.

### Orchestration vs Execution Boundary

Sections before Workflow are orchestration — main conversation agent resolves arguments, selects route, and packages inputs. Workflow sections are execution — self-contained blocks that run with resolved inputs, either by orchestrator directly or by delegated agent.

Orchestration sections (Trigger, Route) prepare inputs. Route is central orchestration section — resolves arguments, validates inputs, selects Workflow, and dispatches. `--delegate` is a dispatch modifier handled within Route: spawn background agent with resolved Workflow instead of executing inline. Workflow sections contain everything needed to execute, including Report and supporting subsections. Workflows never re-resolve arguments or re-route — they assume orchestration is complete.

When delegating to agents, orchestrator resolves all prompt template placeholders before handoff — agents receive fully resolved prompts with no template variables. Orchestrator passes selected Workflow section and Rules — never full SKILL.md body. Agents receive resolved inputs and execution instructions without exposure to alternative workflows, routing logic, or argument parsing. System-managed variables (`$ARGUMENTS`, `${CLAUDE_SESSION_ID}`) and environment variables (`${CLAUDE_PLUGIN_ROOT}`) are resolved mechanically by Claude Code and shell respectively — orchestrator resolves skill-defined placeholders in Workflow prompt templates.

Orchestrator does not pre-read component files to inline content. Workflow steps dictate when component files are read and by whom — each executor reads what it needs at execution time. This keeps agent context precisely scoped.

String substitution variables available in body:
- `$ARGUMENTS` — All arguments passed when invoking skill
- `$ARGUMENTS[N]` or `$N` — Specific argument by 0-based index
- `${CLAUDE_SESSION_ID}` — Current session ID

## Standard Arguments

Reusable argument patterns for skills that accept targets, spawn agents, or scope evaluation. Not all arguments apply to every skill — include only those relevant to skill's domain. Arguments follow Skill Argument Notation defined in agent-authoring rules.

| Argument | Role | Description |
|----------|------|-------------|
| `--target` | Gate + subject | Required flag carrying target value; presence triggers execution, value identifies what to operate on; without it, skill responds with description and usage hint |
| `[--delegate]` | Dispatch modifier | Route spawns background agent with resolved Workflow instead of executing inline |
| `[--pattern <glob> ...]` | Filter | Passthrough to navigator CLI for file enumeration; repeatable for OR-combined matching; ignored when target is single file |
| `[--all]` | Boundary override | Includes `.claude/` files in target enumeration; without it, `.claude/` excluded by default |

### Target Resolution

{target} is evaluated against deterministic matches first. Unmatched values fall through to natural language interpretation where orchestrator derives adjustments and confirms with user before proceeding.

Route pattern for {target} evaluation:

```
1. If not --target:
  1. EXIT — respond with skill description and argument-hint
2. If ({target} starts with `/` and contains no spaces) or ({target} is a path ending with `/SKILL.md`):
  1. If {target} starts with `/`:
    1. Resolve skill path — run navigator CLI `resolve-skill` (strip leading `/` from {target})
    2. If exit code 1: EXIT — report skill not found
  2. {target-directory} = parent of resolved SKILL.md path
3. Else if {target} is file path:
  1. {target-file} = {target}
4. Else if {target} is directory path:
  1. {target-directory} = {target}
5. Else:
  1. Interpret {target} as natural language goal — derive adjustments, assign variables, present for user confirmation
```

Skills define their own deterministic {target} values (e.g., `project`, `self`) as additional branches before the natural language fallback.

Navigator CLI resolves skill names across all discovery locations in priority order:

```
python3 ${CLAUDE_PLUGIN_ROOT}/skills/navigator/scripts/navigator_cli.py resolve-skill <name>
```

Exits with code 1 if skill not found. Skills should EXIT with error when resolution fails.

### Route Dispatch Pattern

Route evaluates {target} and selects Workflow regardless of --delegate. Dispatch step determines delivery mechanism — inline execution or background agent handoff.

```
## Route

1. If not --target:
  1. EXIT — respond with skill description and argument-hint
2. Evaluate {target} against deterministic matches
  1. If ({target} starts with `/` and contains no spaces) or ({target} is a path ending with `/SKILL.md`):
    1. If {target} starts with `/`:
      1. Resolve skill path via navigator `resolve-skill` (strip leading `/` from {target})
      2. If exit code 1: EXIT — report skill not found
    2. {target-directory} = parent of resolved SKILL.md path
  2. Else if {target} is file path:
    1. {target-file} = {target}
  3. Else if {target} is directory path:
    1. {target-directory} = {target}
  4. Else:
    1. Interpret {target} as natural language goal — derive adjustments, assign variables, present for confirmation
3. Prepare inputs for selected Workflow
4. Dispatch
  1. If --delegate:
    1. Resolve all prompt template placeholders in selected Workflow
    2. Spawn background agent with resolved Workflow and Rules — agent reads component files at execution time
    3. Present agent report as-is
  2. Else:
    1. Proceed to selected Workflow
```

### Constraints

- --delegate requires Workflow to be fully autonomous — no interactive checkpoints; skills with interactive workflows (e.g., level-by-level user approval) must reject --delegate in Route
- --delegate causes all agent spawns within Workflow to run in background — orchestrator hides underlying processes from user
- Natural language {target} evaluation occurs in Route as fallback after deterministic matches — orchestrator interprets goal, derives adjustments, assigns variables, and presents for user confirmation before proceeding
- When natural language adjustments conflict with other provided flags, orchestrator surfaces conflict and works with user to resolve — no implicit precedence
- Deterministic {target} values execute without interpretation or confirmation
- --pattern is only meaningful for directory targets — Route ignores it when target resolves to single file

## Directory Structure

```
skill-name/
├── SKILL.md               # Main instructions (required)
├── _component-name.md     # Extracted component (optional)
├── references/            # Detailed reference docs (optional)
├── examples/              # Example output (optional)
└── scripts/               # Executable scripts (optional)
```

Keep SKILL.md under 500 lines. Move detailed reference material to separate files. Extract components to `_{name}.md` files alongside SKILL.md to reduce SKILL.md size and scope agent context.

## Workflow Encapsulation

Workflow section is self-contained — everything agent needs to execute belongs inside it or is referenced by it. This includes:

- Numbered steps using Process Flow Notation
- `### Report` subheading defining output format
- Explicit file read steps for extracted components (`Read _component.md`)
- Supporting subsections (e.g., file roles, interpreting results)

Agent given Workflow section and Rules section can execute without referencing other parts of SKILL.md. Component files are read at execution time by the agent running the workflow, not pre-loaded by the orchestrator.

### Multi-Path Workflows

Skills with distinct execution paths use separate Workflow sections instead of conditional branching within one Workflow. Each path is self-contained with its own steps, report format, and any supporting subsections.

```
## Workflow: Default
1. Step
2. Step
### Report
- Output format for default path

## Workflow: Alternate Mode
1. Step
2. Step
### Report
- Output format for alternate path
```

Routing logic (which path to execute) belongs in `## Route` section — not inside Workflow sections. Agent receives one complete Workflow without needing to filter irrelevant branches.

Single-path skills use `## Workflow` without suffix.

### Components

Components are reusable content blocks (prompts, evaluation criteria, reference material) shared across multiple workflows. Components serve workflows — they are never executed independently.

Prefer extracted `_{name}.md` files alongside SKILL.md over inline `## Components` sections. Extracted files scope agent context — each agent reads only files it needs, and intermediary agents (coordinators, dispatchers) pass file references without loading content they do not use.

```
skill-name/
├── SKILL.md
├── _instructions.md
└── _criteria.md
```

Workflows include explicit read steps for extracted components:

```
## Workflow: Mode A
1. Spawn agent with {target} and instructions:
  1. Read `_instructions.md` and `_criteria.md`
  2. Follow instructions against {target}
### Report
- Mode A specific format

## Workflow: Mode B
1. Spawn coordinating agent with {targets} and instructions:
  1. For each target in {targets}:
    1. Spawn sub-agent with target and instructions:
      1. Read `_instructions.md` and `_criteria.md`
      2. Follow instructions against target
  2. Collect sub-agent reports
### Report
- Mode B specific format
```

When content is used by only one workflow, keep it as a workflow subsection — components are for content shared across 2+ workflows. Underscore prefix signals internal (consistent with `_{purpose}.py` pattern for internal modules).

## File Enumeration

Skills that accept path argument and can operate on directories must use navigator CLI for file enumeration — never invent ad-hoc file listing (glob, `git ls-files`, agent judgment).

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/navigator/scripts/navigator_cli.py list <path> [--pattern "*.py"]
```

Navigator applies project-wide exclude rules (`.git`, `.venv`, `__pycache__`, etc.) and traversal limits deterministically. `--pattern` filters by basename glob and is repeatable for OR-combined matching.

Skills should:
- Accept `--pattern` as passthrough argument when user wants to scope to specific file types
- Ignore `--pattern` when target is single file (nothing to filter)
- Document `--pattern` in `argument-hint` frontmatter when supported

## Sub-Agent Interactivity Constraint

AskUserQuestion only works in main conversation context. Agents spawned via Agent tool run autonomously — they cannot prompt user mid-execution.

Design rule: skills that spawn agents must be fully autonomous — no interactive checkpoints inside delegated work. Preferred approach is report pattern: skill runs autonomously, collects all findings, presents report with recommendations. User decides next steps after reviewing.

When interactive decisions are unavoidable mid-workflow, use orchestration pattern — structure them as orchestration steps in main conversation between autonomous agent calls.

## User Choices and Confirmations

When workflow steps present choices or request confirmation in main conversation, use `AskUserQuestion` tool with `options` parameter — not freeform text with numbered lists. Structured options give user selectable choices instead of requiring typed responses.

Does not apply to open-ended questions requiring freeform input or sub-agent contexts (AskUserQuestion only works in main conversation).

Else handling for unexpected responses:
- Orchestrator context — Else may jump forward or backward to appropriate step; do not prescribe specific outcomes
- Steps processable by either orchestrator or spawned agent — Else defaults to EXIT; spawned agents cannot prompt user for alternative input

## Discovery and Loading

Claude Code uses three-level progressive loading:

1. Metadata only — `name` + `description` (~100 words) always in context so Claude knows available skills
2. Full body — loaded when skill is invoked by user or Claude
3. Bundled resources — scripts, references, assets loaded on-demand during execution

Discovery locations (highest priority wins):

| Scope | Path |
|-------|------|
| Enterprise | Managed settings |
| Personal | `~/.claude/skills/*/SKILL.md` |
| Project | `.claude/skills/*/SKILL.md` |
| Plugin (--plugin-dir) | `<plugin>/skills/*/SKILL.md` — local development; shadows marketplace for same plugin |
| Plugin (marketplace) | `~/.claude/plugins/` → installed plugin `installPath` → `skills/*/SKILL.md` |
