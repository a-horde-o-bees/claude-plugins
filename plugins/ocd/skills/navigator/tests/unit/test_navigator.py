"""Unit tests for navigator operations."""

from pathlib import Path

import pytest

from skills.navigator import (
    _compute_git_hash,
    _compute_file_metrics,
    _mark_parents_stale,
    _is_pattern,
    _matches_any_rule,
    get_connection,
    get_undescribed,
    governance_for,
    governance_load,
    governance_order,
    init_db,
    list_files,
    list_governance,
    remove_entry,
    scan_path,
    search_entries,
    set_entry,
    describe_path,
    SCHEMA,
)


@pytest.fixture
def db_path(tmp_path):
    """Create a temporary database with schema."""
    path = str(tmp_path / "test.db")
    conn = get_connection(path)
    conn.executescript(SCHEMA)
    conn.close()
    return path


@pytest.fixture
def populated_db(db_path):
    """Database with sample entries."""
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
def db_with_rules(db_path):
    """Database with pattern-based rules."""
    conn = get_connection(db_path)
    rules = [
        ("**/__pycache__", None, None, 1, 0, None, None),
        ("**/tests", None, None, 0, 0, "Test suites", None),
        ("**/__init__.py", None, None, 0, 1, "Package marker", None),
    ]
    for r in rules:
        conn.execute(
            "INSERT INTO entries (path, parent_path, entry_type, exclude, traverse, description, git_hash) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)", r,
        )
    conn.commit()
    conn.close()
    return db_path


# --- _is_pattern ---


class TestIsPattern:
    def test_glob_pattern(self):
        assert _is_pattern("**/__init__.py") is True

    def test_single_wildcard(self):
        assert _is_pattern("src/*.py") is True

    def test_concrete_path(self):
        assert _is_pattern("src/main.py") is False

    def test_directory_path(self):
        assert _is_pattern("src/lib") is False


# --- _matches_any_rule ---


class TestMatchesAnyRule:
    def _make_rules(self, patterns):
        """Create mock rule rows from pattern strings."""
        rules = []
        for pat, desc in patterns:
            rules.append({"path": pat, "exclude": 0, "traverse": 1, "description": desc})
        return rules

    def test_double_star_matches_nested(self):
        rules = self._make_rules([("**/__init__.py", "Package marker")])
        result = _matches_any_rule("src/lib/__init__.py", rules)
        assert result is not None
        assert result["description"] == "Package marker"

    def test_double_star_matches_top_level(self):
        rules = self._make_rules([("**/tests", "Test suites")])
        result = _matches_any_rule("tests", rules)
        assert result is not None

    def test_no_match(self):
        rules = self._make_rules([("**/__init__.py", "Package marker")])
        result = _matches_any_rule("src/main.py", rules)
        assert result is None

    def test_literal_pattern(self):
        rules = self._make_rules([("src/main.py", "Entry point")])
        result = _matches_any_rule("src/main.py", rules)
        assert result is not None

    def test_literal_no_match(self):
        rules = self._make_rules([("src/main.py", "Entry point")])
        result = _matches_any_rule("src/other.py", rules)
        assert result is None

    def test_empty_rules(self):
        result = _matches_any_rule("src/main.py", [])
        assert result is None


# --- _compute_git_hash ---


class TestComputeGitHash:
    def test_file_hash(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello\n")
        h = _compute_git_hash(str(f))
        assert h is not None
        assert len(h) == 40

    def test_same_content_same_hash(self, tmp_path):
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_text("content")
        f2.write_text("content")
        assert _compute_git_hash(str(f1)) == _compute_git_hash(str(f2))

    def test_different_content_different_hash(self, tmp_path):
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_text("content1")
        f2.write_text("content2")
        assert _compute_git_hash(str(f1)) != _compute_git_hash(str(f2))

    def test_nonexistent_file(self):
        assert _compute_git_hash("/nonexistent/file.txt") is None

    def test_directory(self, tmp_path):
        assert _compute_git_hash(str(tmp_path)) is None


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
            rows = conn.execute("SELECT * FROM entries").fetchall()
            assert len(rows) == 2
            conn.close()
        finally:
            db_ctx.SEED_PATH = original

    def test_upserts_changed_seed_rules(self, tmp_path):
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
            # Change the seed rule
            csv_path.write_text(
                "path,entry_type,exclude,traverse,description\n"
                "**/tests,directory,0,0,Updated description\n"
            )
            result = init_db(db)
            assert "1 updated" in result
            conn = get_connection(db)
            row = conn.execute(
                "SELECT description FROM entries WHERE path = '**/tests'"
            ).fetchone()
            assert row[0] == "Updated description"
            conn.close()
        finally:
            db_ctx.SEED_PATH = original

    def test_adds_new_seed_rules(self, tmp_path):
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
            # Add a new seed rule
            csv_path.write_text(
                "path,entry_type,exclude,traverse,description\n"
                "**/tests,directory,0,0,Test suites\n"
                "**/.vscode,directory,1,0,\n"
            )
            result = init_db(db)
            assert "1 added" in result
            conn = get_connection(db)
            rows = conn.execute("SELECT * FROM entries").fetchall()
            assert len(rows) == 2
            conn.close()
        finally:
            db_ctx.SEED_PATH = original


# --- describe_path ---


class TestDescribePath:
    def test_file_with_description(self, populated_db):
        result = describe_path(populated_db, "src/main.py")
        assert "src/main.py" in result
        assert "Application entry point" in result

    def test_file_null_description(self, populated_db):
        result = describe_path(populated_db, "src/lib/core.py")
        assert "[?]" in result

    def test_file_empty_description(self, populated_db):
        result = describe_path(populated_db, "src/config.py")
        assert "src/config.py" in result
        assert "[?]" not in result
        assert "config" not in result.split("\n")[1] if len(result.split("\n")) > 1 else True

    def test_directory_lists_children(self, populated_db):
        result = describe_path(populated_db, "src/lib")
        assert "src/lib/" in result
        assert "Library modules" in result
        assert "src/lib/utils.py" in result
        assert "src/lib/core.py" in result

    def test_directory_null_description(self, db_path):
        conn = get_connection(db_path)
        conn.execute(
            "INSERT INTO entries (path, parent_path, entry_type, description) "
            "VALUES ('mydir', '', 'directory', NULL)"
        )
        conn.commit()
        conn.close()
        result = describe_path(db_path, "mydir")
        assert "[?]" in result

    def test_directory_children_sorted_dirs_first(self, populated_db):
        result = describe_path(populated_db, "src")
        lines = result.split("\n")
        child_lines = [l for l in lines if l.startswith("- ")]
        # lib/ (directory) should come before .py files
        lib_idx = next(i for i, l in enumerate(child_lines) if "lib/" in l)
        main_idx = next(i for i, l in enumerate(child_lines) if "main.py" in l)
        assert lib_idx < main_idx

    def test_children_null_show_question_mark(self, populated_db):
        result = describe_path(populated_db, "src/lib")
        assert "core.py [?]" in result

    def test_children_empty_no_marker(self, populated_db):
        result = describe_path(populated_db, "src")
        # config.py has empty string description — no [?], no description text
        config_line = [l for l in result.split("\n") if "config.py" in l][0]
        assert "[?]" not in config_line
        assert " - " not in config_line

    def test_excludes_excluded_children(self, db_path):
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
        result = describe_path(db_path, "dir")
        assert "visible" in result
        assert "hidden" not in result

    def test_not_found(self, db_path):
        result = describe_path(db_path, "nonexistent")
        assert "(no entries)" in result

    def test_dot_path(self, populated_db):
        result = describe_path(populated_db, ".")
        assert "./" in result


# --- set_entry ---


class TestSetEntry:
    def test_add_new_file(self, db_path, tmp_path):
        f = tmp_path / "newfile.py"
        f.write_text("content")
        result = set_entry(db_path, str(f), description="New file")
        assert "Added" in result

    def test_add_new_directory(self, db_path, tmp_path):
        d = tmp_path / "newdir"
        d.mkdir()
        result = set_entry(db_path, str(d), description="New dir")
        assert "Added" in result
        assert "directory" in result

    def test_update_existing(self, populated_db):
        result = set_entry(populated_db, "src/main.py", description="Updated")
        assert "Updated" in result
        conn = get_connection(populated_db)
        row = conn.execute("SELECT description FROM entries WHERE path = 'src/main.py'").fetchone()
        assert row["description"] == "Updated"
        conn.close()

    def test_set_empty_string_description(self, populated_db):
        set_entry(populated_db, "src/lib/core.py", description="")
        conn = get_connection(populated_db)
        row = conn.execute("SELECT description FROM entries WHERE path = 'src/lib/core.py'").fetchone()
        assert row["description"] == ""
        conn.close()

    def test_set_traverse_flag(self, populated_db):
        set_entry(populated_db, "src/lib", traverse=0)
        conn = get_connection(populated_db)
        row = conn.execute("SELECT traverse FROM entries WHERE path = 'src/lib'").fetchone()
        assert row["traverse"] == 0
        conn.close()

    def test_set_exclude_flag(self, populated_db):
        set_entry(populated_db, "src/lib", exclude=1)
        conn = get_connection(populated_db)
        row = conn.execute("SELECT exclude FROM entries WHERE path = 'src/lib'").fetchone()
        assert row["exclude"] == 1
        conn.close()

    def test_add_pattern(self, db_path):
        result = set_entry(db_path, "**/*.log", exclude=1)
        assert "Added" in result
        assert "pattern" in result

    def test_no_changes(self, populated_db):
        result = set_entry(populated_db, "src/main.py")
        assert "No changes" in result

    def test_stores_git_hash_on_describe(self, populated_db, tmp_path):
        f = tmp_path / "hashtest.py"
        f.write_text("content")
        set_entry(populated_db, str(f), description="Test")
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
        result = remove_entry(populated_db, "src/main.py")
        assert "Removed: src/main.py" in result

    def test_remove_not_found(self, populated_db):
        result = remove_entry(populated_db, "nonexistent")
        assert "Not found" in result

    def test_remove_recursive(self, populated_db):
        result = remove_entry(populated_db, "src/lib", recursive=True)
        assert "Removed" in result
        conn = get_connection(populated_db)
        rows = conn.execute(
            "SELECT path FROM entries WHERE path = 'src/lib' OR path LIKE 'src/lib/%'"
        ).fetchall()
        assert len(rows) == 0
        conn.close()

    def test_remove_recursive_file_error(self, populated_db):
        result = remove_entry(populated_db, "src/main.py", recursive=True)
        assert "Error" in result

    def test_remove_all(self, populated_db):
        # Add a pattern rule
        conn = get_connection(populated_db)
        conn.execute(
            "INSERT INTO entries (path, entry_type, exclude) VALUES ('**/*.log', NULL, 1)"
        )
        conn.commit()
        conn.close()

        result = remove_entry(populated_db, "", all_entries=True)
        assert "Removed all" in result
        assert "rules preserved" in result

        conn = get_connection(populated_db)
        concrete = conn.execute("SELECT COUNT(*) FROM entries WHERE path NOT LIKE '%*%'").fetchone()[0]
        patterns = conn.execute("SELECT COUNT(*) FROM entries WHERE path LIKE '%*%'").fetchone()[0]
        assert concrete == 0
        assert patterns == 1
        conn.close()


# --- search_entries ---


class TestSearchEntries:
    def test_finds_matching(self, populated_db):
        result = search_entries(populated_db, "Utility")
        assert "utils.py" in result
        assert "1 results" in result

    def test_case_insensitive(self, populated_db):
        result = search_entries(populated_db, "utility")
        assert "utils.py" in result

    def test_no_match(self, populated_db):
        result = search_entries(populated_db, "nonexistent")
        assert "No entries matching" in result

    def test_excludes_patterns(self, db_with_rules):
        result = search_entries(db_with_rules, "Package")
        assert "No entries matching" in result


# --- get_undescribed ---


class TestGetUndescribed:
    def test_returns_deepest(self, populated_db):
        result = get_undescribed(populated_db)
        # core.py has NULL description, its parent is src/lib
        assert "src/lib/" in result
        assert "core.py [?]" in result

    def test_shows_progress_count(self, populated_db):
        result = get_undescribed(populated_db)
        assert "remaining" in result
        assert "directories" in result

    def test_no_work_remaining(self, db_path):
        conn = get_connection(db_path)
        conn.execute(
            "INSERT INTO entries (path, entry_type, description) VALUES ('a.py', 'file', 'Described')"
        )
        conn.commit()
        conn.close()
        result = get_undescribed(db_path)
        assert "No work remaining" in result

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
        result = get_undescribed(db_path)
        assert "No work remaining" in result

    def test_directory_itself_null(self, db_path):
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
        result = get_undescribed(db_path)
        assert "dir/" in result
        assert "[?]" in result


# --- list_files ---


class TestListFiles:
    @pytest.fixture
    def list_tree(self, tmp_path):
        """Create filesystem tree with database and seed rules for list testing."""
        project = tmp_path / "project"
        project.mkdir()
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
            "INSERT INTO entries (path, entry_type, exclude) "
            "VALUES ('**/__pycache__', NULL, 1)"
        )
        conn.execute(
            "INSERT INTO entries (path, entry_type, exclude, traverse, description) "
            "VALUES ('**/tests', NULL, 0, 0, 'Test suites')"
        )
        conn.commit()
        conn.close()

        return {"project": project, "db": db}

    def test_lists_all_files(self, list_tree):
        result = list_files(list_tree["db"], str(list_tree["project"]))
        lines = result.strip().split("\n")
        paths = [Path(p).name for p in lines]
        assert "main.py" in paths
        assert "README.md" in paths
        assert "app.py" in paths
        assert "config.py" in paths
        assert "notes.md" in paths

    def test_excludes_pycache_files(self, list_tree):
        result = list_files(list_tree["db"], str(list_tree["project"]))
        assert "main.cpython.pyc" not in result

    def test_no_directories_in_output(self, list_tree):
        result = list_files(list_tree["db"], str(list_tree["project"]))
        lines = result.strip().split("\n")
        for line in lines:
            assert not line.endswith("/")
            assert "src" != Path(line).name or Path(line).suffix

    def test_pattern_filters_by_extension(self, list_tree):
        result = list_files(
            list_tree["db"], str(list_tree["project"]), patterns=["*.py"]
        )
        lines = result.strip().split("\n")
        for line in lines:
            assert line.endswith(".py")
        paths = [Path(p).name for p in lines]
        assert "main.py" in paths
        assert "app.py" in paths

    def test_pattern_excludes_non_matching(self, list_tree):
        result = list_files(
            list_tree["db"], str(list_tree["project"]), patterns=["*.py"]
        )
        assert "README.md" not in result
        assert "notes.md" not in result

    def test_multiple_patterns(self, list_tree):
        result = list_files(
            list_tree["db"], str(list_tree["project"]),
            patterns=["*.py", "*.md"],
        )
        lines = result.strip().split("\n")
        assert len(lines) == 5

    def test_pattern_no_match(self, list_tree):
        result = list_files(
            list_tree["db"], str(list_tree["project"]), patterns=["*.rs"]
        )
        assert result == ""

    def test_sorted_output(self, list_tree):
        result = list_files(list_tree["db"], str(list_tree["project"]))
        lines = result.strip().split("\n")
        assert lines == sorted(lines)

    def test_shallow_dir_contents_excluded(self, list_tree):
        result = list_files(list_tree["db"], str(list_tree["project"]))
        assert "test_main.py" not in result


# --- scan_path ---


class TestScanPath:
    @pytest.fixture
    def scan_tree(self, tmp_path, db_path):
        """Create a filesystem tree and database for scan testing."""
        # Create filesystem
        src = tmp_path / "src"
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

        return {"tmp_path": tmp_path, "db_path": db_path, "src": src}

    def test_adds_missing_entries(self, scan_tree):
        db_path = scan_tree["db_path"]
        src = scan_tree["src"]

        # Seed rules
        conn = get_connection(db_path)
        conn.execute(
            "INSERT INTO entries (path, entry_type, exclude) VALUES ('**/__pycache__', NULL, 1)"
        )
        conn.execute(
            "INSERT INTO entries (path, entry_type, exclude, traverse, description) "
            "VALUES ('**/tests', NULL, 0, 0, 'Test suites')"
        )
        conn.execute(
            "INSERT INTO entries (path, entry_type, description) "
            "VALUES ('**/__init__.py', NULL, 'Package marker')"
        )
        conn.commit()
        conn.close()

        result = scan_path(db_path, str(src))
        assert "Added" in result
        assert "removed 0" in result

    def test_excludes_pycache(self, tmp_path):
        """Test exclusion with isolated filesystem and database."""
        src = tmp_path / "project"
        src.mkdir()
        (src / "main.py").write_text("print('hello')")
        cache = src / "__pycache__"
        cache.mkdir()
        (cache / "main.cpython.pyc").write_text("bytecode")

        db = str(tmp_path / "excl.db")
        conn = get_connection(db)
        conn.executescript(SCHEMA)
        conn.execute(
            "INSERT INTO entries (path, entry_type, exclude) VALUES ('**/__pycache__', NULL, 1)"
        )
        conn.commit()
        conn.close()

        scan_path(db, str(src))

        conn = get_connection(db)
        # Check no entries for __pycache__ dir or its contents
        cache_path = str(cache)
        rows = conn.execute(
            "SELECT path FROM entries WHERE (path = ? OR path LIKE ?) AND path NOT LIKE '%*%'",
            (cache_path, cache_path + "/%"),
        ).fetchall()
        assert len(rows) == 0
        conn.close()

    def test_shallow_lists_but_doesnt_enter(self, scan_tree):
        db_path = scan_tree["db_path"]
        src = scan_tree["src"]

        conn = get_connection(db_path)
        conn.execute(
            "INSERT INTO entries (path, entry_type, exclude) VALUES ('**/__pycache__', NULL, 1)"
        )
        conn.execute(
            "INSERT INTO entries (path, entry_type, exclude, traverse, description) "
            "VALUES ('**/tests', NULL, 0, 0, 'Test suites')"
        )
        conn.commit()
        conn.close()

        scan_path(db_path, str(src))

        conn = get_connection(db_path)
        # tests directory itself should exist
        tests_path = str(src / "tests")
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
            "INSERT INTO entries (path, entry_type, exclude) VALUES ('**/__pycache__', NULL, 1)"
        )
        conn.execute(
            "INSERT INTO entries (path, entry_type, description) "
            "VALUES ('**/__init__.py', NULL, 'Package marker')"
        )
        conn.commit()
        conn.close()

        scan_path(db_path, str(src))

        conn = get_connection(db_path)
        init_path = str(src / "lib" / "__init__.py")
        row = conn.execute(
            "SELECT description FROM entries WHERE path = ?", (init_path,)
        ).fetchone()
        assert row["description"] == "Package marker"
        conn.close()

    def test_removes_stale_entries(self, scan_tree):
        db_path = scan_tree["db_path"]
        src = scan_tree["src"]

        conn = get_connection(db_path)
        conn.execute(
            "INSERT INTO entries (path, parent_path, entry_type, description) "
            "VALUES (?, ?, 'file', 'Gone')",
            (str(src / "deleted.py"), str(src)),
        )
        conn.commit()
        conn.close()

        result = scan_path(db_path, str(src))
        assert "removed 1" in result

    def test_detects_changed_files(self, scan_tree):
        db_path = scan_tree["db_path"]
        src = scan_tree["src"]
        main_path = str(src / "main.py")

        # First scan to populate
        scan_path(db_path, str(src))

        # Set description (stores hash)
        set_entry(db_path, main_path, description="Entry point")

        # Modify file
        (src / "main.py").write_text("print('changed')")

        result = scan_path(db_path, str(src))
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
            "INSERT INTO entries (path, entry_type, exclude) VALUES ('**/__pycache__', NULL, 1)"
        )
        conn.commit()
        conn.close()

        scan_path(db_path, str(src))
        result = scan_path(db_path, str(src))
        assert "Added 0" in result
        assert "removed 0" in result

    def test_stale_parent_when_file_added(self, scan_tree):
        db_path = scan_tree["db_path"]
        src = scan_tree["src"]

        # Initial scan
        scan_path(db_path, str(src))

        # Describe the src directory
        set_entry(db_path, str(src), description="Source directory")

        # Add a new file
        (src / "newfile.py").write_text("new content")

        result = scan_path(db_path, str(src))
        assert "Added 1" in result
        assert "staled" in result

        # Parent should be stale with description preserved
        conn = get_connection(db_path)
        row = conn.execute(
            "SELECT description, stale FROM entries WHERE path = ?", (str(src),)
        ).fetchone()
        assert row["description"] == "Source directory"
        assert row["stale"] == 1
        conn.close()

    def test_stale_parent_when_file_removed(self, scan_tree):
        db_path = scan_tree["db_path"]
        src = scan_tree["src"]

        # Initial scan and describe parent
        scan_path(db_path, str(src))
        set_entry(db_path, str(src), description="Source directory")

        # Remove a file
        (src / "utils.py").unlink()

        result = scan_path(db_path, str(src))
        assert "removed 1" in result
        assert "staled" in result

        conn = get_connection(db_path)
        row = conn.execute(
            "SELECT description, stale FROM entries WHERE path = ?", (str(src),)
        ).fetchone()
        assert row["description"] == "Source directory"
        assert row["stale"] == 1
        conn.close()

    def test_stale_ancestor_chain(self, scan_tree):
        db_path = scan_tree["db_path"]
        src = scan_tree["src"]
        lib_path = str(src / "lib")
        core_path = str(src / "lib" / "core.py")

        # Scan and describe both src and lib
        scan_path(db_path, str(src))
        set_entry(db_path, str(src), description="Source directory")
        set_entry(db_path, lib_path, description="Library modules")
        set_entry(db_path, core_path, description="Core module")

        # Modify core.py
        (src / "lib" / "core.py").write_text("class Updated: pass")

        scan_path(db_path, str(src))

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
            "SELECT description, stale FROM entries WHERE path = ?", (str(src),)
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

        set_entry(populated_db, "src/lib", description="Updated description")

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

        result = get_undescribed(populated_db)
        assert "src/lib/" in result
        assert "[~]" in result

    def test_get_undescribed_no_work_when_no_stale_or_null(self, populated_db):
        conn = get_connection(populated_db)
        conn.execute("UPDATE entries SET description = 'described' WHERE description IS NULL")
        conn.commit()
        conn.close()

        result = get_undescribed(populated_db)
        assert "No work remaining" in result

    def test_describe_path_stale_file(self, populated_db):
        conn = get_connection(populated_db)
        conn.execute("UPDATE entries SET stale = 1 WHERE path = 'src/main.py'")
        conn.commit()
        conn.close()

        result = describe_path(populated_db, "src/main.py")
        assert "[~] Application entry point" in result

    def test_describe_path_stale_directory(self, populated_db):
        conn = get_connection(populated_db)
        conn.execute("UPDATE entries SET stale = 1 WHERE path = 'src/lib'")
        conn.commit()
        conn.close()

        result = describe_path(populated_db, "src/lib")
        assert "[~] Library modules" in result

    def test_describe_path_stale_child(self, populated_db):
        conn = get_connection(populated_db)
        conn.execute("UPDATE entries SET stale = 1 WHERE path = 'src/main.py'")
        conn.commit()
        conn.close()

        result = describe_path(populated_db, "src")
        main_line = [l for l in result.split("\n") if "main.py" in l][0]
        assert "[~] Application entry point" in main_line


# --- _compute_file_metrics ---


class TestComputeFileMetrics:
    def test_text_file(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("line1\nline2\nline3\n")
        m = _compute_file_metrics(str(f))
        assert m["git_hash"] is not None
        assert len(m["git_hash"]) == 40
        assert m["line_count"] == 3
        assert m["char_count"] == len("line1\nline2\nline3\n")

    def test_file_no_trailing_newline(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("line1\nline2")
        m = _compute_file_metrics(str(f))
        assert m["line_count"] == 2

    def test_empty_file(self, tmp_path):
        f = tmp_path / "empty.txt"
        f.write_text("")
        m = _compute_file_metrics(str(f))
        assert m["git_hash"] is not None
        assert m["line_count"] == 0
        assert m["char_count"] == 0

    def test_single_newline(self, tmp_path):
        f = tmp_path / "newline.txt"
        f.write_text("\n")
        m = _compute_file_metrics(str(f))
        assert m["line_count"] == 1
        assert m["char_count"] == 1

    def test_directory(self, tmp_path):
        m = _compute_file_metrics(str(tmp_path))
        assert m["git_hash"] is None
        assert m["line_count"] is None
        assert m["char_count"] is None

    def test_nonexistent(self):
        m = _compute_file_metrics("/nonexistent/file.txt")
        assert m["git_hash"] is None
        assert m["line_count"] is None
        assert m["char_count"] is None

    def test_consistent_with_git_hash(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("content")
        m = _compute_file_metrics(str(f))
        h = _compute_git_hash(str(f))
        assert m["git_hash"] == h


# --- scan stores metrics ---


class TestScanMetrics:
    @pytest.fixture
    def metrics_tree(self, tmp_path, db_path):
        project = tmp_path / "project"
        project.mkdir()
        (project / "a.py").write_text("line1\nline2\n")
        (project / "b.md").write_text("# Title\n\nBody text here.\n")
        sub = project / "sub"
        sub.mkdir()
        (sub / "c.py").write_text("x = 1\n")
        return {"project": project, "db": db_path}

    def test_scan_stores_line_count(self, metrics_tree):
        scan_path(metrics_tree["db"], str(metrics_tree["project"]))
        conn = get_connection(metrics_tree["db"])
        row = conn.execute(
            "SELECT line_count FROM entries WHERE path LIKE '%a.py'"
        ).fetchone()
        assert row["line_count"] == 2
        conn.close()

    def test_scan_stores_char_count(self, metrics_tree):
        scan_path(metrics_tree["db"], str(metrics_tree["project"]))
        conn = get_connection(metrics_tree["db"])
        row = conn.execute(
            "SELECT char_count FROM entries WHERE path LIKE '%a.py'"
        ).fetchone()
        assert row["char_count"] == len("line1\nline2\n")
        conn.close()

    def test_scan_updates_metrics_on_change(self, metrics_tree):
        scan_path(metrics_tree["db"], str(metrics_tree["project"]))
        # Modify file
        a_py = metrics_tree["project"] / "a.py"
        a_py.write_text("line1\nline2\nline3\n")
        scan_path(metrics_tree["db"], str(metrics_tree["project"]))
        conn = get_connection(metrics_tree["db"])
        row = conn.execute(
            "SELECT line_count FROM entries WHERE path LIKE '%a.py'"
        ).fetchone()
        assert row["line_count"] == 3
        conn.close()

    def test_directories_have_null_metrics(self, metrics_tree):
        scan_path(metrics_tree["db"], str(metrics_tree["project"]))
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
        set_entry(db_path, str(f), description="Test file")
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
        set_entry(db_path, str(f), description="v1")
        f.write_text("a = 1\nb = 2\nc = 3\n")
        set_entry(db_path, str(f), description="v2")
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
    def sizes_tree(self, tmp_path):
        project = tmp_path / "project"
        project.mkdir()
        (project / "a.py").write_text("line1\nline2\n")
        (project / "b.md").write_text("# Title\n")
        db = str(tmp_path / "sizes.db")
        conn = get_connection(db)
        conn.executescript(SCHEMA)
        conn.close()
        # Scan to populate entries with metrics
        scan_path(db, str(project))
        return {"project": project, "db": db}

    def test_sizes_false_no_columns(self, sizes_tree):
        result = list_files(sizes_tree["db"], str(sizes_tree["project"]), sizes=False)
        for line in result.strip().split("\n"):
            assert "\t" not in line

    def test_sizes_true_has_columns(self, sizes_tree):
        result = list_files(sizes_tree["db"], str(sizes_tree["project"]), sizes=True)
        for line in result.strip().split("\n"):
            parts = line.split("\t")
            assert len(parts) == 3
            assert parts[1].isdigit()
            assert parts[2].isdigit()

    def test_sizes_values_correct(self, sizes_tree):
        result = list_files(
            sizes_tree["db"], str(sizes_tree["project"]),
            patterns=["*.py"], sizes=True,
        )
        line = result.strip()
        parts = line.split("\t")
        assert parts[1] == "2"  # line_count
        assert parts[2] == str(len("line1\nline2\n"))  # char_count


# --- Governance ---


class TestGovernanceLoad:
    @pytest.fixture
    def gov_env(self, tmp_path):
        """Create manifest and database for governance testing."""
        db = str(tmp_path / "gov.db")
        conn = get_connection(db)
        conn.executescript(SCHEMA)
        conn.close()

        manifest = tmp_path / "manifest.yaml"
        manifest.write_text(
            "settings:\n"
            "  lines_warn_threshold: 500\n"
            "  lines_fail_threshold: 2000\n"
            "\n"
            "conventions:\n"
            "  .claude/rules/design-principles.md:\n"
            '    pattern: "*"\n'
            "    dependencies: []\n"
            "  .claude/rules/workflow.md:\n"
            '    pattern: "*"\n'
            "    dependencies: [.claude/rules/design-principles.md]\n"
            "  .claude/ocd/conventions/python.md:\n"
            '    pattern: "*.py"\n'
            "    dependencies: [.claude/rules/design-principles.md]\n"
        )
        return {"db": db, "manifest": str(manifest)}

    def test_loads_governance_entries(self, gov_env):
        governance_load(gov_env["db"], gov_env["manifest"])
        conn = get_connection(gov_env["db"])
        count = conn.execute("SELECT COUNT(*) as c FROM governance").fetchone()["c"]
        assert count == 3
        conn.close()

    def test_sets_auto_loaded_for_rules(self, gov_env):
        governance_load(gov_env["db"], gov_env["manifest"])
        conn = get_connection(gov_env["db"])
        row = conn.execute(
            "SELECT auto_loaded FROM governance WHERE entry_path = '.claude/rules/design-principles.md'"
        ).fetchone()
        assert row["auto_loaded"] == 1
        conn.close()

    def test_sets_not_auto_loaded_for_conventions(self, gov_env):
        governance_load(gov_env["db"], gov_env["manifest"])
        conn = get_connection(gov_env["db"])
        row = conn.execute(
            "SELECT auto_loaded FROM governance WHERE entry_path = '.claude/ocd/conventions/python.md'"
        ).fetchone()
        assert row["auto_loaded"] == 0
        conn.close()

    def test_flips_dependencies_to_governs(self, gov_env):
        governance_load(gov_env["db"], gov_env["manifest"])
        conn = get_connection(gov_env["db"])
        # design-principles governs workflow (workflow depends on design-principles)
        row = conn.execute(
            "SELECT * FROM governs WHERE governor_path = '.claude/rules/design-principles.md' "
            "AND governed_path = '.claude/rules/workflow.md'"
        ).fetchone()
        assert row is not None
        conn.close()

    def test_governs_count(self, gov_env):
        governance_load(gov_env["db"], gov_env["manifest"])
        conn = get_connection(gov_env["db"])
        count = conn.execute("SELECT COUNT(*) as c FROM governs").fetchone()["c"]
        # design-principles governs workflow, design-principles governs python
        assert count == 2
        conn.close()

    def test_stores_settings(self, gov_env):
        governance_load(gov_env["db"], gov_env["manifest"])
        conn = get_connection(gov_env["db"])
        row = conn.execute(
            "SELECT value FROM config WHERE key = 'lines_warn_threshold'"
        ).fetchone()
        assert row["value"] == "500"
        conn.close()

    def test_idempotent_reload(self, gov_env):
        governance_load(gov_env["db"], gov_env["manifest"])
        governance_load(gov_env["db"], gov_env["manifest"])
        conn = get_connection(gov_env["db"])
        count = conn.execute("SELECT COUNT(*) as c FROM governance").fetchone()["c"]
        assert count == 3
        conn.close()

    def test_creates_entry_rows(self, gov_env):
        governance_load(gov_env["db"], gov_env["manifest"])
        conn = get_connection(gov_env["db"])
        row = conn.execute(
            "SELECT entry_type FROM entries WHERE path = '.claude/rules/design-principles.md'"
        ).fetchone()
        assert row is not None
        assert row["entry_type"] == "file"
        conn.close()

    def test_returns_summary(self, gov_env):
        result = governance_load(gov_env["db"], gov_env["manifest"])
        assert "3 governance entries" in result
        assert "2 governs relationships" in result


class TestListGovernance:
    def test_lists_entries(self, tmp_path):
        db = str(tmp_path / "gov.db")
        conn = get_connection(db)
        conn.executescript(SCHEMA)
        conn.execute("INSERT INTO entries (path, entry_type) VALUES ('rules/a.md', 'file')")
        conn.execute("INSERT INTO governance (entry_path, pattern, auto_loaded) VALUES ('rules/a.md', '*', 1)")
        conn.commit()
        conn.close()

        result = list_governance(db)
        assert "rules/a.md" in result
        assert "[rule]" in result
        assert "*" in result

    def test_empty(self, db_path):
        result = list_governance(db_path)
        assert "No governance entries." in result


class TestGovernanceFor:
    @pytest.fixture
    def gov_db(self, tmp_path):
        db = str(tmp_path / "gov.db")
        manifest = tmp_path / "manifest.yaml"
        manifest.write_text(
            "settings:\n"
            "  lines_warn_threshold: 10\n"
            "  lines_fail_threshold: 20\n"
            "\n"
            "conventions:\n"
            "  rules/principles.md:\n"
            '    pattern: "*"\n'
            "    dependencies: []\n"
            "  conventions/python.md:\n"
            '    pattern: "*.py"\n'
            "    dependencies: [rules/principles.md]\n"
        )
        conn = get_connection(db)
        conn.executescript(SCHEMA)
        conn.close()
        governance_load(db, str(manifest))

        # Add a file entry with line count for threshold testing
        conn = get_connection(db)
        conn.execute(
            "INSERT OR REPLACE INTO entries (path, entry_type, line_count, char_count) "
            "VALUES ('src/app.py', 'file', 15, 500)"
        )
        conn.execute(
            "INSERT OR REPLACE INTO entries (path, entry_type, line_count, char_count) "
            "VALUES ('src/huge.py', 'file', 25, 2000)"
        )
        conn.commit()
        conn.close()
        return db

    def test_matches_by_pattern(self, gov_db):
        result = governance_for(gov_db, ["src/app.py"])
        assert "conventions/python.md" in result
        assert "rules/principles.md" in result

    def test_wildcard_matches_all(self, gov_db):
        result = governance_for(gov_db, ["README.md"])
        assert "rules/principles.md" in result

    def test_no_match(self, db_path):
        result = governance_for(db_path, ["test.py"])
        assert "No governance matches." in result

    def test_multiple_files(self, gov_db):
        result = governance_for(gov_db, ["src/app.py", "README.md"])
        assert "src/app.py" in result
        assert "README.md" in result

    def test_warn_tag(self, gov_db):
        result = governance_for(gov_db, ["src/app.py"])
        assert "[warn: 15 lines]" in result

    def test_fail_tag(self, gov_db):
        result = governance_for(gov_db, ["src/huge.py"])
        assert "[fail: 25 lines]" in result

    def test_criteria_header(self, gov_db):
        result = governance_for(gov_db, ["src/app.py"])
        assert result.startswith("Criteria:")


class TestGovernanceOrder:
    @pytest.fixture
    def ordered_db(self, tmp_path):
        db = str(tmp_path / "gov.db")
        manifest = tmp_path / "manifest.yaml"
        manifest.write_text(
            "conventions:\n"
            "  rules/principles.md:\n"
            '    pattern: "*"\n'
            "    dependencies: []\n"
            "  rules/workflow.md:\n"
            '    pattern: "*"\n'
            "    dependencies: [rules/principles.md]\n"
            "  conventions/python.md:\n"
            '    pattern: "*.py"\n'
            "    dependencies: [rules/principles.md]\n"
            "  conventions/skill-md.md:\n"
            '    pattern: "SKILL.md"\n'
            "    dependencies: [rules/principles.md, rules/workflow.md]\n"
        )
        conn = get_connection(db)
        conn.executescript(SCHEMA)
        conn.close()
        governance_load(db, str(manifest))
        return db

    def test_level_ordering(self, ordered_db):
        result = governance_order(ordered_db)
        assert "Level 0:" in result
        assert "Level 1:" in result

    def test_root_at_level_0(self, ordered_db):
        result = governance_order(ordered_db)
        lines = result.split("\n")
        level_0_start = lines.index("Level 0:")
        level_1_start = lines.index("Level 1:")
        level_0_entries = [l.strip() for l in lines[level_0_start + 1:level_1_start]]
        assert "rules/principles.md" in level_0_entries

    def test_dependents_after_dependencies(self, ordered_db):
        result = governance_order(ordered_db)
        lines = result.split("\n")
        # skill-md depends on both principles and workflow, so level 2
        assert "Level 2:" in result
        level_2_start = lines.index("Level 2:")
        level_2_entries = [l.strip() for l in lines[level_2_start + 1:] if l.strip()]
        assert "conventions/skill-md.md" in level_2_entries

    def test_empty_governance(self, db_path):
        result = governance_order(db_path)
        assert "No governance entries." in result

    def test_cycle_detection(self, tmp_path):
        db = str(tmp_path / "cycle.db")
        conn = get_connection(db)
        conn.executescript(SCHEMA)
        conn.execute("INSERT INTO entries (path, entry_type) VALUES ('a.md', 'file')")
        conn.execute("INSERT INTO entries (path, entry_type) VALUES ('b.md', 'file')")
        conn.execute("INSERT INTO governance (entry_path, pattern, auto_loaded) VALUES ('a.md', '*', 0)")
        conn.execute("INSERT INTO governance (entry_path, pattern, auto_loaded) VALUES ('b.md', '*', 0)")
        conn.execute("INSERT INTO governs (governor_path, governed_path) VALUES ('a.md', 'b.md')")
        conn.execute("INSERT INTO governs (governor_path, governed_path) VALUES ('b.md', 'a.md')")
        conn.commit()
        conn.close()

        result = governance_order(db)
        assert "Cycle detected" in result


# --- Scan-time governance matching ---


class TestScanGovernance:
    @pytest.fixture
    def gov_scan_tree(self, tmp_path):
        """Project tree with governance loaded, ready for scan."""
        project = tmp_path / "project"
        project.mkdir()
        (project / "app.py").write_text("x = 1\n")
        (project / "README.md").write_text("# Readme\n")
        sub = project / "sub"
        sub.mkdir()
        (sub / "helper.py").write_text("y = 2\n")

        db = str(tmp_path / "scan_gov.db")
        conn = get_connection(db)
        conn.executescript(SCHEMA)
        conn.close()

        # Write and load a governance manifest
        manifest = tmp_path / "manifest.yaml"
        manifest.write_text(
            "conventions:\n"
            "  rules/all.md:\n"
            '    pattern: "*"\n'
            "    dependencies: []\n"
            "  conventions/python.md:\n"
            '    pattern: "*.py"\n'
            "    dependencies: [rules/all.md]\n"
        )
        governance_load(db, str(manifest))
        return {"project": project, "db": db}

    def test_scan_populates_governs(self, gov_scan_tree):
        scan_path(gov_scan_tree["db"], str(gov_scan_tree["project"]))
        conn = get_connection(gov_scan_tree["db"])
        rows = conn.execute("SELECT * FROM governs WHERE governor_path = 'conventions/python.md'").fetchall()
        governed = [r["governed_path"] for r in rows]
        # Should match .py files but not README.md
        assert any("app.py" in g for g in governed)
        assert any("helper.py" in g for g in governed)
        assert not any("README.md" in g for g in governed)
        conn.close()

    def test_scan_wildcard_governs_all_files(self, gov_scan_tree):
        scan_path(gov_scan_tree["db"], str(gov_scan_tree["project"]))
        conn = get_connection(gov_scan_tree["db"])
        rows = conn.execute("SELECT * FROM governs WHERE governor_path = 'rules/all.md'").fetchall()
        governed = [r["governed_path"] for r in rows]
        assert any("app.py" in g for g in governed)
        assert any("README.md" in g for g in governed)
        assert any("helper.py" in g for g in governed)
        conn.close()

    def test_scan_removes_stale_governs(self, gov_scan_tree):
        scan_path(gov_scan_tree["db"], str(gov_scan_tree["project"]))
        # Delete a file
        app_py = gov_scan_tree["project"] / "app.py"
        app_py.unlink()
        # Re-scan
        scan_path(gov_scan_tree["db"], str(gov_scan_tree["project"]))
        conn = get_connection(gov_scan_tree["db"])
        rows = conn.execute(
            "SELECT governed_path FROM governs WHERE governor_path = 'conventions/python.md'"
        ).fetchall()
        governed = [r["governed_path"] for r in rows]
        assert not any("app.py" in g for g in governed)
        conn.close()

    def test_scan_pattern_excludes_governance_from_pattern_match(self, gov_scan_tree):
        # Before scan, only explicit governs exist from governance_load
        conn = get_connection(gov_scan_tree["db"])
        before = conn.execute(
            "SELECT COUNT(*) as c FROM governs WHERE governor_path = 'conventions/python.md'"
        ).fetchone()["c"]
        conn.close()

        scan_path(gov_scan_tree["db"], str(gov_scan_tree["project"]))

        # After scan, python.md governs .py files but NOT other governance entries
        conn = get_connection(gov_scan_tree["db"])
        rows = conn.execute(
            "SELECT governed_path FROM governs WHERE governor_path = 'conventions/python.md'"
        ).fetchall()
        governed = {r["governed_path"] for r in rows}
        # Should have file entries from scan
        assert any("app.py" in g for g in governed)
        # Should NOT have governance entries added by scan pattern matching
        assert "rules/all.md" not in governed
        conn.close()
