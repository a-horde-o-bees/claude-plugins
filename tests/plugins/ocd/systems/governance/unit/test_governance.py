"""Unit tests for governance operations in systems.governance._governance.

Covers dependency ordering (topological sort of governance chains),
entry listing, and pattern-based file-to-convention matching including
exclude filters and list-pattern variants. Frontmatter parsing lives
in test_frontmatter.py.
"""

from pathlib import Path

import pytest

from systems.governance import (
    governance_list,
    governance_match,
    governance_order,
)


def _write_governance_file(
    path: Path,
    includes: str | list[str],
    governed_by: list[str] | None = None,
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
