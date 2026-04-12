"""Unit tests for paths_list (list_files) including size output."""

from pathlib import Path

import pytest

from servers.navigator._db import get_connection, SCHEMA
from servers.navigator._scanner import scan_path
from servers.navigator import paths_list


class TestListFiles:
    @pytest.fixture
    def list_tree(self, project_dir, tmp_path):
        """Create filesystem tree with database and seed rules for list testing."""
        project = project_dir
        (project / "main.py").write_text("print('hello')")
        (project / "README.md").write_text("# Readme")
        src = project / "src"
        src.mkdir()
        (src / "app.py").write_text("class App: pass")
        (src / "config.py").write_text("CONFIG = {}")
        (src / "notes.md").write_text("# Notes")
        cache = project / "__pycache__"
        cache.mkdir()
        (cache / "main.cpython.pyc").write_text("bytecode")
        tests = project / "tests"
        tests.mkdir()
        (tests / "test_main.py").write_text("def test(): pass")

        db = str(tmp_path / "list.db")
        conn = get_connection(db)
        conn.executescript(SCHEMA)
        conn.execute(
            "INSERT INTO patterns (pattern, entry_type, exclude) "
            "VALUES ('**/__pycache__', NULL, 1)"
        )
        conn.execute(
            "INSERT INTO patterns (pattern, entry_type, exclude, traverse, description) "
            "VALUES ('**/tests', NULL, 0, 0, 'Test suites')"
        )
        conn.commit()
        conn.close()

        return {"project": project, "db": db}

    def test_lists_all_files(self, list_tree):
        result = paths_list(list_tree["db"], "")
        names = [Path(e["path"]).name for e in result]
        assert "main.py" in names
        assert "README.md" in names
        assert "app.py" in names
        assert "config.py" in names
        assert "notes.md" in names

    def test_excludes_pycache_files(self, list_tree):
        result = paths_list(list_tree["db"], "")
        all_paths = [e["path"] for e in result]
        assert not any("main.cpython.pyc" in p for p in all_paths)

    def test_no_directories_in_output(self, list_tree):
        result = paths_list(list_tree["db"], "")
        for entry in result:
            assert not entry["path"].endswith("/")

    def test_pattern_filters_by_extension(self, list_tree):
        result = paths_list(
            list_tree["db"], "", patterns=["*.py"]
        )
        for entry in result:
            assert entry["path"].endswith(".py")
        names = [Path(e["path"]).name for e in result]
        assert "main.py" in names
        assert "app.py" in names

    def test_pattern_excludes_non_matching(self, list_tree):
        result = paths_list(
            list_tree["db"], "", patterns=["*.py"]
        )
        all_paths = [e["path"] for e in result]
        assert not any("README.md" in p for p in all_paths)
        assert not any("notes.md" in p for p in all_paths)

    def test_multiple_patterns(self, list_tree):
        result = paths_list(
            list_tree["db"], "",
            patterns=["*.py", "*.md"],
        )
        assert len(result) == 5

    def test_pattern_no_match(self, list_tree):
        result = paths_list(
            list_tree["db"], "", patterns=["*.rs"]
        )
        assert result == []

    def test_sorted_output(self, list_tree):
        result = paths_list(list_tree["db"], "")
        file_paths = [e["path"] for e in result]
        assert file_paths == sorted(file_paths)

    def test_shallow_dir_contents_excluded(self, list_tree):
        result = paths_list(list_tree["db"], "")
        all_paths = [e["path"] for e in result]
        assert not any("test_main.py" in p for p in all_paths)


class TestListSizes:
    @pytest.fixture
    def sizes_tree(self, project_dir, tmp_path):
        (project_dir / "a.py").write_text("line1\nline2\n")
        (project_dir / "b.md").write_text("# Title\n")
        db = str(tmp_path / "sizes.db")
        conn = get_connection(db)
        conn.executescript(SCHEMA)
        conn.close()
        # Scan to populate entries with metrics
        scan_path(db)
        return {"project": project_dir, "db": db}

    def test_sizes_false_no_columns(self, sizes_tree):
        result = paths_list(sizes_tree["db"], "", sizes=False)
        for entry in result:
            assert "line_count" not in entry

    def test_sizes_true_has_columns(self, sizes_tree):
        result = paths_list(sizes_tree["db"], "", sizes=True)
        for entry in result:
            assert "line_count" in entry
            assert "char_count" in entry
            assert isinstance(entry["line_count"], int)
            assert isinstance(entry["char_count"], int)

    def test_sizes_values_correct(self, sizes_tree):
        result = paths_list(
            sizes_tree["db"], "",
            patterns=["*.py"], sizes=True,
        )
        assert len(result) == 1
        assert result[0]["line_count"] == 2
        assert result[0]["char_count"] == len("line1\nline2\n")
