"""Unit tests for paths_undescribed (get_undescribed)."""

from subsystems.navigator._db import get_connection
from subsystems.navigator import paths_undescribed


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
