"""Unit tests for paths_upsert (set_entry)."""

import pytest

from systems.navigator._db import get_connection
from systems.navigator import paths_upsert


class TestSetEntry:
    def test_add_new_file(self, db_path, tmp_path):
        f = tmp_path / "newfile.py"
        f.write_text("content")
        result = paths_upsert(db_path, str(f), purpose="New file")
        assert result["action"] == "added"

    def test_add_new_directory(self, db_path, tmp_path):
        d = tmp_path / "newdir"
        d.mkdir()
        result = paths_upsert(db_path, str(d), purpose="New dir")
        assert result["action"] == "added"
        assert result["type"] == "directory"

    def test_update_existing(self, populated_db):
        result = paths_upsert(populated_db, "src/main.py", purpose="Updated")
        assert result["action"] == "updated"
        conn = get_connection(populated_db)
        row = conn.execute("SELECT purpose FROM paths WHERE path = 'src/main.py'").fetchone()
        assert row["purpose"] == "Updated"
        conn.close()

    def test_set_empty_string_description(self, populated_db):
        paths_upsert(populated_db, "src/lib/core.py", purpose="")
        conn = get_connection(populated_db)
        row = conn.execute("SELECT purpose FROM paths WHERE path = 'src/lib/core.py'").fetchone()
        assert row["purpose"] == ""
        conn.close()

    def test_set_traverse_flag(self, populated_db):
        paths_upsert(populated_db, "src/lib", traverse=0)
        conn = get_connection(populated_db)
        row = conn.execute("SELECT traverse FROM paths WHERE path = 'src/lib'").fetchone()
        assert row["traverse"] == 0
        conn.close()

    def test_set_exclude_flag(self, populated_db):
        paths_upsert(populated_db, "src/lib", exclude=1)
        conn = get_connection(populated_db)
        row = conn.execute("SELECT exclude FROM paths WHERE path = 'src/lib'").fetchone()
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
        paths_upsert(populated_db, str(f), purpose="Test")
        conn = get_connection(populated_db)
        row = conn.execute(
            "SELECT git_hash FROM paths WHERE path = ?", (str(f),)
        ).fetchone()
        assert row["git_hash"] is not None
        assert len(row["git_hash"]) == 40
        conn.close()
