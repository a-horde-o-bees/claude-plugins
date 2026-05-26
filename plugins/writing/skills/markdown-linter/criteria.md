# Markdown Linting Criteria

The mechanically-checkable formatting rules a project markdown linter must enforce. The `markdown-linter` skill builds tooling against this list. Each criterion notes whether a built-in linter rule typically covers it or a custom rule is needed.

## Opening heading

- The first content line is a level-1 heading (`#`). [built-in: first-line-heading]
- The heading text names the file. [custom rule]

The description beneath the heading is authoring judgment, not mechanical — out of scope for the linter. See `/description-authoring`.

## Blank-line separation

A blank line separates any two adjacent elements of different formatting types:

- Headings
- Paragraphs (including single-line labels ending in `:`)
- Lists (numbered or bulleted, including nested content)
- Code blocks (fenced or indented)
- Tables
- Blockquotes

Does not apply between consecutive elements of the same type, or inside YAML frontmatter. [built-in: blanks-around-headings / -lists / -fences, plus a custom check for the label-paragraph case]

## Paragraph wrapping

- Each paragraph is a single source line — no manual hard-wrapping. [custom rule]
- One list item per line. [built-in / custom]

## Special-character escaping

Characters a renderer may interpret outside code — `{}`, `<>`, `*`, `_` — appear inside inline backticks or a fenced block when used literally. Applies in prose, table cells, and list items.

Caveat: distinguishing a literal `<>` from intended HTML, or `*` from intended emphasis, needs context a linter lacks. Treat as warn-level, not a hard fail. [custom rule, warn]
