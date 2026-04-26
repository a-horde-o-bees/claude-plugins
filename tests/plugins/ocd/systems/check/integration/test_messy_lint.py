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
BLANK_AT_FENCE_START = "Markdown - blank line at start of fenced block"
BLANK_AT_FENCE_END = "Markdown - blank line at end of fenced block"


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


class TestFrontmatterOpacity:
    """YAML frontmatter is parsed separately from markdown body. The
    scanner must not apply markdown rules to its content — `<`, `>`,
    `{`, `}` in YAML values are not literal-character violations, and
    blank-line discipline does not apply.

    Fixture frontmatter (lines 1–6 after the shift): the title key,
    an `argument-hint` with nested angle brackets, a placeholder-key
    with `{frontmatter-placeholder}`, and an emphasis-look-alike line.
    """

    def test_angle_brackets_in_argument_hint_not_flagged(
        self, messy_markdown: Path
    ):
        hits = [
            v for v in _violations_by_rule(messy_markdown, LITERAL)
            if "argument-hint" in v.context
        ]
        assert not hits, (
            f"angle brackets inside YAML frontmatter incorrectly flagged: {hits}"
        )

    def test_brace_placeholder_in_frontmatter_not_flagged(
        self, messy_markdown: Path
    ):
        hits = [
            v for v in _violations_by_rule(messy_markdown, LITERAL)
            if "frontmatter-placeholder" in v.context
        ]
        assert not hits, (
            f"`{{...}}` inside YAML frontmatter incorrectly flagged: {hits}"
        )

    def test_strict_emphasis_chars_in_frontmatter_not_flagged(
        self, messy_markdown: Path
    ):
        from systems.check._markdown import scan_file

        violations = [v for v in scan_file(messy_markdown, strict=True)
                      if v.rule == LITERAL]
        hits = [v for v in violations if "emphasis-look-alike" in v.context]
        assert not hits, (
            f"`*` / `_` inside YAML frontmatter incorrectly flagged in strict "
            f"mode: {hits}"
        )

    def test_blank_line_rules_not_applied_inside_frontmatter(
        self, messy_markdown: Path
    ):
        """Frontmatter has back-to-back YAML keys (no blank lines) and
        ends adjacent to the level-1 heading. None of the four blank-line
        rules should fire on lines inside or at the boundary of the
        frontmatter block.
        """
        text = messy_markdown.read_text(encoding="utf-8").splitlines()
        # Find the closing `---` line index (1-indexed)
        closer_idx = next(
            (i + 1 for i, line in enumerate(text)
             if i > 0 and line.rstrip() == "---"),
            None,
        )
        assert closer_idx is not None, "fixture frontmatter has no closing `---`"
        from systems.check._markdown import scan_blank_lines

        violations = scan_blank_lines(messy_markdown)
        flagged_in_frontmatter = [
            v for v in violations if v.line <= closer_idx
        ]
        assert not flagged_in_frontmatter, (
            f"blank-line rules fired inside YAML frontmatter: "
            f"{flagged_in_frontmatter}"
        )


class TestFencedCodeBlockOpacity:
    """A fenced code block is one structural unit — like a paragraph.
    Blank-line rules don't peek inside, and the closing fence is not
    a "block start" needing a blank line above (its predecessor is
    code body).

    Fixture section: `## Fenced Code Block — Single Structural Unit`.
    """

    def _fence_lines(self, path: Path) -> tuple[int, int]:
        """Return (open_line, close_line) — 1-indexed — for the fixture
        ```python ... ``` block.
        """
        lines = path.read_text(encoding="utf-8").splitlines()
        open_line = next(
            (i + 1 for i, line in enumerate(lines) if line.strip() == "```python"),
            None,
        )
        assert open_line is not None, "fixture python fence opener missing"
        close_line = next(
            (i + 1 for i, line in enumerate(lines)
             if i + 1 > open_line and line.strip() == "```"),
            None,
        )
        assert close_line is not None, "fixture python fence closer missing"
        return open_line, close_line

    def test_heading_like_line_inside_fence_not_flagged(
        self, messy_markdown: Path
    ):
        """`### def looks_like_heading():` inside a fence resembles a
        heading at the prefix level but is code. Neither
        missing-blank-before-block nor missing-blank-after-heading must
        fire on it.
        """
        open_line, close_line = self._fence_lines(messy_markdown)
        for rule in (NO_BLANK_BEFORE_BLOCK, NO_BLANK_AFTER_HEADING):
            hits = [
                v for v in _violations_by_rule(messy_markdown, rule)
                if open_line < v.line < close_line
            ]
            assert not hits, (
                f"{rule} fired on fence-interior line: {hits}"
            )

    def test_closing_fence_not_flagged_as_block_start(
        self, messy_markdown: Path
    ):
        """The closing ``` of a fenced block is the end of the block,
        not the start of a new one — the line above it is code body
        which is necessarily non-blank, so flagging it as missing-
        blank-before-block would be unconditional.
        """
        _, close_line = self._fence_lines(messy_markdown)
        hits = [
            v for v in _violations_by_rule(messy_markdown, NO_BLANK_BEFORE_BLOCK)
            if v.line == close_line
        ]
        assert not hits, (
            f"closing fence flagged as missing-blank-before-block: {hits}"
        )

    def test_opening_fence_with_blank_above_does_not_fire(
        self, messy_markdown: Path
    ):
        """Sanity: the fixture's python fence has a blank line above
        its opener. Confirm the rule still respects that — i.e. the
        rule is still active on opener lines, not silenced wholesale.
        """
        open_line, _ = self._fence_lines(messy_markdown)
        hits = [
            v for v in _violations_by_rule(messy_markdown, NO_BLANK_BEFORE_BLOCK)
            if v.line == open_line
        ]
        assert not hits, (
            f"opener with blank line above incorrectly flagged: {hits}"
        )


class TestFenceInnerDiscipline:
    """Some discipline rules pierce fence opacity:

      - Multi-blank consolidation applies inside fences (runs of blank
        lines are noise the same as in prose).
      - The fence body must not begin with a blank line.
      - The fence body must not end with a blank line.

    Fixture section: `## Fenced Code Block — Inner Discipline Still Applies`.
    """

    def test_consecutive_blanks_inside_fence_flagged(
        self, messy_markdown: Path
    ):
        """`first body line / (blank) / (blank) / second body line` inside
        a fence fires the multi-blank rule on the second blank.
        """
        lines = messy_markdown.read_text(encoding="utf-8").splitlines()
        anchor = next(
            (i + 1 for i, line in enumerate(lines)
             if "first body line" in line),
            None,
        )
        assert anchor is not None, "fixture missing `first body line` anchor"
        # The two blank lines follow at anchor+1 and anchor+2; the rule
        # fires on the second blank (anchor + 2).
        hits = [
            v for v in _violations_by_rule(messy_markdown, CONSECUTIVE_BLANKS)
            if v.line == anchor + 2
        ]
        assert hits, (
            f"multi-blank rule did not fire on consecutive blanks inside "
            f"a fenced block at line {anchor + 2}"
        )

    def test_blank_at_start_of_fence_flagged(self, messy_markdown: Path):
        """Fixture has a fence whose first body line is blank — the
        opener is followed immediately by an empty line. The new rule
        must fire on that blank line.
        """
        hits = _violations_by_rule(messy_markdown, BLANK_AT_FENCE_START)
        assert hits, (
            "expected at least one blank-at-start-of-fence violation"
        )

    def test_blank_at_end_of_fence_flagged(self, messy_markdown: Path):
        """Fixture has a fence whose last body line is blank — the
        closer is preceded immediately by an empty line. The new rule
        must fire on that blank line.
        """
        hits = _violations_by_rule(messy_markdown, BLANK_AT_FENCE_END)
        assert hits, (
            "expected at least one blank-at-end-of-fence violation"
        )

    def test_fence_inner_violations_autofix(self, fixture_copy: Path):
        """Autofix deletes the offending blanks: leading-inside, trailing-
        inside, and multi-blank-runs all converge to clean code blocks.
        """
        from systems.check._markdown import fix_blank_lines

        fix_blank_lines(fixture_copy)
        for rule in (CONSECUTIVE_BLANKS, BLANK_AT_FENCE_START, BLANK_AT_FENCE_END):
            assert not _violations_by_rule(fixture_copy, rule), (
                f"{rule} survived autofix"
            )
