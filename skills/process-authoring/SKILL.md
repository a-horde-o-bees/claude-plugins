---
name: process-authoring
description: Apply when authoring an agent process with control flow beyond a linear sequence (e.g. conditionals, loops, variable binding, sub-routine calls, error handling, nested blocks) to keep non-trivial processes readable and unambiguously executable. Not needed for simple sequential steps or lists.
---

# process-authoring

**process-authoring sets expectations, not meanings.** This guide is never in the executing agent's context — only the authored process is. So a construct cannot *define* a meaning the executor is bound to honor; it can only pick wording whose plain reading **reliably evokes the intended behavior in an agent that has never read this guide.**

The bar is therefore empirical. Each construct below names a behavior and the wording meant to evoke it cold; when wording fails to evoke its behavior, the *phrasing* is the defect to strengthen — never the executor faulted for "misreading" a meaning it was never given. `tests/` measures each construct this way (cold `claude -p`, no guide loaded), so a weak-evoking construct shows as a low hit-rate rather than a surprise in production.

## Steps

- **`1.`** — a numbered step: one ordered action or construct.
- **`-`** — a bullet: an unordered list or sub-item of a step.
- **Indentation** — scope, 4 spaces per level: a construct ending in `:` opens a block, indented lines are its children, and outdenting to the parent ends it.
- **Grouping subheading** — a label between contiguous steps; numbering continues across them.

## Annotations

- **`—`** (em-dash) — an inline note on a step.
- **`>`** (blockquote) — a standalone note between steps.

An annotation describes, never instructs — keep executable actions out, since an agent runs any instruction it reads wherever it sits.

## Variables

A variable uses `{curly-dashes}` and is visible at any later depth; bind it before referencing it.

**`{name}: <block>`** — binds the name to the block's value:

- inline value — `{x}: 42`
- bash stdout — `` {x}: Bash: `cmd` ``
- a call's return — `{x}: Call: [label](target)`
- an applied block's result — `{x}: Apply /skill to: <block>`
- a conditional — `{x}: <a> if <cond> else <b>`
- an indented sub-block — its final assignment or return
- a loop accumulator — `{acc}:` then a `For each:` block that builds it

## Conditionals

- **`If X:`** — run the block when X is true.
- **`Else if X:`** / **`Else:`** — exclusive chain after an `If`; one branch fires.
- **`If`** / **`If`** (consecutive) — independent; each will fire.

## Loops

- **`For each {item} in {collection}:`** / **`While X:`** — iterate.
- **`Continue next`** — skip to the next iteration.
- **`Break loop`** — exit the loop.
- **`Go to step N`** / **`Go to step X.Y.Z`** — jump to a step.

## Invocations

A step delegates by a prefix. The **prefix is the behavior**; the **target is what runs and how it resolves** — the two are independent, so each behavior takes either target form.

Behaviors:

- **`Call: target`** — *procedural*: read and follow the target as steps within the current context.
- **`Apply target to:`** — *behavioral*: run the indented block **through** the target as a lens — a discipline that shapes *how* the steps execute, not steps themselves. Opens a block; binds when assigned (`{x}: Apply /description-authoring, /concise-prose to: <block>`). Listed targets combine into a single lens over the block, interpreted together rather than as successive passes: `Apply /a, [b](#b) to:`.

Targets:

- **`/skill-name`** — a skill, resolved **by name** through the harness priority chain (never a hard-coded path) and run via the Skill tool. `Call: /skill` dispatches the skill; it does not Read its file. The harness **force-loads** the skill into context, so its steps cannot be paraphrased away unseen — prefer this form for a load-bearing sub-process.
- **`[label](target)`** — a file or section at a **known path**, resolved by reading it: `Call:` reads the target and follows it inline. Forms: `#anchor` (a `##` section of this document, resolved once the document is read whole or flattened), `relative.md`, `relative.md#section`, or `/absolute.md`. A file target is only as reliable as the executor actually opening it — an un-opened file is invisible, so its steps get improvised from the call site instead of run. When the target's exact steps are load-bearing (their wording carries a constraint unguessable from the call site), prefer the force-loaded `/skill` form, or gate a later step on an outcome only the file's steps produce.

Return:

- **`Return to caller`** — hands control back from a called section or file.
- **`Return to caller:`** — hands a returned result back to the caller (e.g. from a spawned agent).

### Tools

- **`Bash:`** — runs a shell command: `` `cmd` ``.
- **`Read:`** — loads content without executing it; the read-only counterpart to `Call:`.
- **`Grep:`** — searches file contents.
- **`Glob:`** — matches file paths.
- **`Tool: args`** — any other MCP tool, invoked by name.

### Procedure vs script

A process is **agent-facing instructions** (procedures) plus the **mechanical code** they invoke (scripts). Splitting it wrong is the defect this notation exists to expose, so classify every step by one test: *could a deterministic function with no agent context produce this result?* Yes → script; no → procedure.

- **Procedure** — reasoning, judgment, and contextual sequencing the agent steers; orchestration whose composition depends on intermediate results (skill calls, tool invocations, agent spawns); and the user-facing surface (review gates, clarifying questions, error-recovery dialogue).
- **Script** (a `Bash:` call or invoked module) — deterministic operations with no agent context (parsing, filtering, aggregation, format conversion, fixed-rule classification).

Prefer a script wherever one suffices — it preserves the agent's focus and context for the judgment only an agent can supply.

Two misclassifications to catch, each corrected in one direction:

- **Mechanical work stranded in a procedure** — a step doing parsing, filtering, or formatting the agent performs by hand. Tell: a deterministic function could replace it with nothing lost. Push it into a script.
- **Judgment buried in a script** — code branching on context, resolving ambiguity, or deciding what the agent should steer. Tell: a comment hedges ("if ambiguous…", a heuristic, a guessed default). Lift that decision into the calling procedure; leave the script the deterministic part.

## Spawn

- **`Spawn agent to:`** — delegates to a new agent with its own context.
- **`Spawn agent to: Call: [label](_file.md)`** — keeps the caller's context clean; only the agent reads the file.
- **`Spawn async agent to:`** — runs agents concurrently; the next outdented step runs after they complete.
- **`Spawn background agent to:`** — runs the agent in the background.

## Exit

- **`Exit process`** — terminate the whole flow from any depth, unwinding all nested calls.
- **`Exit process:`** — terminate while emitting content.

## Error handling

- **`If Error:`** — catches failures from its sibling steps above and their descendants; depth determines scope.

## Arguments

A process declares its input surface CLI-style so an invoker knows what to pass.

| Format | Interpretation |
| --- | --- |
| `<value>` / `[value]` | required / optional value |
| `<x \| y>` / `[x \| y]` | choice — one alternative |
| `[--flag]` | boolean flag |
| `--flag <value>` / `[--flag <value>]` | flag with a value |
| `[--flag <v> ...]` | repeatable flag |

- **`{flag}`** — references a flag's value.

Pair flags with their verb inline — `<verb1 | verb2 --flag <v>>` — rather than at top level. Prefer a positional value for a single required subject; a flag for optional, named, or convention-bound inputs (`--branch`).

## Gotchas

- **A load-bearing step must have a consumer** — a step nothing consumes is advisory and often silently skipped under load; bind its finding, write its artifact, or gate a future step or conditional on it.
