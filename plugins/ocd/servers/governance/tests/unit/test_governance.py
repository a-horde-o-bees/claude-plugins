"""Unit tests for governance operations."""

from pathlib import Path

import pytest

from servers.governance import (
    governance_list,
    governance_match,
    governance_order,
)
from servers.governance._frontmatter import (
    normalize_patterns,
    parse_governance,
    read_frontmatter,
)


def _write_governance_file(path: Path, includes, governed_by: list = None, excludes=None) -> None:
    """Create a markdown file with governance frontmatter at path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(includes, list):
        quoted = ", ".join(f'"{p}"' for p in includes)
        lines = ["---", f"includes: [{quoted}]"]
    else:
        lines = ["---", f'includes: "{includes}"']
    if excludes:
        if isinstance(excludes, list):
            lines.append("excludes:")
            for exc in excludes:
                lines.append(f'  - "{exc}"')
        else:
            lines.append(f'excludes: "{excludes}"')
    if governed_by:
        lines.append("governed_by:")
        for dep in governed_by:
            lines.append(f"  - {dep}")
    lines += ["---", ""]
    path.write_text("\n".join(lines))


class TestGovernanceOrder:
    def _write_chain(self, project_dir, files: dict[str, list[str]]) -> None:
        """Write governance files under project_dir.

        files maps relative path -> list of governed_by paths.
        """
        for rel, governed_by in files.items():
            _write_governance_file(
                project_dir / rel,
                includes="*",
                governed_by=governed_by if governed_by else None,
            )

    def test_empty(self, project_dir):
        result = governance_order()
        assert result == {"levels": [], "dangling": []}

    def test_single_root(self, project_dir):
        self._write_chain(project_dir, {".claude/rules/a.md": []})
        result = governance_order()
        assert result["dangling"] == []
        assert result["levels"] == [[{"path": ".claude/rules/a.md", "governors": []}]]

    def test_simple_chain(self, project_dir):
        self._write_chain(
            project_dir,
            {
                ".claude/rules/a.md": [],
                ".claude/rules/b.md": [".claude/rules/a.md"],
                ".claude/rules/c.md": [".claude/rules/b.md"],
            },
        )
        result = governance_order()
        assert result["dangling"] == []
        paths_per_level = [[e["path"] for e in level] for level in result["levels"]]
        assert paths_per_level == [
            [".claude/rules/a.md"],
            [".claude/rules/b.md"],
            [".claude/rules/c.md"],
        ]

    def test_independent_siblings_in_one_level(self, project_dir):
        self._write_chain(
            project_dir,
            {
                ".claude/rules/a.md": [],
                ".claude/rules/b.md": [],
                ".claude/rules/c.md": [
                    ".claude/rules/a.md",
                    ".claude/rules/b.md",
                ],
            },
        )
        result = governance_order()
        assert result["dangling"] == []
        levels = result["levels"]
        assert len(levels) == 2
        level0_paths = {e["path"] for e in levels[0]}
        assert level0_paths == {".claude/rules/a.md", ".claude/rules/b.md"}
        assert levels[1] == [
            {
                "path": ".claude/rules/c.md",
                "governors": [".claude/rules/a.md", ".claude/rules/b.md"],
            }
        ]

    def test_bidirectional_pair_collapses_to_level(self, project_dir):
        self._write_chain(
            project_dir,
            {
                ".claude/rules/a.md": [".claude/rules/b.md"],
                ".claude/rules/b.md": [".claude/rules/a.md"],
            },
        )
        result = governance_order()
        assert result["dangling"] == []
        assert len(result["levels"]) == 1
        level_paths = {e["path"] for e in result["levels"][0]}
        assert level_paths == {".claude/rules/a.md", ".claude/rules/b.md"}

    def test_three_cycle_collapses_to_level(self, project_dir):
        self._write_chain(
            project_dir,
            {
                ".claude/rules/a.md": [".claude/rules/b.md"],
                ".claude/rules/b.md": [".claude/rules/c.md"],
                ".claude/rules/c.md": [".claude/rules/a.md"],
            },
        )
        result = governance_order()
        assert result["dangling"] == []
        assert len(result["levels"]) == 1
        level_paths = {e["path"] for e in result["levels"][0]}
        assert level_paths == {
            ".claude/rules/a.md",
            ".claude/rules/b.md",
            ".claude/rules/c.md",
        }

    def test_dangling_reference_returns_dangling(self, project_dir):
        self._write_chain(
            project_dir,
            {".claude/rules/a.md": [".claude/rules/missing.md"]},
        )
        result = governance_order()
        assert result["levels"] == []
        assert result["dangling"] == [
            {
                "entry_path": ".claude/rules/a.md",
                "missing": ".claude/rules/missing.md",
            }
        ]

    def test_foundations_before_dependents(self, project_dir):
        self._write_chain(
            project_dir,
            {
                ".claude/rules/a.md": [],
                ".claude/rules/b.md": [".claude/rules/a.md"],
            },
        )
        result = governance_order()
        paths = [e["path"] for level in result["levels"] for e in level]
        assert paths.index(".claude/rules/a.md") < paths.index(".claude/rules/b.md")


class TestGovernanceList:
    def test_lists_entries(self, project_dir):
        _write_governance_file(project_dir / ".claude/rules/design-principles.md", "*")
        _write_governance_file(project_dir / ".claude/conventions/py.md", "*.py")

        result = governance_list()
        assert len(result) == 2
        rule = next(r for r in result if r["mode"] == "rule")
        conv = next(r for r in result if r["mode"] == "convention")
        assert rule["path"] == ".claude/rules/design-principles.md"
        assert rule["includes"] == "*"
        assert conv["path"] == ".claude/conventions/py.md"

    def test_empty(self, project_dir):
        result = governance_list()
        assert result == []


class TestGovernanceMatch:
    @pytest.fixture
    def gov_files(self, project_dir):
        _write_governance_file(project_dir / ".claude/rules/principles.md", "*")
        _write_governance_file(
            project_dir / ".claude/conventions/ocd/python.md", "*.py",
            governed_by=[".claude/rules/principles.md"],
        )

    def test_matches_conventions_only(self, gov_files):
        result = governance_match(["src/app.py"])
        assert ".claude/conventions/ocd/python.md" in result["matches"]["src/app.py"]
        assert ".claude/rules/principles.md" not in result["matches"]["src/app.py"]

    def test_wildcard_rule_excluded(self, gov_files):
        result = governance_match(["README.md"])
        assert result["matches"] == {}

    def test_no_match(self, project_dir):
        result = governance_match(["test.py"])
        assert result["matches"] == {}

    def test_multiple_files(self, gov_files):
        result = governance_match(["src/app.py", "README.md"])
        assert "src/app.py" in result["matches"]
        assert "README.md" not in result["matches"]

    def test_conventions_aggregated(self, gov_files):
        result = governance_match(["src/app.py"])
        assert ".claude/conventions/ocd/python.md" in result["conventions"]
        assert ".claude/rules/principles.md" not in result["conventions"]

    def test_include_rules(self, gov_files):
        result = governance_match(["src/app.py"], include_rules=True)
        assert ".claude/conventions/ocd/python.md" in result["matches"]["src/app.py"]
        assert ".claude/rules/principles.md" in result["matches"]["src/app.py"]

    def test_reflects_disk_changes(self, project_dir):
        """Disk-only match reflects file changes without explicit reload."""
        _write_governance_file(
            project_dir / ".claude/conventions/py.md", "*.py",
        )
        result = governance_match(["app.py"])
        assert ".claude/conventions/py.md" in result["matches"]["app.py"]

        # Change pattern — next call sees the change
        _write_governance_file(
            project_dir / ".claude/conventions/py.md", "*.pyi",
        )
        result = governance_match(["app.py"])
        assert "app.py" not in result["matches"]

        result = governance_match(["app.pyi"])
        assert ".claude/conventions/py.md" in result["matches"]["app.pyi"]


class TestGovernanceMatchExcludes:
    @pytest.fixture
    def excludes_files(self, project_dir):
        _write_governance_file(project_dir / ".claude/rules/principles.md", "*")
        _write_governance_file(
            project_dir / ".claude/conventions/server.md", "servers/*.py",
            excludes=["__init__.py", "_helpers.py"],
        )
        _write_governance_file(
            project_dir / ".claude/conventions/ocd/python.md", "*.py",
        )

    def test_excludes_filters_basename(self, excludes_files):
        result = governance_match(["servers/__init__.py"])
        matched = result["matches"].get("servers/__init__.py", [])
        assert ".claude/conventions/ocd/python.md" in matched
        assert ".claude/conventions/server.md" not in matched

    def test_excludes_allows_normal_files(self, excludes_files):
        result = governance_match(["servers/navigator.py"])
        matched = result["matches"]["servers/navigator.py"]
        assert ".claude/conventions/server.md" in matched
        assert ".claude/conventions/ocd/python.md" in matched

    def test_excludes_filters_helpers(self, excludes_files):
        result = governance_match(["servers/_helpers.py"])
        matched = result["matches"].get("servers/_helpers.py", [])
        assert ".claude/conventions/server.md" not in matched
        assert ".claude/conventions/ocd/python.md" in matched

    def test_excludes_in_conventions_list(self, excludes_files):
        result = governance_match(["servers/__init__.py", "servers/navigator.py"])
        assert ".claude/conventions/server.md" in result["conventions"]


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


class TestListPatternGovernanceMatch:
    @pytest.fixture
    def list_gov_files(self, project_dir):
        _write_governance_file(project_dir / ".claude/rules/all.md", "*")
        _write_governance_file(
            project_dir / ".claude/conventions/ocd/testing.md",
            ["test_*.*", "*_test.*", "conftest.*"],
        )

    def test_matches_test_prefix(self, list_gov_files):
        result = governance_match(["test_utils.py"])
        assert ".claude/conventions/ocd/testing.md" in result["matches"]["test_utils.py"]

    def test_matches_test_suffix(self, list_gov_files):
        result = governance_match(["app_test.py"])
        assert ".claude/conventions/ocd/testing.md" in result["matches"]["app_test.py"]

    def test_matches_conftest(self, list_gov_files):
        result = governance_match(["conftest.py"])
        assert ".claude/conventions/ocd/testing.md" in result["matches"]["conftest.py"]

    def test_no_match_regular_file(self, list_gov_files):
        result = governance_match(["app.py"])
        assert "app.py" not in result["matches"]

    def test_multiple_files_mixed(self, list_gov_files):
        result = governance_match(["test_foo.py", "app.py", "bar_test.py"])
        assert "test_foo.py" in result["matches"]
        assert "app.py" not in result["matches"]
        assert "bar_test.py" in result["matches"]

    def test_all_list_patterns(self, list_gov_files):
        result = governance_match([
            "test_app.py", "utils_test.py", "conftest.py", "app.py",
        ])
        assert ".claude/conventions/ocd/testing.md" in result["matches"].get("test_app.py", [])
        assert ".claude/conventions/ocd/testing.md" in result["matches"].get("utils_test.py", [])
        assert ".claude/conventions/ocd/testing.md" in result["matches"].get("conftest.py", [])
        assert "app.py" not in result["matches"]
