# Process Flow Notation

Structured programming for agent workflows. Indentation scopes blocks. Required in always-on context — agents must parse and follow this notation during execution, not only when authoring.

## Execution Model

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

## Scoping

Indentation is scope mechanism — 4 spaces per level, no depth limit. All `{prefix}:` constructs open a block. Single-action blocks may inline after colon. Multi-action blocks place actions as indented children — never mix inline action with indented children on same block. Return to parent indentation signals end of block.

Flow control keywords are scope-relative — indentation determines which scope they exit:

| Keyword | Exits | Content |
|---------|-------|---------|
| `Continue next {item}` | Current iteration — skip to next | Self-describing via loop variable |
| `Break loop` | Current loop — exit entirely | Reason after em dash |
| `Exit to user` | Current process — halt workflow | Reason after em dash |
| `Return` / `Return:` | Agent block — hand back to caller | Optional (`Return:` + children, or bare `Return`) |

`Go to step N. Label` jumps forward or backward to numbered step — always includes both step number and label to survive renumbering.

## Agent Spawning

`Spawn agent with:` delegates work to spawned agent. Indented children are agent instructions. Return to parent indentation signals control back to caller. `Return` / `Return:` defines what agent hands back.

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

Within skills, intelligent work delegation uses `Spawn agent with:` exclusively. Tool calls (CLI scripts, bash commands) are not agent spawns and remain unrestricted. Orchestrator applies user-directed corrections inline — no agent spawn needed for directed fixes.

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

`If X:`/`Else if X:`/`Else:` prefix. `If/Else if` is mutually exclusive — stop at first match. Chain may end with `Else if` or `Else`. `Else` is universal fallback when all prior conditions fail. Repeated `If/If` at same level is independent evaluation — multiple conditions may fire. Standalone `If` with no `Else` is valid — alternative is "proceed to next step." Never mix two forms in same chain.

```
1. If condition: single action
2. Else if condition:
    1. Action A
    2. Action B
3. Else: fallback action
```

## Iteration and Events

`For each {item} in {collection}:` iterates over collection — names both loop variable and source. `While X:` repeats while condition holds. `When X:` is event-triggered — reactive to state change rather than evaluated at fixed point in sequence.

```
1. For each {file} in {target-files}:
    1. If {file} invalid: Continue next {file}
    2. Process {file}
    3. If threshold reached: Break loop — all targets processed
2. When event occurs:
    1. Handle event
```

## Assignment

`{name} = value` sets named variable for downstream steps. Variable names use curly braces and dashes. Variables use shared scope — assignment makes variable available to all subsequent steps at any depth, including inside `Spawn agent with:` blocks. This matches natural language reading where context carries forward sequentially. Variables must be assigned before use — unassigned references are authoring errors.

```
1. {target-directory} = parent of resolved SKILL.md path
2. If condition:
    1. {selected-workflow} = Self-Evaluation
3. Pass {target-directory} to navigator CLI
```

## Concurrency

`async` prefix marks concurrent execution. Return to parent indentation signals await point.

```
1. Dispatch operations
    - async Operation A
    - async Operation B
2. Action (awaits concurrent operations)
```

## Presentation Format

Numbers are ordered execution or evaluation. Bullets (`-`) are unordered sub-items.

Em dash (`—`) separates step label from optional description. Label is action verb or short imperative; description elaborates context, purpose, or constraints — never imperative action that could be executed independently. Include em dash descriptions only when they add value; omit when label or children are self-evident. Semicolons add qualifications or constraints inline.

```
1. Label — description of action; supporting context; constraint or exception
```

Subprocesses are extracted under own heading with own steps, referenced by name in parent flow. Heading depth is one level below parent heading.

Grouping headings organize contiguous steps within single process. Steps continue numbering across headings — heading is label, not numbering reset.

## Skill Argument Notation

Notation for skill `argument-hint` frontmatter and workflow argument references. Required in always-on context — agents must parse argument hints to understand skill interfaces and follow `{flag}` references to resolve values during workflow execution.

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
