---
includes: "*.md"
governed_by:
  - .claude/rules/ocd/design-principles.md
  - .claude/rules/ocd/markdown.md
---

# Process Flow Notation

Structured programming for agent workflows. Indentation scopes blocks. Required in always-on context — agents must parse and follow this notation during execution, not only when authoring.

## Steps

Numbered steps are ordered execution. Each step is an action or construct.

```
1. Read configuration
2. Validate inputs
3. Process data
4. Report results
```

Bullets (`-`) are unordered sub-items within a step.

```
1. Collect results:
    - Changes applied
    - Observations found
    - Errors encountered
```

## Scoping

Indentation is the scope mechanism — 4 spaces per level, no depth limit. All constructs ending with `:` open a block. Single-action blocks may inline after the colon. Multi-action blocks place actions as indented children — never mix an inline action with indented children on the same block. Outdenting to the parent indentation signals the end of a block.

## Comments

Two forms of non-executable annotation at different positions.

**`—`** — inline annotation on a step line. Elaborates context, purpose, or constraints — never an imperative action that could be executed independently. Include only when the label or children are not self-evident. Semicolons add qualifications inline.

```
1. Read file — only the first 100 lines; skip binary files
2. Process results
```

**`>`** — standalone annotation between steps. Provides rationale, purpose, or design notes for surrounding steps. Sits between steps without breaking numbering and is never acted on.

```
3. Classify each finding

> Defects are safe to auto-apply. Observations require user judgment.

4. Apply defects
```

Grouping headings organize contiguous steps within a single process. Steps continue numbering across headings — a heading is a label, not a numbering reset. Every grouping heading is followed by a blockquote explaining why these steps form a distinct group.

```
### Setup

> Gather inputs before dispatch.

1. Read configuration
2. Discover scope

### Dispatch

> All agents launch concurrently.

3. Block push
4. Spawn agents
5. Unblock push
```

## Assignment

**`{name} = value`** — sets a named variable for downstream steps. Variable names use curly braces and dashes. Variables use shared scope — assignment makes the variable available to all subsequent steps at any depth. Variables must be assigned before use — unassigned references are authoring errors.

```
1. {target-path} = resolved SKILL.md path
2. If condition:
    1. {mode} = evaluation
3. Process {target-path}
```

Curly-brace notation is reserved for values assigned once and referenced later. When a step describes the shape of returned data — e.g., the fields a `Return to caller:` hands back, the structure of a tool's output — use plain prose, not `{name}`. Decoration without downstream reference adds no execution meaning.

## Conditionals

**`If X:`** — evaluates condition, executes block if true

**`Else if X:`** — mutually exclusive alternative in an If chain, stop at first match

**`Else:`** — universal fallback when all prior conditions fail

Two distinct forms: If/Else if/Else is mutually exclusive — only one branch fires. Consecutive If/If at the same level is independent evaluation — multiple conditions may fire. A new If at the same level implicitly ends the previous chain. Standalone If with no Else is valid — the alternative is "proceed to next step."

```
> Mutually exclusive — only one branch fires

1. If condition A: action A
2. Else if condition B: action B
3. Else: fallback

> Independent — both are evaluated separately

4. If condition C: action C
5. If condition D: action D
```

When an agent encounters If, If, Else at the same level, the Else belongs to the second If — the first If ended when the second If began. If the enclosed steps suggest the author intended a mutually exclusive chain, the pattern is malformed — correct it or surface to the user.

```
> Correct — verbose mode is independent of target existence

4. If verbose mode: enable logging
5. If target exists: process target
6. Else: report target not found

> Malformed — file/directory/unknown is mutually exclusive, should be If/Else if/Else

4. If target is file: process file
5. If target is directory: process directory
6. Else: report unknown target type
```

## Loops

**`For each {item} in {collection}:`** — iterates over a collection, names both loop variable and source

**`While X:`** — repeats while condition holds

**`Continue next`** — exits current iteration and skips to next `For each:` element

**`Break loop`** — exits current `For each:` or `While:` loop

**`Go to step N. Label`** — jumps to a different step; includes both step number and label to survive renumbering

```
1. For each {file} in {target-files}:
    1. If {file} invalid: Continue next {file}
    2. Process {file}
    3. If threshold reached: Break loop
```

## Invocations

All delegations follow the same structural pattern — mechanism: followed by what that mechanism needs.

| Prefix | Mechanism | Example |
|--------|-----------|---------|
| skill: | Skill tool | skill: /&lt;plugin&gt;:&lt;skill-name&gt; |
| bash: | Bash tool | bash: `command` |
| tool name: | Dedicated tool (e.g., Read, Grep, Glob, MCP tools) | tool-name: arg=value |
| Call: | Read and follow a file or section | Call: `_component-name.md` |
| Spawn: | Delegate to a new agent | Spawn: Call: `_component-name.md` |

```
1. skill: /<plugin>:<skill-name>
2. bash: `command`
3. Read: `file-path`
4. tool-name: arg=value
```

Invocation types are optional — omit when the mechanism is unambiguous from context. Use when a workflow mixes mechanisms and the agent needs to distinguish. Steps without an invocation type are executed by agent judgment. The prefix can appear after an em dash — `1. Action — skill: /<plugin>:<skill-name>`.

## Arguments

PFN content declares arguments in CLI-style format and references them in workflow steps using `--flag` (presence checks) and `{flag}` (value resolution). Consumer conventions that embed PFN workflows (e.g., skills, tool interfaces) declare their argument surface in this form.

### Declaration

Arguments are declared in CLI-style format.

| Required | Optional | Description |
|----------|----------|-------------|
| `<value>` | `[value]` | Value placeholder |
| `<x \| y>` | `[x \| y]` | Choice — one of the listed alternatives |
| N/A | `[--flag]` | Boolean flag — presence means true, absence means false |
| `--flag <value>` | `[--flag <value>]` | Flag with value |
| N/A | `[--flag <value> ...]` | Repeatable — flag may appear multiple times |

Angle brackets `<>` denote required values. Square brackets `[]` denote optional elements.

```
--required-flag <value> [--optional-flag <value> ...] [--boolean-flag]
```

### Verb-Flag Pairing

When flags apply to specific verbs, pair them inline inside the choice rather than listing them at the top level. The top-level form loses the association — readers can't tell which verb a flag belongs to or whether it's required for that verb.

| Shape | Example |
|-------|---------|
| Flag required for one verb only | `<verb1 \| verb2 --flag <value>>` |
| Flag optional on one verb only | `<verb1 \| verb2 [--flag <value>]>` |
| Flag applies to all verbs | `<verb1 \| verb2> --flag <value>` |

Inline pairing communicates at a glance which verb owns the flag and whether it's required for that verb. Flat listing at the top level implies the flag is universal when it isn't.

### Positional vs Flag

Prefer positional values over flags when the input is a single required subject. `<path>` reads cleaner than `--target <path>` — the skill name already establishes what's being operated on; the flag adds ceremony without semantic value. Use a flag when the skill accepts multiple named inputs that need disambiguation, when the input is genuinely optional and a flag is a natural default gate, or when convention ties the name to established ecosystem meaning (e.g., `--branch`, `--scope`).

### Reference

**`--flag`** — refers to the flag itself, existence and iteration.

**`{flag}`** — resolves to the value.

```
1. If --flag:
    1. For each --flag:
        1. Action using {flag}

2. If {variable-name} matches condition:
    1. Action
3. Else if {variable-name} matches other condition:
    1. Action
```

## Call

**`Call:`** — reads and follows a file or section as instructions in the current execution context

**`Return to caller`** — exits the current `Call:` block, handing control back to the invoking subflow

Distinct from Read: which loads content into context without executing it.

**Component file.** An `_*.md` file containing steps extracted for reuse via `Call:` or `Spawn: Call:`. The underscore prefix marks it internal to the enclosing flow's directory. Consumer conventions define when extraction is warranted; PFN defines the invocation mechanics.

```
1. Call: `_component-name.md`
2. Call: `_component-name.md` ({variable-name} = Content)
3. Call: `_component-name.md`
    - {variable-name} = Content
    - {variable-name} = Content
```

Arguments passed in parentheses or as indented assignments become variables available within the called content. Called files declare expected variables in a `### Variables` section:

```
# Component Flow

### Variables

- {variable-name} — Annotation
- {variable-name} — Annotation

### Process

1. For each {item} in {collection}:
    1. Action
```

`Call:` to a section heading invokes an inline subprocess within the same document:

```
1. Call: Section-Name ({variable-name} = Content)

## Section-Name

1. Action
2. Return to caller: Content
```

## Spawn

**`Spawn:`** — delegates work to a new agent in its own execution context

**`Return to caller`** — exits the current `Spawn:` block, handing the result back to the invoking subflow

Extracting agent instructions into a component file and using `Spawn: Call:` keeps the caller's context clean while giving the agent exactly what it needs — the caller never reads the file, and the agent reads only its own instructions. Inline spawn instructions work for short sequences but load the caller's context with content only the agent uses.

```
1. Spawn: Call: `_component-name.md`
2. Spawn: Call: `_component-name.md` ({variable-name} = Content)
3. Spawn:
    1. Call: `_component-name.md` ({variable-name} = Content)
    2. Return to caller:
        - Content
```

### async

**`async`** — prefix on `Spawn:` that runs the agent concurrently. Outdenting to the parent indentation signals the await point.

```
1. For each {item} in {collection}:
    1. async Spawn:
        1. Call: `_component-name.md` ({variable-name} = {item})
        2. Return to caller:
            - Content
2. Action
```

### Continue

**`Continue {agent-ref}:`** — resumes a previously-spawned agent, retaining its full accumulated context from prior cycles. The agent reference is captured as a variable from the `Spawn:` step.

Use `Continue` when a long-running workflow needs checkpoints between cycles and each cycle must build on prior context. Use a fresh `Spawn:` when no prior context is needed.

```
1. Spawn:
    1. Call: `_component-name.md` ({variable-name} = Content)
    2. Return to caller:
        - Content
2. {agent-ref} = the spawned agent
3. Action
4. If {variable-name} matches condition:
    1. Continue {agent-ref}:
        1. Call: `_component-name.md` ({variable-name} = Content)
        2. Return to caller:
            - Content
5. Action
```

## Exit

**`Exit to user`** — exits the entire process flow back to the human at the top of the chain, regardless of how deeply nested the current block is. Used for both normal-flow exits (precondition failures, early completion) and error-path exits within `Error Handling:` blocks. Intentional exits in normal flow do not trigger Error Handling; only unhandled failures do.

**`Exit to user:`** — exits while emitting content, symmetric with `Return to caller:` but jumps to the top instead of one level up. Inline form for a single emission; block form when multiple items exit together.

```
1. If precondition fails: Exit to user: Content
2. If recoverable error: Exit to user: Content — Annotation
3. If multi-item exit: Exit to user:
    - Content
    - Content
```

Em-dash on an `Exit to user:` line annotates *why* the exit fires (context for the reader); content after `:` is *what* gets emitted to the user. Never use em-dash to carry emission content.

## Error Handling

**`Error Handling:`** — catches failures from all sibling steps above it and their descendants within the same parent block

Always the last step in a block that needs error recovery.

```
1. Action
2. Spawn:
    1. Call: `_component-name.md`
    2. Return to caller:
        - Content
3. Action
4. Error Handling:
    1. Action
    2. Exit to user: Content — Annotation
```

> Comment — Error Handling at step 4 catches failures from steps 1-3 and all their descendants. It does not catch failures from steps outside its parent block.

Error Handling can be nested at different depths for different scopes:

```
1. Action
2. Inner block:
    1. Action
    2. Action
    3. Error Handling:
        1. Action
        2. Exit to user: Content — Annotation
3. Action
4. Error Handling:
    1. Action
    2. Exit to user: Content — Annotation
```

## Reference

PFN constructs and their programming analogues:

| Concept | PFN Syntax | Python Analogy |
|---------|------------|----------------|
| Sequential | Numbered steps | Lines of code |
| Unordered | Bullets (-) | List items |
| Scope | 4-space indentation | 4-space indentation |
| Inline comment | — (em dash) | `# end-of-line comment` |
| Block comment | > (blockquote) | `# standalone comment` |
| Assignment | {name} = value | `name = value` |
| Conditional | If/Else if/Else: | `if/elif/else:` |
| Iteration | For each:, While: | `for:`, `while:` |
| Loop control | Continue next, Break loop | `continue`, `break` |
| Jump | Go to step N. Label | — |
| Invocation | mechanism: content | Uniform calling convention |
| Call | Call: | `function()` |
| Spawn | Spawn: | `asyncio.create_task()` |
| Resume | Continue {agent-ref}: | Message to running coroutine |
| Return | Return to caller / Return to caller: | `return` / `return value` |
| Concurrency | async Spawn: | `asyncio.TaskGroup` |
| Error handling | Error Handling: | `except:` |
| Exit | Exit to user / Exit to user: | `sys.exit()` / `sys.exit(value)` |
