---
includes: "SKILL.md"
governed_by:
  - .claude/rules/ocd/design-principles.md
  - .claude/rules/ocd/process-flow-notation.md
  - .claude/rules/ocd/markdown.md
---

# SKILL.md Conventions

SKILL.md defines slash command behavior. Claude Code parses frontmatter for metadata and loads markdown body when skill is invoked. Skills are user-triggered interactive workflows.

## Body Structure

Sections are ordered for progressive consumption — identity and concept first, then constraints, then execution.

Sections fall into three categories:

- **Prescribed** — every skill includes these
- **Common** — established patterns; include when relevant to the skill's domain
- **Domain-specific** — child conventions define additional sections for their domain; this list is not exhaustive

| Section | Category | Description |
|---------|----------|-------------|
| YAML Frontmatter | Prescribed | Metadata block parsed by Claude Code before the markdown body |
| `# /skill-name` | Prescribed | Title matching slash command; unqualified name |
| Description paragraph | Prescribed | Purpose statement per Purpose Statement guidance |
| `## Process Model` | Common | How the skill operates and why — when mechanics are not self-evident from steps |
| `## Scope` | Common | What the skill operates on and how arguments modify the target set |
| `## Rules` | Common | Constraints for the skill executor; spawned-agent-facing constraints belong in component files |
| `## Workflow` | Prescribed | Full process flow in Process Flow Notation — argument resolution, validation, execution, output |
| `### Report` | Common | Output format subheading within Workflow |

Child conventions (e.g., audit-skill-md.md) may prescribe additional sections, promote Common sections to Prescribed for their domain, or define domain-specific subsections within Workflow.

## YAML Frontmatter

Frontmatter declares skill metadata for Claude Code. The `name` field is required on every skill; other fields are optional.

```yaml
---
name: skill-name
description: What this skill does and when to use it
---
```

Fields:

| Field | Default | Description |
|-------|---------|-------------|
| `name` | Required | Slash command name. Matches the directory name exactly. Lowercase letters, numbers, hyphens only (max 64 characters). Must be declared explicitly — folder-derived names do not resolve unqualified via the Skill tool (it returns "Unknown skill" or "not a prompt-based skill"), which breaks cross-skill `skill:` invocations. Do not prefix with the plugin name — Claude Code namespaces plugin slash commands automatically via `/<plugin>:<command>`. |
| `description` | First markdown paragraph | Canonical purpose statement — same text as the body description paragraph. Loaded at metadata level for skill discovery; Claude uses this to decide when skill is relevant. |
| `argument-hint` | None | Autocomplete hint shown after `/command`. Format follows Argument Declaration in Process Flow Notation. |
| `disable-model-invocation` | `false` | Prevents Claude from auto-loading skill |
| `user-invocable` | `true` | Set `false` to hide from `/` menu |
| `allowed-tools` | None | Tools allowed without permission prompts. Supports wildcards (e.g., `Bash(git *)`) |
| `model` | Inherited | Override model for this skill |
| `context` | None | Set `fork` to run in subagent context |
| `agent` | None | Subagent type when `context: fork` (e.g., `Explore`, `Plan`, `general-purpose`) |

Scalar fields (description, name, argument-hint, etc.) are single lines — no artificial line breaks, consistent with the paragraph wrapping rule. Do not use YAML block scalar operators (`|` or `>`) for values that are a single paragraph.

List fields (`allowed-tools`, etc.) — use YAML block-style lists, one item per line with `- ` prefix. Not flow-style arrays (`[a, b]`).

## Standard Arguments

Common argument patterns with established infrastructure. These are not exhaustive — skills define their own arguments for their domain. Include standard arguments when their infrastructure is relevant; define domain-specific arguments as needed. Arguments follow Argument Declaration defined in Process Flow Notation.

| Argument | Role | Description |
|----------|------|-------------|
| `--target` | Gate + subject | Required flag carrying target value; presence triggers execution, value identifies what to operate on; without it, skill emits its description and argument-hint to the user |
| `[--pattern <glob> ...]` | Filter | Passthrough to navigator for file enumeration; repeatable for OR-combined matching; ignored when target is single file |
| `[--all]` | Boundary override | Includes `.claude/` files in target enumeration; without it, `.claude/` excluded by default |

### Target Resolution

`{target}` is evaluated against deterministic matches first. Unmatched values fall through to natural language interpretation where skill executor derives adjustments and confirms with user before proceeding.

Place these argument-resolution steps at the top of Workflow:

```
1. If not --target: Exit to user: skill description and argument-hint

> Check if target is a skill — slash-name or direct SKILL.md path

2. If ({target} starts with `/` and contains no spaces) or ({target} is a path ending with `/SKILL.md`):
    1. If {target} starts with `/`:
        1. bash: `python3 ${CLAUDE_PLUGIN_ROOT}/run.py subsystems.navigator resolve-skill {target}`
        2. If exit code 1: Exit to user: skill not found
    2. {target-directory} = parent of resolved SKILL.md path

> Not a skill — add domain-specific deterministic branches here (e.g., `project`, `self`)

3. Else if {target} is file path:
    1. {target-file} = {target}
4. Else if {target} is directory path:
    1. {target-directory} = {target}
5. Else:
    1. Interpret {target} as natural language goal — derive adjustments, assign variables, present for user confirmation
```

### Constraints

- When natural language adjustments conflict with other provided flags, skill executor surfaces the conflict and works with user to resolve — no implicit precedence
- `--pattern` is only meaningful for directory targets — ignore it when target resolves to single file

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

## Components

Component files (see Process Flow Notation) live alongside SKILL.md. Typical contents: extracted sub-flows, agent workflows, evaluation criteria, reference material.

### When to extract

Extract a sub-flow into a component file when either holds:

- The sub-flow is dispatched via `Spawn:` to an isolated agent — the agent reads only its own instructions, keeping the caller's context clean
- The sub-flow is optional — conditional on arguments or runtime state, not traversed by every invocation — so the caller avoids loading instructions that won't execute on the paths that skip it

Mandatory sub-flows that run on every invocation stay inline regardless of size. If the caller always reads them anyway, extraction saves no context.

## Delegation

Within skills, intelligent work delegation uses `Spawn:` exclusively. Tool calls (CLI scripts, bash commands) are not agent spawns and remain unrestricted. The skill executor applies user-directed corrections inline — no agent spawn needed for directed fixes.

## File Enumeration

Skills that operate on directories must use the `paths_list` MCP tool for file enumeration — never invent ad-hoc file listing (glob, `git ls-files`, agent judgment). Navigator applies project-wide exclude rules and traversal limits deterministically.

## User Interaction

User interaction works in SKILL.md because the skill executor runs in the main conversation. Spawned agents run autonomously and cannot prompt the user. When presenting choices, use `AskUserQuestion` with `options` parameter for structured selection instead of freeform text with numbered lists.

## Environment Variables

Claude Code automatically populates these variables in skill context:

- `$ARGUMENTS` — all arguments passed when invoking skill
- `$ARGUMENTS[N]` or `$N` — specific argument by 0-based index
- `${CLAUDE_SESSION_ID}` — current session ID
- `${CLAUDE_PLUGIN_ROOT}` — plugin installation directory

`${CLAUDE_SESSION_ID}` and `${CLAUDE_PLUGIN_ROOT}` are also available in hook and MCP server contexts.

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
