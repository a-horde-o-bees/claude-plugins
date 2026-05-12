# workflows/ Conventions

Content standards for files under a system's `workflows/` subdirectory. A workflow is a multi-step procedure consumed top-to-bottom: the agent reads it once and executes each step in order. One file per procedure.

## Purpose Statement

Opens with an L1 heading naming the procedure (matches the filename) and a one-paragraph purpose statement: what this procedure accomplishes and when to invoke it. A reader landing on the file decides from those two lines whether to continue.

## Body Structure

Sections fall into three categories:

- **Prescribed** — every workflow includes these
- **Common** — established patterns; include when relevant to the procedure's domain
- **Domain-specific** — child conventions may prescribe additional sections; this list is not exhaustive

| Section | Category | Description |
|---------|----------|-------------|
| `# <procedure-name>` | Prescribed | L1 heading naming the procedure |
| Purpose paragraph | Prescribed | One paragraph: what this accomplishes and when to invoke |
| `## Arguments` | Common | Argument surface — declared in CLI-style format per Process Flow Notation |
| `## Workflow` | Prescribed | Step-by-step procedure in Process Flow Notation |
| `### Report` | Common | Output format subheading within Workflow |

## Argument Surface

Workflows that accept arguments declare them in CLI-style format following the Argument Declaration in Process Flow Notation:

```
<verb> [--flag <value>] <positional>
```

Required values use `<>`; optional values use `[]`. The workflow body references arguments via `--flag` (presence) and `{flag}` (value).

## Process Flow Notation

The `## Workflow` section follows Process Flow Notation in full — numbered steps, scoped indentation, mechanism-prefixed invocations (`bash:`, `Read:`, `Spawn:`, `Call:`), conditional and loop constructs as needed. See `process-flow-notation.md` for the canonical notation.

## Cross-References

When a workflow needs reference content (a layout, a rule, a tool surface), it points at a file in the sibling `components/` directory rather than embedding it inline. Conditional content that only some paths need extracts via the same pattern — paths that don't traverse the branch never load the reference.

A workflow file is a procedure, not a documentation hub. It carries the actions; details live in `components/<topic>.md`.

## Filename and Location

Workflow files live at `<system>/workflows/<topic>.md`. Filename matches the procedure's name (e.g., `install.md`, `uninstall.md`, `scan.md`). Lowercase, kebab-case for multi-word names.

A workflow listed by `<system>/CLAUDE.md`'s navigation index uses the same name in its purpose-statement entry.
