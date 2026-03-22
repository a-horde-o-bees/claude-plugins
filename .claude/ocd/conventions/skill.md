---
pattern: "SKILL.md"
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
| `## File Map` | Dependencies and created files (see markdown.md File Map pattern) |
| Description paragraph | What skill does (also serves as `description` fallback if no frontmatter) |
| `## Process Model` | Conceptual model of how skill operates and why (optional — for skills with non-obvious mechanics) |
| `## Trigger` | When user invokes this skill |
| `## Resolve Arguments` | Argument parsing and validation, before Workflow |
| `## Delegate Execution` | Instructions for `--delegate` agent delegation (optional — only for self-contained skills) |
| `## Workflow` | Numbered steps using Process Flow Notation |
| `## Rules` | Constraints and guardrails |
| `## Report` | Output format for skill results |

Not all sections required — simple skills may only need title, description, and rules list.

Process Model is optional — only for skills where the workflow's correctness depends on mechanics that are not self-evident from the steps themselves.

Resolve Arguments separates argument parsing from Workflow — Workflow assumes arguments are already resolved. Delegate Execution is optional — only for skills that are fully autonomous (no user interaction mid-workflow). Report defines the output format used by both inline execution and delegated agents.

String substitution variables available in body:
- `$ARGUMENTS` — All arguments passed when invoking skill
- `$ARGUMENTS[N]` or `$N` — Specific argument by 0-based index
- `${CLAUDE_SESSION_ID}` — Current session ID

## Directory Structure

```
skill-name/
├── SKILL.md           # Main instructions (required)
├── references/        # Detailed reference docs (optional)
├── examples/          # Example output (optional)
└── scripts/           # Executable scripts (optional)
```

Keep SKILL.md under 500 lines. Move detailed reference material to separate files.

## Sub-Agent Interactivity Constraint

AskUserQuestion only works in main conversation context. Sub-agents spawned via Task tool run autonomously — they cannot prompt user mid-execution.

Design rule: Skills that spawn sub-agents must be fully autonomous — no interactive checkpoints inside delegated work. Preferred approach is report pattern: skill runs autonomously, collects all findings, presents report with recommendations. User decides next steps after reviewing.

When interactive decisions are unavoidable mid-workflow, use orchestration pattern — structure them as orchestration steps in main conversation between autonomous sub-agent calls.

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
| Plugin | `<plugin>/skills/*/SKILL.md` |
