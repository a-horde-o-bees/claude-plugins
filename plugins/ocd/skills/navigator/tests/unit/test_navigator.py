"""Unit tests for navigator operations."""

from pathlib import Path

import pytest

from skills.navigator._db import get_connection, init_db, SCHEMA
from skills.navigator._scanner import (
    _compute_git_hash,
    _compute_file_metrics,
    _mark_parents_stale,
    _matches_pattern_any,
    scan_path,
)
from skills.navigator import (
    paths_undescribed,
    paths_list,
    paths_remove,
    paths_search,
    paths_upsert,
    paths_get,
)


@pytest.fixture
def db_path(tmp_path):
    """Create a temporary database with schema at tmp_path root.

    Lives outside the per-test CLAUDE_PROJECT_DIR (tmp_path/project) so
    the scanner doesn't index the database file as a project entry.
    """
    path = str(tmp_path / "test.db")
    conn = get_connection(path)
    conn.executescript(SCHEMA)
    conn.close()
    return path


@pytest.fixture
def populated_db(db_path, project_dir):
    """Database with sample entries and real files on disk matching them.

    Files are created under the project_dir so the scanner's reconciliation
    leaves the fixture entries in place instead of deleting them.
    """
    files = {
        "src/lib/utils.py": "utils",
        "src/lib/core.py": "core",
        "src/main.py": "main",
        "src/config.py": "",
    }
    for rel, content in files.items():
        target = project_dir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)

    conn = get_connection(db_path)
    entries = [
        ("src", None, "directory", 0, 1, "Source code", None),
        ("src/lib", "src", "directory", 0, 1, "Library modules", None),
        ("src/lib/utils.py", "src/lib", "file", 0, 1, "Utility functions", None),
        ("src/lib/core.py", "src/lib", "file", 0, 1, None, None),
        ("src/main.py", "src", "file", 0, 1, "Application entry point", None),
        ("src/config.py", "src", "file", 0, 1, "", None),
    ]
    for e in entries:
        conn.execute(
            "INSERT INTO entries (path, parent_path, entry_type, exclude, traverse, description, git_hash) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)", e,
        )
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def db_with_patterns(db_path):
    """Database with glob patterns in the patterns table."""
    conn = get_connection(db_path)
    pats = [
        ("**/__pycache__", None, 1, 0, None),
        ("**/tests", None, 0, 0, "Test suites"),
        ("**/__init__.py", None, 0, 1, "Package marker"),
    ]
    for p in pats:
        conn.execute(
            "INSERT INTO patterns (pattern, entry_type, exclude, traverse, description) "
            "VALUES (?, ?, ?, ?, ?)", p,
        )
    conn.commit()
    conn.close()
    return db_path


# --- _matches_pattern_any ---


class TestMatchesAnyPattern:
    def _make_patterns(self, items):
        """Create mock pattern rows from (glob, description) pairs."""
        return [
            {"pattern": pat, "exclude": 0, "traverse": 1, "description": desc}
            for pat, desc in items
        ]

    def test_double_star_matches_nested(self):
        pats = self._make_patterns([("**/__init__.py", "Package marker")])
        result = _matches_pattern_any("src/lib/__init__.py", pats)
        assert result is not None
        assert result["description"] == "Package marker"

    def test_double_star_matches_top_level(self):
        pats = self._make_patterns([("**/tests", "Test suites")])
        result = _matches_pattern_any("tests", pats)
        assert result is not None

    def test_no_match(self):
        pats = self._make_patterns([("**/__init__.py", "Package marker")])
        result = _matches_pattern_any("src/main.py", pats)
        assert result is None

    def test_literal_pattern(self):
        pats = self._make_patterns([("src/main.py", "Entry point")])
        result = _matches_pattern_any("src/main.py", pats)
        assert result is not None

    def test_literal_no_match(self):
        pats = self._make_patterns([("src/main.py", "Entry point")])
        result = _matches_pattern_any("src/other.py", pats)
        assert result is None

    def test_empty_patterns(self):
        result = _matches_pattern_any("src/main.py", [])
        assert result is None


# --- _compute_git_hash ---


class TestComputeGitHash:
    def test_file_hash(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello\n")
        h = _compute_git_hash(f)
        assert h is not None
        assert len(h) == 40

    def test_same_content_same_hash(self, tmp_path):
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_text("content")
        f2.write_text("content")
        assert _compute_git_hash(f1) == _compute_git_hash(f2)

    def test_different_content_different_hash(self, tmp_path):
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_text("content1")
        f2.write_text("content2")
        assert _compute_git_hash(f1) != _compute_git_hash(f2)

    def test_nonexistent_file(self):
        assert _compute_git_hash(Path("/nonexistent/file.txt")) is None

    def test_directory(self, tmp_path):
        assert _compute_git_hash(tmp_path) is None


# --- _mark_parents_stale ---


class TestMarkParentsStale:
    def test_marks_parent_descriptions_stale(self, populated_db):
        conn = get_connection(populated_db)
        result = _mark_parents_stale(conn, "src/lib/utils.py")
        conn.commit()

        assert "src/lib" in result
        assert "src" in result

        row = conn.execute("SELECT description, stale FROM entries WHERE path = 'src/lib'").fetchone()
        assert row["description"] == "Library modules"
        assert row["stale"] == 1
        row = conn.execute("SELECT description, stale FROM entries WHERE path = 'src'").fetchone()
        assert row["description"] == "Source code"
        assert row["stale"] == 1
        conn.close()

    def test_skips_already_null(self, populated_db):
        conn = get_connection(populated_db)
        conn.execute("UPDATE entries SET description = NULL WHERE path = 'src/lib'")
        conn.commit()

        result = _mark_parents_stale(conn, "src/lib/utils.py")
        conn.commit()

        assert "src/lib" not in result
        assert "src" in result
        conn.close()

    def test_skips_already_stale(self, populated_db):
        conn = get_connection(populated_db)
        conn.execute("UPDATE entries SET stale = 1 WHERE path = 'src/lib'")
        conn.commit()

        result = _mark_parents_stale(conn, "src/lib/utils.py")
        conn.commit()

        assert "src/lib" not in result
        assert "src" in result
        conn.close()

    def test_no_parents(self, db_path):
        conn = get_connection(db_path)
        conn.execute(
            "INSERT INTO entries (path, parent_path, entry_type) VALUES ('root_file.py', '', 'file')"
        )
        conn.commit()

        result = _mark_parents_stale(conn, "root_file.py")
        assert result == []
        conn.close()


# --- init_db ---


class TestInitDb:
    def test_creates_database(self, tmp_path):
        path = str(tmp_path / "new.db")
        result = init_db(path)
        assert "Initialized" in result
        assert Path(path).exists()

    def test_idempotent(self, tmp_path):
        path = str(tmp_path / "new.db")
        init_db(path)
        # Manually add a non-seed entry
        conn = get_connection(path)
        conn.execute("INSERT INTO entries (path, entry_type) VALUES ('test', 'file')")
        conn.commit()
        conn.close()
        result = init_db(path)
        assert "all current" in result
        # Non-seed entry preserved
        conn = get_connection(path)
        row = conn.execute("SELECT * FROM entries WHERE path = 'test'").fetchone()
        assert row is not None
        conn.close()

    def test_seeds_from_csv(self, tmp_path):
        csv_path = tmp_path / "seed.csv"
        csv_path.write_text(
            "path,entry_type,exclude,traverse,description\n"
            "**/__pycache__,directory,1,0,\n"
            "**/tests,directory,0,0,Test suites\n"
        )
        db = str(tmp_path / "seeded.db")
        from ... import _db as db_ctx
        original = db_ctx.SEED_PATH
        try:
            db_ctx.SEED_PATH = csv_path
            result = init_db(db)
            assert "2 added" in result
            conn = get_connection(db)
            rows = conn.execute("SELECT * FROM patterns").fetchall()
            assert len(rows) == 2
            # Entries table should be empty — patterns don't leak in
            entry_rows = conn.execute("SELECT * FROM entries").fetchall()
            assert len(entry_rows) == 0
            conn.close()
        finally:
            db_ctx.SEED_PATH = original

    def test_upserts_changed_seed_patterns(self, tmp_path):
        csv_path = tmp_path / "seed.csv"
        csv_path.write_text(
            "path,entry_type,exclude,traverse,description\n"
            "**/tests,directory,0,0,Test suites\n"
        )
        db = str(tmp_path / "upsert.db")
        from ... import _db as db_ctx
        original = db_ctx.SEED_PATH
        try:
            db_ctx.SEED_PATH = csv_path
            init_db(db)
            # Change the seed pattern
            csv_path.write_text(
                "path,entry_type,exclude,traverse,description\n"
                "**/tests,directory,0,0,Updated description\n"
            )
            result = init_db(db)
            assert "1 updated" in result
            conn = get_connection(db)
            row = conn.execute(
                "SELECT description FROM patterns WHERE pattern = '**/tests'"
            ).fetchone()
            assert row[0] == "Updated description"
            conn.close()
        finally:
            db_ctx.SEED_PATH = original

    def test_adds_new_seed_patterns(self, tmp_path):
        csv_path = tmp_path / "seed.csv"
        csv_path.write_text(
            "path,entry_type,exclude,traverse,description\n"
            "**/tests,directory,0,0,Test suites\n"
        )
        db = str(tmp_path / "add.db")
        from ... import _db as db_ctx
        original = db_ctx.SEED_PATH
        try:
            db_ctx.SEED_PATH = csv_path
            init_db(db)
            # Add a new seed pattern
            csv_path.write_text(
                "path,entry_type,exclude,traverse,description\n"
                "**/tests,directory,0,0,Test suites\n"
                "**/.vscode,directory,1,0,\n"
            )
            result = init_db(db)
            assert "1 added" in result
            conn = get_connection(db)
            rows = conn.execute("SELECT * FROM patterns").fetchall()
            assert len(rows) == 2
            conn.close()
        finally:
            db_ctx.SEED_PATH = original


# --- describe_path ---


class TestDescribePath:
    def test_file_with_description(self, populated_db):
        result = paths_get(populated_db, "src/main.py")
        assert result["path"] == "src/main.py"
        assert result["description"] == "Application entry point"
        assert result["type"] == "file"

    def test_file_null_description(self, populated_db):
        result = paths_get(populated_db, "src/lib/core.py")
        assert result["description"] is None

    def test_file_empty_description(self, populated_db):
        result = paths_get(populated_db, "src/config.py")
        assert result["path"] == "src/config.py"
        assert result["description"] == ""

    def test_directory_lists_children(self, populated_db):
        result = paths_get(populated_db, "src/lib")
        assert result["path"] == "src/lib/"
        assert result["description"] == "Library modules"
        child_paths = [c["path"] for c in result["children"]]
        assert "src/lib/utils.py" in child_paths
        assert "src/lib/core.py" in child_paths

    def test_directory_null_description(self, db_path):
        conn = get_connection(db_path)
        conn.execute(
            "INSERT INTO entries (path, parent_path, entry_type, description) "
            "VALUES ('mydir', '', 'directory', NULL)"
        )
        conn.commit()
        conn.close()
        result = paths_get(db_path, "mydir")
        assert result["description"] is None

    def test_directory_children_sorted_dirs_first(self, populated_db):
        result = paths_get(populated_db, "src")
        children = result["children"]
        # lib/ (directory) should come before .py files
        lib_idx = next(i for i, c in enumerate(children) if c["type"] == "directory")
        main_idx = next(i for i, c in enumerate(children) if "main.py" in c["path"])
        assert lib_idx < main_idx

    def test_children_null_show_question_mark(self, populated_db):
        result = paths_get(populated_db, "src/lib")
        core = next(c for c in result["children"] if "core.py" in c["path"])
        assert core["description"] is None

    def test_children_empty_no_marker(self, populated_db):
        result = paths_get(populated_db, "src")
        config = next(c for c in result["children"] if "config.py" in c["path"])
        assert config["description"] == ""

    def test_excludes_excluded_children(self, db_path, project_dir):
        (project_dir / "dir").mkdir()
        (project_dir / "dir" / "hidden").write_text("")
        (project_dir / "dir" / "visible").write_text("")

        conn = get_connection(db_path)
        conn.execute(
            "INSERT INTO entries (path, parent_path, entry_type, description) "
            "VALUES ('dir', '', 'directory', 'A directory')"
        )
        conn.execute(
            "INSERT INTO entries (path, parent_path, entry_type, exclude) "
            "VALUES ('dir/hidden', 'dir', 'file', 1)"
        )
        conn.execute(
            "INSERT INTO entries (path, parent_path, entry_type, description) "
            "VALUES ('dir/visible', 'dir', 'file', 'Visible file')"
        )
        conn.commit()
        conn.close()
        result = paths_get(db_path, "dir")
        child_paths = [c["path"] for c in result["children"]]
        assert "dir/visible" in child_paths
        assert "dir/hidden" not in child_paths

    def test_not_found(self, db_path):
        result = paths_get(db_path, "nonexistent")
        assert result["children"] is None

    def test_dot_path(self, populated_db):
        result = paths_get(populated_db, ".")
        assert result["path"] == "./"


# --- set_entry ---


class TestSetEntry:
    def test_add_new_file(self, db_path, tmp_path):
        f = tmp_path / "newfile.py"
        f.write_text("content")
        result = paths_upsert(db_path, str(f), description="New file")
        assert result["action"] == "added"

    def test_add_new_directory(self, db_path, tmp_path):
        d = tmp_path / "newdir"
        d.mkdir()
        result = paths_upsert(db_path, str(d), description="New dir")
        assert result["action"] == "added"
        assert result["type"] == "directory"

    def test_update_existing(self, populated_db):
        result = paths_upsert(populated_db, "src/main.py", description="Updated")
        assert result["action"] == "updated"
        conn = get_connection(populated_db)
        row = conn.execute("SELECT description FROM entries WHERE path = 'src/main.py'").fetchone()
        assert row["description"] == "Updated"
        conn.close()

    def test_set_empty_string_description(self, populated_db):
        paths_upsert(populated_db, "src/lib/core.py", description="")
        conn = get_connection(populated_db)
        row = conn.execute("SELECT description FROM entries WHERE path = 'src/lib/core.py'").fetchone()
        assert row["description"] == ""
        conn.close()

    def test_set_traverse_flag(self, populated_db):
        paths_upsert(populated_db, "src/lib", traverse=0)
        conn = get_connection(populated_db)
        row = conn.execute("SELECT traverse FROM entries WHERE path = 'src/lib'").fetchone()
        assert row["traverse"] == 0
        conn.close()

    def test_set_exclude_flag(self, populated_db):
        paths_upsert(populated_db, "src/lib", exclude=1)
        conn = get_connection(populated_db)
        row = conn.execute("SELECT exclude FROM entries WHERE path = 'src/lib'").fetchone()
        assert row["exclude"] == 1
        conn.close()

    def test_rejects_pattern(self, db_path):
        with pytest.raises(ValueError, match="glob patterns"):
            paths_upsert(db_path, "**/*.log", exclude=1)

    def test_no_changes(self, populated_db):
        result = paths_upsert(populated_db, "src/main.py")
        assert result["action"] == "none"

    def test_stores_git_hash_on_describe(self, populated_db, tmp_path):
        f = tmp_path / "hashtest.py"
        f.write_text("content")
        paths_upsert(populated_db, str(f), description="Test")
        conn = get_connection(populated_db)
        row = conn.execute(
            "SELECT git_hash FROM entries WHERE path = ?", (str(f),)
        ).fetchone()
        assert row["git_hash"] is not None
        assert len(row["git_hash"]) == 40
        conn.close()


# --- remove_entry ---


class TestRemoveEntry:
    def test_remove_single(self, populated_db):
        result = paths_remove(populated_db, "src/main.py")
        assert result["action"] == "removed"

    def test_remove_not_found(self, populated_db):
        result = paths_remove(populated_db, "nonexistent")
        assert result["action"] == "not_found"

    def test_remove_recursive(self, populated_db):
        result = paths_remove(populated_db, "src/lib", recursive=True)
        assert result["action"] == "removed_recursive"
        conn = get_connection(populated_db)
        rows = conn.execute(
            "SELECT path FROM entries WHERE path = 'src/lib' OR path LIKE 'src/lib/%'"
        ).fetchall()
        assert len(rows) == 0
        conn.close()

    def test_remove_recursive_file_error(self, populated_db):
        result = paths_remove(populated_db, "src/main.py", recursive=True)
        assert result["action"] == "error"

    def test_remove_all(self, populated_db):
        # Add a pattern rule
        conn = get_connection(populated_db)
        conn.execute(
            "INSERT INTO patterns (pattern, entry_type, exclude) VALUES ('**/*.log', NULL, 1)"
        )
        conn.commit()
        conn.close()

        result = paths_remove(populated_db, "", all_entries=True)
        assert result["action"] == "removed_all"

        conn = get_connection(populated_db)
        entries_count = conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
        patterns_count = conn.execute("SELECT COUNT(*) FROM patterns").fetchone()[0]
        assert entries_count == 0
        assert patterns_count == 1
        conn.close()


# --- search_entries ---


class TestSearchEntries:
    def test_finds_matching(self, populated_db):
        result = paths_search(populated_db, "Utility")
        assert len(result["results"]) == 1
        assert "utils.py" in result["results"][0]["path"]

    def test_case_insensitive(self, populated_db):
        result = paths_search(populated_db, "utility")
        assert len(result["results"]) == 1

    def test_no_match(self, populated_db):
        result = paths_search(populated_db, "nonexistent")
        assert result["results"] == []

    def test_excludes_patterns(self, db_with_patterns):
        """Patterns live in a separate table — search only hits entries."""
        result = paths_search(db_with_patterns, "Package")
        assert result["results"] == []


# --- get_undescribed ---


class TestGetUndescribed:
    def test_returns_deepest(self, populated_db):
        result = paths_undescribed(populated_db)
        assert not result["done"]
        assert result["target"] == "src/lib"
        # core.py in listing has null description
        core = next(c for c in result["listing"]["children"] if "core.py" in c["path"])
        assert core["description"] is None

    def test_shows_progress_count(self, populated_db):
        result = paths_undescribed(populated_db)
        assert result["remaining"] > 0
        assert result["directories"] > 0

    def test_no_work_remaining(self, db_path, project_dir):
        (project_dir / "a.py").write_text("")
        conn = get_connection(db_path)
        conn.execute(
            "INSERT INTO entries (path, entry_type, description) VALUES ('a.py', 'file', 'Described')"
        )
        conn.commit()
        conn.close()
        result = paths_undescribed(db_path)
        assert result["done"]

    def test_empty_string_not_undescribed(self, db_path):
        conn = get_connection(db_path)
        conn.execute(
            "INSERT INTO entries (path, parent_path, entry_type, description) "
            "VALUES ('dir', '', 'directory', 'A dir')"
        )
        conn.execute(
            "INSERT INTO entries (path, parent_path, entry_type, description) "
            "VALUES ('dir/file.py', 'dir', 'file', '')"
        )
        conn.commit()
        conn.close()
        result = paths_undescribed(db_path)
        assert result["done"]

    def test_directory_itself_null(self, db_path, project_dir):
        (project_dir / "dir").mkdir()
        (project_dir / "dir" / "file.py").write_text("")
        conn = get_connection(db_path)
        conn.execute(
            "INSERT INTO entries (path, parent_path, entry_type, description) "
            "VALUES ('dir', '', 'directory', NULL)"
        )
        conn.execute(
            "INSERT INTO entries (path, parent_path, entry_type, description) "
            "VALUES ('dir/file.py', 'dir', 'file', 'Described')"
        )
        conn.commit()
        conn.close()
        result = paths_undescribed(db_path)
        assert not result["done"]
        assert result["listing"]["description"] is None


# --- list_files ---


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


# --- scan_path ---


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
        src = scan_tree["src"]

        # Seed rules
        conn = get_connection(db_path)
        conn.execute(
            "INSERT INTO patterns (pattern, entry_type, exclude) VALUES ('**/__pycache__', NULL, 1)"
        )
        conn.execute(
            "INSERT INTO patterns (pattern, entry_type, exclude, traverse, description) "
            "VALUES ('**/tests', NULL, 0, 0, 'Test suites')"
        )
        conn.execute(
            "INSERT INTO patterns (pattern, entry_type, description) "
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
            "INSERT INTO patterns (pattern, entry_type, exclude) VALUES ('**/__pycache__', NULL, 1)"
        )
        conn.commit()
        conn.close()

        scan_path(db)

        conn = get_connection(db)
        # Check no entries for __pycache__ dir or its contents
        rows = conn.execute(
            "SELECT path FROM entries WHERE path = '__pycache__' OR path LIKE '__pycache__/%'"
        ).fetchall()
        assert len(rows) == 0
        conn.close()

    def test_shallow_lists_but_doesnt_enter(self, scan_tree):
        db_path = scan_tree["db_path"]
        src = scan_tree["src"]

        conn = get_connection(db_path)
        conn.execute(
            "INSERT INTO patterns (pattern, entry_type, exclude) VALUES ('**/__pycache__', NULL, 1)"
        )
        conn.execute(
            "INSERT INTO patterns (pattern, entry_type, exclude, traverse, description) "
            "VALUES ('**/tests', NULL, 0, 0, 'Test suites')"
        )
        conn.commit()
        conn.close()

        scan_path(db_path, "src")

        conn = get_connection(db_path)
        # tests directory itself should exist
        tests_path = "src/tests"
        tests_row = conn.execute(
            "SELECT * FROM entries WHERE path = ?", (tests_path,)
        ).fetchone()
        assert tests_row is not None

        # test_main.py inside tests should NOT exist
        test_file = conn.execute(
            "SELECT * FROM entries WHERE path LIKE ?", (tests_path + "/%",)
        ).fetchall()
        assert len(test_file) == 0
        conn.close()

    def test_prescribed_descriptions_applied(self, scan_tree):
        db_path = scan_tree["db_path"]
        src = scan_tree["src"]

        conn = get_connection(db_path)
        conn.execute(
            "INSERT INTO patterns (pattern, entry_type, exclude) VALUES ('**/__pycache__', NULL, 1)"
        )
        conn.execute(
            "INSERT INTO patterns (pattern, entry_type, description) "
            "VALUES ('**/__init__.py', NULL, 'Package marker')"
        )
        conn.commit()
        conn.close()

        scan_path(db_path, "src")

        conn = get_connection(db_path)
        init_path = "src/lib/__init__.py"
        row = conn.execute(
            "SELECT description FROM entries WHERE path = ?", (init_path,)
        ).fetchone()
        assert row["description"] == "Package marker"
        conn.close()

    def test_removes_stale_entries(self, scan_tree):
        db_path = scan_tree["db_path"]

        conn = get_connection(db_path)
        conn.execute(
            "INSERT INTO entries (path, parent_path, entry_type, description) "
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
        paths_upsert(db_path, main_path, description="Entry point")

        # Modify file
        (src / "main.py").write_text("print('changed')")

        result = scan_path(db_path, "src")
        assert "changed 1" in result

        # Description should be preserved but marked stale
        conn = get_connection(db_path)
        row = conn.execute(
            "SELECT description, stale FROM entries WHERE path = ?", (main_path,)
        ).fetchone()
        assert row["description"] == "Entry point"
        assert row["stale"] == 1
        conn.close()

    def test_idempotent(self, scan_tree):
        db_path = scan_tree["db_path"]
        src = scan_tree["src"]

        conn = get_connection(db_path)
        conn.execute(
            "INSERT INTO patterns (pattern, entry_type, exclude) VALUES ('**/__pycache__', NULL, 1)"
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
        paths_upsert(db_path, "src", description="Source directory")

        # Add a new file
        (src / "newfile.py").write_text("new content")

        result = scan_path(db_path, "src")
        assert "Added 1" in result
        assert "staled" in result

        # Parent should be stale with description preserved
        conn = get_connection(db_path)
        row = conn.execute(
            "SELECT description, stale FROM entries WHERE path = ?", ("src",)
        ).fetchone()
        assert row["description"] == "Source directory"
        assert row["stale"] == 1
        conn.close()

    def test_stale_parent_when_file_removed(self, scan_tree):
        db_path = scan_tree["db_path"]
        src = scan_tree["src"]

        # Initial scan and describe parent
        scan_path(db_path, "src")
        paths_upsert(db_path, "src", description="Source directory")

        # Remove a file
        (src / "utils.py").unlink()

        result = scan_path(db_path, "src")
        assert "removed 1" in result
        assert "staled" in result

        conn = get_connection(db_path)
        row = conn.execute(
            "SELECT description, stale FROM entries WHERE path = ?", ("src",)
        ).fetchone()
        assert row["description"] == "Source directory"
        assert row["stale"] == 1
        conn.close()

    def test_stale_ancestor_chain(self, scan_tree):
        db_path = scan_tree["db_path"]
        src = scan_tree["src"]
        lib_path = "src/lib"
        core_path = "src/lib/core.py"

        # Scan and describe both src and lib
        scan_path(db_path, "src")
        paths_upsert(db_path, "src", description="Source directory")
        paths_upsert(db_path, lib_path, description="Library modules")
        paths_upsert(db_path, core_path, description="Core module")

        # Modify core.py
        (src / "lib" / "core.py").write_text("class Updated: pass")

        scan_path(db_path, "src")

        conn = get_connection(db_path)
        # File itself stale
        row = conn.execute(
            "SELECT description, stale FROM entries WHERE path = ?", (core_path,)
        ).fetchone()
        assert row["description"] == "Core module"
        assert row["stale"] == 1

        # Parent stale
        row = conn.execute(
            "SELECT description, stale FROM entries WHERE path = ?", (lib_path,)
        ).fetchone()
        assert row["description"] == "Library modules"
        assert row["stale"] == 1

        # Grandparent stale
        row = conn.execute(
            "SELECT description, stale FROM entries WHERE path = ?", ("src",)
        ).fetchone()
        assert row["description"] == "Source directory"
        assert row["stale"] == 1
        conn.close()


# --- stale behavior ---


class TestStaleBehavior:
    def test_stale_cleared_on_set_description(self, populated_db):
        conn = get_connection(populated_db)
        conn.execute("UPDATE entries SET stale = 1 WHERE path = 'src/lib'")
        conn.commit()
        conn.close()

        paths_upsert(populated_db, "src/lib", description="Updated description")

        conn = get_connection(populated_db)
        row = conn.execute(
            "SELECT description, stale FROM entries WHERE path = 'src/lib'"
        ).fetchone()
        assert row["description"] == "Updated description"
        assert row["stale"] == 0
        conn.close()

    def test_get_undescribed_includes_stale(self, populated_db):
        # Set all NULL descriptions to something so only stale triggers
        conn = get_connection(populated_db)
        conn.execute("UPDATE entries SET description = 'described' WHERE description IS NULL")
        conn.execute("UPDATE entries SET stale = 1 WHERE path = 'src/lib'")
        conn.commit()
        conn.close()

        result = paths_undescribed(populated_db)
        assert not result["done"]
        assert result["listing"]["stale"]

    def test_get_undescribed_no_work_when_no_stale_or_null(self, populated_db):
        conn = get_connection(populated_db)
        conn.execute("UPDATE entries SET description = 'described' WHERE description IS NULL")
        conn.commit()
        conn.close()

        result = paths_undescribed(populated_db)
        assert result["done"]

    def test_describe_path_stale_file(self, populated_db):
        conn = get_connection(populated_db)
        conn.execute("UPDATE entries SET stale = 1 WHERE path = 'src/main.py'")
        conn.commit()
        conn.close()

        result = paths_get(populated_db, "src/main.py")
        assert result["stale"]
        assert result["description"] == "Application entry point"

    def test_describe_path_stale_directory(self, populated_db):
        conn = get_connection(populated_db)
        conn.execute("UPDATE entries SET stale = 1 WHERE path = 'src/lib'")
        conn.commit()
        conn.close()

        result = paths_get(populated_db, "src/lib")
        assert result["stale"]
        assert result["description"] == "Library modules"

    def test_describe_path_stale_child(self, populated_db):
        conn = get_connection(populated_db)
        conn.execute("UPDATE entries SET stale = 1 WHERE path = 'src/main.py'")
        conn.commit()
        conn.close()

        result = paths_get(populated_db, "src")
        main_child = next(c for c in result["children"] if "main.py" in c["path"])
        assert main_child["stale"]
        assert main_child["description"] == "Application entry point"


# --- _compute_file_metrics ---


class TestComputeFileMetrics:
    def test_text_file(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("line1\nline2\nline3\n")
        m = _compute_file_metrics(f)
        assert m["git_hash"] is not None
        assert len(m["git_hash"]) == 40
        assert m["line_count"] == 3
        assert m["char_count"] == len("line1\nline2\nline3\n")

    def test_file_no_trailing_newline(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("line1\nline2")
        m = _compute_file_metrics(f)
        assert m["line_count"] == 2

    def test_empty_file(self, tmp_path):
        f = tmp_path / "empty.txt"
        f.write_text("")
        m = _compute_file_metrics(f)
        assert m["git_hash"] is not None
        assert m["line_count"] == 0
        assert m["char_count"] == 0

    def test_single_newline(self, tmp_path):
        f = tmp_path / "newline.txt"
        f.write_text("\n")
        m = _compute_file_metrics(f)
        assert m["line_count"] == 1
        assert m["char_count"] == 1

    def test_directory(self, tmp_path):
        m = _compute_file_metrics(tmp_path)
        assert m["git_hash"] is None
        assert m["line_count"] is None
        assert m["char_count"] is None

    def test_nonexistent(self):
        m = _compute_file_metrics(Path("/nonexistent/file.txt"))
        assert m["git_hash"] is None
        assert m["line_count"] is None
        assert m["char_count"] is None

    def test_consistent_with_git_hash(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("content")
        m = _compute_file_metrics(f)
        h = _compute_git_hash(f)
        assert m["git_hash"] == h


# --- scan stores metrics ---


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
            "SELECT line_count FROM entries WHERE path LIKE '%a.py'"
        ).fetchone()
        assert row["line_count"] == 2
        conn.close()

    def test_scan_stores_char_count(self, metrics_tree):
        scan_path(metrics_tree["db"])
        conn = get_connection(metrics_tree["db"])
        row = conn.execute(
            "SELECT char_count FROM entries WHERE path LIKE '%a.py'"
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
            "SELECT line_count FROM entries WHERE path LIKE '%a.py'"
        ).fetchone()
        assert row["line_count"] == 3
        conn.close()

    def test_directories_have_null_metrics(self, metrics_tree):
        scan_path(metrics_tree["db"])
        conn = get_connection(metrics_tree["db"])
        row = conn.execute(
            "SELECT line_count, char_count FROM entries WHERE entry_type = 'directory' LIMIT 1"
        ).fetchone()
        assert row["line_count"] is None
        assert row["char_count"] is None
        conn.close()


# --- set_entry stores metrics ---


class TestSetEntryMetrics:
    def test_stores_metrics_on_describe(self, db_path, tmp_path):
        f = tmp_path / "test.py"
        f.write_text("a = 1\nb = 2\n")
        paths_upsert(db_path, str(f), description="Test file")
        conn = get_connection(db_path)
        row = conn.execute(
            "SELECT line_count, char_count FROM entries WHERE path = ?",
            (str(f),),
        ).fetchone()
        assert row["line_count"] == 2
        assert row["char_count"] == len("a = 1\nb = 2\n")
        conn.close()

    def test_updates_metrics_on_redescribe(self, db_path, tmp_path):
        f = tmp_path / "test.py"
        f.write_text("a = 1\n")
        paths_upsert(db_path, str(f), description="v1")
        f.write_text("a = 1\nb = 2\nc = 3\n")
        paths_upsert(db_path, str(f), description="v2")
        conn = get_connection(db_path)
        row = conn.execute(
            "SELECT line_count FROM entries WHERE path = ?",
            (str(f),),
        ).fetchone()
        assert row["line_count"] == 3
        conn.close()


# --- list --sizes ---


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


# --- Governance ---
