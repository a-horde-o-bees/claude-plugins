---
pattern: "*"
depends:
  - .claude/rules/ocd-design-principles.md
---

# Process Flow Notation

Structured programming for agent workflows. Indentation scopes blocks. Required in always-on context — agents must parse and follow this notation during execution, not only when authoring.

## Execution Model

PFN constructs map to familiar programming concepts:

| Concept | PFN Syntax | Python Analogy |
|---------|------------|----------------|
| Sequential | Numbered steps | Lines of code |
| Scope | 4-space indentation | 4-space indentation |
| Conditional | `If/Else if/Else:` | `if/elif/else:` |
| Iteration | `For each:`, `While:` | `for:`, `while:` |
| Event trigger | `When:` | Signal handler |
| Assignment | `{name} = value` | `name = value` |
| Skip iteration | `Continue next {item}` | `continue` |
| Exit loop | `Break loop` | `break` |
| Exit to user | `Exit to user` | `sys.exit()` |
| Agent call | `Spawn agent with:` | `async def` + `await` |
| Return to caller | `Return` / `Return:` | `return` / `return value` |
| Concurrency | `async` prefix | `asyncio.TaskGroup` |
| Jump | `Go to step N. Label` | — |
| Subroutine | Subprocess heading | `def` |
| Invocation type | `skill:`, `bash:`, `{tool}:` | decorator / annotation |

## Scoping

Indentation is the scope mechanism — 4 spaces per level, no depth limit. All `{prefix}:` constructs open a block. Single-action blocks may inline after the colon. Multi-action blocks place actions as indented children — never mix an inline action with indented children on the same block. Return to parent indentation signals the end of a block.

Flow control keywords are scope-relative — indentation determines which scope they exit:

| Keyword | Exits | Content |
|---------|-------|---------|
| `Continue next {item}` | Current iteration — skip to next | Self-describing via loop variable |
| `Break loop` | Current loop — exit entirely | Reason after em dash |
| `Exit to user` | Current process — halt workflow | Reason after em dash |
| `Return` / `Return:` | Agent block — hand back to caller | Optional (`Return:` + children, or bare `Return`) |

`Go to step N. Label` jumps forward or backward to a numbered step — always includes both step number and label to survive renumbering.

## Agent Spawning

`Spawn agent with:` delegates work to a spawned agent. Indented children are the agent instructions. Return to parent indentation signals control back to the caller. `Return` / `Return:` defines what the agent hands back.

```
1. Spawn agent with conflict detection:
    1. Read all files at current level
    2. If no conflicts found: Return
    3. Identify semantic conflicts
    4. Return:
        - Horizontal conflicts with citations
        - Vertical conflicts with citations
2. Present results to user
```

Within skills, intelligent work delegation uses `Spawn agent with:` exclusively. Tool calls (CLI scripts, bash commands) are not agent spawns and remain unrestricted. The orchestrator applies user-directed corrections inline — no agent spawn needed for directed fixes.

`async` composes with `Spawn agent with:` for concurrent agents:

```
1. For each {file} in {target-files}:
    1. Spawn agent with conformity check:
        1. Read instructions
        2. Apply to {file}
        3. Return:
            - Changes applied
            - Observations
    - async agent per target file
2. Review all results
```

## Conditionals

`If X:`/`Else if X:`/`Else:` prefix. `If/Else if` is mutually exclusive — stop at first match. Chain may end with `Else if` or `Else`. `Else` is the universal fallback when all prior conditions fail. Repeated `If/If` at the same level is independent evaluation — multiple conditions may fire. Standalone `If` with no `Else` is valid — the alternative is "proceed to next step." Never mix the two forms in the same chain.

```
1. If condition: single action
2. Else if condition:
    1. Action A
    2. Action B
3. Else: fallback action
```

## Iteration and Events

`For each {item} in {collection}:` iterates over a collection — names both the loop variable and source. `While X:` repeats while the condition holds. `When X:` is event-triggered — reactive to a state change rather than evaluated at a fixed point in the sequence.

```
1. For each {file} in {target-files}:
    1. If {file} invalid: Continue next {file}
    2. Process {file}
    3. If threshold reached: Break loop — all targets processed
2. When event occurs:
    1. Handle event
```

## Assignment

`{name} = value` sets a named variable for downstream steps. Variable names use curly braces and dashes. Variables use shared scope — assignment makes the variable available to all subsequent steps at any depth, including inside `Spawn agent with:` blocks. This matches natural language reading where context carries forward sequentially. Variables must be assigned before use — unassigned references are authoring errors.

```
1. {target-directory} = parent of resolved SKILL.md path
2. If condition:
    1. {selected-workflow} = Self-Evaluation
3. Pass {target-directory} to target CLI
```

## Concurrency

`async` prefix marks concurrent execution. Return to parent indentation signals the await point.

```
1. Dispatch operations
    - async Operation A
    - async Operation B
2. Action (awaits concurrent operations)
```

## Presentation Format

Numbers are ordered execution or evaluation. Bullets (`-`) are unordered sub-items.

Em dash (`—`) separates step label from optional description. Label is an action verb or short imperative; description elaborates context, purpose, or constraints — never an imperative action that could be executed independently. Include em dash descriptions only when they add value; omit when the label or children are self-evident. Semicolons add qualifications or constraints inline.

```
1. Label — description of action; supporting context; constraint or exception
```

Subprocesses are extracted under their own heading with their own steps, referenced by name in the parent flow. Heading depth is one level below the parent heading.

Grouping headings organize contiguous steps within a single process. Steps continue numbering across headings — a heading is a label, not a numbering reset.

## Invocation Types

When a step delegates to a specific execution mechanism, an invocation type prefixes the command: `{mechanism}: {command}`. This disambiguates how the agent executes the step — which tool or interface to use.

| Prefix | Mechanism | Example |
|--------|-----------|---------|
| `skill:` | Skill tool | `skill: /ocd-commit` |
| `bash:` | Bash tool | `bash: \`claude plugins marketplace update\`` |
| `{tool}:` | Dedicated tool (Read, Grep, Glob, etc.) | `Read: \`settings.json\`` |

The prefix can appear after an em dash (`1. Commit — skill: /ocd-commit`) or standalone (`- bash: \`command\``). Invocation types are optional — omit when the mechanism is unambiguous from context. Use when a workflow mixes mechanisms and the agent needs to distinguish between them. Steps without an invocation type are executed by agent judgment.

```
1. Commit — skill: `/ocd-commit`
2. Push — skill: `/ocd-push --branch main`
3. Marketplace refresh — bash: `claude plugins marketplace update`
4. Update plugins:
    - bash: `claude plugins update ocd@marketplace`
    - bash: `claude plugins update blueprint@marketplace`
5. If rules changed:
    1. Suggest session restart
```

## Skill Argument Notation

Notation for skill `argument-hint` frontmatter and workflow argument references. Required in always-on context — agents must parse argument hints to understand skill interfaces and follow `{flag}` references to resolve values during workflow execution.

### Argument Hint Format

The `argument-hint` field in SKILL.md frontmatter declares skill arguments using CLI-style format. Agents read this to understand what arguments a skill accepts, which are required, and what values they expect.

Format elements:

| Required | Optional | Description |
|----------|----------|-------------|
| `<value>` | `[value]` | Value placeholder |
| `<x \| y>` | `[x \| y]` | Choice — one of the listed alternatives |
| N/A | `[--flag]` | Boolean flag — presence means true, absence means false |
| `--flag <value>` | `[--flag <value>]` | Flag with value — flag consumes the following value |
| N/A | `[--flag <value> ...]` | Repeatable — flag may appear multiple times, each with its own value |

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

`--flag` refers to the flag itself — existence, iteration over instances:
- Conditions check presence — `If --flag:` or `If not --flag:`
- Iteration over repeatable instances — `For each --flag:`

`{flag}` always resolves to the value associated with the flag:
- For value flags — `{flag}` resolves to the text value passed with the flag
- For repeatable flags — `{flag}` inside `For each --flag:` resolves to the current item's value
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
        1. Pass {pattern} to target CLI as filter
```

```
1. If --delegate:
    1. Spawn background agent
2. Else:
    1. Execute inline
```

### Relationship to Process Flow Notation

Skill Argument Notation extends Process Flow Notation for skill-specific constructs. PFN defines how to write workflow steps (conditionals, iteration, flow control). Argument notation defines how those steps reference skill inputs. Both are required context — PFN for step structure, argument notation for data flow within steps.
