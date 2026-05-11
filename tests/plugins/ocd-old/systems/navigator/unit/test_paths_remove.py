"""Unit tests for paths_remove (remove_entry)."""

from systems.navigator._db import get_connection
from systems.navigator import paths_remove


class TestRemoveEntry:
    def test_remove_single(self, populated_db):
        result = paths_remove(populated_db, "src/main.py")
        assert result["action"] == "removed"

    def test_remove_not_found(self, populated_db):
        result = paths_remove(populated_db, "nonexistent")
        assert result["action"] == "not_found"

    def test_remove_recursive(self, populated_db):
        result = paths_remove(populated_db, "src/lib", mode="recursive")
        assert result["action"] == "removed_recursive"
        conn = get_connection(populated_db)
        rows = conn.execute(
            "SELECT path FROM paths WHERE path = 'src/lib' OR path LIKE 'src/lib/%'"
        ).fetchall()
        assert len(rows) == 0
        conn.close()

    def test_remove_recursive_file_error(self, populated_db):
        result = paths_remove(populated_db, "src/main.py", mode="recursive")
        assert result["action"] == "error"

    def test_remove_all(self, populated_db):
        # Add a pattern rule
        conn = get_connection(populated_db)
        conn.execute(
            "INSERT INTO path_patterns (pattern, entry_type, exclude) VALUES ('**/*.log', NULL, 1)"
        )
        conn.commit()
        conn.close()

        result = paths_remove(populated_db, "", mode="all")
        assert result["action"] == "removed_all"

        conn = get_connection(populated_db)
        entries_count = conn.execute("SELECT COUNT(*) FROM paths").fetchone()[0]
        patterns_count = conn.execute("SELECT COUNT(*) FROM path_patterns").fetchone()[0]
        assert entries_count == 0
        assert patterns_count == 1
        conn.close()
