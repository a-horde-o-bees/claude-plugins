"""Integration tests for convention consumption efficiency.

Exercises governance_match through the full stack to verify that the
backend supports efficient convention loading — deduplicated results,
batch support, excludes filtering, and consistent output across calls.

These tests verify the backend gives agents everything they need to
avoid redundant convention reads. Agent-level compliance (actually
reading each convention once) depends on tool descriptions and server
instructions, which are tested empirically.
"""

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from skills.navigator._db import get_connection, SCHEMA
from skills.navigator._governance import governance_load, governance_match
from servers import navigator as nav_server


def _write_gov_file(path: Path, matches, excludes=None, governed_by=None):
    """Create a governance file with frontmatter."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(matches, list):
        quoted = ", ".join(f'"{p}"' for p in matches)
        lines = ["---", f"matches: [{quoted}]"]
    else:
        lines = ["---", f'matches: "{matches}"']
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
    lines += ["---", "", "# Convention content", ""]
    path.write_text("\n".join(lines))


@pytest.fixture
def gov_env(tmp_path):
    """Set up a realistic governance environment mirroring the project structure.

    Conventions:
    - python.md: matches *.py
    - mcp-server.md: matches servers/*.py, excludes __init__.py and _helpers.py
    - skill-md.md: matches SKILL.md
    - markdown.md: matches *.md

    Rules:
    - design-principles.md: matches * (auto-loaded, excluded from governance_match by default)
    """
    db_path = str(tmp_path / "nav.db")
    conn = get_connection(db_path)
    conn.executescript(SCHEMA)
    conn.close()

    # Rules
    _write_gov_file(
        tmp_path / ".claude/rules/design-principles.md", "*",
    )

    # Conventions
    _write_gov_file(
        tmp_path / ".claude/conventions/python.md", "*.py",
        governed_by=[".claude/rules/design-principles.md"],
    )
    _write_gov_file(
        tmp_path / ".claude/conventions/mcp-server.md", "servers/*.py",
        excludes=["__init__.py", "_helpers.py"],
        governed_by=[".claude/rules/design-principles.md", ".claude/conventions/python.md"],
    )
    _write_gov_file(
        tmp_path / ".claude/conventions/skill-md.md", "SKILL.md",
        governed_by=[".claude/rules/design-principles.md"],
    )
    _write_gov_file(
        tmp_path / ".claude/conventions/markdown.md", "*.md",
        governed_by=[".claude/rules/design-principles.md"],
    )

    governance_load(db_path, str(tmp_path))
    return db_path


class TestSingleFileBaseline:
    """Scenario 1: Modify 1 .py file — baseline convention loading."""

    def test_single_python_file_returns_one_convention(self, gov_env):
        result = governance_match(gov_env, ["src/app.py"])
        assert result["conventions"] == [".claude/conventions/python.md"]
        assert len(result["matches"]["src/app.py"]) == 1

    def test_rules_excluded_by_default(self, gov_env):
        result = governance_match(gov_env, ["src/app.py"])
        assert ".claude/rules/design-principles.md" not in result["conventions"]


class TestBatchSameConvention:
    """Scenario 2: Modify 5 .py files — convention should appear once, not five times."""

    def test_five_python_files_return_one_convention(self, gov_env):
        files = [f"src/file{i}.py" for i in range(5)]
        result = governance_match(gov_env, files)
        # Conventions list is deduplicated — python.md appears once
        assert result["conventions"] == [".claude/conventions/python.md"]

    def test_per_file_matches_all_present(self, gov_env):
        files = [f"src/file{i}.py" for i in range(5)]
        result = governance_match(gov_env, files)
        # Each file individually matches python.md
        for f in files:
            assert f in result["matches"]
            assert ".claude/conventions/python.md" in result["matches"][f]

    def test_batch_equals_individual_conventions(self, gov_env):
        """Batch call returns same conventions as individual calls combined."""
        files = [f"src/file{i}.py" for i in range(5)]
        batch_result = governance_match(gov_env, files)

        individual_conventions = set()
        for f in files:
            r = governance_match(gov_env, [f])
            individual_conventions.update(r["conventions"])

        assert set(batch_result["conventions"]) == individual_conventions


class TestMixedConventions:
    """Scenario 3: Mixed file types — each convention appears once."""

    def test_python_and_skill_files(self, gov_env):
        files = ["src/a.py", "src/b.py", "src/c.py", "skills/nav/SKILL.md", "skills/init/SKILL.md"]
        result = governance_match(gov_env, files)
        conventions = set(result["conventions"])
        assert ".claude/conventions/python.md" in conventions
        assert ".claude/conventions/skill-md.md" in conventions
        # SKILL.md also matches markdown.md (*.md)
        assert ".claude/conventions/markdown.md" in conventions
        # Exactly these three, no more
        assert len(conventions) == 3

    def test_each_file_gets_correct_conventions(self, gov_env):
        files = ["src/a.py", "skills/nav/SKILL.md"]
        result = governance_match(gov_env, files)
        assert result["matches"]["src/a.py"] == [".claude/conventions/python.md"]
        skill_conventions = set(result["matches"]["skills/nav/SKILL.md"])
        assert ".claude/conventions/skill-md.md" in skill_conventions
        assert ".claude/conventions/markdown.md" in skill_conventions


class TestServerFileConventions:
    """Scenario 4: Server .py file — gets both python.md and mcp-server.md."""

    def test_server_file_gets_both_conventions(self, gov_env):
        result = governance_match(gov_env, ["servers/navigator.py"])
        conventions = set(result["conventions"])
        assert ".claude/conventions/python.md" in conventions
        assert ".claude/conventions/mcp-server.md" in conventions
        assert len(conventions) == 2

    def test_server_init_excluded_from_mcp_convention(self, gov_env):
        result = governance_match(gov_env, ["servers/__init__.py"])
        conventions = set(result["conventions"])
        # __init__.py matches python.md but is excluded from mcp-server.md
        assert ".claude/conventions/python.md" in conventions
        assert ".claude/conventions/mcp-server.md" not in conventions

    def test_server_helpers_excluded_from_mcp_convention(self, gov_env):
        result = governance_match(gov_env, ["servers/_helpers.py"])
        conventions = set(result["conventions"])
        assert ".claude/conventions/python.md" in conventions
        assert ".claude/conventions/mcp-server.md" not in conventions

    def test_multiple_server_files_deduplicated(self, gov_env):
        files = ["servers/friction.py", "servers/decisions.py", "servers/navigator.py"]
        result = governance_match(gov_env, files)
        conventions = set(result["conventions"])
        # Same two conventions for all three files
        assert conventions == {".claude/conventions/python.md", ".claude/conventions/mcp-server.md"}


class TestIdempotentCalls:
    """Scenario 5: Repeated calls return identical results."""

    def test_same_files_same_result(self, gov_env):
        files = ["src/a.py", "src/b.py"]
        result1 = governance_match(gov_env, files)
        result2 = governance_match(gov_env, files)
        assert result1 == result2

    def test_different_files_same_type_same_conventions(self, gov_env):
        """Second batch of same file type returns same conventions list."""
        batch1 = [f"src/batch1_{i}.py" for i in range(5)]
        batch2 = [f"src/batch2_{i}.py" for i in range(5)]
        result1 = governance_match(gov_env, batch1)
        result2 = governance_match(gov_env, batch2)
        assert result1["conventions"] == result2["conventions"]

    def test_superset_batch_no_new_conventions(self, gov_env):
        """Adding more files of same type doesn't add conventions."""
        small = ["src/a.py"]
        large = ["src/a.py", "src/b.py", "src/c.py", "src/d.py", "src/e.py"]
        result_small = governance_match(gov_env, small)
        result_large = governance_match(gov_env, large)
        assert result_small["conventions"] == result_large["conventions"]


class TestMCPServerLayer:
    """Same scenarios through the MCP server function layer."""

    @pytest.fixture
    def server_env(self, gov_env):
        with (
            patch.object(nav_server, "DB_PATH", gov_env),
            patch.object(nav_server, "_auto_scan", return_value=None),
            patch.object(nav_server, "_check_db", return_value=None),
        ):
            yield gov_env

    def test_batch_python_files_via_server(self, server_env):
        result = json.loads(nav_server.governance_match(
            [f"src/file{i}.py" for i in range(5)]
        ))
        assert result["conventions"] == [".claude/conventions/python.md"]

    def test_server_file_excludes_via_server(self, server_env):
        result = json.loads(nav_server.governance_match(["servers/__init__.py"]))
        conventions = set(result["conventions"])
        assert ".claude/conventions/mcp-server.md" not in conventions

    def test_mixed_batch_via_server(self, server_env):
        result = json.loads(nav_server.governance_match(
            ["src/app.py", "servers/friction.py", "skills/nav/SKILL.md"]
        ))
        conventions = set(result["conventions"])
        assert ".claude/conventions/python.md" in conventions
        assert ".claude/conventions/mcp-server.md" in conventions
        assert ".claude/conventions/skill-md.md" in conventions
