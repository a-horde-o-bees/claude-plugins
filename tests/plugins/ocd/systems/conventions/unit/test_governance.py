"""Unit tests for convention matching in systems.conventions._matching.

Covers entry listing and pattern-based file-to-convention matching
including exclude filters and list-pattern variants. Frontmatter parsing
lives in test_frontmatter.py.
"""

from pathlib import Path

import pytest

from systems.conventions import (
    governance_list,
    governance_match,
)


def _write_governance_file(
    path: Path,
    includes: str | list[str],
    excludes: list[str] | str | None = None,
) -> None:
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
    lines += ["---", ""]
    path.write_text("\n".join(lines))


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
            project_dir / ".claude/conventions/server.md", "systems/navigator/*.py",
            excludes=["__init__.py", "_server_helpers.py"],
        )
        _write_governance_file(
            project_dir / ".claude/conventions/ocd/python.md", "*.py",
        )

    def test_excludes_filters_basename(self, excludes_files):
        result = governance_match(["systems/navigator/__init__.py"])
        matched = result["matches"].get("systems/navigator/__init__.py", [])
        assert ".claude/conventions/ocd/python.md" in matched
        assert ".claude/conventions/server.md" not in matched

    def test_excludes_allows_normal_files(self, excludes_files):
        result = governance_match(["systems/navigator/server.py"])
        matched = result["matches"]["systems/navigator/server.py"]
        assert ".claude/conventions/server.md" in matched
        assert ".claude/conventions/ocd/python.md" in matched

    def test_excludes_filters_helpers(self, excludes_files):
        result = governance_match(["systems/navigator/_server_helpers.py"])
        matched = result["matches"].get("systems/navigator/_server_helpers.py", [])
        assert ".claude/conventions/server.md" not in matched
        assert ".claude/conventions/ocd/python.md" in matched

    def test_excludes_in_conventions_list(self, excludes_files):
        result = governance_match(["systems/navigator/__init__.py", "systems/navigator/server.py"])
        assert ".claude/conventions/server.md" in result["conventions"]


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
