---
includes: "SKILL.md"
governed_by:
  - .claude/rules/ocd/design-principles.md
  - .claude/rules/ocd/process-flow-notation.md
  - .claude/conventions/ocd/markdown.md
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
| `name` | Directory name | Slash command name. Lowercase letters, numbers, hyphens only (max 64 characters). Do not prefix with the plugin name — Claude Code namespaces plugin slash commands automatically (`/<plugin>:<command>` on collision, `/<command>` when unique), so a redundant prefix double-namespaces. |
| `description` | First markdown paragraph | Canonical purpose statement — same text as the body description paragraph. Loaded at metadata level for skill discovery; Claude uses this to decide when skill is relevant. |
| `argument-hint` | None | Autocomplete hint shown after `/command`. Format follows Skill Argument Notation in Process Flow Notation rules. |
| `disable-model-invocation` | `false` | Prevents Claude from auto-loading skill |
| `user-invocable` | `true` | Set `false` to hide from `/` menu |
| `allowed-tools` | None | Tools allowed without permission prompts. Supports wildcards (e.g., `Bash(git *)`) |
| `model` | Inherited | Override model for this skill |
| `context` | None | Set `fork` to run in subagent context |
| `agent` | None | Subagent type when `context: fork` (e.g., `Explore`, `Plan`, `general-purpose`) |

Scalar fields (description, name, argument-hint, etc.) are single lines — no artificial line breaks, consistent with the paragraph wrapping rule. Do not use YAML block scalar operators (`|` or `>`) for values that are a single paragraph.

List fields (`allowed-tools`, etc.) — use YAML block-style lists, one item per line with `- ` prefix. Not flow-style arrays (`[a, b]`).

## Body Structure

Markdown body follows skill after frontmatter. Claude loads full body only when skill is invoked.

Sections fall into three categories:

- **Prescribed** — every skill includes these (simple skills may reduce to title, description, and rules)
- **Common** — established patterns with supporting infrastructure; include when relevant to the skill's domain
- **Domain-specific** — child conventions define additional sections for their domain; this list is not exhaustive

| Section | Category | Description |
|---------|----------|-------------|
| `# /skill-name` | Prescribed | Title matching slash command; uses unqualified name (Claude Code handles namespace qualification at invocation) |
| Description paragraph | Prescribed | Canonical purpose statement; doubles as `description` fallback when frontmatter omits it |
| `## Trigger` | Prescribed | When user invokes this skill |
| `## Route` | Prescribed | Resolve arguments, validate inputs, select Workflow, dispatch; omit for argument-free skills that dispatch directly to Workflow |
| `## Workflow` | Prescribed | Numbered steps using Process Flow Notation; encapsulates everything agent needs to execute |
| `## Rules` | Common | Constraints for the skill executor that apply broadly or govern multiple steps; agent-facing constraints belong in component files; omit when all constraints are step-specific and inlined |
| `## Error Handling` | Prescribed | How the skill responds to failures; minimum: report failure with available details. Skills with domain-specific error recovery replace the default with appropriate handling |
| `## Process Model` | Common | Conceptual model of how skill operates and why — for skills where workflow correctness depends on mechanics not self-evident from steps themselves |
| `## Components` | Common | Reusable content blocks shared across multiple workflows; prefer extracted `_{name}.md` files over inline sections |
| `### Report` | Common | Output format subheading within Workflow — a content standard (what the report contains), distinct from PFN's `Return:` which is flow control |

Child conventions (e.g., evaluation-skill-md.md) may prescribe additional sections, promote Common sections to Prescribed for their domain, or define domain-specific subsections within Workflow.

### Orchestration vs Execution Boundary

Sections before Workflow are orchestration — the skill executor resolves arguments, selects route, and packages inputs. The Workflow section is what the skill executor follows. When the Workflow spawns agents, those agents read component files — they are not given assembled sections or pre-composed instructions.

Agent spawn instructions contain file paths, not file contents. The agent reads each file at execution time in its own context. The skill executor never reads component files to inline their content — it references them by path in spawn instructions and the agent opens them. System-managed variables (`$ARGUMENTS`, `${CLAUDE_SESSION_ID}`) and environment variables (`${CLAUDE_PLUGIN_ROOT}`) are resolved mechanically by Claude Code and shell respectively.

Constraints follow the same boundary. Rules in SKILL.md apply to the skill executor. Agent-facing constraints — behavioral guardrails, format requirements, scope restrictions — belong in the component files that agents read. Each execution context receives exactly its own instructions through file compartmentalization.

String substitution variables available in body:

- `$ARGUMENTS` — All arguments passed when invoking skill
- `$ARGUMENTS[N]` or `$N` — Specific argument by 0-based index
- `${CLAUDE_SESSION_ID}` — Current session ID

## Standard Arguments

Common argument patterns with established infrastructure. These are not exhaustive — skills define their own arguments for their domain. Include standard arguments when their infrastructure is relevant; define domain-specific arguments as needed. Arguments follow Skill Argument Notation defined in Process Flow Notation rules.

| Argument | Role | Description |
|----------|------|-------------|
| `--target` | Gate + subject | Required flag carrying target value; presence triggers execution, value identifies what to operate on; without it, skill responds with description and usage hint |
| `[--pattern <glob> ...]` | Filter | Passthrough to navigator CLI for file enumeration; repeatable for OR-combined matching; ignored when target is single file |
| `[--all]` | Boundary override | Includes `.claude/` files in target enumeration; without it, `.claude/` excluded by default |

### Target Resolution

{target} is evaluated against deterministic matches first. Unmatched values fall through to natural language interpretation where skill executor derives adjustments and confirms with user before proceeding.

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
python3 ${CLAUDE_PLUGIN_ROOT}/run.py servers.navigator.cli resolve-skill <name>
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
4. Dispatch Workflow
```

### Constraints

- Natural language {target} evaluation occurs in Route as fallback after deterministic matches — skill executor interprets goal, derives adjustments, assigns variables, and presents for user confirmation before proceeding
- When natural language adjustments conflict with other provided flags, skill executor surfaces conflict and works with user to resolve — no implicit precedence
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
- `### Report` subheading when the skill produces structured output
- Explicit file read steps for extracted components (`Read _component.md`)
- Supporting subsections (e.g., file roles, interpreting results)

The Workflow section and the component files it references form a complete execution surface — the skill executor follows the Workflow, and spawned agents read the component files they are directed to. Agent-facing constraints live in those component files, not in the SKILL.md Rules section.

CLI references in workflows and reference files must be full executable commands — never shorthand. An agent should be able to copy a command verbatim and run it. Include interpreter, launcher path, module, subcommand, and all required flags (e.g., `--db`). Shorthand forces agents to discover invocation patterns, which wastes tokens and risks incorrect construction.

### Multi-Path Workflows

Skills with distinct execution paths extract each path into a component file rather than using conditional branching within one Workflow. Route selects the path; the Workflow dispatches to the selected component file. Each path is self-contained in its own file with its own steps, constraints, and report format — the executor reads one file and follows it without filtering irrelevant branches.

```
skill-name/
├── SKILL.md
├── _workflow-default.md
└── _workflow-alternate.md
```

Routing logic (which path to execute) belongs in `## Route`. The `## Workflow` section dispatches to the selected component. Duplication across component files is acceptable — compartmentalized workflows are safer for agent adherence than shared abstractions that require cross-file reasoning.

Single-path skills keep steps inline in `## Workflow`.

### Components

Components are extracted `_{name}.md` files alongside SKILL.md. They carry content that the skill executor does not need in its own context — agent workflows, evaluation criteria, reference material, prompt templates, and agent-facing constraints. Components serve workflows and are never executed independently.

Two reasons to extract a component:

- **Context scoping** — the spawn instruction directs the agent to read a focused component file rather than carrying all agent-level detail in SKILL.md. A component file can contain a self-contained agent workflow (PFN steps the agent executes), evaluation criteria, or any instructions the agent needs that the skill executor does not. Extract even for a single workflow when the motivation is keeping the skill executor's context lean and the agent's context focused.
- **Reuse** — content shared across multiple workflows lives in a component rather than duplicated inline.

Prefer extracted files over inline `## Components` sections. Underscore prefix signals internal (consistent with `_{purpose}.py` pattern for internal modules).

```
skill-name/
├── SKILL.md
├── _agent-workflow.md
└── _criteria.md
```

Workflows include explicit read steps for extracted components:

```
## Workflow
1. Spawn agent with evaluation({target}):
    1. Read `_evaluation-workflow.md`
    2. Follow workflow against {target}
    3. Return:
        - Results
```

## File Enumeration

Skills that accept path argument and can operate on directories must use the `paths_list` MCP tool for file enumeration — never invent ad-hoc file listing (glob, `git ls-files`, agent judgment).

Navigator applies project-wide exclude rules (`.git`, `.venv`, `__pycache__`, etc.) and traversal limits deterministically. The `patterns` parameter filters by basename glob and accepts arrays for OR-combined matching.

Skills should:

- Accept `--pattern` as passthrough argument when user wants to scope to specific file types
- Ignore `--pattern` when target is single file (nothing to filter)
- Document `--pattern` in `argument-hint` frontmatter when supported

## User Interaction Boundary

User interaction (AskUserQuestion, clarification, confirmation) works in SKILL.md because the skill executor runs in the main conversation. Spawned agents receive their own component files and run autonomously — they cannot prompt the user mid-execution.

When interactive decisions span multiple agent dispatches, structure them as skill executor steps between spawn calls. Each spawned agent is autonomous; the skill executor mediates between calls in main conversation.

## User Choices and Confirmations

When skill executor steps present choices or request confirmation, use `AskUserQuestion` tool with `options` parameter — not freeform text with numbered lists. Structured options give user selectable choices instead of requiring typed responses.

Does not apply to open-ended questions requiring freeform input or spawned agent contexts (AskUserQuestion only works in main conversation).

Else handling for unexpected responses:

- Skill executor context — Else may jump forward or backward to appropriate step; do not prescribe specific outcomes
- Steps processable by either skill executor or spawned agent — Else defaults to Exit to user; spawned agents cannot prompt user for alternative input

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
