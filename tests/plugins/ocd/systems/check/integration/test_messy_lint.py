"""Integration tests for the markdown lint against the shared messy fixture.

Tests act as regression guards for:
  - Literal-character detection (`{`, `}`, `<`, `>`) in unprotected
    positions; HTML tags and blockquote markers are exempt.
  - Blank-line discipline rules (blank line in continuous list,
    missing blank before block, missing blank after heading,
    multiple sequential blank lines).
  - Auto-fix behavior for blank-line rules (idempotent, preserves
    non-offending content).
  - Literal-char violations are NOT auto-fixed (they need human/agent
    judgment for context-appropriate wrapping).
  - Headings and blockquotes are legitimate list-continuation
    interrupters — blanks around them are required and must NOT be
    flagged as "Markdown - blank line in continuous list".

Rule labels are descriptive strings — see `_markdown.py`:

  "Markdown - unprotected literal character"
  "Markdown - blank line in continuous list"
  "Markdown - missing blank line before block"
  "Markdown - missing blank line after heading"
  "Markdown - multiple sequential blank lines"
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from systems.check._markdown import scan_file


LITERAL = "Markdown - unprotected literal character"
BLANK_IN_LIST = "Markdown - blank line in continuous list"
NO_BLANK_BEFORE_BLOCK = "Markdown - missing blank line before block"
NO_BLANK_AFTER_HEADING = "Markdown - missing blank line after heading"
CONSECUTIVE_BLANKS = "Markdown - multiple sequential blank lines"


@pytest.fixture
def fixture_copy(tmp_path: Path, messy_markdown: Path) -> Path:
    """Writable copy of the fixture — for auto-fix tests that mutate."""
    dest = tmp_path / "messy-markdown.md"
    shutil.copy(messy_markdown, dest)
    return dest


def _violations_by_rule(path: Path, rule: str) -> list:
    return [v for v in scan_file(path) if v.rule == rule]


class TestLiteralCharDetection:
    def test_finds_preserved_placeholders_as_benign_violations(
        self, messy_markdown: Path
    ):
        """The `{preserved-*}` placeholders are technically rule
        violations per markdown.md but are in benign contexts (prose,
        list item, blockquote) where they won't be consumed. The lint
        should still report them — narrowing to "only risky positions"
        is a separate concern from basic detection.
        """
        placeholder_hits = [v for v in _violations_by_rule(messy_markdown, LITERAL) if v.char == "{"]
        context_texts = [v.context for v in placeholder_hits]
        assert any("preserved-prose" in c for c in context_texts)
        assert any("preserved-list" in c for c in context_texts)
        assert any("preserved-blockquote" in c for c in context_texts)

    def test_finds_literal_placeholder_in_prose(self, messy_markdown: Path):
        hits = [
            v for v in _violations_by_rule(messy_markdown, LITERAL)
            if v.char == "{" and "literal-placeholder" in v.context
        ]
        assert hits, "expected { violation on `{literal-placeholder}` prose line"

    def test_arrow_literal_detected(self, messy_markdown: Path):
        """`proposes -> Aaron` — `>` is an unprotected literal."""
        hits = [
            v for v in _violations_by_rule(messy_markdown, LITERAL)
            if v.char == ">" and "proposes -> Aaron" in v.context
        ]
        assert hits, "expected > violation on arrow prose line"

    def test_math_style_literal_detected(self, messy_markdown: Path):
        """`volunteers > 50` — `>` is an unprotected literal."""
        hits = [
            v for v in _violations_by_rule(messy_markdown, LITERAL)
            if v.char == ">" and "volunteers > 50" in v.context
        ]
        assert hits, "expected > violation on math prose line"

    def test_blockquote_marker_not_flagged(self, messy_markdown: Path):
        """A `> Blockquote: …` line's leading `>` is markdown syntax, not
        a literal, and must not be flagged at col 1.
        """
        false_positive = [
            v for v in _violations_by_rule(messy_markdown, LITERAL)
            if v.char == ">" and v.col == 1
        ]
        assert not false_positive, (
            f"blockquote `>` marker incorrectly flagged: {false_positive}"
        )

    def test_attr_list_syntax_still_reported(self, messy_markdown: Path):
        """`### SubHead {#consumed-id}` has a legitimate attr_list `{`.
        The scanner doesn't know intent, so it still reports — this is
        intentional broad-defensiveness. Keeping as a regression anchor:
        if we ever narrow the lint to risky-position-only, this test
        changes meaning.
        """
        hits = [
            v for v in _violations_by_rule(messy_markdown, LITERAL)
            if v.char == "{" and "#consumed-id" in v.context
        ]
        assert hits, "scanner should still report { at attr_list position"


class TestBlankLineRules:
    """Descriptive-rule-label checks against the messy fixture."""

    def test_blank_in_continuous_list_flagged(self, messy_markdown: Path):
        """A blank line between two same-indent list items with no
        interrupting block must fire the continuous-list rule."""
        hits = _violations_by_rule(messy_markdown, BLANK_IN_LIST)
        assert hits, (
            "expected at least one blank-in-list violation from the "
            "`## BLANK-IN-LIST Violation` section of the fixture"
        )

    def test_missing_blank_before_block_flagged(self, messy_markdown: Path):
        """A heading preceded directly by prose (no blank line) fires
        the missing-blank-before-block rule."""
        hits = _violations_by_rule(messy_markdown, NO_BLANK_BEFORE_BLOCK)
        # Find the one anchored to `### Subheading missing blank above`
        matching = [v for v in hits if "missing blank above" in v.context]
        assert matching, (
            "expected heading with `missing blank above` to be flagged"
        )

    def test_missing_blank_after_heading_flagged(self, messy_markdown: Path):
        """A heading followed directly by content (no blank line) fires
        the missing-blank-after-heading rule."""
        hits = _violations_by_rule(messy_markdown, NO_BLANK_AFTER_HEADING)
        matching = [v for v in hits if "Heading needs blank after" in v.context]
        assert matching, (
            "expected `Heading needs blank after` to be flagged"
        )

    def test_consecutive_blanks_flagged(self, messy_markdown: Path):
        """Two blank lines in a row fires the consecutive-blanks rule
        on the second blank."""
        hits = _violations_by_rule(messy_markdown, CONSECUTIVE_BLANKS)
        assert hits, "expected at least one consecutive-blanks violation"


class TestListInterruptionExemption:
    """Headings and blockquotes breaking up a list are legitimate
    continuation patterns. The blanks *required* around those blocks
    must NOT be flagged as blank-line-in-continuous-list violations.

    Fixture section: `## List With Heading And Blockquote Interruption`.
    """

    def test_blanks_around_heading_interruption_not_flagged(
        self, messy_markdown: Path
    ):
        """Layout: `- Item A` / (blank) / `### Subheading` / (blank)
        / `- Item B`. The two blanks surround a heading — required by
        the missing-blank-before-block and missing-blank-after-heading
        rules — and must NOT fire blank-in-list.
        """
        text = messy_markdown.read_text(encoding="utf-8").splitlines()
        # Identify the heading line by its unique text
        heading_matches = [
            i for i, line in enumerate(text)
            if line.strip() == "### Interrupting Subheading"
        ]
        assert heading_matches, (
            "fixture is missing `### Interrupting Subheading`"
        )
        heading_idx = heading_matches[0]

        # The blanks immediately above and below the heading
        blank_before = heading_idx  # 1-indexed line = heading_idx
        blank_after = heading_idx + 2  # line after heading (1-indexed)

        hits = _violations_by_rule(messy_markdown, BLANK_IN_LIST)
        flagged_lines = {v.line for v in hits}
        assert blank_before not in flagged_lines, (
            f"blank line before list-interrupting heading at L{blank_before} "
            f"was incorrectly flagged as blank-in-list"
        )
        assert blank_after not in flagged_lines, (
            f"blank line after list-interrupting heading at L{blank_after} "
            f"was incorrectly flagged as blank-in-list"
        )

    def test_blanks_around_blockquote_interruption_not_flagged(
        self, messy_markdown: Path
    ):
        """Layout: `- Item C` / (blank) / `> comment` / (blank) /
        `- Item D`. Blankquotes require a blank line above and below,
        so the two blanks must NOT fire blank-in-list.
        """
        text = messy_markdown.read_text(encoding="utf-8").splitlines()
        bq_matches = [
            i for i, line in enumerate(text)
            if line.strip() == "> Interrupting blockquote comment"
        ]
        assert bq_matches, (
            "fixture is missing `> Interrupting blockquote comment`"
        )
        bq_idx = bq_matches[0]

        blank_before = bq_idx
        blank_after = bq_idx + 2

        hits = _violations_by_rule(messy_markdown, BLANK_IN_LIST)
        flagged_lines = {v.line for v in hits}
        assert blank_before not in flagged_lines, (
            f"blank line before interrupting blockquote at L{blank_before} "
            f"was incorrectly flagged as blank-in-list"
        )
        assert blank_after not in flagged_lines, (
            f"blank line after interrupting blockquote at L{blank_after} "
            f"was incorrectly flagged as blank-in-list"
        )


class TestBlankLineAutoFix:
    """Blank-line rules are safe to auto-fix deterministically — unlike
    literal-char violations which need judgment."""

    def test_autofix_removes_blank_in_list(self, fixture_copy: Path):
        from systems.check._markdown import fix_blank_lines

        fix_blank_lines(fixture_copy)
        assert not _violations_by_rule(fixture_copy, BLANK_IN_LIST)

    def test_autofix_inserts_blank_before_block(self, fixture_copy: Path):
        from systems.check._markdown import fix_blank_lines

        fix_blank_lines(fixture_copy)
        assert not _violations_by_rule(fixture_copy, NO_BLANK_BEFORE_BLOCK)

    def test_autofix_inserts_blank_after_heading(self, fixture_copy: Path):
        from systems.check._markdown import fix_blank_lines

        fix_blank_lines(fixture_copy)
        assert not _violations_by_rule(fixture_copy, NO_BLANK_AFTER_HEADING)

    def test_autofix_collapses_consecutive_blanks(self, fixture_copy: Path):
        from systems.check._markdown import fix_blank_lines

        fix_blank_lines(fixture_copy)
        assert not _violations_by_rule(fixture_copy, CONSECUTIVE_BLANKS)

    def test_autofix_idempotent(self, fixture_copy: Path):
        """Running the autofix a second time must produce zero changes."""
        from systems.check._markdown import fix_blank_lines

        fix_blank_lines(fixture_copy)
        after_first = fixture_copy.read_bytes()
        fix_blank_lines(fixture_copy)
        after_second = fixture_copy.read_bytes()
        assert after_first == after_second, "autofix is not idempotent"

    def test_autofix_preserves_literal_char_violations(self, fixture_copy: Path):
        """Autofix targets blank-line rules only; literal-char violations
        (which need judgment) stay flagged.
        """
        from systems.check._markdown import fix_blank_lines

        fix_blank_lines(fixture_copy)
        assert _violations_by_rule(fixture_copy, LITERAL), (
            "autofix should not touch literal-char violations"
        )
