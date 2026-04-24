---
log-role: reference
---

# PDF

Decisions governing the `/ocd:pdf` skill and its PDF generation stack.

## WeasyPrint over md-to-pdf (Puppeteer/Chromium)

### Context

The earlier `/ocd:md-to-pdf` skill depended on the globally-installed npm package of the same name, which drives Puppeteer under the hood and prints via headless Chromium. PDFs rendered that way had broken text layers — spaces dropped, characters reordered on copy/paste, and grep/ATS tooling received scrambled text. The visual output looked correct; the underlying text stream did not. For artifacts meant to be copied, searched, or parsed by automated systems (resumes, cover letters, recommendation letters read by ATS), the broken text layer defeated the purpose of emitting a PDF in the first place.

### Options Considered

**Stay with md-to-pdf and work around the text layer** — try alternative Chromium print flags, CSS tweaks, or post-process extraction. Rejected: the root cause is the Chromium PDF emitter, not the CSS. No flag fixes the layer; post-processing cannot reconstruct text that was never emitted correctly.

**Pandoc + LaTeX** — high-fidelity PDF generation, standard in academic publishing. Rejected: heavy system dependency (TeX Live), long cold-start times, and CSS-to-LaTeX requires a separate styling language.

**wkhtmltopdf** — HTML-to-PDF via Qt WebKit. Rejected: upstream project is stalled, CSS support lags modern browsers, and Qt WebKit is itself deprecated.

**WeasyPrint** — Python-native CSS-to-PDF engine. Produces correct, structured text layers. Pure Python install via `uv` into the plugin's isolated venv — no system packages, no globally-installed tools, no browser subprocess.

### Decision

WeasyPrint, replacing md-to-pdf entirely. The skill renamed from `/ocd:md-to-pdf` to `/ocd:pdf` and shifted from an npm dependency to a Python dependency in the plugin's `pyproject.toml`.

Preset naming reflects purpose rather than font: `compact` replaces `roboto` as the tight-margin preset tuned for single-page printable documents; `github` stays as the neutral GitHub-flavored base.

### Consequences

- **Enables:** PDFs with correct text layers — grep, ATS ingestion, copy/paste, and PDF search all work against the real text content
- **Enables:** plugin-isolated dependency management — WeasyPrint installs into the ocd plugin's venv via the existing SessionStart dependency-diff flow, no user-level npm install required
- **Constrains:** WeasyPrint's CSS support is narrower than Chromium's — advanced layout features (CSS Grid beyond basics, some filter effects, newer paint modules) degrade or are unsupported. Presets must stay within WeasyPrint's supported subset
- **Constrains:** `@font-face` declarations using remote fonts need explicit `FontConfiguration()` threading; default font loading is fragile across environments
- **Constrains:** remote `@import` in CSS is brittle — offline or rate-limited environments fail to load fonts. Prefer locally-vendored font files for presets where font choice matters to output

### Future Migration Target

Accumulated WeasyPrint friction (bugs listed across the decisions below) has shifted the stance on previously-rejected alternatives. If further WeasyPrint issues require a migration, try **Pandoc + LaTeX** first. The earlier rejection was driven by system-dependency weight (TeX Live install); that cost is now worth paying if the alternative is continuing to accumulate workarounds. Playwright / Chromium stays rejected on text-layer grounds (the original reason md-to-pdf was dropped). Typst is viable but would require rewriting CSS presets as Typst templates — heavier than the LaTeX switch.

## @font-face requires FontConfiguration + explicit per-weight faces

### Context

WeasyPrint 56+ dropped the cairo backend and with it the synthetic-italic rendering that earlier versions produced from regular faces. Italic content (`<em>`, `*text*`) now requires an actual italic font face in the stack. Additionally, `@font-face` rules declared in a stylesheet are silently dropped unless a `FontConfiguration` object is threaded through both `CSS()` and `write_pdf()`. A session debugging "italic not rendering" found real italic text in HTML, correct `@font-face` rules in the CSS, and no rendered italic — because the font declarations were invisibly ignored and fallback fonts without italic faces served instead.

### Options Considered

**Rely on the cairo synthetic italic (pre-56 behavior)** — not available in current WeasyPrint; no flag reinstates it.

**Import Roboto italic via remote `@import` from Google Fonts** — appeared to work at parse time (no warnings) but produced no italic in output. Root cause: WeasyPrint silently dropped the `@font-face` rules without a `FontConfiguration`. Rejected: even with `FontConfiguration`, remote `@import` is fragile across offline/restricted environments.

**Declare one `@font-face` with a weight range (`font-weight: 100 900`)** — valid CSS4 syntax. WeasyPrint emits `Ignored 'font-weight: 100 900' at N:C, invalid value.` warning and drops the declaration. Rejected: not supported.

**Bundle variable-font woff2 files next to the preset CSS, declare each needed weight explicitly.** One variable-font file per italic state (Regular, Italic), referenced by relative `url('./Roboto-Regular.woff2')`. A separate `@font-face` per weight (400, 500, 600, 700) — all pointing at the same file — satisfies WeasyPrint's per-weight parser while letting the variable font supply any weight on demand. Accepted.

### Decision

`_generate.py` passes `FontConfiguration()` to both `CSS(font_config=...)` and `write_pdf(font_config=...)`. The `compact` preset bundles `Roboto-Regular.woff2` and `Roboto-Italic.woff2` alongside `compact.css` and declares eight `@font-face` rules (Regular 400/500/600/700 and Italic 400/500/600/700) all pointing at the corresponding variable-font file via relative URLs.

### Consequences

- **Enables:** italic rendering works offline; no network fetch at render time; deterministic output
- **Enables:** preset CSS + fonts travels as a portable bundle — users copy the folder, everything moves together
- **Constrains:** adding weights beyond 400–700 requires additional `@font-face` declarations (variable-font range syntax unavailable)
- **Constrains:** presets that depend on font choice must bundle their own font files; they cannot rely on system fonts or remote `@import`

## Ordered-list numbering continuation across interrupting blocks

### Context

Process Flow Notation (PFN) workflow docs routinely interleave numbered steps with blockquote commentary that separates the list mid-flow. python-markdown without the `sane_lists` extension treats the blockquote as a full list terminator — the second half of the numbered list restarts at 1 rather than continuing. Even with `sane_lists` producing `<ol start="3">`, WeasyPrint ignores the HTML `start` attribute (open bug since 2016 — Kozea/WeasyPrint#398, #643, #2003, #2158) and renders the second ol starting at 1.

### Options Considered

**Accept renumbering at 1** — rejected: breaks the document's instructional flow; readers lose track of step indices.

**Rewrite source to avoid interrupting blockquotes** — rejected: inline commentary between steps is a documented PFN convention. Forcing authors to refactor is a rule change, not a fix.

**Use a custom CSS counter + `::before` pseudo-element for markers** — replaces native list numbering with author-controlled counters. Rejected: too invasive for a rendering-engine workaround; disturbs other list behavior and compounds the existing `list-style-position: inside` strategy.

**Enable `sane_lists` + post-process HTML to translate `<ol start="N">` into inline `counter-reset: list-item <N-1>`.** WeasyPrint honors CSS `counter-reset` even when ignoring the HTML `start` attribute. Python-markdown emits the HTML attribute; a single regex in `_generate.py` adds the inline style while preserving the original attribute. Accepted.

### Decision

`_generate.py` enables the `sane_lists` markdown extension and post-processes HTML output with:

```python
re.sub(
    r'<ol start="(\d+)"',
    lambda m: f'<ol start="{m.group(1)}" style="counter-reset: list-item {int(m.group(1)) - 1}"',
    html_body,
)
```

The HTML `start` attribute is preserved (other consumers honor it) and the inline CSS counter-reset makes WeasyPrint render the correct starting number.

### Consequences

- **Enables:** numbered workflow steps survive blockquote interruptions with intact numbering
- **Constrains:** nested ordered lists inside an ol with an explicit start attribute could theoretically inherit the counter-reset scope. Kozea/WeasyPrint#1685 documents the nested-counter interaction; our scope (top-level ol only) is not affected in practice but authors should avoid nesting an ol inside an explicit-start ol

## List-marker rendering: inline positioning + hyphen markers

### Context

Default CSS `list-style-position: outside` places list markers in a separate PDF text run positioned in the left margin. WeasyPrint's emitter follows the CSS — the marker column becomes its own text sequence independent of the bullet content. This produces three compounding problems:

1. **PDF viewer selection:** dragging through bullets grabs the marker column across unrelated sections of the document, or skips markers entirely. Users see "bullets are separate entities from the text beside them."
2. **ATS text extraction:** parsers using pypdf / pdfminer / poppler's `pdftotext` see the list markers as a disconnected column of glyphs (orphaned roman numerals, stray hyphens). The structural association between marker and content is lost.
3. **Nested ordered lists:** nested-level markers (`i.`, `ii.`, `iii.`) appear stacked in isolation with no adjacent content in extraction.

Additionally: default `list-style-type: disc` produces a Unicode bullet (U+2022) that extracts as a non-ASCII glyph; ASCII hyphen (U+002D) preserves markdown-source fidelity better for downstream consumers.

### Options Considered

**`list-style-position: outside` with `::before` pseudo-element bullets** — tried. Improves selection behavior in some viewers, still breaks clipboard copy (marker isolated on its own line), still breaks nested ordered-list extraction. Rejected.

**`list-style-type: "- "` alone (CSS3 arbitrary string marker)** — marker renders as hyphen but pypdf extraction produces no marker at all (list-style-type string does not always contribute to the extracted text layer). Rejected: loses the marker signal entirely for ATS consumers.

**`list-style-position: inside` + default `disc` markers** — solves selection and extraction by putting markers in the same text run as content. Works for all list depths and types. Visual shift: bullets indent with the content rather than hanging outside. Accepted for structural fix.

**`list-style-position: inside` + `list-style-type: "- "` for `ul`** — combines the inline structural fix with a hyphen marker. Best extraction behavior; best markdown-source fidelity. Accepted.

### Decision

Preset CSS sets:

```css
.markdown-body ul, .markdown-body ol {
  list-style-position: inside;
}
.markdown-body ul {
  list-style-type: "- ";
}
```

Em-dash (`—`) is reserved for sentence-level separators inside bullet text so marker and content remain visually distinct. Ordered lists use default decimal numbering.

### Consequences

- **Enables:** PDF selection follows content order; clipboard copy preserves marker+content; pypdf/ATS extraction reads `- Bullet text` as a single logical line
- **Enables:** uniform rendering across nested list depths — nested `ol` markers (roman, alpha) stay inline with content instead of orphaning
- **Constrains:** bullets no longer hang outside the content box — minor visual shift versus traditional print conventions
- **Constrains:** `list-style-type: "- "` is CSS3 and WeasyPrint-supported, but other renderers may not honor it. Reconsider if presets ever target engines with weaker CSS3 list-style support

## Tagged PDF output (`pdf_tags=True`)

### Context

WeasyPrint's default output has no tag tree (`/StructTreeRoot`). PDF viewers that support structured text selection and screen readers fall back to spatial-order selection without it — the "select top-down, grabs everything in a column" behavior seen with untagged PDFs. Tagged output emits a logical reading-order tree that most viewers consult for selection and accessibility tools use for navigation.

### Options Considered

**Ship untagged PDFs (default)** — simpler output, slightly smaller files. Rejected for output artifacts that will be human-read, copied from, or machine-processed.

**Tag only specific document types (resumes, letters)** — would require the skill or caller to thread a flag. Rejected: tagging has essentially no cost for the output category this skill targets; make it default.

**Ship tagged PDFs (`pdf_tags=True`)** — accepted.

### Decision

`_generate.py` passes `pdf_tags=True` to `write_pdf()`.

### Consequences

- **Enables:** PDF viewers that honor the struct tree follow logical document order for selection; screen readers get a navigable tree
- **Enables:** downstream tools that use `/StructTreeRoot` (some advanced ATS pipelines, accessibility scanners) get richer structural metadata
- **Constrains:** slight file-size increase versus untagged output (typically single-digit percent)

## HTML tables forbidden for company/role headers

### Context

Resume authors reach for `<table>` elements to get right-aligned date columns (company on left, employment dates on right). The visual result looks clean but the PDF text emitter serializes table cells left-to-right row-by-row and interleaves the table structure with surrounding prose. ATS extractors receive a chaotic reading order: bullet content from one entry appears BEFORE the company name and dates that should have preceded it; later in the document, the date tokens appear as orphaned fragments after the Education or Certifications sections. Empirically verified by pypdf extraction: the "with-tables" fixture dumped Honeywell/CritSuccess/USACE dates at the end of document, completely dissociated from their companies.

### Options Considered

**Use `<table>` for right-aligned dates, accept the ATS cost** — rejected: ATS parsing is the reason the PDF exists for resume artifacts. Breaking parse order defeats the purpose.

**Use CSS float or flexbox to right-align dates without a table** — viable but WeasyPrint's float and flex support has its own edge cases; would need separate regression coverage.

**Drop right-aligned dates; use `**Company** — *dates*` as a single paragraph** — simpler source, natural reading order, zero ATS risk. Visual cost: dates inline with company name rather than columnar. Accepted.

### Decision

Company/role headers in resume templates use plain paragraph format:

```markdown
**Company Name** — *Date Range*

**Role Title**

- Bullet
```

Preset CSS has no `.role-header` table rules. `<table>` usage in content is discouraged for any artifact intended for ATS consumption.

### Consequences

- **Enables:** ATS and pypdf-based extractors see company → role → bullets in correct order
- **Enables:** italic dates render through standard `<em>` styling — no table-cell CSS plumbing required
- **Constrains:** visually columnar date layouts are not available via tables; must be achieved via CSS (float, flex, grid) if ever needed, with separate test coverage
- **Constrains:** authors lose a common resume idiom — the preset's conventions must be documented so users don't reach for `<table>` by reflex
