---
tagline: Content standards for components/ — reference blocks, one per topic
---

# components/ Conventions

Content standards for files under a system's `components/` subdirectory. A component is a reference block: a layout, a rule, a schema, a tool surface — content the agent looks up to apply, not a procedure executed top-to-bottom. One file per topic.

## Purpose Statement

Opens with an L1 heading naming the topic (matches the filename) and a one-paragraph purpose statement: what this content is and when to consult it. A reader landing on the file decides from those two lines whether to continue.

## Body Structure

Reference content. No fixed section template — structure follows the topic's natural shape. Common patterns:

- **Layout reference** — describes a structural shape (e.g., file layout, schema). Sections by component or field.
- **Rule reference** — enumerated rules with rationale. Sections by rule, or one flat list.
- **Tool reference** — describes a tool surface, its inputs and outputs. Sections by tool or operation.
- **Decision matrix** — table mapping conditions to actions. Sections by decision domain.

A component file does not contain executable procedures. Steps belong in `workflows/<topic>.md`. If a component starts accumulating action verbs, the content has shifted from reference to procedure and should split.

## Reference Pattern

Consumers reach for a component to answer a specific question, not to read it cover to cover. Structure for lookup:

- Headings name the question or domain so a reader skims to what they need
- Tables, lists, and structured prose over running narrative when the content is enumerable
- Cross-references to sibling components or workflows when adjacent context helps

## Cross-References

A component referenced from a workflow appears in that workflow's body via path:

```
Read: `components/<topic>.md`
```

The workflow loads the component on demand; consumers that don't reach the relevant step never pay the cost. See `system-structure.md` for the extraction criteria that drive when to split content into a component file.

## Filename and Location

Component files live at `<system>/components/<topic>.md`. Filename matches the topic (e.g., `scope-matrix.md`, `frontmatter-fields.md`, `dispatch-table.md`). Lowercase, kebab-case for multi-word names.

A component listed by `<system>/CLAUDE.md`'s navigation index uses the same name in its purpose-statement entry.
