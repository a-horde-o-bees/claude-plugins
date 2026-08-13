---
name: procedure-authoring
description: Apply when authoring an agent procedure with control flow beyond a linear sequence (e.g. conditionals, loops, variable binding, sub-routine calls, error handling) to keep non-trivial procedures readable and unambiguously executable. Not needed for simple sequential steps or lists.
---

# procedure-authoring

Apply when authoring an agent procedure with control flow beyond a linear sequence (e.g. conditionals, loops, variable binding, sub-routine calls, error handling) to keep non-trivial procedures readable and unambiguously executable. Not needed for simple sequential steps or lists.

**procedure-authoring sets expectations, not meanings.** This guide is never in the executing agent's context — only the authored procedure is. So a construct cannot *define* a meaning the executor is bound to honor; it can only pick wording whose plain reading **reliably evokes the intended behavior in an agent that has never read this guide.**

The bar is therefore empirical. Each construct below names a behavior and the wording meant to evoke it cold; when wording fails to evoke its behavior, the *phrasing* is the defect to strengthen — never the executor faulted for "misreading" a meaning it was never given. `tests/` measures each construct this way (cold `claude -p`, no guide loaded), so a weak-evoking construct shows as a low hit-rate rather than a surprise in production.

## Steps

- **`1.`** — a numbered step: one ordered action or construct.
- **`-`** — a bullet: an unordered list or sub-item of a step.
- **Indentation** — scope, 4 spaces per level: a construct ending in `:` opens a block, indented lines are its children, and outdenting to the parent ends it.
- **Grouping subheading** — a label between contiguous steps; numbering continues across them.

A load-bearing step must have a consumer — a step nothing consumes is advisory and often silently skipped under load; bind its finding, write its artifact, or gate a future step or conditional on it.

## Annotations

- **`—`** (em-dash) — an inline note on a step.
- **`>`** (blockquote) — a standalone note between steps.

An annotation describes, never instructs — keep executable actions out, since an agent runs any instruction it reads wherever it sits.

## Variables

A variable is written `` `{curly-dashes}` `` — braces inside backticks, a code span, so it sits in standard markdown without renderer or linter collisions — and is visible at any later depth; bind it before referencing it. Inside a larger code span or fence the braces stay bare (`--branch {branch}`).

**`{name}: <block>`** — binds the name to the block's value:

- inline value — `{x}: 42`
- bash stdout — `` {x}: Bash: `cmd` ``
- a call's return — `{x}: Call: [label](#anchor)`
- an applied block's result — `{x}: Apply [lens](#anchor) to: <block>`
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

A step delegates only to text already in context. The document is loaded whole, so its own `##` sections are reliable targets; text outside it is not — an un-opened file is invisible, its steps get improvised from the call site instead of run, and the miss appears under real orchestration load even though cold single-task tests pass every wording. No verb choice fixes an absent target.

- **`Call: [label](#anchor)`** — *procedural*: follow the section as steps within the current context.
- **`Apply [label](#anchor) to:`** — *behavioral*: run the indented block **through** the section as a lens — a discipline that shapes *how* the steps execute, not steps themselves. Opens a block; binds when assigned (`{x}: Apply [lens](#anchor) to: <block>`). Listed targets combine into a single lens over the block, interpreted together rather than as successive passes: `Apply [a](#a), [b](#b) to:`. When the lens is a sibling skill, the label is its slash reference — `Apply [/concise-prose](#concise-prose) to:` — declaring the dependency and resolving to its flattened unit at once.

Text a procedure depends on but does not own is materialized or mechanized, never fetched by the executor:

- **A sibling skill's discipline** — reference it as `/skill-name` where the procedure uses it; the build inlines the skill under `## Dependencies` and links the reference to that unit, an ordinary in-document target.
- **Deterministic work** — a script the step runs with `Bash:`. Token relief comes from mechanization, never from making the executor navigate to text stored elsewhere.
- **Steps meant for a fresh context** — a spawn whose directive names the file; the spawned agent starts empty, so reading the file is its first act, not a hop it may skip (see Spawn).
- **Provenance or background** — cite by bare name; a citation is not an invocation, and its miss costs nothing.

Return:

- **`Return to caller`** — hands control back from a called section.
- **`Return to caller:`** — hands a returned result back to the caller (e.g. from a spawned agent).

Never gate an invocation on a judgment the target owns. A condition restating the target's own trigger — *if the entry needs composing fresh*, over a lens whose whole job is deciding that — makes the discipline contingent on the decision it exists to make; the executor skips it and never meets the text that would have flipped its judgment. Invoke unconditionally — the target self-limits.

## Tools

- **`Bash:`** — runs a shell command: `` `cmd` ``.
- **`Read:`** — loads content without executing it; the read-only counterpart to `Call:`.
- **`Grep:`** — searches file contents.
- **`Glob:`** — matches file paths.
- **`Tool: args`** — any other MCP tool, invoked by name.

## Spawn

- **`Spawn agent to:`** — delegates to a new agent with its own context. A directive that names a file (`Spawn agent to: read and follow _plan.md`) keeps the caller's context clean; only the agent reads it.
- **`Spawn async agent to:`** — runs agents concurrently; the next outdented step runs after they complete.
- **`Spawn background agent to:`** — runs the agent in the background.
- **Route data around the caller** — a step whose output only a spawned agent consumes runs inside the spawn: the caller passes the directive and bare variables (paths, ids), never content it doesn't itself consume. Content relayed through the caller is read, written, and re-read — paid in the costliest context — and anchors the spawn to the caller's framing besides.

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

## What belongs in a procedure — the gate on every line

The executor sees only the authored procedure, cold, and runs any instruction it reads wherever it sits — so descriptive prose mixed into the steps both dilutes the actionable signal and risks being executed as a step. Classify every line by the **actionability test**: *would an executor need this to perform the task?*

- **Procedure** (keep) — reasoning, judgment, and contextual sequencing the agent steers; orchestration whose composition depends on intermediate results (section calls, tool invocations, agent spawns); and the user-facing surface (review gates, clarifying questions, error-recovery dialogue).
- **Script** (→ a `Bash:` call or invoked module) — deterministic operations with no agent context: parsing, filtering, aggregation, format conversion, fixed-rule classification. The tell: *could a deterministic function with no agent context produce this result?* Yes → script. Prefer one wherever it suffices; it preserves the agent's focus for the judgment only an agent can supply.
- **Durable structure** (→ the architecture doc) — the shape, boundaries, and external facts a reader needs *before* the steps make sense and that survive a rewrite. Not a step; state it there and link.
- **Why this and not that** (→ the decision record) — a choice made over rejected alternatives. The procedure *runs* the choice; the reasoning belongs there. Link.
- **Derivable** (cut) — anything the executor reconstructs from the steps themselves or the artifacts they touch.

Two misclassifications to catch, each corrected in one direction:

- **Mechanical work stranded in a procedure** — a step doing parsing, filtering, or formatting the agent performs by hand. Tell: a deterministic function could replace it with nothing lost. Push it into a script.
- **Judgment buried in a script** — code branching on context, resolving ambiguity, or deciding what the agent should steer. Tell: a comment hedges ("if ambiguous…", a heuristic, a guessed default). Lift that decision into the calling procedure; leave the script the deterministic part.
