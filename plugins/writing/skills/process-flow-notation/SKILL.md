---
name: process-flow-notation
description: Apply when authoring an agent process flow with control flow beyond a linear sequence — conditionals, loops, variable binding, sub-routine calls, error handling, or nested blocks. Defines the notation that keeps non-trivial workflows readable and unambiguously executable. Plain sequential steps don't need PFN — write them as ordinary numbered markdown.
---

# Process Flow Notation

Structured programming for agent workflows. Skills author process flows in this notation; agents execute them by reading it — an agent interprets a flow without this manual in context.

Each construct is given once as a **format and its outcome**: write it this way, and this is what happens. This is one cohesive set of formats whose interpretation tests reliably; it does not restate how constructs combine, police malformed input, or claim guaranteed interpretation.

## When to use

Use PFN when a flow has control flow beyond a linear sequence — conditionals, loops, variables, sub-routine calls, error handling, nesting. Otherwise plain numbered markdown is enough.

## Steps

- A **numbered step** is one ordered action or construct. Keep one executable action per step — don't compound actions on a line, and don't place an action inside an annotation (the agent runs any instruction it reads).
- **Bullets** (`-`) are unordered sub-items of a step.
- **Indentation** is scope, 4 spaces per level: a construct ending in `:` opens a block, indented lines are its children, and outdenting to the parent ends it.
- A **grouping heading** labels contiguous steps; numbering continues across it.

## Annotations

- **`—`** (em-dash) — an inline note on a step.
- **`>`** (blockquote) — a standalone note between steps.

## Variables

**`{name}: <block>`** binds a variable to the block's value:

- inline value — `{x}: 42`
- bash stdout — `` {x}: bash: `cmd` ``
- a call's return — `{x}: Call: _file.md`
- a conditional — `{x}: <a> if <cond> else <b>`
- an indented sub-block — its final assignment or return
- a loop accumulator — `{acc}:` then a `For each:` block that builds it

Names use `{curly-dashes}` and are visible at any later depth; reference a name after binding it. Use `{...}` for values reused later; describe the shape of returned data in plain prose.

## Conditionals

- **`If X:`** — run the block when X is true.
- **`Else if X:`** / **`Else:`** — exclusive chain after an `If`; one branch fires.
- Consecutive **`If`** / **`If`** — independent; each may fire.

## Loops

- **`For each {item} in {collection}:`** / **`While X:`** — iterate.
- **`Continue next`** — skip to the next iteration.
- **`Break loop`** — exit the loop.
- **`Go to step N`** — jump to a step.

## Invocations

A step's action delegates by a prefix; the target sets the mechanism:

- **`skill:`** — the Skill tool: `skill: /<plugin>:<skill-name>`, written bare (no trailing parenthetical — the whole skill applies).
- **`bash:`** — the Bash tool: `` bash: `cmd` ``.
- **`Read:` / `Grep:` / `Glob:` / MCP tools** — a named tool: `tool-name: args`.
- **`Call:`** — read and follow a file or section as steps; a file or section, never a `/skill`.
- **`Spawn:`** — delegate to a new agent.

Reuse logic by factoring it into a `Call:` section or component file rather than repeating a `skill:`. The prefix is optional when the mechanism is clear, required when a flow mixes mechanisms. For a step's inline-vs-script placement, see `/workflow-vs-script`.

## Call and sections

- **`Call:`** reads and follows a file or section as instructions in the current context; **`Read:`** loads content without executing it.
- **`Return to caller`** hands control back.
- A **component file** is an `_*.md` of reusable steps in the flow's directory; the caller passes `{var}` values in parentheses or as indented assignments, and the file references them.
- **`Call: Section-Name`** runs a `##` section of the same document.

## Spawn

- **`Spawn:`** delegates to a new agent in its own context; **`Return to caller`** hands the result back.
- `Spawn: Call: _file.md` keeps the caller's context clean — only the agent reads the file.
- **`async Spawn:`** runs agents concurrently; the next outdented step runs after they complete.

## Exit

- **`Exit process`** — terminate the whole flow from any depth, unwinding all nested calls.
- **`Exit process:`** — terminate while emitting content (inline for one item, a block for several).

## Error Handling

- **`Error Handling:`** — the last step in a block; catches failures from its sibling steps above and their descendants.
- Nest at different depths for different scopes.

## Arguments

A skill declares its input surface CLI-style so an invoker knows what to pass — the skill's signature, not control flow. The body references a value as `{flag}` and a flag's presence as `--flag`.

| Format | Means |
|---|---|
| `<value>` / `[value]` | required / optional value |
| `<x \| y>` / `[x \| y]` | choice — one alternative |
| `[--flag]` | boolean flag |
| `--flag <value>` / `[--flag <value>]` | flag with a value |
| `[--flag <v> ...]` | repeatable flag |

Pair a flag with one verb inline — `<verb1 | verb2 --flag <v>>` — rather than at top level. Prefer a positional value for a single required subject; a flag for optional, named, or convention-bound inputs (`--branch`).
