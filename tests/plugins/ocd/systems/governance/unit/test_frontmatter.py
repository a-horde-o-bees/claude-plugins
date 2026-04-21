"""Unit tests for governance._frontmatter.

Covers pattern normalization (string vs JSON list), frontmatter
extraction from markdown files, and block-style vs flow-style YAML
parsing of the `includes`/`excludes` fields.
"""

from systems.governance._frontmatter import (
    normalize_patterns,
    parse_governance,
    read_frontmatter,
)


class TestNormalizePatterns:
    def test_single_string(self):
        assert normalize_patterns("*.py") == ["*.py"]

    def test_json_list(self):
        result = normalize_patterns('["test_*.*", "*_test.*", "conftest.*"]')
        assert result == ["test_*.*", "*_test.*", "conftest.*"]

    def test_single_element_list(self):
        assert normalize_patterns('["*.py"]') == ["*.py"]

    def test_empty_list(self):
        assert normalize_patterns("[]") == []


class TestReadFrontmatter:
    def test_reads_frontmatter_between_delimiters(self, tmp_path):
        f = tmp_path / "doc.md"
        f.write_text("---\nkey: value\nother: thing\n---\n\n# Body\n")
        assert read_frontmatter(f) == ["key: value", "other: thing"]

    def test_returns_none_when_no_opening_delimiter(self, tmp_path):
        f = tmp_path / "doc.md"
        f.write_text("# Just a heading\n\nNo frontmatter here.\n")
        assert read_frontmatter(f) is None

    def test_returns_none_when_missing_closing_delimiter(self, tmp_path):
        f = tmp_path / "doc.md"
        f.write_text("---\nkey: value\nstill going\n")
        assert read_frontmatter(f) is None

    def test_returns_none_for_empty_file(self, tmp_path):
        f = tmp_path / "doc.md"
        f.write_text("")
        assert read_frontmatter(f) is None

    def test_returns_none_for_missing_file(self, tmp_path):
        assert read_frontmatter(tmp_path / "nope.md") is None

    def test_stops_at_closing_without_reading_body(self, tmp_path):
        f = tmp_path / "doc.md"
        body_marker = "SENTINEL_SHOULD_NOT_BE_PARSED"
        f.write_text(f"---\nkey: value\n---\n\n{body_marker}\n")
        lines = read_frontmatter(f)
        assert lines == ["key: value"]
        assert body_marker not in (lines or [])

    def test_empty_frontmatter_block(self, tmp_path):
        f = tmp_path / "doc.md"
        f.write_text("---\n---\n\n# Body\n")
        assert read_frontmatter(f) == []


class TestBlockStylePattern:
    def test_block_style_includes_parsed(self, tmp_path):
        """Block-style YAML list for includes is parsed correctly."""
        gov_file = tmp_path / "testing.md"
        gov_file.write_text(
            "---\n"
            "includes:\n"
            '  - "test_*.*"\n'
            '  - "*_test.*"\n'
            '  - "conftest.*"\n'
            "governed_by:\n"
            "  - .claude/rules/design.md\n"
            "---\n\n"
            "# Testing\n"
        )
        result = parse_governance(gov_file)
        assert result is not None
        patterns = normalize_patterns(result["includes"])
        assert patterns == ["test_*.*", "*_test.*", "conftest.*"]
        assert result["governed_by"] == [".claude/rules/design.md"]

    def test_flow_style_includes(self, tmp_path):
        """Flow-style YAML list for includes works."""
        gov_file = tmp_path / "testing.md"
        gov_file.write_text(
            '---\n'
            'includes: ["test_*.*", "*_test.*"]\n'
            '---\n\n'
            '# Testing\n'
        )
        result = parse_governance(gov_file)
        assert result is not None
        patterns = normalize_patterns(result["includes"])
        assert patterns == ["test_*.*", "*_test.*"]

    def test_single_includes(self, tmp_path):
        """Single string includes works."""
        gov_file = tmp_path / "python.md"
        gov_file.write_text(
            '---\n'
            'includes: "*.py"\n'
            '---\n\n'
            '# Python\n'
        )
        result = parse_governance(gov_file)
        assert result is not None
        assert result["includes"] == "*.py"

    def test_excludes_parsed(self, tmp_path):
        """Excludes field is parsed from frontmatter."""
        gov_file = tmp_path / "server.md"
        gov_file.write_text(
            '---\n'
            'includes: "servers/*.py"\n'
            'excludes:\n'
            '  - "__init__.py"\n'
            '  - "_helpers.py"\n'
            '---\n\n'
            '# Server\n'
        )
        result = parse_governance(gov_file)
        assert result is not None
        assert result["includes"] == "servers/*.py"
        excludes = normalize_patterns(result["excludes"])
        assert excludes == ["__init__.py", "_helpers.py"]
