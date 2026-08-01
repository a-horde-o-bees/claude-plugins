# Lint spec

The formatting rules `scripts/lint.mjs` enforces on demand — the source of truth the script realizes.

Spec and script change together, and `.fixtures/` (a violations file, a conformant file, and the expected findings) makes that mechanical: extend the fixtures with each rule change, then confirm `node scripts/lint.mjs --self-test` passes.

Each rule carries its id and severity: an **error** must be fixed; a **warn** is a judgment call — the script cannot distinguish a violation from intended markup.

## Opening heading

- The first content line (after any YAML frontmatter) is a level-1 heading. `opening-heading` [error]
- The heading text names the file — lenient normalized match; for `SKILL.md` the parent folder is the name; README and CLAUDE.md files are skipped, container files whose heading names the project. `heading-names-file` [warn]

The description beneath the heading is authoring judgment (see description-authoring) — out of the script's scope.

## Blank lines

- A blank line separates any two adjacent elements of different formatting types — headings, paragraphs (including single-line labels ending in `:`), list items, code fences, table rows, blockquotes, horizontal rules. Not required between consecutive elements of the same type; frontmatter is exempt. `blanks-around` [error]
- Within a list, no blank line separates two same-indent items with nothing between them — a continuous list stays continuous. `continuous-list` [error]
- Inside a fenced code block, no blank line sits immediately after the opening fence or immediately before the closing fence. `fence-padding` [error]

## Line breaks

- Each paragraph is a single source line — no manual hard-wrapping. `one-line-paragraphs` [error]
- One list item per line — no continuation lines under an item. `one-line-items` [error]

## Indentation

- List indentation is spaces only, a multiple of 4 — nested lists indent 4 spaces per level, matching procedure-authoring's scope indentation. `list-indent` [error]

## Special-character escaping

- `{}` and `<>` used literally belong inside a code span (single- or double-backtick) or a fence. Flagged wherever they appear outside code in prose, table cells, and list items; autolinks, email autolinks, and HTML comments are exempt. `escape-special` [warn]

Emphasis markers `*` and `_` are left to author judgment — flagging them would fire on every intended emphasis.

## Severity overrides

A project retunes rule severities without forking the skill: the nearest `.claude/markdown-lint.json` at or above a linted file maps the rule ids above to `"off"`, `"warn"`, or `"error"` — e.g. `{"escape-special": "off", "heading-names-file": "error"}`. Severity only — a different rule set is a skill shadow.
