"""Tests for logs/research/_scripts/sample_tools.py.

Heading-tree parse/serialize round-trip, sibling-duplicate detection,
cross-sample counting, and section consolidation. Uses tmp_path with
synthetic markdown fixtures — no dependency on the live research corpora.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from sample_tools import (
    CHAIN_SEPARATOR,
    DuplicateHeadingError,
    Section,
    check_no_duplicate_headings,
    consolidate_section,
    count_sections,
    heading_text,
    parse_headings,
    serialize,
)


def _write_md(directory: Path, name: str, content: str) -> Path:
    """Dedent + write a markdown fixture; return the path."""
    path = directory / name
    path.write_text(textwrap.dedent(content).lstrip("\n"), encoding="utf-8")
    return path


# ─── heading_text normalization ──────────────────────────────────────────

class TestHeadingText:
    def test_strips_leading_hashes(self):
        assert heading_text("## Transport") == "Transport"

    def test_strips_leading_spaces_then_hashes(self):
        assert heading_text("  ### Nested") == "Nested"

    def test_strips_trailing_whitespace(self):
        assert heading_text("## Transport   ") == "Transport"

    def test_strips_atx_closing_hashes(self):
        assert heading_text("## Transport ##") == "Transport"

    def test_strips_attr_list_id(self):
        assert heading_text("## Transport {#transport-id}") == "Transport"

    def test_strips_attr_list_class_and_id(self):
        assert heading_text("## Transport {.class1 .class2 #id}") == "Transport"

    def test_strips_closing_hashes_and_attr_list(self):
        assert heading_text("## Transport {#id} ##") == "Transport"

    def test_embedded_hash_without_space_preserved(self):
        # A `#` inside text (no space before it) is NOT a closing marker
        assert heading_text("## C# Language") == "C# Language"


# ─── parse_headings ──────────────────────────────────────────────────────

class TestParseHeadings:
    def test_empty_file(self, tmp_path: Path):
        p = _write_md(tmp_path, "empty.md", "")
        root = parse_headings(p)
        assert root.heading_line == ""
        assert root.level == 0
        assert root.direct_content == ""
        assert root.children == []

    def test_no_headings_content_goes_to_root(self, tmp_path: Path):
        p = _write_md(tmp_path, "no_headings.md", """
            Just some prose.

            No headings here.
        """)
        root = parse_headings(p)
        assert root.children == []
        assert "Just some prose." in root.direct_content
        assert "No headings here." in root.direct_content

    def test_single_heading(self, tmp_path: Path):
        p = _write_md(tmp_path, "one.md", """
            # Title

            Content under title.
        """)
        root = parse_headings(p)
        assert len(root.children) == 1
        assert root.children[0].heading_line == "# Title"
        assert root.children[0].level == 1
        assert root.children[0].lineno == 1
        assert "Content under title." in root.children[0].direct_content

    def test_nested_tree(self, tmp_path: Path):
        p = _write_md(tmp_path, "nested.md", """
            # Title

            ## Section A

            Content A.

            ### Subsection A1

            A1 content.

            ## Section B

            Content B.
        """)
        root = parse_headings(p)
        assert len(root.children) == 1
        title = root.children[0]
        assert title.heading_line == "# Title"
        assert len(title.children) == 2

        section_a = title.children[0]
        assert section_a.heading_line == "## Section A"
        assert section_a.level == 2
        assert len(section_a.children) == 1
        assert section_a.children[0].heading_line == "### Subsection A1"
        assert section_a.children[0].level == 3

        section_b = title.children[1]
        assert section_b.heading_line == "## Section B"
        assert section_b.children == []

    def test_preamble_before_first_heading_lives_on_root(self, tmp_path: Path):
        p = _write_md(tmp_path, "preamble.md", """
            Preamble prose.

            # Actual Title

            Body.
        """)
        root = parse_headings(p)
        assert "Preamble prose." in root.direct_content
        assert len(root.children) == 1

    def test_lineno_tracks_heading_source_line(self, tmp_path: Path):
        p = _write_md(tmp_path, "lineno.md", """
            # Title

            Intro.

            ## Second
        """)
        root = parse_headings(p)
        assert root.children[0].lineno == 1
        assert root.children[0].children[0].lineno == 5

    def test_indented_code_block_is_not_heading(self, tmp_path: Path):
        # 4+ spaces of indent means code block; leading # is literal
        p = _write_md(tmp_path, "code.md", """
            # Real Heading

                # This is code, not a heading

            After.
        """)
        root = parse_headings(p)
        assert len(root.children) == 1
        assert root.children[0].heading_line == "# Real Heading"


# ─── serialize round-trip ────────────────────────────────────────────────

class TestSerialize:
    def test_roundtrip_preserves_source(self, tmp_path: Path):
        original = textwrap.dedent("""
            # Title

            Preamble text.

            ## Section A

            Content A.

            ### Subsection A1

            A1 content.

            ## Section B

            Content B.
        """).lstrip("\n")
        p = tmp_path / "f.md"
        p.write_text(original, encoding="utf-8")
        root = parse_headings(p)
        assert serialize(root) == original

    def test_empty_section_serializes_empty(self):
        root = Section(heading_line="", level=0, direct_content="", children=[], lineno=0)
        assert serialize(root) == ""

    def test_root_preamble_preserved(self, tmp_path: Path):
        original = "Preamble here.\n\n# Title\n\nBody.\n"
        p = tmp_path / "f.md"
        p.write_text(original, encoding="utf-8")
        root = parse_headings(p)
        assert serialize(root) == original

    def test_heading_line_verbatim_including_attr_list(self, tmp_path: Path):
        original = "## Config {#config-id}\n\nBody.\n"
        p = tmp_path / "f.md"
        p.write_text(original, encoding="utf-8")
        root = parse_headings(p)
        assert root.children[0].heading_line == "## Config {#config-id}"
        assert serialize(root) == original


# ─── duplicate-heading detection ─────────────────────────────────────────

class TestCheckNoDuplicateHeadings:
    def test_no_duplicates_passes(self, tmp_path: Path):
        p = _write_md(tmp_path, "clean.md", """
            # Title

            ## A

            ## B

            ### A
        """)
        check_no_duplicate_headings(p)  # no raise

    def test_sibling_duplicates_raises(self, tmp_path: Path):
        p = _write_md(tmp_path, "dup.md", """
            # Title

            ## Section

            ## Section
        """)
        with pytest.raises(DuplicateHeadingError) as exc_info:
            check_no_duplicate_headings(p)
        assert "Section" in exc_info.value.chain_key
        assert exc_info.value.first_lineno == 3
        assert exc_info.value.second_lineno == 5

    def test_nested_sibling_duplicates_raises(self, tmp_path: Path):
        p = _write_md(tmp_path, "nested_dup.md", """
            # Title

            ## Tests

            ### Unit

            ### Unit
        """)
        with pytest.raises(DuplicateHeadingError) as exc_info:
            check_no_duplicate_headings(p)
        # Full chain from root — `Title > Tests > Unit` — so reviewer sees scope
        expected = CHAIN_SEPARATOR.join(["Title", "Tests", "Unit"])
        assert exc_info.value.chain_key == expected

    def test_same_text_under_different_parents_passes(self, tmp_path: Path):
        p = _write_md(tmp_path, "different_parents.md", """
            # Title

            ## Tests

            ### Unit

            ## Coverage

            ### Unit
        """)
        check_no_duplicate_headings(p)  # no raise — different parents

    def test_attr_list_siblings_detected(self, tmp_path: Path):
        """`## Config {#id1}` and `## Config {#id2}` normalize to same text."""
        p = _write_md(tmp_path, "attr_dup.md", """
            # Title

            ## Config {#first}

            ## Config {#second}
        """)
        with pytest.raises(DuplicateHeadingError):
            check_no_duplicate_headings(p)


# ─── count_sections ──────────────────────────────────────────────────────

class TestCountSections:
    def test_aggregates_across_files(self, tmp_path: Path):
        sample_dir = tmp_path / "samples"
        sample_dir.mkdir()
        _write_md(sample_dir, "a.md", """
            # Root

            ## Identification

            ## Transport
        """)
        _write_md(sample_dir, "b.md", """
            # Root

            ## Identification

            ## Tests
        """)
        counts = count_sections(sample_dir)
        assert sorted(counts["Root"]) == [sample_dir / "a.md", sample_dir / "b.md"]
        root_ident = "Root" + CHAIN_SEPARATOR + "Identification"
        assert sorted(counts[root_ident]) == [sample_dir / "a.md", sample_dir / "b.md"]
        assert counts["Root" + CHAIN_SEPARATOR + "Transport"] == [sample_dir / "a.md"]
        assert counts["Root" + CHAIN_SEPARATOR + "Tests"] == [sample_dir / "b.md"]

    def test_skips_underscore_prefixed_files(self, tmp_path: Path):
        sample_dir = tmp_path / "samples"
        sample_dir.mkdir()
        _write_md(sample_dir, "real.md", "# Root\n## Included\n")
        _write_md(sample_dir, "_template.md", "# Root\n## Ignored\n")
        _write_md(sample_dir, "_missing--foo.md", "# Root\n## AlsoIgnored\n")
        counts = count_sections(sample_dir)
        assert "Root" + CHAIN_SEPARATOR + "Included" in counts
        assert "Root" + CHAIN_SEPARATOR + "Ignored" not in counts
        assert "Root" + CHAIN_SEPARATOR + "AlsoIgnored" not in counts

    def test_empty_directory(self, tmp_path: Path):
        sample_dir = tmp_path / "samples"
        sample_dir.mkdir()
        assert count_sections(sample_dir) == {}


# ─── consolidate_section ─────────────────────────────────────────────────

class TestConsolidateSection:
    def test_returns_content_per_matching_file(self, tmp_path: Path):
        sample_dir = tmp_path / "samples"
        sample_dir.mkdir()
        _write_md(sample_dir, "a.md", """
            # Root

            ## Transport

            STDIO only.
        """)
        _write_md(sample_dir, "b.md", """
            # Root

            ## Transport

            HTTP and SSE.
        """)
        results = consolidate_section("Root" + CHAIN_SEPARATOR + "Transport", sample_dir)
        assert len(results) == 2
        contents = {path.name: content for path, content in results}
        assert "STDIO only." in contents["a.md"]
        assert "HTTP and SSE." in contents["b.md"]

    def test_omits_files_missing_the_section(self, tmp_path: Path):
        sample_dir = tmp_path / "samples"
        sample_dir.mkdir()
        _write_md(sample_dir, "a.md", "# Root\n\n## Transport\n\nX\n")
        _write_md(sample_dir, "b.md", "# Root\n\n## Tests\n\nY\n")
        results = consolidate_section("Root" + CHAIN_SEPARATOR + "Transport", sample_dir)
        assert len(results) == 1
        assert results[0][0].name == "a.md"

    def test_nested_chain_key(self, tmp_path: Path):
        sample_dir = tmp_path / "samples"
        sample_dir.mkdir()
        _write_md(sample_dir, "a.md", """
            # Root

            ## Transport

            ### Configuration

            env vars.
        """)
        chain = "Root" + CHAIN_SEPARATOR + "Transport" + CHAIN_SEPARATOR + "Configuration"
        results = consolidate_section(chain, sample_dir)
        assert len(results) == 1
        assert "env vars." in results[0][1]

    def test_consolidated_content_includes_subtree(self, tmp_path: Path):
        """Returned content for a section includes its nested children too."""
        sample_dir = tmp_path / "samples"
        sample_dir.mkdir()
        _write_md(sample_dir, "a.md", """
            # Root

            ## Transport

            Transport intro.

            ### Configuration

            Config details.
        """)
        results = consolidate_section("Root" + CHAIN_SEPARATOR + "Transport", sample_dir)
        assert len(results) == 1
        content = results[0][1]
        assert "Transport intro." in content
        assert "### Configuration" in content
        assert "Config details." in content

    def test_chain_key_not_found_returns_empty(self, tmp_path: Path):
        sample_dir = tmp_path / "samples"
        sample_dir.mkdir()
        _write_md(sample_dir, "a.md", "# Root\n\n## A\n")
        results = consolidate_section("Root" + CHAIN_SEPARATOR + "Nonexistent", sample_dir)
        assert results == []
