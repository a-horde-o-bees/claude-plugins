"""Unit tests for scope_analyze.

Covers the composition in scope_analyze — calls references_map + size
lookup + governance_match and returns a unified matrix. References_map
and governance_match each have their own unit tests; this suite
validates only the assembly (size lookup, governance_index inversion,
total_lines aggregation).
"""

from pathlib import Path

import pytest

from systems.navigator import scope_analyze
from systems.navigator._db import get_connection


@pytest.fixture
def scope_fixture(db_path: str, project_dir: Path) -> str:
    """Seed db with two files (one sized, one sizeless), plus a governance
    file matching *.py. Returns db_path.
    """
    # Real files on disk
    (project_dir / "src").mkdir(parents=True)
    (project_dir / "src" / "app.py").write_text("print('hello')\n")
    (project_dir / "src" / "stub.py").write_text("")

    # Governance file under .claude/ so governance_match picks it up
    conv_dir = project_dir / ".claude" / "conventions"
    conv_dir.mkdir(parents=True)
    (conv_dir / "python.md").write_text('---\nincludes: "*.py"\n---\n\n# Python\n')

    # DB rows with line_count/char_count populated for app.py, null for stub.py
    conn = get_connection(db_path)
    conn.execute(
        "INSERT INTO paths (path, parent_path, entry_type, exclude, traverse, "
        "purpose, git_hash, line_count, char_count) VALUES "
        "('src', NULL, 'directory', 0, 1, NULL, NULL, NULL, NULL)",
    )
    conn.execute(
        "INSERT INTO paths (path, parent_path, entry_type, exclude, traverse, "
        "purpose, git_hash, line_count, char_count) VALUES "
        "('src/app.py', 'src', 'file', 0, 1, 'application', NULL, 1, 15)",
    )
    conn.execute(
        "INSERT INTO paths (path, parent_path, entry_type, exclude, traverse, "
        "purpose, git_hash, line_count, char_count) VALUES "
        "('src/stub.py', 'src', 'file', 0, 1, NULL, NULL, NULL, NULL)",
    )
    conn.commit()
    conn.close()
    return db_path


class TestScopeAnalyze:
    def test_returns_expected_top_level_keys(self, scope_fixture: str) -> None:
        result = scope_analyze(scope_fixture, ["src/app.py"])
        assert set(result.keys()) == {
            "files", "governance_index", "total_lines", "total_files",
        }

    def test_size_lookup_populates_line_and_char_counts(
        self, scope_fixture: str,
    ) -> None:
        result = scope_analyze(scope_fixture, ["src/app.py"])
        app_entry = next(f for f in result["files"] if f["path"] == "src/app.py")
        assert app_entry["line_count"] == 1
        assert app_entry["char_count"] == 15

    def test_empty_file_shows_zero_line_count(self, scope_fixture: str) -> None:
        """Empty file: scanner populates line_count=0, not None.

        _ensure_scanned runs at the top of scope_analyze and stamps sizes
        from disk — NULL rows get overwritten with real counts. A zero-
        byte file has line_count=0, char_count=0.
        """
        result = scope_analyze(scope_fixture, ["src/stub.py"])
        stub_entry = next(f for f in result["files"] if f["path"] == "src/stub.py")
        assert stub_entry["line_count"] == 0
        assert stub_entry["char_count"] == 0

    def test_governance_index_inverted(self, scope_fixture: str) -> None:
        """governance_index maps governance-file → files, not file → governance."""
        result = scope_analyze(scope_fixture, ["src/app.py"])
        assert ".claude/conventions/python.md" in result["governance_index"]
        assert "src/app.py" in result["governance_index"][".claude/conventions/python.md"]

    def test_total_lines_sums_non_null(self, scope_fixture: str) -> None:
        """total_lines sums line_count across files, skipping None values."""
        result = scope_analyze(scope_fixture, ["src/app.py", "src/stub.py"])
        # app.py = 1 line; stub.py has None line_count — excluded from sum
        assert result["total_lines"] == 1

    def test_total_files_counts_entries(self, scope_fixture: str) -> None:
        result = scope_analyze(scope_fixture, ["src/app.py", "src/stub.py"])
        assert result["total_files"] == len(result["files"])
