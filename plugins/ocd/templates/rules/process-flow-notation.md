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

Indentation is the scope mechanism — 4 spaces per level, no depth limit. All constructs ending with `:` open a block. Single-action blocks may inline after the colon. Multi-action blocks place actions as indented children — never mix an inline action with indented children on the same block. Return to parent indentation signals the end of a block.

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

Curly-brace notation is reserved for values assigned once and referenced later. When a step describes the shape of returned data — the fields a Return: hands back, the structure of a tool's output — use plain prose, not `{name}`. Decoration without downstream reference adds no execution meaning.

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

**`When X:`** — event-triggered, reactive to a state change rather than evaluated at a fixed point in the sequence

**`Continue next`** — exits current iteration and skips to next `For each:` element

**`Break loop`** — exits current `For each:` or `While:` loop

**`Go to step N. Label`** — jumps to a different step; includes both step number and label to survive renumbering

```
1. For each {file} in {target-files}:
    1. If {file} invalid: Continue next {file}
    2. Process {file}
    3. If threshold reached: Break loop
2. When event occurs:
    1. Handle event
```

## Invocations

All delegations follow the same structural pattern — mechanism: followed by what that mechanism needs.

| Prefix | Mechanism | Example |
|--------|-----------|---------|
| skill: | Skill tool | skill: /ocd:commit |
| bash: | Bash tool | bash: `git status --porcelain` |
| tool name: | Dedicated tool (Read, Grep, Glob, MCP tools) | Read: `settings.json`, scope_analyze: paths=[{skill-path}] |
| Call: | Read and follow a file or section | Call: `_protocol.md` |
| Spawn: | Delegate to a new agent | Spawn: Call: `_workflow.md` |

```
1. skill: /ocd:commit
2. bash: `git status --porcelain`
3. Read: `settings.json`
4. scope_analyze: paths=[{skill-path}]
```

Invocation types are optional — omit when the mechanism is unambiguous from context. Use when a workflow mixes mechanisms and the agent needs to distinguish. Steps without an invocation type are executed by agent judgment. The prefix can appear after an em dash — `1. Commit — skill: /ocd:commit`.

Target format for `skill:` follows `/plugin:skill` when invoking a plugin skill, or `/skill` only when invoking a project-local skill. See `skill-md.md` Cross-Skill References for rationale.

## Arguments

PFN content declares arguments in CLI-style format and references them in workflow steps using `--flag` (presence checks) and `{flag}` (value resolution). The primary consumer is skill `argument-hint` frontmatter.

### Declaration

Arguments are declared in CLI-style format — in SKILL.md frontmatter this is the `argument-hint` field.

| Required | Optional | Description |
|----------|----------|-------------|
| `<value>` | `[value]` | Value placeholder |
| `<x \| y>` | `[x \| y]` | Choice — one of the listed alternatives |
| N/A | `[--flag]` | Boolean flag — presence means true, absence means false |
| `--flag <value>` | `[--flag <value>]` | Flag with value |
| N/A | `[--flag <value> ...]` | Repeatable — flag may appear multiple times |

Angle brackets `<>` denote required values. Square brackets `[]` denote optional elements.

```
--target <path | /skill-name> [--pattern <glob> ...] [--all]
```

### Reference

**`--flag`** — refers to the flag itself, existence and iteration.

**`{flag}`** — resolves to the value.

```
1. If --pattern:
    1. For each --pattern:
        1. Pass {pattern} to target CLI

2. If {target} starts with `/`:
    1. Resolve skill path from {target}
3. Else if {target} is `project`:
    1. Set target directory to project root
```

## Call

**`Call:`** — reads and follows a file or section as instructions in the current execution context

**`Return`** — exits the current `Call:` block, handing control back to the caller

Distinct from Read: which loads content into context without executing it.

```
1. Call: `_protocol.md`
2. Call: `_protocol.md` ({target} = resolved path)
3. Call: `_protocol.md`
    - {target} = resolved path
    - {scope} = scope result
```

Arguments passed in parentheses or as indented assignments become variables available within the called content. Called files declare expected variables in a `### Variables` section:

```
# Protocol Workflow

### Variables

- {target} — the resolved target path
- {scope} — scope_analyze result with governance metadata

### Process

1. For each {file} in {scope} files:
    1. Evaluate {file} against {target}
```

`Call:` to a section heading invokes an inline subprocess within the same document:

```
1. Call: Validation ({input} = collected data)

## Validation

1. Check {input} against schema
2. Return validation result
```

## Spawn

**`Spawn:`** — delegates work to a new agent in its own execution context

**`Return`** — exits the current `Spawn:` block, handing results back to the caller

Extracting agent instructions into a file and using `Spawn: Call:` keeps the caller's context clean while giving the agent exactly what it needs — the caller never reads the file, and the agent reads only its own instructions. Inline spawn instructions work for short sequences but load the caller's context with content only the agent uses.

Within skills, intelligent work delegation uses Spawn: exclusively. Tool calls (CLI scripts, bash commands) are not agent spawns and remain unrestricted. The skill executor applies user-directed corrections inline — no agent spawn needed for directed fixes.

```
1. Spawn: Call: `_workflow.md`
2. Spawn: Call: `_workflow.md` ({target} = resolved path)
3. Spawn:
    1. Call: `_evaluation-workflow.md` ({scope} = scope result)
    2. Return:
        - Findings
```

### async

**`async`** — prefix on `Spawn:` that runs the agent concurrently. Return to parent indentation signals the await point.

```
1. For each {file} in {target-files}:
    1. async Spawn:
        1. Call: `_conformity-check.md` ({file} = {file})
        2. Return:
            - Findings
2. Review all results
```

### isolation: "worktree"

**`isolation: "worktree"`** — parenthetical modifier on `Spawn:` that runs the agent in a git worktree, an isolated copy of the repository where file changes, commits, and skill invocations stay contained. Worktree creation and cleanup are handled by the system. Composes with `async`:

```
1. async Spawn (isolation: "worktree"):
    1. Call: `_migration.md` ({target} = migration target)
    2. Return:
        - Changes applied
2. Review results
```

### Continue

**`Continue {agent-ref}:`** — resumes a previously-spawned agent, retaining its full accumulated context from prior cycles. The agent reference is captured as a variable from the `Spawn:` step.

Use `Continue` when a long-running workflow needs checkpoints between cycles and each cycle must build on prior context. Use a fresh `Spawn:` when no prior context is needed.

```
1. Spawn:
    1. Call: `_level-evaluation.md` ({files} = {first-level-files})
    2. Return:
        - Findings for this level
2. {agent-ref} = the spawned agent
3. Process returned findings, decide whether to proceed
4. If continue:
    1. Continue {agent-ref}:
        1. Call: `_level-evaluation.md` ({files} = {next-level-files})
        2. Return:
            - Findings for this level
5. Process the new return the same way
```

## Error Handling

**`Error Handling:`** — catches failures from all sibling steps above it and their descendants within the same parent block

**`Exit to caller`** — exits the current process; intentional exits in normal flow do not trigger Error Handling, only unhandled failures do

Always the last step in a block that needs error recovery.

```
1. Block push
2. Spawn agents:
    1. Call: `_workflow.md`
    2. Return:
        - Findings
3. Unblock push
4. Error Handling:
    1. Unblock push — bash: `git config --unset remote.origin.pushurl`
    2. Exit to caller — dispatch failed
```

> Error Handling at step 4 catches failures from steps 1-3 and all their descendants. It does not catch failures from steps outside its parent block.

Error Handling can be nested at different depths for different scopes:

```
1. Outer operation
2. Inner block:
    1. Risky step A
    2. Risky step B
    3. Error Handling:
        1. Clean up inner resources
        2. Exit to caller — inner block failed
3. Continue with outer
4. Error Handling:
    1. Clean up outer resources
    2. Exit to caller — outer operation failed
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
| Event | When: | Signal handler |
| Loop control | Continue next, Break loop | `continue`, `break` |
| Jump | Go to step N. Label | — |
| Invocation | mechanism: content | Uniform calling convention |
| Call | Call: | `function()` |
| Spawn | Spawn: | `asyncio.create_task()` |
| Resume | Continue {agent-ref}: | Message to running coroutine |
| Return | Return / Return: | `return` / `return value` |
| Concurrency | async Spawn: | `asyncio.TaskGroup` |
| Isolation | Spawn (isolation: "worktree"): | Subprocess in temp directory |
| Error handling | Error Handling: | `except:` |
| Exit | Exit to caller | `sys.exit()` |
