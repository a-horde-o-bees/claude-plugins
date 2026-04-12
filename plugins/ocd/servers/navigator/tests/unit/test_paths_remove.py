"""Unit tests for paths_remove (remove_entry)."""

from servers.navigator._db import get_connection
from servers.navigator import paths_remove


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
