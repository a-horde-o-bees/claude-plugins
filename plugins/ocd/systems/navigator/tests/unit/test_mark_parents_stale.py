"""Unit tests for _mark_parents_stale."""

from systems.navigator._db import get_connection
from systems.navigator._scanner import _mark_parents_stale


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
