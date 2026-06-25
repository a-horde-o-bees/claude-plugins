---
name: export-pdf
description: Use whenever a markdown file needs to be rendered/exported to PDF with a tuned visual style — a single-page document (resume, cover letter, recommendation letter) or a multi-page one (report, brief, table-heavy deliverable); GFM tables and pagination are handled. The PDF defaults next to the source markdown. Distinct from the base `pdf` skill (which handles read, merge, split, OCR, forms); export-pdf is specifically for markdown→PDF rendering via the bundled reportlab-based renderer.
---

# export-pdf

Render a markdown artifact to PDF using the bundled `scripts/pdf-render.py` — a reportlab renderer with PEP 723 inline metadata declaring `reportlab` and `markdown-it-py` as deps. Invocation via `uv run` resolves dependencies ephemerally each call; no persistent venv to maintain. Style presets are selectable via `--style <name>` and live as Python modules under `styles/`.

## Process

1. **Locate the bundled renderer.** The script lives at `~/.claude/skills/export-pdf/scripts/pdf-render.py`. Confirm before invoking:

   ```
   test -f ~/.claude/skills/export-pdf/scripts/pdf-render.py && echo "OK"
   ```

2. **Render** (one call per markdown source):

   ```
   uv run ~/.claude/skills/export-pdf/scripts/pdf-render.py --src <path/to/source.md> [--dest <path/to/output.pdf>] [--style <name>]
   ```

   `--style` defaults to `compact`. **`--dest` defaults to the source path with a `.pdf` extension** — i.e. the PDF lands next to the source markdown; pass `--dest` only to redirect it elsewhere. Existing PDFs are overwritten.

   **Link rewriting** is on by default: `[label](X.md)` and `[label](X.md#anchor)` are rewritten to `[label](X.pdf)` / `[label](X.pdf#anchor)` so cross-document links resolve to rendered companions. Each rewritten target is checked at end of render; missing companions emit a stderr `Warning:` block. Override flags:
   - `--no-rewrite-md-links` — keep `.md` targets unchanged in the PDF (rare).
   - `--strip-local-links` — escape hatch that drops the link wrapper entirely for any non-`http(s)`/`mailto:`/`#anchor` target. Use only when the recipient won't have *any* companion files.

3. **Post-batch link check** (run after all PDFs in a delivery are generated):

   ```
   uv run ~/.claude/skills/export-pdf/scripts/pdf-link-check.py <pdf>... [--ignore <glob>]
   ```

   Walks each PDF's link annotations and reports any local-file URI whose target doesn't exist relative to the PDF's directory. Per-render warnings can have false positives in a batch (a later render may produce the missing target); the post-batch check is the definitive verdict. Exits 0 when all local links resolve.

4. **Verify output exists**:

   ```
   test -f <path/to/output.pdf>
   ```

## Triggers

- Any single-file or batch markdown→PDF render — single-page (resume, cover letter, recommendation letter) or multi-page (report, brief, table-heavy deliverable).
- Materials transitioning to a "prepared" or "final" state where PDF delivery is required alongside the markdown source.
- Refresh of an existing PDF after the underlying markdown has changed.

## Style presets

Style presets are Python modules under `~/.claude/skills/export-pdf/styles/<name>.py`. A style module declares only the constants it wants to override; everything else falls through to **reportlab's library defaults**, not to compact's. A style with a single declared constant is valid; reportlab handles the rest with its built-in defaults.

**Overridable constants** (all optional; consumed by the renderer if set):

| Group | Constant | Effect (when set) |
|---|---|---|
| Fonts | `BODY_FONT` | Bullet marker font |
| | `BOLD_FONT`, `ITALIC_FONT` | Available to `make_styles()` for ParagraphStyle composition |
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
| Inline code | `CODE_FONT_NAME`, `CODE_FONT_SIZE` | `<font face="…" size="…">` wrapping ``code`` |
| Tables | `TABLE_HEADER_BG_COLOR` | Header-row background fill (no default — omit for no fill) |
| | `TABLE_GRID_COLOR` | Grid line color (falls back to `RULE_COLOR`, then reportlab grey) |
| | `TABLE_FONT_SIZE` | Cell font size (default 9) |
| | `TABLE_PADDING` | Cell padding (default 4) |

**`make_styles()`** is optional. If a style module doesn't define it, the renderer uses an internal minimum-sufficient default that produces size-differentiated headings via reportlab's `Times-Roman` (no font/color opinions). When defined, it returns a six-key dict (`h1`, `h2`, `h3`, `h4`, `body`, `bullet_text`) and the renderer uses it verbatim.

**Two renderer-level fallbacks worth knowing** (since reportlab has no library default that fits):

- **Inline code** — when `CODE_FONT_NAME` / `CODE_FONT_SIZE` are unset, the renderer wraps `` `code` `` in `<font face="Courier" size="9">`. Reportlab has no native inline-code concept, so the renderer must pick something; Courier 9pt is the conventional fallback.
- **Heading hierarchy in the generic `make_styles()`** — sizes only (18/14/12/11/10/10 for h1/h2/h3/h4/body/bullet_text). No font or color override — Times-Roman default applies.

Everything else (margins, page size, HR thickness, HR color, bullet character, bullet indent, link color) is reportlab-default when not declared.

Shipped presets:

| Preset | Description |
|--------|-------------|
| `compact` (default) | Tight single-page document layout — Helvetica family, 1.3cm margins, 10pt body, UPPERCASE H2 with hairline `#d0d7de` rule, `•` bullets, blue `#0550ae` links. Tuned for resumes, cover letters, recommendation letters. Declares every constant explicitly to serve as the canonical example. |

If invoked with `--style <name>` for a preset that doesn't exist, the renderer prints the available presets and exits 2.

## Adding a custom style preset

Minimum viable: a single property change.

```python
# styles/red-link.py
LINK_COLOR = "#cc0000"
```

That's a complete, valid style module. Every other constant and `make_styles()` falls back to reportlab/renderer defaults — the output won't look like compact, it'll look like default reportlab with red links.

For a curated starting point, copy `compact.py`:

```
cp ~/.claude/skills/export-pdf/styles/compact.py ~/.claude/skills/export-pdf/styles/<your-name>.py
```

Then edit. The full reportlab `ParagraphStyle` API is available when defining `make_styles()` — fontSize, leading, alignment, spaceBefore, spaceAfter, leftIndent, etc.

Render with `--style <your-name>`.

## Markdown features supported

- H1–H4 headings
- Paragraphs (continuation lines joined; blank-line-separated)
- Bulleted lists (`- ` prefix). One level of nesting: a `  - ` sub-bullet (two-space indent) renders as an indented child list under its parent item, marked with `SUB_BULLET_CHAR` (default `–`). A plain two-space-indented line (no `- `) still folds into its item as continuation text.
- Inline bold (`**text**`)
- Inline italic (`*text*` or `_text_` — underscore form respects word boundaries, so `snake_case` and `__dunder__` are left alone)
- Inline code (`` `text` `` — renders in Courier 9pt)
- Links (`[label](url)` — underlined, blue)
- Horizontal rules (`---`)
- GFM tables (`| a | b |\n|---|---|\n| 1 | 2 |`) — equal column widths, header row bold, inline formatting inside cells. Alignment markers (`:---`, `:---:`, `---:`) honored (the separator needs 3+ dashes per column). A `<br>` / `<br/>` inside a cell renders as a line break (the one place HTML is honored), letting a cell stack two lines — e.g. a calendar day number over its value.
- **Calendar tables** — a table whose header row is exactly `Sun | Mon | Tue | Wed | Thu | Fri | Sat` is auto-rendered as a month grid: each cell `**N**<br>value` becomes a boxed day with a shaded, deemphasized day-number strip (~1/3) over its value (~2/3), the compartments divided by shading rather than a rule. Empty cells are out-of-month padding. No marker needed — the weekday header is the trigger.
- XML-safe (auto-escapes `&`, `<`, `>` in content)

Not implemented (rare): blockquotes, ordered lists, bullet nesting beyond one level, footnotes, images, fenced code blocks. If a future artifact needs one, extend `scripts/pdf-render.py` rather than forking the process.

## Inputs

- The markdown source(s) to render
- `uv` must be installed on the system
- The bundled `scripts/pdf-render.py` (PEP 723 metadata handles `reportlab` + `markdown-it-py` resolution)

Does NOT read project-state files. Pure file-conversion process with no project-context dependencies.

## When to reach for the base `pdf` skill instead

Reach for `pdf` (not export-pdf) when:

- Reading or extracting text/tables from an existing PDF.
- Merging, splitting, or rotating PDFs.
- Filling PDF forms.
- Encrypting/decrypting or watermarking PDFs.
- OCR on scanned PDFs.
- Extracting images.

Reach for export-pdf specifically when the task is **render-markdown-to-PDF with this skill's visual style** (single- or multi-page). The two skills are complementary.
