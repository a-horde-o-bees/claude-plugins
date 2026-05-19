---
name: markdown-authoring
description:
---

# Markdown

Content standards for markdown files.

## Heading and Description

Every file opens with a level-1 heading (`#`) matching the file's name, immediately followed by a description following /description-authoring.

## Blank Line Separation

A blank line separates any two different formatting element types. Without separation, renderers may merge or misinterpret adjacent elements.

Formatting element types:

- Headings
- Paragraphs (including single-line labels ending in `:`)
- Lists (numbered or bulleted, including nested content within list items)
- Code blocks (fenced or indented)
- Tables
- Blockquotes

Content within the same type (consecutive list items, consecutive paragraphs, nested lists) follows standard markdown rules.

Blank line separation does not apply inside YAML frontmatter (between `---` delimiters).

## Paragraph Wrapping

Paragraphs are single lines in source; renderers handle visual wrapping. Manual wrapping fragments paragraphs into a fixed visual layout and complicates diffs, since any edit that shifts a word ripples through subsequent lines.

Lists keep one item per line. Code blocks preserve their internal formatting. Tables follow markdown table syntax.

## Special Characters

Characters that markdown renderers may interpret — `{}`, `<>`, `*`, `_` — must appear within backtick-delimited inline code or fenced code blocks when used literally. Without protection, renderers strip `<>` as HTML tags, template engines consume `{}` as variables, and `*`/`_` trigger emphasis. Applies anywhere these characters appear outside code blocks — prose, table cells, list items.

