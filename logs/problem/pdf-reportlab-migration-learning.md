# PDF rendering — reportlab/Helvetica outperforms WeasyPrint/Roboto-woff2 in sharpness; integration tests have a coverage gap

Surfaced 2026-05-12 during the `job-search` project's HDR Power Platform Developer materials prep. Carries forward a learning that should inform any future migration of the `/ocd:pdf` skill.

## What was observed

A `job-search` user reported copy/paste garbling on PDFs rendered by the current `/ocd:pdf` WeasyPrint + compact-preset pipeline: pasted glyphs appeared as PUA codepoints (`􀁢􀀖􀀔...` / U+F862, U+F016 range) — the canonical "broken cmap, encoded by glyph index" pattern that originally motivated the move from md-to-pdf to WeasyPrint (see `logs/decision/pdf.md`).

Investigation could NOT reproduce the garbling at the PDF-text-layer level:

- `pypdf.PdfReader().pages[0].extract_text()` against the rendered PDFs returned clean Unicode (em-dashes, curly quotes, ampersands, special punctuation all readable).
- An explicit PUA-codepoint scan over the extracted text returned zero matches in the U+E000–U+F8FF range.
- This held across multiple regenerated PDFs (resume + cover letter + rec letter shapes).

Most likely diagnosis (unverified — user-side viewer not identified): a PDF viewer's clipboard handler bypassing the ToUnicode cmap and emitting glyph indices as PUA codepoints. This is a viewer-side behavior; some Linux viewers (xpdf), some browser PDF previews, and some pdf-to-text utilities exhibit it. The PDF text layer itself appears correct.

## Integration test coverage gap

`tests/plugins/ocd-old/systems/pdf/integration/test_messy_rendering.py` exists as the regression guard for the original md-to-pdf migration. It currently checks:

- An italic-named font face is embedded in the PDF (`test_roboto_italic_embeds_with_preset_css`) — verifies font selection, NOT cmap correctness
- Specific ASCII substrings survive `extract_text()` (`test_prose_placeholder_survives`, etc.) — confirms basic extraction works for ASCII
- Bullet markers stay inline with text (`test_bullet_marker_and_text_same_line`)

What is **NOT** asserted:

- Extracted text contains no PUA codepoints (`assert not any(0xE000 <= ord(c) <= 0xF8FF for c in extracted_text)`)
- Extended Unicode characters (em-dashes, curly quotes, em-space, soft hyphens) round-trip through extraction
- The fixture `fixture_messy.md` itself does not contain em-dashes, curly quotes, or extended Unicode chars beyond ASCII + a few placeholders

Result: a future regression in font cmap handling for extended characters could ship without the existing tests failing. The original md-to-pdf-era regression that motivated the WeasyPrint move would NOT be caught by the current test suite if it reappeared on the extended-Unicode codepath.

**Fix shape:** add to `fixture_messy.md` a "Unicode round-trip" section containing em-dashes (`—`), en-dashes (`–`), curly quotes (`""`, `''`), apostrophes (`'`), ellipses (`…`), and other commonly-emitted typographic punctuation. Add a corresponding test class asserting `extract_text()` returns these exact codepoints and that NO character in the result lands in the PUA range. This converts the symptom we couldn't fully diagnose into a hard regression guard regardless of root cause.

## Alternative pipeline tested — reportlab/Helvetica

To rule out the cmap concern for the user's submission, an alternative pipeline was prototyped: custom Python script using `reportlab` (the library the Anthropic `/pdf` skill recommends for PDF creation). Path:

- `.claude/pdf-render.py` at `job-search` project root (PEP 723 inline metadata declaring `reportlab` dep)
- Invoked via `uv run .claude/pdf-render.py --src X.md --dest X.pdf` — ephemeral dependency resolution, no persistent venv
- Helvetica built-in (reportlab's reliable cmap path; no woff2 font subsetting concerns)
- Visual style mirrors the compact preset: tight letter margins, uppercase H2 with hairline rule below, dash bullets, blue links, mixed bold/italic
- Markdown parser is custom (handles H1-H4, paragraphs, bullets, bold/italic/links/code spans, horizontal rules) — purpose-built for resume/cover-letter/rec-letter shape

The user evaluated the rendered HDR resume side-by-side with the WeasyPrint output and reported the reportlab version "strikingly sharp and good." Aesthetic verdict, not text-layer verdict — both pipelines extract cleanly via pypdf.

## Considerations for `/ocd:pdf` skill migration

If/when `ocd:pdf` migrates away from WeasyPrint, this learning suggests:

**The reportlab path looks viable and produces visually-cleaner output, but it loses the CSS-driven preset model.**

- WeasyPrint consumes CSS → users can author presets as standalone `.css` files, swap them in `.claude/ocd/pdf/templates/<preset>/`, and the engine renders. The CSS is the configuration.
- Reportlab requires Python primitives (ParagraphStyle, ListFlowable, etc.) — presets would need to become Python style modules rather than CSS files. Different mental model, different swap mechanic.
- Reportlab's built-in fonts (Helvetica, Times-Roman, Courier) have proper cmaps natively. WeasyPrint requires careful font-file selection (the woff2 bundle approach in the current compact preset is fragile — see `logs/decision/pdf.md` *Constrains* section).

**Library choice aligns with Anthropic's `/pdf` skill recommendation.**

- The Anthropic-shipped `/pdf` user-level skill (at `~/.claude/skills/pdf/SKILL.md`) recommends `reportlab` as the PDF-creation library. Adopting reportlab in `ocd:pdf` aligns the plugin's stack with the Anthropic-blessed approach.
- The `/pdf` skill provides documentation and form-handling scripts, but no markdown-rendering executor. A reportlab-based renderer in `ocd:pdf` would complement the `/pdf` skill rather than duplicate it.

**Dependency-management pattern proven via PEP 723 + `uv run`.**

- The job-search prototype uses PEP 723 inline metadata in the script header to declare `reportlab` as a dep; `uv run script.py` resolves it ephemerally each invocation.
- This pattern eliminated persistent venv management entirely — no `uv venv` + `uv pip install` setup, no `.venv` to maintain.
- Worth considering for `ocd-run pdf` if the migration happens — the plugin's current dependency model (pyproject + venv) could be replaced with PEP 723 + on-demand resolution if reportlab is the sole dep.

**Cover the test gap regardless of pipeline choice.**

- The PUA-codepoint regression-guard test should be added to the existing `test_messy_rendering.py` BEFORE any migration, not after. Adding it now (against the current WeasyPrint pipeline) verifies that the current state is good, and provides a known-passing baseline for migration validation.
- If we keep WeasyPrint, the test prevents future font-cmap regressions on extended Unicode.
- If we migrate to reportlab, the same test validates the new pipeline against the same regression class.

## Audit scope

- Add Unicode round-trip section to `tests/plugins/ocd-old/systems/pdf/integration/fixture_messy.md` (em-dashes, en-dashes, curly quotes, ellipses, common typographic punctuation)
- Add `TestUnicodeRoundTrip` class to `test_messy_rendering.py` asserting:
  - All added Unicode chars are present in `extracted_text` verbatim
  - No character in `extracted_text` lands in the PUA range U+E000–U+F8FF
- Verify the current WeasyPrint+Roboto-woff2 pipeline passes the new tests (establish baseline)
- Decide whether `ocd:pdf` migrates to reportlab:
  - If yes: re-architect presets as Python style modules instead of CSS files; evaluate PEP 723 + `uv run` over the current pyproject+venv model
  - If no: document the user-side viewer caveat (some viewers exhibit copy/paste-PUA behavior independent of PDF correctness) somewhere visible in the skill docs
- Either way: the regression test should ship first

## Reference artifact

The reportlab prototype lives at `/home/dev/projects/job-search/.claude/pdf-render.py`. ~180 lines, single-file, PEP 723 metadata. Worth reading before designing the reportlab branch of `ocd:pdf` — covers the markdown-to-Flowables mapping, ParagraphStyle setup, inline-format XML escaping, and link/bold/italic handling for the resume-shape document.
