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
| `## Components` | Reusable content blocks (prompts, evaluation criteria) shared across multiple workflows; serve workflows, never executed independently (optional — only for multi-path skills with shared content) |
| `## Rules` | Constraints and guardrails |

Not all sections required — simple skills may only need title, description, and rules list.

Process Model is optional — only for skills where workflow correctness depends on mechanics not self-evident from steps themselves.

### Orchestration vs Execution Boundary

Sections before Workflow are orchestration — main conversation agent resolves arguments, selects route, and packages inputs. Workflow sections are execution — self-contained blocks that run with resolved inputs, either by orchestrator directly or by delegated agent.

Orchestration sections (Trigger, Route) prepare inputs. Route is central orchestration section — resolves arguments, validates inputs, selects Workflow, and dispatches. `--delegate` is a dispatch modifier handled within Route: spawn background agent with resolved Workflow instead of executing inline. Workflow sections contain everything needed to execute, including Report and supporting subsections. Workflows never re-resolve arguments or re-route — they assume orchestration is complete.

When delegating to agents, orchestrator resolves all prompt template placeholders before handoff — agents receive fully resolved prompts with no template variables. Orchestrator passes selected Workflow section, referenced Components, and Rules — never full SKILL.md body. Agents receive resolved inputs and execution instructions without exposure to alternative workflows, routing logic, or argument parsing. System-managed variables (`$ARGUMENTS`, `${CLAUDE_SESSION_ID}`) and environment variables (`${CLAUDE_PLUGIN_ROOT}`) are resolved mechanically by Claude Code and shell respectively — orchestrator resolves skill-defined placeholders in Workflow prompt templates.

String substitution variables available in body:
- `$ARGUMENTS` — All arguments passed when invoking skill
- `$ARGUMENTS[N]` or `$N` — Specific argument by 0-based index
- `${CLAUDE_SESSION_ID}` — Current session ID

## Standard Arguments

Reusable argument patterns for skills that accept paths, spawn agents, or scope evaluation. Not all arguments apply to every skill — include only those relevant to skill's domain.

| Argument | Role | Description |
|----------|------|-------------|
| `--check` | Gate | Required to trigger execution; without it, skill responds with description and usage hint |
| `--delegate` | Dispatch modifier | Route spawns background agent with resolved Workflow instead of executing inline |
| `--focus "..."` | Scope modifier | Narrows evaluation to focus-related aspects; orchestrator adapts behavior intelligently, asks user for clarification when ambiguous |
| `--pattern "..."` | Filter | Passthrough to navigator CLI for file enumeration; repeatable for OR-combined matching; ignored when target is single file |
| `--all` | Boundary override | Includes `.claude/` files in target enumeration; without it, `.claude/` excluded by default |

### Route Dispatch Pattern

Route resolves arguments and selects Workflow regardless of `--delegate`. Dispatch step determines delivery mechanism — inline execution or background agent handoff.

```
## Route

1. If `--check` not in `$ARGUMENTS`:
  1. Respond with skill description and argument-hint, then stop
2. Strip flags — extract standard arguments from `$ARGUMENTS`
3. Resolve target — validate remaining arguments, resolve paths, enumerate files
  1. If arguments invalid:
    1. EXIT — report error
4. Discover criteria or prepare inputs for selected Workflow
5. Dispatch
  1. If `--delegate`:
    1. Resolve all prompt template placeholders in selected Workflow
    2. Spawn background agent with resolved Workflow and Rules
    3. Present agent report as-is
  2. Else:
    1. Proceed to selected Workflow
```

### Constraints

- `--delegate` requires Workflow to be fully autonomous — no interactive checkpoints; skills with interactive workflows (e.g., level-by-level user approval) must reject `--delegate` in Route
- `--focus` is accepted in all routes — each Workflow adapts scope based on focus text; when focus applicability is ambiguous, orchestrator asks user before proceeding
- `--pattern` is only meaningful for directory targets — Route ignores it when target resolves to single file

## Directory Structure

```
skill-name/
├── SKILL.md           # Main instructions (required)
├── references/        # Detailed reference docs (optional)
├── examples/          # Example output (optional)
└── scripts/           # Executable scripts (optional)
```

Keep SKILL.md under 500 lines. Move detailed reference material to separate files.

## Workflow Encapsulation

Workflow section is self-contained — everything agent needs to execute belongs inside it or is bundled alongside it. This includes:

- Numbered steps using Process Flow Notation
- `### Report` subheading defining output format
- Prompt templates used by agent spawning steps (inline or via component reference)
- Supporting subsections (e.g., file roles, interpreting results)

Agent given Workflow section, referenced Components, and Rules section can execute without referencing other parts of SKILL.md.

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

`## Components` section contains reusable content blocks (prompts, evaluation criteria, reference material) shared across multiple workflows. Components serve workflows — they are never executed independently.

Workflows reference components by name, same as PFN subprocess references. Orchestrator identifies referenced components, resolves transitively (components may reference other components), and bundles them alongside the workflow when dispatching. Agent receives distinct sections — orchestrator does not inline component content into workflow text.

```
## Components

### Audit Prompt
<prompt content>

### Evaluation Criteria
<criteria content>

## Workflow: Mode A
1. Spawn agent with Audit Prompt
2. Evaluate using Evaluation Criteria
### Report
- Mode A specific format

## Workflow: Mode B
1. For each item:
  1. Spawn agent with Audit Prompt
2. Evaluate using Evaluation Criteria
### Report
- Mode B specific format
```

When content is used by only one workflow, keep it as a workflow subsection — components are for content shared across 2+ workflows. Minor duplication across workflows (e.g., slightly different report formats with common elements) is acceptable for clarity of each workflow's needs.

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
