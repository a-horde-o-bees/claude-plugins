# Lint spec

The formatting rules `scripts/lint.mjs` enforces on demand — the source of truth the script realizes. Change spec and script together; `.fixtures/` (a violations file, a conformant file, and the expected findings) realizes that check mechanically — extend the fixtures with each rule change, then confirm `node scripts/lint.mjs --self-test` passes.

Each rule is an **error** (must fix) or a **warn** (judgment call — the script cannot distinguish a violation from intended markup).

## Opening heading

- The first content line (after any YAML frontmatter) is a level-1 heading. [error]
- The heading text names the file — lenient normalized match; for `SKILL.md` the parent folder is the name; README and CLAUDE.md files are skipped — container files whose heading names the project. [warn]

The description beneath the heading is authoring judgment (see description-authoring) — out of the script's scope.

## Blank-line separation

A blank line separates any two adjacent elements of different formatting types — headings, paragraphs (including single-line labels ending in `:`), list items, code fences, table rows, blockquotes, horizontal rules. Not required between consecutive elements of the same type; frontmatter is exempt. [error]

Within a list, no blank line separates two same-indent items with nothing between them — a continuous list stays continuous. [error]

Inside a fenced code block, no blank line sits immediately after the opening fence or immediately before the closing fence. [error]

## Paragraph wrapping

- Each paragraph is a single source line — no manual hard-wrapping. [error]
- One list item per line — no continuation lines under an item. [error]

## Indentation

- List indentation is spaces only, a multiple of 4 — nested lists indent 4 spaces per level, matching procedure-authoring's scope indentation. [error]

## Special-character escaping

`{}` and `<>` used literally belong inside a code span (single- or double-backtick) or a fence. Flagged wherever they appear outside code in prose, table cells, and list items; autolinks, email autolinks, and HTML comments are exempt. Emphasis markers `*` and `_` are left to author judgment — flagging them would fire on every intended emphasis. [warn]

## Severity overrides

A project retunes rule severities without forking the skill: the nearest `.claude/markdown-lint.json` at or above a linted file maps rule ids to `"off"`, `"warn"`, or `"error"` — e.g. `{"escape-special": "off", "heading-names-file": "error"}`. Rule ids: `opening-heading`, `heading-names-file`, `blanks-around`, `one-line-items`, `one-line-paragraphs`, `continuous-list`, `fence-padding`, `list-indent`, `escape-special`. Severity only — a different rule set is a skill shadow.
