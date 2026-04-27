"""Tests for systems.log.research._compliance.

Heading-tree diff against a template; outlier detection; open-enumeration
recognition via `<placeholder>` convention; top-level order checking.
Uses tmp_path with synthetic markdown fixtures — no dependency on the
live research corpora.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from systems.log.research._compliance import (
    ComplianceReport,
    HeadingMismatch,
    OrderViolation,
    compare_to_template,
    compliance_summary,
    is_placeholder,
)


def _write_md(directory: Path, name: str, content: str) -> Path:
    """Dedent + write a markdown fixture; return the path."""
    path = directory / name
    path.write_text(textwrap.dedent(content).lstrip("\n"), encoding="utf-8")
    return path


# ─── is_placeholder convention ───────────────────────────────────────────


class TestIsPlaceholder:
    def test_angle_bracketed_text_is_placeholder(self):
        assert is_placeholder("<host name>")

    def test_canonical_text_is_not_placeholder(self):
        assert not is_placeholder("Claude Desktop")

    def test_single_word_in_brackets_is_placeholder(self):
        assert is_placeholder("<host>")

    def test_partial_brackets_are_not_placeholders(self):
        assert not is_placeholder("<incomplete")
        assert not is_placeholder("incomplete>")

    def test_empty_brackets_are_not_placeholders(self):
        # PLACEHOLDER_PATTERN requires at least one character inside
        assert not is_placeholder("<>")

    def test_text_around_brackets_disqualifies(self):
        # Pattern anchors to start/end; embedded brackets don't count
        assert not is_placeholder("Foo <bar>")
        assert not is_placeholder("<bar> Foo")

    def test_whitespace_is_stripped(self):
        assert is_placeholder("  <host name>  ")


# ─── compare_to_template — clean fixtures ────────────────────────────────


class TestCleanSample:
    def test_sample_matching_template_exactly_has_no_issues(self, tmp_path):
        template = _write_md(tmp_path, "_TEMPLATE.md", """
            # Sample

            ## Identification

            ### url

            ### one-line purpose

            ## Notable structural choices
        """)
        sample = _write_md(tmp_path, "good.md", """
            # Sample

            ## Identification

            ### url

            https://example.com/foo

            ### one-line purpose

            A foo.

            ## Notable structural choices

            Anything goes here.
        """)
        report = compare_to_template(sample, template)
        assert report.is_clean
        assert report.outliers == []
        assert report.out_of_order == []

    def test_sample_with_subset_of_template_sections_is_clean(self, tmp_path):
        """Sections are optional; omitting them is not a violation."""
        template = _write_md(tmp_path, "_TEMPLATE.md", """
            # Sample

            ## Identification

            ### url

            ## Transport

            ### supported transports

            ## Distribution
        """)
        sample = _write_md(tmp_path, "minimal.md", """
            # Sample

            ## Identification

            ### url

            https://example.com
        """)
        report = compare_to_template(sample, template)
        assert report.is_clean
        # Missing entries are informational, not violations
        assert "Sample > Transport" in report.missing
        assert "Sample > Distribution" in report.missing


# ─── compare_to_template — outlier detection ─────────────────────────────


class TestOutliers:
    def test_top_level_outlier_is_flagged(self, tmp_path):
        template = _write_md(tmp_path, "_TEMPLATE.md", """
            # Sample

            ## Identification

            ### url
        """)
        sample = _write_md(tmp_path, "extra.md", """
            # Sample

            ## Identification

            ### url

            https://example.com

            ## Vulnerability Assessment

            Some content.
        """)
        report = compare_to_template(sample, template)
        assert len(report.outliers) == 1
        outlier = report.outliers[0]
        assert outlier.chain_key == "Sample > Vulnerability Assessment"
        assert outlier.lineno > 0
        assert outlier.content_snippet == "Some content."

    def test_sub_purpose_outlier_is_flagged(self, tmp_path):
        template = _write_md(tmp_path, "_TEMPLATE.md", """
            # Sample

            ## Identification

            ### url
            ### stars
        """)
        sample = _write_md(tmp_path, "wrong-label.md", """
            # Sample

            ## Identification

            ### url

            https://example.com

            ### popularity

            12345
        """)
        report = compare_to_template(sample, template)
        assert len(report.outliers) == 1
        assert report.outliers[0].chain_key == "Sample > Identification > popularity"

    def test_canonical_sub_purpose_under_canonical_section_is_clean(self, tmp_path):
        template = _write_md(tmp_path, "_TEMPLATE.md", """
            # Sample

            ## Section

            ### canonical-sub
        """)
        sample = _write_md(tmp_path, "good.md", """
            # Sample

            ## Section

            ### canonical-sub

            yes
        """)
        report = compare_to_template(sample, template)
        assert report.is_clean


# ─── compare_to_template — open-enumeration via placeholder ──────────────


class TestOpenEnumeration:
    def test_placeholder_marks_parent_as_open_enumeration(self, tmp_path):
        template = _write_md(tmp_path, "_TEMPLATE.md", """
            # Sample

            ## Host integrations

            ### <host name>

            ### pitfalls observed
        """)
        sample = _write_md(tmp_path, "with-hosts.md", """
            # Sample

            ## Host integrations

            ### Claude Desktop

            JSON snippet.

            ### Cursor

            Install button.
        """)
        report = compare_to_template(sample, template)
        # Neither Claude Desktop nor Cursor is in canonical chains, but their
        # parent is open-enumeration → not outliers
        assert report.outliers == []

    def test_open_enumeration_does_not_blanket_other_sections(self, tmp_path):
        """An open-enumeration parent doesn't make sibling sections open."""
        template = _write_md(tmp_path, "_TEMPLATE.md", """
            # Sample

            ## Hosts

            ### <host name>

            ## Identification

            ### url
        """)
        sample = _write_md(tmp_path, "mixed.md", """
            # Sample

            ## Hosts

            ### Claude Desktop

            ## Identification

            ### url

            https://example.com

            ### unknown-field

            value
        """)
        report = compare_to_template(sample, template)
        assert len(report.outliers) == 1
        assert report.outliers[0].chain_key == "Sample > Identification > unknown-field"

    def test_canonical_sibling_under_open_parent_is_still_recognized(self, tmp_path):
        """Open-parent sections may also have canonical children (e.g. pitfalls)."""
        template = _write_md(tmp_path, "_TEMPLATE.md", """
            # Sample

            ## Host integrations

            ### <host name>

            ### pitfalls observed
        """)
        sample = _write_md(tmp_path, "host-with-pitfalls.md", """
            # Sample

            ## Host integrations

            ### Claude Desktop

            ### pitfalls observed

            Some real pitfall.
        """)
        report = compare_to_template(sample, template)
        assert report.is_clean


# ─── compare_to_template — order checking ────────────────────────────────


class TestOrder:
    def test_correct_order_is_clean(self, tmp_path):
        template = _write_md(tmp_path, "_TEMPLATE.md", """
            # Sample

            ## A
            ## B
            ## C
        """)
        sample = _write_md(tmp_path, "ordered.md", """
            # Sample

            ## A

            content

            ## B

            content

            ## C

            content
        """)
        report = compare_to_template(sample, template)
        assert report.out_of_order == []

    def test_swapped_top_level_sections_are_flagged(self, tmp_path):
        template = _write_md(tmp_path, "_TEMPLATE.md", """
            # Sample

            ## A
            ## B
            ## C
        """)
        sample = _write_md(tmp_path, "swapped.md", """
            # Sample

            ## A

            content

            ## C

            content

            ## B

            content
        """)
        report = compare_to_template(sample, template)
        assert len(report.out_of_order) == 1
        violation = report.out_of_order[0]
        assert violation.heading == "B"
        assert violation.appears_after == "C"

    def test_omitted_sections_do_not_break_order(self, tmp_path):
        """Subsequence-of-template, not exact match — skipping is fine."""
        template = _write_md(tmp_path, "_TEMPLATE.md", """
            # Sample

            ## A
            ## B
            ## C
            ## D
        """)
        sample = _write_md(tmp_path, "subset.md", """
            # Sample

            ## A

            content

            ## C

            content
        """)
        report = compare_to_template(sample, template)
        assert report.out_of_order == []


# ─── compliance_summary — corpus aggregation ─────────────────────────────


class TestCorpusSummary:
    def test_aggregates_outliers_across_samples(self, tmp_path):
        template = _write_md(tmp_path, "_TEMPLATE.md", """
            # Sample

            ## Identification

            ### url
        """)
        _write_md(tmp_path, "good.md", """
            # Sample

            ## Identification

            ### url

            https://a.com
        """)
        _write_md(tmp_path, "bad-1.md", """
            # Sample

            ## Identification

            ### url

            https://b.com

            ### popularity

            100
        """)
        _write_md(tmp_path, "bad-2.md", """
            # Sample

            ## Identification

            ### url

            https://c.com

            ### popularity

            200
        """)
        summary = compliance_summary(tmp_path, tmp_path / "_TEMPLATE.md")
        # Skips _TEMPLATE.md (underscore prefix); processes 3 sample files
        assert len(summary.reports) == 3
        # Same outlier name appears in 2 samples
        assert "Sample > Identification > popularity" in summary.outlier_counts
        assert len(summary.outlier_counts["Sample > Identification > popularity"]) == 2

    def test_skips_underscore_prefixed_files(self, tmp_path):
        template = _write_md(tmp_path, "_TEMPLATE.md", "# Sample\n## A\n")
        _write_md(tmp_path, "_INDEX.md", "# Index\n")
        _write_md(tmp_path, "sample.md", "# Sample\n## A\nyes\n")
        summary = compliance_summary(tmp_path, tmp_path / "_TEMPLATE.md")
        assert len(summary.reports) == 1
        assert summary.reports[0].sample_path.name == "sample.md"

    def test_empty_directory_returns_empty_summary(self, tmp_path):
        template = _write_md(tmp_path, "_TEMPLATE.md", "# Sample\n## A\n")
        summary = compliance_summary(tmp_path, tmp_path / "_TEMPLATE.md")
        assert summary.reports == []
        assert summary.outlier_counts == {}
        assert summary.missing_counts == {}


# ─── ComplianceReport API ────────────────────────────────────────────────


class TestComplianceReport:
    def test_is_clean_with_no_outliers_or_violations(self, tmp_path):
        template = _write_md(tmp_path, "_TEMPLATE.md", "# Sample\n## A\n")
        sample = _write_md(tmp_path, "s.md", "# Sample\n## A\ncontent\n")
        report = compare_to_template(sample, template)
        assert report.is_clean

    def test_is_clean_false_with_outliers(self, tmp_path):
        template = _write_md(tmp_path, "_TEMPLATE.md", "# Sample\n## A\n")
        sample = _write_md(tmp_path, "s.md", "# Sample\n## A\n## Z\ncontent\n")
        report = compare_to_template(sample, template)
        assert not report.is_clean

    def test_is_clean_ignores_missing_entries(self, tmp_path):
        """Missing template chains are informational; don't fail is_clean."""
        template = _write_md(tmp_path, "_TEMPLATE.md", "# Sample\n## A\n## B\n## C\n")
        sample = _write_md(tmp_path, "s.md", "# Sample\n## A\ncontent\n")
        report = compare_to_template(sample, template)
        assert report.is_clean
        assert len(report.missing) > 0
