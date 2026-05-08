# Process Flow Notation

Structured programming for agent workflows. Loaded by sources that declare `requires: process-flow-notation` in their frontmatter — agents read this once when any dependent fires, then parse and follow the notation in those sources.

## Steps

Numbered steps are ordered execution. Each step is an atomic action or construct — do not compound multiple steps into one call, and do not write compound commands inside a single step. Sequential structure is the contract.

```
1. Read configuration
2. Validate inputs
3. Process data
```

Bullets (`-`) are unordered sub-items within a step.

```
1. Collect results:
    - Changes applied
    - Observations found
```

## Scoping

Indentation is the scope mechanism — 4 spaces per level. All constructs ending with `:` open a block. Single-action blocks may inline after the colon; multi-action blocks place actions as indented children. Outdenting to the parent indentation ends the block.

## Comments

**`—`** (em dash) — inline annotation on a step line. Elaborates context, purpose, or constraints — never an imperative action. Semicolons add qualifications inline.

**`>`** (blockquote) — standalone annotation between steps. Provides rationale or design notes; never acted on.

```
1. Read file — only the first 100 lines; skip binary files

> Defects auto-apply; observations require user judgment.

2. Process results
```

Grouping headings organize contiguous steps within a single process. Steps continue numbering across headings — a heading is a label, not a numbering reset. Every grouping heading is followed by a blockquote explaining why these steps form a distinct group.

## Assignment

**`{name} = value`** — sets a named variable for downstream steps. Names use curly braces and dashes. Variables share scope across the document; assignment makes them available at any subsequent depth. Unassigned references are authoring errors.

```
1. {target-path} = resolved SKILL.md path
2. If condition:
    1. {mode} = evaluation
3. Process {target-path}
```

Curly-brace notation is reserved for values assigned once and referenced later. When describing the shape of returned data (e.g., fields a `Return to caller:` hands back), use plain prose — decoration without downstream reference adds no execution meaning.

## Conditionals

**`If X:`** — executes block if true.

**`Else if X:`** — mutually exclusive alternative in an If chain; stops at first match.

**`Else:`** — universal fallback when all prior conditions in the chain fail.

If/Else if/Else is mutually exclusive — only one branch fires. Consecutive If/If at the same level is independent — multiple may fire. A new If at the same level implicitly ends the previous chain. If/If/Else is malformed when the author meant a mutually-exclusive set; correct or surface to the user.

```
> Mutually exclusive

1. If condition A: action A
2. Else if condition B: action B
3. Else: fallback

> Independent

4. If condition C: action C
5. If condition D: action D
```

## Loops

**`For each {item} in {collection}:`** — iterates a collection, names both loop variable and source.

**`While X:`** — repeats while condition holds.

**`Continue next`** — exits current iteration, skips to next element.

**`Break loop`** — exits the enclosing `For each:` or `While:`.

**`Go to step N. Label`** — jumps to a different step; both number and label survive renumbering.

```
1. For each {file} in {target-files}:
    1. If {file} invalid: Continue next {file}
    2. Process {file}
    3. If threshold reached: Break loop
```

## Invocations

All delegations follow the same shape — mechanism followed by what that mechanism needs.

| Prefix | Mechanism |
|--------|-----------|
| `skill:` | Skill tool — `skill: /<plugin>:<skill-name>` |
| `bash:` | Bash tool — `` bash: `command` `` |
| `tool-name:` | Dedicated tool (Read, Grep, Glob, MCP tools) — `tool-name: arg=value` |
| `Call:` | Read and follow a file or section |
| `Spawn:` | Delegate to a new agent |

Invocation prefix is optional when the mechanism is unambiguous from context; required when a workflow mixes mechanisms. The prefix may appear after an em-dash: `1. Action — skill: /<plugin>:<skill-name>`.

## Arguments

PFN content declares arguments in CLI-style format and references them in workflow steps using `--flag` (presence) and `{flag}` (value). Consumer conventions that embed PFN workflows declare their argument surface in this form.

### Declaration

| Required | Optional | Meaning |
|----------|----------|---------|
| `<value>` | `[value]` | Value placeholder |
| `<x \| y>` | `[x \| y]` | Choice — one of the alternatives |
| N/A | `[--flag]` | Boolean flag — presence means true |
| `--flag <value>` | `[--flag <value>]` | Flag with value |
| N/A | `[--flag <value> ...]` | Repeatable — flag may appear multiple times |

`<>` denotes required, `[]` denotes optional. Example: `--required <value> [--optional <value> ...] [--boolean-flag]`.

### Verb-Flag Pairing

When flags apply to specific verbs, pair them inline inside the choice rather than at the top level:

| Shape | Example |
|-------|---------|
| Flag required for one verb only | `<verb1 \| verb2 --flag <value>>` |
| Flag optional on one verb only | `<verb1 \| verb2 [--flag <value>]>` |
| Flag applies to all verbs | `<verb1 \| verb2> --flag <value>` |

Top-level listing loses the verb association; inline pairing is unambiguous.

### Positional vs Flag

Prefer positional values over flags when the input is a single required subject — the skill name already establishes the operating context; the flag adds ceremony without semantic value. Use a flag when the skill accepts multiple named inputs, when the input is genuinely optional (a flag is a natural default gate), or when convention ties the name to ecosystem meaning (`--branch`, `--scope`).

### Reference

**`--flag`** refers to the flag itself (presence, iteration). **`{flag}`** resolves to the value.

```
1. If --flag:
    1. For each --flag:
        1. Action using {flag}
```

## Call

**`Call:`** — reads and follows a file or section as instructions in the current execution context. Distinct from Read: which loads content without executing.

**`Return to caller`** — exits the current `Call:` block, handing control back.

Component file: an `_*.md` file containing steps extracted for reuse. The underscore prefix marks it internal to the enclosing flow's directory.

```
1. Call: `_component-name.md`
2. Call: `_component-name.md` ({var} = Content)
3. Call: `_component-name.md`
    - {var-1} = Content
    - {var-2} = Content
```

Arguments passed in parentheses or as indented assignments become variables in the called content. Called files declare expected variables in a `### Variables` section.

`Call:` to a section heading invokes an inline subprocess in the same document:

```
1. Call: Section-Name ({var} = Content)

## Section-Name

1. Action
2. Return to caller: Content
```

## Spawn

**`Spawn:`** — delegates work to a new agent in its own execution context.

**`Return to caller`** — exits the current `Spawn:` block, handing the result back.

Extracting agent instructions into a component file and using `Spawn: Call:` keeps the caller's context clean — the caller never reads the file; the agent reads only its own instructions.

```
1. Spawn: Call: `_component-name.md`
2. Spawn: Call: `_component-name.md` ({var} = Content)
3. Spawn:
    1. Call: `_component-name.md` ({var} = Content)
    2. Return to caller:
        - Content
```

### async

**`async`** — prefix on `Spawn:` that runs the agent concurrently. Outdenting to the parent indentation signals the await point.

```
1. For each {item} in {collection}:
    1. async Spawn:
        1. Call: `_component-name.md` ({var} = {item})
        2. Return to caller: Content
2. Action
```

### Continue

**`Continue {agent-ref}:`** — resumes a previously-spawned agent, retaining its full accumulated context. Use when a long-running workflow needs checkpoints between cycles and each must build on prior context; use a fresh `Spawn:` when no prior context is needed.

```
1. Spawn:
    1. Call: `_component-name.md`
2. {agent-ref} = the spawned agent
3. If condition:
    1. Continue {agent-ref}:
        1. Call: `_component-name.md`
```

## Exit

**`Exit to user`** — exits the entire process flow back to the human at the top of the chain, regardless of nesting. Used for both normal-flow exits (precondition failures, early completion) and error-path exits within `Error Handling:`. Intentional exits do not trigger Error Handling; only unhandled failures do.

**`Exit to user:`** — exits while emitting content. Inline form for a single emission; block form when multiple items exit together.

```
1. If precondition fails: Exit to user: Content
2. If recoverable error: Exit to user: Content — Annotation
3. If multi-item exit: Exit to user:
    - Content
    - Content
```

Em-dash on an `Exit to user:` line annotates *why* the exit fires (context for the reader); content after `:` is *what* gets emitted. Never use em-dash to carry emission content.

## Error Handling

**`Error Handling:`** — catches failures from all sibling steps above it and their descendants within the same parent block. Always the last step in a block that needs error recovery.

```
1. Action
2. Spawn:
    1. Call: `_component-name.md`
3. Action
4. Error Handling:
    1. Action
    2. Exit to user: Content — Annotation
```

Error Handling at step 4 catches failures from steps 1-3 and all their descendants; not from steps outside its parent block. Nest at different depths for different scopes.
