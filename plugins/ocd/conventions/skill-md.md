---
matches: "SKILL.md"
governed_by:
  - .claude/rules/ocd-design-principles.md
  - .claude/rules/ocd-process-flow-notation.md
  - .claude/conventions/markdown.md
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
| `argument-hint` | None | Autocomplete hint shown after `/command`. Format follows Skill Argument Notation in Process Flow Notation rules. |
| `disable-model-invocation` | `false` | Prevents Claude from auto-loading skill |
| `user-invocable` | `true` | Set `false` to hide from `/` menu |
| `allowed-tools` | None | Tools allowed without permission prompts. Supports wildcards (e.g., `Bash(git *)`) |
| `model` | Inherited | Override model for this skill |
| `context` | None | Set `fork` to run in subagent context |
| `agent` | None | Subagent type when `context: fork` (e.g., `Explore`, `Plan`, `general-purpose`) |

Multi-line descriptions — use YAML block scalar operator (`|` or `>`) for multi-line values. Bare multi-line descriptions (wrapped by formatters without operator) break parser.

List fields (`allowed-tools`, etc.) — use YAML block-style lists, one item per line with `- ` prefix. Not flow-style arrays (`[a, b]`).

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

Sections before Workflow are orchestration — main conversation agent resolves arguments, selects route, and packages inputs. Workflow sections are execution — self-contained blocks that may run directly or by spawned agents. Workflows never re-resolve arguments or re-route — they assume orchestration is complete.

When dispatching to agents, agent receives resolved inputs and execution instructions without exposure to alternative workflows, routing logic, or argument parsing. Workflow agent may spawn additional agents internally which it coordinates. System-managed variables (`$ARGUMENTS`, `${CLAUDE_SESSION_ID}`) and environment variables (`${CLAUDE_PLUGIN_ROOT}`) are resolved mechanically by Claude Code and shell respectively.

Orchestrator does not pre-read component files to inline content. Workflow steps dictate when component files are read and by whom — each executor reads what it needs at execution time.

String substitution variables available in body:

- `$ARGUMENTS` — All arguments passed when invoking skill
- `$ARGUMENTS[N]` or `$N` — Specific argument by 0-based index
- `${CLAUDE_SESSION_ID}` — Current session ID

## Standard Arguments

Reusable argument patterns for skills that accept targets, spawn agents, or scope evaluation. Not all arguments apply to every skill — include only those relevant to skill's domain. Arguments follow Skill Argument Notation defined in Process Flow Notation rules.

| Argument | Role | Description |
|----------|------|-------------|
| `--target` | Gate + subject | Required flag carrying target value; presence triggers execution, value identifies what to operate on; without it, skill responds with description and usage hint |
| `[--auto]` | Dispatch wrapper | Wraps selected workflow in convergence loop; spawns fresh agent per iteration, checks git diff for convergence; requires fix-producing workflow and clean working tree; see --auto section |
| `[--delegate]` | Dispatch modifier | Workflow agent spawns in background; see --delegate section for requirements |
| `[--pattern <glob> ...]` | Filter | Passthrough to navigator CLI for file enumeration; repeatable for OR-combined matching; ignored when target is single file |
| `[--all]` | Boundary override | Includes `.claude/` files in target enumeration; without it, `.claude/` excluded by default |

### Target Resolution

{target} is evaluated against deterministic matches first. Unmatched values fall through to natural language interpretation where orchestrator derives adjustments and confirms with user before proceeding.

Route pattern for {target} evaluation:

```
1. If not --target: Exit to user — respond with skill description and argument-hint
2. If ({target} starts with `/` and contains no spaces) or ({target} is a path ending with `/SKILL.md`):
    1. If {target} starts with `/`:
        1. Resolve skill path — run navigator CLI `resolve-skill` (strip leading `/` from {target})
        2. If exit code 1: Exit to user — report skill not found
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
python3 ${CLAUDE_PLUGIN_ROOT}/run.py skills.navigator resolve-skill <name>
```

Exits with code 1 if skill not found. Skills should Exit to user with error when resolution fails.

### Route Dispatch Pattern

Route evaluates {target} and selects Workflow.

```
## Route

1. If not --target: Exit to user — respond with skill description and argument-hint
2. Evaluate {target} against deterministic matches
    1. If ({target} starts with `/` and contains no spaces) or ({target} is a path ending with `/SKILL.md`):
        1. If {target} starts with `/`:
            1. Resolve skill path via navigator `resolve-skill` (strip leading `/` from {target})
            2. If exit code 1: Exit to user — report skill not found
        2. {target-directory} = parent of resolved SKILL.md path
    2. Else if {target} is file path:
        1. {target-file} = {target}
    3. Else if {target} is directory path:
        1. {target-directory} = {target}
    4. Else:
        1. Interpret {target} as natural language goal — derive adjustments, assign variables, present for confirmation
3. Prepare inputs for selected Workflow
4. Dispatch {selected-workflow}
    - If --auto: Wrap in convergence loop (see --auto section)
    - If --delegate: Agent spawn runs in background
```

### --auto

Skills that declare `--auto` in argument-hint wrap dispatch in a convergence loop. Route selects inner workflow as usual; `--auto` iterates it with fresh agents until stable. Git mechanics are handled by a deterministic tool; the agent manages only workflow dispatch.

Convergence loop:

```
1. Check precondition — bash: `python3 ${CLAUDE_PLUGIN_ROOT}/run.py tools.auto_convergence precondition`
    1. If exit code 1: Exit to user — commit pending changes before running --auto
    2. {baseline} = output (commit hash)
2. {iteration} = 0
3. {prev-diff} = none
4. While {iteration} < 5:
    1. Spawn agent with {selected-workflow}:
        1. Execute workflow
        2. Return:
            - Changes applied
    2. {iteration} = {iteration} + 1
    3. Check convergence — bash: `python3 ${CLAUDE_PLUGIN_ROOT}/run.py tools.auto_convergence check --baseline {baseline} [--prev-diff {prev-diff}]`
    4. {status} = first line of output
    5. {prev-diff} = second line of output (diff file path)
    6. If {status} is `converged`:
        1. Break loop — converged
5. Report convergence metadata: iterations completed, converged status, cumulative diff summary
```

Requirements:

- Workflow must be fix-producing — report-only and interactive workflows reject `--auto` in Route
- Fresh agent per iteration — no accumulated context; agent reads current file state from disk
- Convergence detection is deterministic — the `auto_convergence check` tool compares git diffs between iterations
- Iteration limit (5) is safeguard, not target

### --delegate

`--delegate` backgrounds workflow agent spawn. Without `--delegate`, spawn runs in foreground.

Requirements:

- Workflow must be fully autonomous — no interactive checkpoints
- Skills with interactive workflows must reject `--delegate` in Route
- Spawned agent receives Workflow and Rules; reads component files at execution time

### Agent Spawn Requirement

Skills declaring `--auto` or `--delegate` must spawn agents for Workflow execution. `--auto` spawns fresh agents per iteration; `--delegate` controls foreground vs background. Skills declaring neither have no agent-spawn requirement and may execute workflows directly.

`--auto` and `--delegate` compose — `--delegate` backgrounds the entire convergence loop.

### Constraints

- Natural language {target} evaluation occurs in Route as fallback after deterministic matches — orchestrator interprets goal, derives adjustments, assigns variables, and presents for user confirmation before proceeding
- When natural language adjustments conflict with other provided flags, orchestrator surfaces conflict and works with user to resolve — no implicit precedence
- Deterministic {target} values execute without interpretation or confirmation
- --pattern is only meaningful for directory targets — Route ignores it when target resolves to single file

## Directory Structure

```
skill-name/
├── SKILL.md               # Main instructions (required)
├── __init__.py            # Facade — public interface (optional, for skills with code)
├── __main__.py            # CLI entry point (optional, for skills with code)
├── _component-name.md     # Extracted component (optional)
├── references/            # Detailed reference docs (optional)
└── tests/                 # Test suites (optional)
```

Keep SKILL.md under 500 lines. Move detailed reference material to separate files. Extract components to `_{name}.md` files alongside SKILL.md to reduce SKILL.md size and scope agent context.

## Workflow Encapsulation

Workflow section is self-contained — everything agent needs to execute belongs inside it or is referenced by it. This includes:

- Numbered steps using Process Flow Notation
- `### Report` subheading defining output format — this is a content standard (what the report contains), distinct from PFN's `Return:` which is flow control (where the agent block ends and what data it hands back)
- Explicit file read steps for extracted components (`Read _component.md`)
- Supporting subsections (e.g., file roles, interpreting results)

An agent given the Workflow section and Rules section can execute without referencing other parts of SKILL.md. Component files are read at execution time by the agent running the workflow, not pre-loaded by the orchestrator.

CLI references in workflows and reference files must be full executable commands — never shorthand. An agent should be able to copy a command verbatim and run it. Include interpreter, launcher path, module, subcommand, and all required flags (e.g., `--db`). Shorthand forces agents to discover invocation patterns, which wastes tokens and risks incorrect construction.

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
1. Spawn agent with evaluation({target}):
    1. Read `_instructions.md` and `_criteria.md`
    2. Follow instructions against {target}
    3. Return:
        - Results
### Report
- Mode A specific format

## Workflow: Mode B
1. Spawn agent with coordination({targets}):
    1. For each {target} in {targets}:
        1. Spawn agent with evaluation({target}):
            1. Read `_instructions.md` and `_criteria.md`
            2. Follow instructions against {target}
            3. Return:
                - Results
        - async agent per target
    2. Collect agent reports
    3. Return:
        - Consolidated report
### Report
- Mode B specific format
```

When content is used by only one workflow, keep it as a workflow subsection — components are for content shared across 2+ workflows. Underscore prefix signals internal (consistent with `_{purpose}.py` pattern for internal modules).

## File Enumeration

Skills that accept path argument and can operate on directories must use the `paths_list` MCP tool for file enumeration — never invent ad-hoc file listing (glob, `git ls-files`, agent judgment).

Navigator applies project-wide exclude rules (`.git`, `.venv`, `__pycache__`, etc.) and traversal limits deterministically. The `patterns` parameter filters by basename glob and accepts arrays for OR-combined matching.

Skills should:

- Accept `--pattern` as passthrough argument when user wants to scope to specific file types
- Ignore `--pattern` when target is single file (nothing to filter)
- Document `--pattern` in `argument-hint` frontmatter when supported

## User Interaction Boundary

User interaction (AskUserQuestion, clarification, confirmation) only works in orchestrator context — Route and main conversation. Workflow agents run autonomously and cannot prompt user mid-execution.

The orchestrator handles all user-facing decisions before dispatching the Workflow agent. Workflow agents collect findings and report back — the user decides next steps after reviewing the report.

When interactive decisions span multiple Workflow executions, structure them as orchestrator steps between agent calls. Each agent call is autonomous; orchestrator mediates between calls in main conversation.

## User Choices and Confirmations

When orchestrator steps present choices or request confirmation, use `AskUserQuestion` tool with `options` parameter — not freeform text with numbered lists. Structured options give user selectable choices instead of requiring typed responses.

Does not apply to open-ended questions requiring freeform input or subagent contexts (AskUserQuestion only works in main conversation).

Else handling for unexpected responses:

- Orchestrator context — Else may jump forward or backward to appropriate step; do not prescribe specific outcomes
- Steps processable by either orchestrator or spawned agent — Else defaults to Exit to user; spawned agents cannot prompt user for alternative input

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
