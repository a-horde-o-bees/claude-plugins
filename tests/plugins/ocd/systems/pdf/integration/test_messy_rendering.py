"""Integration tests for PDF rendering of the shared messy fixture.

The fixture combines every pathological case into one markdown file so
generate_pdf runs once per test module and many assertions fan out over
the single rendered PDF's font table and text layer.

These tests act as regression guards for:
  - Italic font-face loading (FontConfiguration in generate_pdf)
  - Placeholder preservation in prose / list / blockquote contexts
  - Legitimate attr_list consumption on trailing-heading attrs
  - Ordered list numbering continuity after a blockquote interrupt
    (requires `sane_lists` extension)
  - Bullet markers inline with text in extraction (list-style-position:
    inside + list-style-type: "- " in the preset CSS)
"""

from __future__ import annotations

from pathlib import Path

import pytest
from pypdf import PdfReader

from systems.pdf import generate_pdf


@pytest.fixture(scope="module")
def rendered_pdf(
    tmp_path_factory,
    messy_markdown: Path,
    preset_compact_css: Path,
) -> Path:
    """Render the messy fixture once per module against the real preset.

    All tests reuse the single rendered PDF. Using the real preset CSS
    (not a synthetic one) means relative @font-face URLs and preset list
    choices are covered end-to-end.
    """
    if not preset_compact_css.is_file():
        pytest.skip(f"preset css not found at {preset_compact_css}")
    tmp = tmp_path_factory.mktemp("messy-render")
    dest = tmp / "messy.pdf"
    generate_pdf(messy_markdown, dest, preset_compact_css)
    assert dest.exists(), "generate_pdf did not produce expected output"
    return dest


@pytest.fixture(scope="module")
def embedded_fonts(rendered_pdf: Path) -> set[str]:
    """Set of BaseFont names embedded in the rendered PDF."""
    reader = PdfReader(str(rendered_pdf))
    fonts: set[str] = set()
    for page in reader.pages:
        resources = page.get("/Resources")
        if not resources:
            continue
        font_dict = resources.get("/Font") if resources else None
        if not font_dict:
            continue
        for _, font_ref in font_dict.items():
            font_obj = font_ref.get_object()
            base_font = font_obj.get("/BaseFont") if font_obj else None
            if base_font:
                fonts.add(str(base_font))
    return fonts


@pytest.fixture(scope="module")
def extracted_text(rendered_pdf: Path) -> str:
    """Concatenated text from every page of the rendered PDF."""
    reader = PdfReader(str(rendered_pdf))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


class TestFontLoading:
    def test_roboto_italic_embeds_with_preset_css(self, embedded_fonts: set[str]):
        """With FontConfiguration wired and @font-face declarations in the
        preset, italic text must resolve to a real italic Roboto face in
        the PDF font table rather than falling back to synthetic italic
        or a different family entirely.
        """
        italic_present = any("Italic" in f for f in embedded_fonts)
        assert italic_present, (
            "No italic font face embedded in the rendered PDF. "
            f"Fonts present: {sorted(embedded_fonts)}"
        )


class TestPlaceholderPreservation:
    """Stand-alone `{...}` placeholders must survive rendering in every
    non-risky markdown context — paragraph, list item, blockquote. The
    python-markdown `attr_list` extension only consumes `{...}` at the
    end of specific block-end positions (trailing heading, trailing
    table cell, link-target attribute)."""

    def test_prose_placeholder_survives(self, extracted_text: str):
        assert "{preserved-prose}" in extracted_text

    def test_list_item_placeholder_survives(self, extracted_text: str):
        assert "{preserved-list}" in extracted_text

    def test_blockquote_placeholder_survives(self, extracted_text: str):
        assert "{preserved-blockquote}" in extracted_text


class TestAttrListLegitimateConsumption:
    def test_heading_attr_list_is_consumed(self, extracted_text: str):
        """`### SubHead {#consumed-id}` is intentional attr_list syntax —
        the `{#consumed-id}` token gets converted to an HTML id attribute
        on the heading and must NOT appear in extracted text.
        """
        assert "{#consumed-id}" not in extracted_text


class TestOrderedListNumberingContinuity:
    def test_list_continues_across_blockquote(self, extracted_text: str):
        """An ordered list split by an intervening blockquote must
        preserve its explicit start number on the second half, rendering
        items 3 and 4 as `3.` and `4.` — not restarting at `1.`. This
        requires the `sane_lists` markdown extension.
        """
        # Must contain "3. Third" and "4. Fourth" verbatim
        assert "3. Third must still render as 3" in extracted_text
        assert "4. Fourth must render as 4" in extracted_text


class TestListInterruptionRendering:
    """Headings and blockquotes that interrupt a list should render
    with blank lines preserved around them — no content should be
    stripped, and both halves of the interrupted list must appear."""

    def test_items_before_and_after_heading_render(self, extracted_text: str):
        assert "Item A before heading interruption" in extracted_text
        assert "Item B before heading interruption" in extracted_text
        assert "Interrupting Subheading" in extracted_text
        assert "Item C after heading and before blockquote interruption" in extracted_text

    def test_items_before_and_after_blockquote_render(self, extracted_text: str):
        assert "Interrupting blockquote comment" in extracted_text
        assert "Item D after blockquote interruption" in extracted_text


class TestListMarkerInline:
    def test_bullet_marker_and_text_same_line(self, extracted_text: str):
        """With `list-style-position: inside` in the preset CSS, bullet
        markers share the same PDF text run as their bullet content.
        Extraction should produce the marker character directly preceding
        the content on the same logical line.
        """
        # We use the preset's list-style-type: "- " marker.
        # Confirm at least one hyphen-prefixed bullet appears in extraction.
        bullet_line_found = any(
            line.strip().startswith("- Bullet") or line.strip().startswith("-Bullet")
            for line in extracted_text.splitlines()
        )
        assert bullet_line_found, (
            "No hyphen-prefixed bullet found in extracted text. "
            f"Lines sampled: {extracted_text.splitlines()[:30]}"
        )
