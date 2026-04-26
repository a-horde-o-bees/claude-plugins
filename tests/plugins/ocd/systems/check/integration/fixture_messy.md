---
title: Frontmatter probe
argument-hint: "<verb1 | verb2 [--flag <value>]>"
placeholder-key: {frontmatter-placeholder}
emphasis-look-alike: *star* and _under_
---

# Messy Fixture for OCD Rendering + Lint Tests

## Summary

This fixture exercises every known pathological case in one file so tests can make many assertions against a single rendered PDF and a single lint scan — keeping test time low. Italic text via *emphasis* must render as real Roboto italic.

## Company Pattern

**Acme Corp** — *Jan 2020 to Present*

**Staff Engineer**

- Bullet one with short prose
- Bullet two wraps to a longer length that spans a typical resume-width line so extraction order can be asserted

## Placeholders That Must Survive Rendering

Prose line: {preserved-prose}.

- List item: {preserved-list}

> Blockquote: {preserved-blockquote}

## Legitimate attr_list Consumption

### SubHead with Attr {#consumed-id}

Body paragraph after the attr_list heading.

## Numbering Broken By Blockquote

1. First item
2. Second item

> Blockquote that interrupts the ordered list

3. Third must still render as 3
4. Fourth must render as 4

## List With Heading And Blockquote Interruption

- Item A before heading interruption
- Item B before heading interruption

### Interrupting Subheading

- Item C after heading and before blockquote interruption

> Interrupting blockquote comment

- Item D after blockquote interruption

## BLANK-IN-LIST Violation

1. List item one
2. List item two

3. List item three has offending blank above

## NO-BLANK-BEFORE-BLOCK Violation

Prose immediately before the subheading without a blank line.
### Subheading missing blank above

## NO-BLANK-AFTER-HEADING Violation

### Heading needs blank after
Direct content line with no blank after the heading.

## CONSECUTIVE-BLANKS Violation

Paragraph one.


Paragraph two after two blank lines.

## Literal Character Violations

Prose with {literal-placeholder} in paragraph context.

Arrow context: proposes -> Aaron responds.

Math context: volunteers > 50 triggers review.

## Fenced Code Block — Single Structural Unit

A fenced code block is treated as one paragraph. Lines that look like
headings inside the body are opaque — they must not fire heading or
block-start rules. The closing fence is the end of the block, not the
start of a new one, so the inevitable non-blank line above it must not
fire missing-blank-before-block.

```python
# This comment line resembles a level-1 heading but is code.
### def looks_like_heading(): pass
x = 1
```

## Fenced Code Block — Inner Discipline Still Applies

Code blocks aren't a free zone for blank-line noise. Multiple sequential
blank lines inside the body must still be flagged for consolidation, and
the body must not begin or end with a blank line.

```text
first body line


second body line after two blanks
```

```text

leading blank above this line
```

```text
trailing blank below this line

```

## End
