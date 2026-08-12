---
name: export-pdf
description: Use whenever a markdown file needs rendering to PDF with a tuned visual style — a single-page document (e.g. resume, cover letter) or a multi-page one (e.g. report, brief, table-heavy deliverable). Covers markdown→PDF rendering only; the base `pdf` skill handles work on existing PDFs (e.g. read, merge, split, OCR, forms).
---

# export-pdf

Use whenever a markdown file needs rendering to PDF with a tuned visual style — a single-page document (e.g. resume, cover letter) or a multi-page one (e.g. report, brief, table-heavy deliverable). Covers markdown→PDF rendering only; the base `pdf` skill handles work on existing PDFs (e.g. read, merge, split, OCR, forms).

Prerequisite: `uv`. Both bundled scripts carry PEP 723 inline metadata declaring their dependencies, so each `uv run` resolves them ephemerally — there is no venv to maintain.

## Render

```
uv run ${CLAUDE_SKILL_DIR}/scripts/pdf-render.py --src <path/to/source.md> [--dest <path/to/output.pdf>] [--style <name>]
```

One call per markdown source; a successful render prints `Generated: <dest>`.

- `--dest` defaults to the source path with a `.pdf` extension, landing the PDF beside its markdown. Pass it only to redirect the output; an existing file at the destination is overwritten.
- `--style` defaults to `compact`. A name with no matching preset prints the available presets and exits 2.

## Local links

Link rewriting is on by default: `[label](X.md)` and `[label](X.md#anchor)` become `[label](X.pdf)` and `[label](X.pdf#anchor)`, so cross-document links resolve to rendered companions. Each rewritten target is checked at end of render, and missing companions emit a stderr `Warning:` block — informational only, since a later render in the same batch may still produce them.

- `--no-rewrite-md-links` — keep `.md` targets unchanged in the PDF (rare).
- `--strip-local-links` — drop the link wrapper entirely for any target that is not `http(s)`, `mailto:`, or a `#anchor`. Use only when the recipient won't have any companion files.

## Post-batch link check

Run once every PDF in a delivery has been generated:

```
uv run ${CLAUDE_SKILL_DIR}/scripts/pdf-link-check.py <pdf>... [--ignore <glob>]
```

It walks each PDF's link annotations and reports every local-file target that doesn't exist relative to the PDF's directory, exiting 0 when all of them resolve — the definitive verdict the per-render warnings cannot give.

## Style presets

`--style <name>` loads the Python module at `${CLAUDE_SKILL_DIR}/styles/<name>.py`. Shipped:

| Preset | Description |
| --- | --- |
| `compact` (default) | Tight single-page document layout — Helvetica family, 1.3cm margins, 10pt body, hairline `#d0d7de` rules, `•` bullets, blue `#0550ae` links. Tuned for resumes, cover letters, recommendation letters. Declares its constants explicitly, to serve as the canonical example. |
| `resume` | Compact with `h3` restyled as a resume entry heading (company + date-range line): roman 11pt base, so inline `**bold**` / `*italic*` markers control weight and slant — `### **Company** - *dates*` renders bold company, light oblique dates. All-bold h3 headings read better under `compact`. |

## Authoring a preset

A preset declares only the constants it wants to override. Whatever it leaves out falls through to reportlab's library defaults, never to another preset's values — so a single declared constant is a complete, valid preset:

```python
# styles/red-link.py
LINK_COLOR = "#cc0000"
```

Every other constant and `make_styles()` then falls back, so the output reads as default reportlab with red links — not as `compact`.

For a curated starting point, copy a shipped preset and edit it:

```
cp ${CLAUDE_SKILL_DIR}/styles/compact.py ${CLAUDE_SKILL_DIR}/styles/<your-name>.py
```

Render the result with `--style <your-name>`.

## Style constants

All optional, each consumed by the renderer only when set:

| Group | Constant | Effect (when set) |
| --- | --- | --- |
| Fonts | `BODY_FONT` | Bullet marker and table-cell font |
| | `BOLD_FONT` | Table header-cell font; available to `make_styles()` |
| | `ITALIC_FONT` | Available to `make_styles()` |
| Colors | `LINK_COLOR` | Adds `color="…"` to inline links |
| | `RULE_COLOR` | Color of horizontal rules (H2-following + `---` break) |
| | `MUTED_COLOR` | Available to `make_styles()` |
| Page | `PAGE_SIZE` | `SimpleDocTemplate(pagesize=…)` |
| | `PAGE_MARGIN` | All four margins (uniform) |
| Horizontal rules | `HR_THICKNESS` | Rule thickness |
| | `H2_RULE_SPACE_AFTER` | Space below H2's hairline rule |
| | `BREAK_RULE_SPACE_BEFORE`, `BREAK_RULE_SPACE_AFTER` | Space around `---` break rule |
| Bullets | `BULLET_CHAR` | Bullet glyph |
| | `BULLET_INDENT`, `BULLET_FONT_SIZE` | ListFlowable indent + bullet font size |
| | `SUB_BULLET_CHAR` | Sub-bullet glyph (default `–`) |
| Inline code | `CODE_FONT_NAME`, `CODE_FONT_SIZE` | `<font face="…" size="…">` wrapping `` `code` `` |
| | `CODE_FONT_FILE` | TTF path registered under `CODE_FONT_NAME` — resolved relative to the skill root when not absolute; a missing file exits 2 |
| | `CODE_TEXT_COLOR`, `CODE_BG_COLOR` | `color=` / `backColor=` on the inline-code `font` tag |
| Tables | `TABLE_HEADER_BG_COLOR` | Header-row background fill (no default — omit for no fill) |
| | `TABLE_GRID_COLOR` | Grid line color (falls back to `RULE_COLOR`, then reportlab grey) |
| | `TABLE_FONT_SIZE` | Cell font size (default 9) |
| | `TABLE_PADDING` | Cell padding (default 4) |

`make_styles()` is optional. Defined, it returns a six-key dict — `h1`, `h2`, `h3`, `h4`, `body`, `bullet_text` — that the renderer uses verbatim, and the full reportlab `ParagraphStyle` API is available inside it (`fontSize`, `leading`, `alignment`, `spaceBefore`, `spaceAfter`, `leftIndent`, and the rest). Undefined, the renderer supplies a minimum-sufficient default: sizes only, 18/14/12/11/10/10 pt across those six keys, in reportlab's `Times-Roman` with no font or color opinion.

Inline code carries the one other renderer-level fallback, since reportlab has no library default that fits: with `CODE_FONT_NAME` / `CODE_FONT_SIZE` unset, `` `code` `` is wrapped in `<font face="Courier" size="9">` — conventional monospace, no color, no background. Everything else left undeclared (margins, page size, rule thickness and color, bullet glyph and indent, link color) renders at plain reportlab defaults.

## Markdown coverage

Supported:

- H1–H4 headings — H2 is uppercased and followed by a horizontal rule.
- Paragraphs — continuation lines join; a blank line separates.
- Bulleted lists (`- ` prefix), one level of nesting: a `  - ` sub-bullet (two-space indent) renders as an indented child list marked with `SUB_BULLET_CHAR` (default `–`), while a two-space-indented line without `- ` folds into its item as continuation text.
- Inline bold (`**text**`), italic (`*text*` or `_text_`, the underscore form respecting word boundaries so `snake_case` and `__dunder__` are left alone), inline code (`` `text` ``), and links (`[label](url)`, rendered underlined).
- Horizontal rules (`---`).
- GFM tables — header row bold, columns sized to their content with wide columns wrapping in-cell when the natural widths overflow the page, inline formatting inside cells, and alignment markers (`:---`, `:---:`, `---:`) honored (the separator needs 3+ dashes per column). A `<br>` or `<br/>` inside a cell renders as a line break — the one place HTML is honored — letting a cell stack two lines.
- Calendar tables — a table whose header row is exactly `Sun | Mon | Tue | Wed | Thu | Fri | Sat` renders as a month grid: each cell `` `**N**<br>value` `` becomes a boxed day with a shaded, deemphasized day-number strip (~1/3) over its value (~2/3), the compartments divided by shading rather than a rule. Empty cells are out-of-month padding. An H3 heading immediately above the table folds in as a spanned title row across the grid. The weekday header is the trigger; no marker needed.
- XML-safe content — `&`, `<`, and `>` are auto-escaped.

Not implemented, all rare: blockquotes, ordered lists, bullet nesting beyond one level, footnotes, images, fenced code blocks. When an artifact needs one, extend `scripts/pdf-render.py` rather than forking the process.
