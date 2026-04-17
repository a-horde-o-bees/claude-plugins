"""Unit tests for stale behavior across paths_upsert, paths_undescribed, and paths_get."""

from systems.navigator._db import get_connection
from systems.navigator import paths_upsert, paths_undescribed, paths_get


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
