"""Unit tests for scan_path and scan-time metrics storage."""

import pytest

from systems.navigator._db import get_connection, SCHEMA
from systems.navigator._scanner import scan_path
from systems.navigator import paths_upsert


class TestScanPath:
    @pytest.fixture
    def scan_tree(self, project_dir, db_path):
        """Create a filesystem tree and database for scan testing."""
        # Create filesystem
        src = project_dir / "src"
        src.mkdir()
        (src / "main.py").write_text("print('hello')")
        (src / "utils.py").write_text("def helper(): pass")
        lib = src / "lib"
        lib.mkdir()
        (lib / "__init__.py").write_text("")
        (lib / "core.py").write_text("class Core: pass")
        # Excluded directory
        cache = src / "__pycache__"
        cache.mkdir()
        (cache / "main.cpython.pyc").write_text("bytecode")
        # Shallow directory
        tests = src / "tests"
        tests.mkdir()
        (tests / "test_main.py").write_text("def test(): pass")

        return {"project_dir": project_dir, "db_path": db_path, "src": src}

    def test_adds_missing_entries(self, scan_tree):
        db_path = scan_tree["db_path"]

        # Seed rules
        conn = get_connection(db_path)
        conn.execute(
            "INSERT INTO path_patterns (pattern, entry_type, exclude) VALUES ('**/__pycache__', NULL, 1)"
        )
        conn.execute(
            "INSERT INTO path_patterns (pattern, entry_type, exclude, traverse, purpose) "
            "VALUES ('**/tests', NULL, 0, 0, 'Test suites')"
        )
        conn.execute(
            "INSERT INTO path_patterns (pattern, entry_type, purpose) "
            "VALUES ('**/__init__.py', NULL, 'Package marker')"
        )
        conn.commit()
        conn.close()

        result = scan_path(db_path, "src")
        assert "Added" in result
        assert "removed 0" in result

    def test_excludes_pycache(self, project_dir, tmp_path):
        """Test exclusion with isolated filesystem and database."""
        (project_dir / "main.py").write_text("print('hello')")
        cache = project_dir / "__pycache__"
        cache.mkdir()
        (cache / "main.cpython.pyc").write_text("bytecode")

        db = str(tmp_path / "excl.db")
        conn = get_connection(db)
        conn.executescript(SCHEMA)
        conn.execute(
            "INSERT INTO path_patterns (pattern, entry_type, exclude) VALUES ('**/__pycache__', NULL, 1)"
        )
        conn.commit()
        conn.close()

        scan_path(db)

        conn = get_connection(db)
        # Check no entries for __pycache__ dir or its contents
        rows = conn.execute(
            "SELECT path FROM paths WHERE path = '__pycache__' OR path LIKE '__pycache__/%'"
        ).fetchall()
        assert len(rows) == 0
        conn.close()

    def test_shallow_lists_but_doesnt_enter(self, scan_tree):
        db_path = scan_tree["db_path"]

        conn = get_connection(db_path)
        conn.execute(
            "INSERT INTO path_patterns (pattern, entry_type, exclude) VALUES ('**/__pycache__', NULL, 1)"
        )
        conn.execute(
            "INSERT INTO path_patterns (pattern, entry_type, exclude, traverse, purpose) "
            "VALUES ('**/tests', NULL, 0, 0, 'Test suites')"
        )
        conn.commit()
        conn.close()

        scan_path(db_path, "src")

        conn = get_connection(db_path)
        # tests directory itself should exist
        tests_path = "src/tests"
        tests_row = conn.execute(
            "SELECT * FROM paths WHERE path = ?", (tests_path,)
        ).fetchone()
        assert tests_row is not None

        # test_main.py inside tests should NOT exist
        test_file = conn.execute(
            "SELECT * FROM paths WHERE path LIKE ?", (tests_path + "/%",)
        ).fetchall()
        assert len(test_file) == 0
        conn.close()

    def test_prescribed_descriptions_applied(self, scan_tree):
        db_path = scan_tree["db_path"]

        conn = get_connection(db_path)
        conn.execute(
            "INSERT INTO path_patterns (pattern, entry_type, exclude) VALUES ('**/__pycache__', NULL, 1)"
        )
        conn.execute(
            "INSERT INTO path_patterns (pattern, entry_type, purpose) "
            "VALUES ('**/__init__.py', NULL, 'Package marker')"
        )
        conn.commit()
        conn.close()

        scan_path(db_path, "src")

        conn = get_connection(db_path)
        init_path = "src/lib/__init__.py"
        row = conn.execute(
            "SELECT purpose FROM paths WHERE path = ?", (init_path,)
        ).fetchone()
        assert row["purpose"] == "Package marker"
        conn.close()

    def test_removes_stale_entries(self, scan_tree):
        db_path = scan_tree["db_path"]

        conn = get_connection(db_path)
        conn.execute(
            "INSERT INTO paths (path, parent_path, entry_type, purpose) "
            "VALUES (?, ?, 'file', 'Gone')",
            ("src/deleted.py", "src"),
        )
        conn.commit()
        conn.close()

        result = scan_path(db_path, "src")
        assert "removed 1" in result

    def test_detects_changed_files(self, scan_tree):
        db_path = scan_tree["db_path"]
        src = scan_tree["src"]
        main_path = "src/main.py"

        # First scan to populate
        scan_path(db_path, "src")

        # Set description (stores hash)
        paths_upsert(db_path, main_path, purpose="Entry point")

        # Modify file
        (src / "main.py").write_text("print('changed')")

        result = scan_path(db_path, "src")
        assert "changed 1" in result

        # Description should be preserved but marked stale
        conn = get_connection(db_path)
        row = conn.execute(
            "SELECT purpose, stale FROM paths WHERE path = ?", (main_path,)
        ).fetchone()
        assert row["purpose"] == "Entry point"
        assert row["stale"] == 1
        conn.close()

    def test_idempotent(self, scan_tree):
        db_path = scan_tree["db_path"]

        conn = get_connection(db_path)
        conn.execute(
            "INSERT INTO path_patterns (pattern, entry_type, exclude) VALUES ('**/__pycache__', NULL, 1)"
        )
        conn.commit()
        conn.close()

        scan_path(db_path, "src")
        result = scan_path(db_path, "src")
        assert "Added 0" in result
        assert "removed 0" in result

    def test_stale_parent_when_file_added(self, scan_tree):
        db_path = scan_tree["db_path"]
        src = scan_tree["src"]

        # Initial scan
        scan_path(db_path, "src")

        # Describe the src directory
        paths_upsert(db_path, "src", purpose="Source directory")

        # Add a new file
        (src / "newfile.py").write_text("new content")

        result = scan_path(db_path, "src")
        assert "Added 1" in result
        assert "staled" in result

        # Parent should be stale with description preserved
        conn = get_connection(db_path)
        row = conn.execute(
            "SELECT purpose, stale FROM paths WHERE path = ?", ("src",)
        ).fetchone()
        assert row["purpose"] == "Source directory"
        assert row["stale"] == 1
        conn.close()

    def test_stale_parent_when_file_removed(self, scan_tree):
        db_path = scan_tree["db_path"]
        src = scan_tree["src"]

        # Initial scan and describe parent
        scan_path(db_path, "src")
        paths_upsert(db_path, "src", purpose="Source directory")

        # Remove a file
        (src / "utils.py").unlink()

        result = scan_path(db_path, "src")
        assert "removed 1" in result
        assert "staled" in result

        conn = get_connection(db_path)
        row = conn.execute(
            "SELECT purpose, stale FROM paths WHERE path = ?", ("src",)
        ).fetchone()
        assert row["purpose"] == "Source directory"
        assert row["stale"] == 1
        conn.close()

    def test_stale_ancestor_chain(self, scan_tree):
        db_path = scan_tree["db_path"]
        src = scan_tree["src"]
        lib_path = "src/lib"
        core_path = "src/lib/core.py"

        # Scan and describe both src and lib
        scan_path(db_path, "src")
        paths_upsert(db_path, "src", purpose="Source directory")
        paths_upsert(db_path, lib_path, purpose="Library modules")
        paths_upsert(db_path, core_path, purpose="Core module")

        # Modify core.py
        (src / "lib" / "core.py").write_text("class Updated: pass")

        scan_path(db_path, "src")

        conn = get_connection(db_path)
        # File itself stale
        row = conn.execute(
            "SELECT purpose, stale FROM paths WHERE path = ?", (core_path,)
        ).fetchone()
        assert row["purpose"] == "Core module"
        assert row["stale"] == 1

        # Parent stale
        row = conn.execute(
            "SELECT purpose, stale FROM paths WHERE path = ?", (lib_path,)
        ).fetchone()
        assert row["purpose"] == "Library modules"
        assert row["stale"] == 1

        # Grandparent stale
        row = conn.execute(
            "SELECT purpose, stale FROM paths WHERE path = ?", ("src",)
        ).fetchone()
        assert row["purpose"] == "Source directory"
        assert row["stale"] == 1
        conn.close()


class TestScanMetrics:
    @pytest.fixture
    def metrics_tree(self, project_dir, db_path):
        (project_dir / "a.py").write_text("line1\nline2\n")
        (project_dir / "b.md").write_text("# Title\n\nBody text here.\n")
        sub = project_dir / "sub"
        sub.mkdir()
        (sub / "c.py").write_text("x = 1\n")
        return {"project": project_dir, "db": db_path}

    def test_scan_stores_line_count(self, metrics_tree):
        scan_path(metrics_tree["db"])
        conn = get_connection(metrics_tree["db"])
        row = conn.execute(
            "SELECT line_count FROM paths WHERE path LIKE '%a.py'"
        ).fetchone()
        assert row["line_count"] == 2
        conn.close()

    def test_scan_stores_char_count(self, metrics_tree):
        scan_path(metrics_tree["db"])
        conn = get_connection(metrics_tree["db"])
        row = conn.execute(
            "SELECT char_count FROM paths WHERE path LIKE '%a.py'"
        ).fetchone()
        assert row["char_count"] == len("line1\nline2\n")
        conn.close()

    def test_scan_updates_metrics_on_change(self, metrics_tree):
        scan_path(metrics_tree["db"])
        # Modify file
        a_py = metrics_tree["project"] / "a.py"
        a_py.write_text("line1\nline2\nline3\n")
        scan_path(metrics_tree["db"])
        conn = get_connection(metrics_tree["db"])
        row = conn.execute(
            "SELECT line_count FROM paths WHERE path LIKE '%a.py'"
        ).fetchone()
        assert row["line_count"] == 3
        conn.close()

    def test_directories_have_null_metrics(self, metrics_tree):
        scan_path(metrics_tree["db"])
        conn = get_connection(metrics_tree["db"])
        row = conn.execute(
            "SELECT line_count, char_count FROM paths WHERE entry_type = 'directory' LIMIT 1"
        ).fetchone()
        assert row["line_count"] is None
        assert row["char_count"] is None
        conn.close()
