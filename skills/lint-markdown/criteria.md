# Markdown Linting Criteria

The mechanically-checkable formatting rules a project markdown linter must enforce. The `markdown-linter` skill builds tooling against this list. Each criterion notes whether a built-in linter rule typically covers it or a custom rule is needed.

## Opening heading

- The first content line is a level-1 heading (`#`). [built-in: first-line-heading]
- The heading text names the file. [custom rule, warn — lenient normalized match; for `SKILL.md` the parent folder is the name; descriptive container files (README, criteria, ...) are skipped]

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

Within a list, no blank line separates two same-indent items (a continuous list) — unless a heading or blockquote interrupts them, in which case the blanks around that interrupter are legitimate. [custom rule]

Inside a fenced code block, no blank line sits immediately after the opening fence or immediately before the closing fence. [custom rule]

## Paragraph wrapping

- Each paragraph is a single source line — no manual hard-wrapping. [custom rule]
- One list item per line. [built-in / custom]

## Indentation

- Nested lists indent 4 spaces per level — the project's Process Flow Notation standard. [built-in: ul-indent, indent 4]

## Special-character escaping

Characters a renderer may interpret outside code — `{}`, `<>`, `*`, `_` — appear inside inline backticks or a fenced block when used literally. Applies in prose, table cells, and list items.

Caveat: a linter cannot tell literal use from intended markup, so this is warn-level, not a hard fail. The rule flags only `{}` and `<>` (template/HTML); emphasis markers `*` and `_` are left to author judgment — flagging them would fire on every intended emphasis. [custom rule, warn — `{}` `<>` only]
