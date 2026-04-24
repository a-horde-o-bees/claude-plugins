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

## End
