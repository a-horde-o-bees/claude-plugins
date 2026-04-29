---
includes: "*.md"
governed_by:
  - .claude/rules/ocd/design-principles.md
---

# Markdown

Base content standards for all markdown files.

## Heading and Purpose Statement

Every file opens with a level-1 heading (`#`) that identifies the file's subject, followed by a purpose statement per Purpose Statement guidance. The heading matches the file's name or subject. The purpose statement conveys scope and role — a reader encountering the file decides whether to read further based on these two lines alone.

## Blank Line Separation

A blank line is required between any two different formatting element types. Without separation, markdown renderers may merge or misinterpret adjacent elements.

Formatting element types:

- Headings
- Paragraphs (including single-line labels ending in `:`)
- Lists (numbered or bulleted, including nested content within list items)
- Code blocks (fenced or indented)
- Tables
- Blockquotes

Transitioning from any one type to a different type requires a blank line. Content that stays within the same type (e.g., consecutive list items, consecutive paragraphs, nested lists within a parent list) follows standard markdown rules for that element.

YAML frontmatter (between `---` delimiters) is not a markdown formatting element — it is parsed separately before the markdown body. Blank line separation rules do not apply inside frontmatter.

## Paragraph Wrapping

Paragraphs are single lines in source. No manual line breaks within a paragraph — renderers handle visual wrapping based on viewport. Manual wrapping fragments paragraphs into a fixed visual layout, complicates diffs (any edit that shifts a word ripples through subsequent lines), and forces every editor to re-flow on every change.

This rule applies to paragraph content only. Lists keep one item per line. Code blocks preserve their internal formatting. Tables follow markdown table syntax. Blank line separation between formatting elements is unchanged.

## Special Characters

Characters that markdown renderers may interpret — `{}`, `<>`, `*`, `_` — must appear within backtick-delimited inline code or fenced code blocks when used literally. Without protection, renderers strip `<>` as HTML tags, template engines consume `{}` as variables, and `*`/`_` trigger emphasis formatting. This applies anywhere these characters appear in prose, table cells, or list items outside code blocks.
