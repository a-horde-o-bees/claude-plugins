"""Unit tests for paths_get (describe_path)."""

from lib.navigator._db import get_connection
from lib.navigator import paths_get


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
