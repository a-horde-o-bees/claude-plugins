# Agent Authoring

Conventions for content consumed by agents: skills, conventions, plans, actions, CLAUDE.md files, and CLI tools.

## Writing Style

### Grammar

- Omit grammar articles (a, an, the) — agents parse structure, not prose
- Prioritize completeness over brevity — missing information causes incorrect assumptions
- Include examples only when a rule is ambiguous without one

### Naming

- Use verbose names that convey purpose; capture full meaning in descriptions
- Do not truncate for visual format
- Script names match domain concept — `navigator_cli.py` not `cli.py` or `pt.py`

### Content Rules

- Describe current reality; do not reference previous states, removed features, or change history
- Examples must be generic — use `module`, `client`, `library` not project-specific names

## Skill Architecture

- Deterministic operations belong in CLI scripts; non-deterministic steps (judgment, context-dependent decisions, natural language generation) remain as agent-executed workflow instructions in SKILL.md
- When continuing a session that was mid-skill, re-read SKILL.md from disk before resuming — carried-over context may be stale

## Structural Principles

- Structural decisions must be deterministic — divide, group, and organize based on functional principles that produce the same result regardless of who evaluates them or when; do not use subjective thresholds ("too big", "complex enough", "feels painful") as triggers for structural action
- Every change must be followed through as if the old way never existed; no compatibility shims, no split conventions; if a refactor touches a function, variable, path, or pattern, update every reference to match

## Process Flow Notation

Notation for workflow documents: skills, conventions, plans, actions. Required in always-on context — agents must parse and follow this notation during execution, not only when authoring. Not a convention candidate.

### Structure

2 spaces per indentation level, no depth limit.

Numbers are ordered execution or evaluation. Bullets are unordered sub-items.

```
1. Ordered action
2. Ordered action
  - Unordered sub-item
  - Unordered sub-item
```

Em dash (`—`) separates step label from description. Label is the action verb or short imperative; description elaborates. Semicolons add qualifications, context, or constraints inline after the action. Hyphen (`-`) is reserved for bullet sub-items.

```
1. Label — description of action; supporting context; constraint or exception
```

### Conditionals

`If X:`/`Else if X:`/`Else:` prefix. `If/Else if` is mutually exclusive — stop at first match. Chain may end with `Else if` or `Else`. `Else` is universal fallback when all prior conditions fail. Repeated `If/If` at same level is independent evaluation — multiple conditions may fire. A standalone `If` with no `Else` is valid — the alternative is "proceed to next step." Never mix the two forms in the same chain — a chain is either `If/Else if` (mutually exclusive) or `If/If` (independent), not both.

```
1. If condition:
  1. Action
2. Else if condition:
  1. Action
3. Else:
  1. Action
```

### Iteration and Events

`For each X:` prefix iterates over a collection. `While X:` prefix repeats while condition holds. `When X:` prefix is an event-triggered step — reactive to a state change rather than evaluated at a fixed point in sequence.

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

`STOP` is early exit from loop, always followed by reason. `EXIT` is early exit from current process, always followed by reason.

```
1. While condition:
  1. Action
  2. If condition:
    1. STOP and report reason
2. If condition:
  1. EXIT and report reason
```

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

Grouping headings organize contiguous steps within a single process. Steps continue numbering across headings — heading is a label, not a numbering reset. Heading depth is one level below the parent process heading.

```
## Agent Workflow

### Discovery

1. Action
2. Action

### Evaluation

3. Action
4. Action
```

## CLI Design

### Agent-facing vs internal scripts

Agent-facing CLIs are executables that agents call directly during tasks. They are the primary interface between agents and deterministic operations. Internal scripts are implementation details called by plugin infrastructure (hooks, commands) — agents never invoke them.

Naming convention:
- `<name>_cli.py` (or `<name>_cli.sh`, etc.) — agent-facing entry point; agents call it directly, read its `--help`, and parse its output
- `<name>.py` (or `<name>.sh`, etc.) — internal library or internal script; called by plugin hooks, commands, or other scripts

Absence of a `_cli` file for a domain concept indicates missing CLI capabilities — deterministic operations should have an agent-facing entry point.

### Interpreter

- `python3` not `python` — explicit interpreter version
- No shebangs, no execute permissions — scripts are invoked via interpreter prefix
