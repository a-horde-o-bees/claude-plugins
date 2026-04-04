---
pattern: "*.md"
depends:
  - .claude/rules/ocd-design-principles.md
---

# Markdown Conventions

Base content standards for all markdown files. Every other convention inherits from these requirements.

## Heading and Purpose Statement

Every file opens with a level-1 heading (`#`) that identifies the file's subject, followed by a purpose statement as defined by the Progressive Disclosure principle. The heading matches the file's name or subject. The purpose statement conveys scope and role — a reader encountering the file decides whether to read further based on these two lines alone.

## Blank Line Separation

Different formatting elements require a blank line between them. Without separation, markdown renderers may merge or misinterpret adjacent elements.

Required blank line between:
- Heading and following content
- Paragraph and list
- Bold/emphasis line and list
- List and paragraph
- Code block and surrounding content
- Table and surrounding content
- Blockquote and surrounding content

Within a single formatting context (consecutive list items, consecutive paragraphs), blank lines follow standard markdown rules for that element.
