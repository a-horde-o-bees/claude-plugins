"""Error handling and edge cases — missing database, invalid operations, source data."""

import importlib
import json
import os
import sqlite3


def parse(result: str):
    return json.loads(result)


def result_text(result: str) -> str:
    """Extract result string from _ok() wrapper."""
    return json.loads(result)["result"]


# =============================================================================
# Missing Database
# =============================================================================


class TestMissingDatabase:
    """Server handles missing database gracefully."""

    def test_read_without_database(self, tmp_path):
        """All tools return clear error when database doesn't exist."""
        os.environ["DB_PATH"] = str(tmp_path / "nonexistent.db")
        import servers.research_db as srv
        importlib.reload(srv)
        srv._helpers.DB_PATH = str(tmp_path / "nonexistent.db")

        result = json.loads(srv.list_entities())
        assert "error" in result
        assert "not initialized" in result["error"].lower()

        result = json.loads(srv.register_entity({"name": "Test"}))
        assert "error" in result

        result = json.loads(srv.get_dashboard())
        assert "error" in result

        result = json.loads(srv.describe_schema())
        assert "error" in result

    def test_init_database_creates_schema(self, tmp_path):
        """init_database creates database when it doesn't exist."""
        db_path = str(tmp_path / "fresh.db")
        os.environ["DB_PATH"] = db_path
        import servers.research_db as srv
        importlib.reload(srv)
        srv.DB_PATH = db_path

        result = json.loads(srv.init_database())
        assert "initialized" in result["result"].lower()

        result = json.loads(srv.describe_schema())
        assert "entities" in result


# =============================================================================
# Invalid Operations
# =============================================================================


class TestErrorHandling:
    """Error cases that agents might encounter."""

    def test_get_nonexistent_entity(self, db):
        result = parse(db["get_entity"]("e999"))
        assert "error" in result

    def test_set_stage_nonexistent_entity(self, db):
        result = parse(db["set_stage"]("e999", "researched"))
        assert "Updated 0" in result.get("result", "")

    def test_describe_invalid_table(self, db):
        result = parse(db["describe_schema"](table="nonexistent"))
        assert "error" in str(result).lower()


# =============================================================================
# Source Data
# =============================================================================


class TestSourceData:
    """Entity source data — structured key-value per source type."""

    def test_create_and_read_source_data(self, db):
        db["register_entity"]({"name": "Test", "url": "https://test.com"})

        # Source data has no domain tool — insert directly via SQLite
        conn = sqlite3.connect(db["path"])
        conn.execute(
            "INSERT INTO entity_source_data (entity_id, source_type, key, value) VALUES (?, ?, ?, ?)",
            ("e1", "github", "stars", "14600"),
        )
        conn.execute(
            "INSERT INTO entity_source_data (entity_id, source_type, key, value) VALUES (?, ?, ?, ?)",
            ("e1", "github", "forks", "1200"),
        )
        conn.commit()
        conn.close()

        # Verify source data appears in entity detail
        detail = result_text(db["get_entity"]("e1"))
        assert "stars" in detail
        assert "14600" in detail
        assert "forks" in detail
        assert "1200" in detail
