---
type: template
---

# Agent Authoring

Conventions for content consumed by agents: skills, conventions, plans, actions, CLAUDE.md files, and CLI tools.

## Writing Style

### Grammar

- Omit grammar articles (a, an, the) — agents parse structure, not prose
- Prioritize completeness over brevity — missing information causes incorrect assumptions
- Include examples only when rule is ambiguous without one

### Naming

- Use verbose names that convey purpose; capture full meaning in descriptions
- Do not truncate for visual format
- Script names match domain concept — `navigator_cli.py` not `cli.py` or `pt.py`
- Skill frontmatter `name` field uses plugin-name prefix — `ocd-navigator` not `navigator`; surfaces plugin name during search

### Content Rules

- Describe current reality; do not reference previous states, removed features, or change history
- Examples must be generic — use `module`, `client`, `library` not project-specific names

## Skill Architecture

- Deterministic operations belong in CLI scripts; non-deterministic steps (judgment, context-dependent decisions, natural language generation) stay in SKILL.md as agent-executed workflow instructions
- When continuing session that was mid-skill, re-read SKILL.md from disk before resuming — carried-over context may be stale

## Conventions

Before creating or modifying files, check for applicable conventions:

```
python3 ${CLAUDE_PLUGIN_ROOT}/skills/conventions/scripts/conventions_cli.py list-matching <file> [<file> ...]
```

Pass all target file paths in single call. Output groups each target file with its matching convention paths. If output is non-empty, read and follow returned convention files before proceeding.

## Structural Principles

- Structural decisions must be deterministic — divide, group, and organize based on functional principles that produce same result regardless of who evaluates them or when; do not use subjective thresholds ("too big", "complex enough", "feels painful") as triggers for structural action
- Every change must be followed through as if old way never existed; no compatibility shims, no split conventions; if refactor touches function, variable, path, or pattern, update every reference to match

## Process Flow Notation

Notation for workflow documents: skills, conventions, plans, actions. Required in always-on context — agents must parse and follow this notation during execution, not only when authoring. Not convention candidate.

### Structure

2 spaces per indentation level, no depth limit.

Numbers are ordered execution or evaluation. Bullets are unordered sub-items.

```
1. Ordered action
2. Ordered action
  - Unordered sub-item
  - Unordered sub-item
```

Em dash (`—`) separates step label from description. Label is action verb or short imperative; description elaborates. Semicolons add qualifications, context, or constraints inline after action. Hyphen (`-`) is reserved for bullet sub-items.

```
1. Label — description of action; supporting context; constraint or exception
```

### Conditionals

`If X:`/`Else if X:`/`Else:` prefix. `If/Else if` is mutually exclusive — stop at first match. Chain may end with `Else if` or `Else`. `Else` is universal fallback when all prior conditions fail. Repeated `If/If` at same level is independent evaluation — multiple conditions may fire. Standalone `If` with no `Else` is valid — alternative is "proceed to next step." Never mix two forms in same chain — chain is either `If/Else if` (mutually exclusive) or `If/If` (independent), not both.

```
1. If condition:
  1. Action
2. Else if condition:
  1. Action
3. Else:
  1. Action
```

### Iteration and Events

`For each X:` prefix iterates over collection. `While X:` prefix repeats while condition holds. `When X:` prefix is event-triggered step — reactive to state change rather than evaluated at fixed point in sequence.

```
1. While condition:
  1. Action
2. For each item:
  1. Action
3. When event occurs:
  1. Action
```

Any `{prefix}:` places all associated actions as indented children. Never inline after colon. Return to parent indentation signals end of body.

### Flow Control

`STOP` is early exit from loop, always followed by reason. `EXIT` is early exit from current process, always followed by reason. `Go to step N. Label` jumps forward or backward to numbered step — always includes both step number and label to survive renumbering.

```
1. While condition:
  1. Action
  2. If condition:
    1. STOP and report reason
2. If condition:
  1. EXIT and report reason
3. If condition:
  1. Go to step 6. Dispatch
```

### Assignment

`{name} = value` sets named variable for use in downstream steps. Variable names use curly braces and dashes (same as argument value references). Assignment is an action within a step — appears after step number or as child of conditional.

```
1. {target-directory} = parent of resolved SKILL.md path
2. If condition:
  1. {selected-workflow} = Self-Evaluation
3. Pass {target-directory} to navigator CLI
```

Variables must be assigned before use. Unassigned variable references are authoring errors — efficacy testing should flag them.

### Concurrency

`async` prefix is concurrent execution. Return to parent indentation signals await point.

```
1. Dispatch operations
  - async Operation A
  - async Operation B
2. Action (awaits concurrent operations)
```

### Subprocesses

Subprocesses are extracted under their own heading with own steps, referenced by name in parent flow. Heading depth is relative to context (one level below parent heading).

```
1. For each item:
  1. Dispatch Subprocess Name

### Subprocess Name

1. Action
2. Action
```

### Grouping Headings

Grouping headings organize contiguous steps within single process. Steps continue numbering across headings — heading is label, not numbering reset. Heading depth is one level below parent process heading.

```
## Agent Workflow

### Discovery

1. Action
2. Action

### Evaluation

3. Action
4. Action
```

## Skill Argument Notation

Notation for skill `argument-hint` frontmatter and workflow argument references. Defines how skills declare arguments and how workflows reference argument values during execution. Required in always-on context — agents must parse argument hints to understand skill interfaces and follow `{flag}` references to resolve values during workflow execution.

### Argument Hint Format

`argument-hint` field in SKILL.md frontmatter declares skill arguments using CLI-style format. Agents read this to understand what arguments skill accepts, which are required, and what values they expect.

Format elements:

| Required | Optional | Description |
|----------|----------|-------------|
| `<value>` | `[value]` | Value placeholder |
| `<x \| y>` | `[x \| y]` | Choice — one of listed alternatives |
| N/A | `[--flag]` | Boolean flag — presence means true, absence means false |
| `--flag <value>` | `[--flag <value>]` | Flag with value — flag consumes following value |
| N/A | `[--flag <value> ...]` | Repeatable — flag may appear multiple times, each with own value |

Angle brackets `<>` denote required values. Square brackets `[]` denote optional elements and drop inner angle brackets. Boolean and repeatable flags are always optional.

Examples:

```
--target <path | /skill-name | project | self | natural language goal> [--pattern <glob> ...] [--all] [--delegate]
```

- `--target` — required flag with required choice value; must be one of: path, /skill-name, `project`, `self`, or natural language goal
- `[--pattern <glob> ...]` — optional repeatable flag with value; each occurrence consumes glob text
- `[--all]` — optional boolean flag; presence means include all
- `[--delegate]` — optional boolean flag; presence means delegate execution

```
--target </skill-name | natural language scenario> [--delegate]
```

- `--target` — required flag with required choice value; skill name or free text
- `[--delegate]` — optional boolean flag

### Workflow Argument References

Workflows reference arguments using two forms — `--flag` for flag existence and `{flag}` for flag value. This separates presence checks from value resolution, making data flow explicit.

`--flag` refers to flag itself — existence, iteration over instances:
- Conditions check presence — `If --flag:` or `If not --flag:`
- Iteration over repeatable instances — `For each --flag:`

`{flag}` always resolves to value associated with flag:
- For value flags — `{flag}` resolves to text value passed with flag
- For repeatable flags — `{flag}` inside `For each --flag:` resolves to current item's value
- Boolean flags have no value — use `--flag` only, never `{flag}`

Reference patterns in workflow steps:

```
1. If {target} starts with `/`:
  1. Resolve skill path from {target}
2. Else if {target} is `project`:
  1. Set target directory to project root
```

```
1. If --pattern:
  1. For each --pattern:
    1. Pass {pattern} to navigator CLI as filter
```

```
1. If --delegate:
  1. Spawn background agent
2. Else:
  1. Execute inline
```

### Relationship to Process Flow Notation

Skill Argument Notation extends Process Flow Notation for skill-specific constructs. PFN defines how to write workflow steps (conditionals, iteration, flow control). Argument notation defines how those steps reference skill inputs. Both are required context — PFN for step structure, argument notation for data flow within steps.

## CLI Design

### Agent-facing vs internal scripts

Agent-facing CLIs are executables that agents call directly during tasks. They are primary interface between agents and deterministic operations. Internal scripts are implementation details called by plugin infrastructure (hooks, commands) — agents never invoke them.

Naming convention:
- `<name>_cli.py` (or `<name>_cli.sh`, etc.) — agent-facing entry point; agents call it directly, read its `--help`, and parse its output
- `<name>.py` (or `<name>.sh`, etc.) — internal library or internal script; called by plugin hooks, commands, or other scripts

Absence of `_cli` file for domain concept indicates missing CLI capabilities — deterministic operations should have agent-facing entry point.

### Interpreter

- `python3` not `python` — explicit interpreter version
- No shebangs, no execute permissions — scripts are invoked via interpreter prefix
