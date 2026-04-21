"""Unit tests for navigator._init.ready.

Covers the four branches of ready(): absent file returns False, present
file with full schema returns True, present file missing an expected
table returns False, corrupt/non-sqlite file returns False (sqlite3.Error
is caught).
"""

from pathlib import Path

from systems.navigator._db import SCHEMA, get_connection
from systems.navigator._init import ready


class TestReady:
    def test_absent_db_returns_false(self, tmp_path: Path) -> None:
        assert ready(tmp_path / "nope.db") is False

    def test_full_schema_returns_true(self, tmp_path: Path) -> None:
        db = tmp_path / "test.db"
        conn = get_connection(str(db))
        conn.executescript(SCHEMA)
        conn.close()
        assert ready(db) is True

    def test_missing_table_returns_false(self, tmp_path: Path) -> None:
        """Present DB with incomplete schema must report not-ready — strict
        subset check, not just file existence."""
        db = tmp_path / "partial.db"
        conn = get_connection(str(db))
        conn.execute("CREATE TABLE paths (path TEXT PRIMARY KEY)")
        conn.commit()
        conn.close()
        assert ready(db) is False

    def test_non_sqlite_file_returns_false(self, tmp_path: Path) -> None:
        """Corrupt or non-sqlite file: sqlite3.Error caught, returns False."""
        db = tmp_path / "garbage.db"
        db.write_text("this is not a sqlite database")
        assert ready(db) is False
