"""Error handling and edge cases — missing database, invalid operations, source data."""

import importlib
import json
import os

def parse(result: str):
    return json.loads(result)


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
        srv.DB_PATH = str(tmp_path / "nonexistent.db")

        result = json.loads(srv.read_records("entities"))
        assert "error" in result
        assert "not initialized" in result["error"].lower()

        result = json.loads(srv.create_records("entities", {"name": "Test"}))
        assert "error" in result

        result = json.loads(srv.query("SELECT 1"))
        assert "error" in result

        result = json.loads(srv.describe_entities())
        assert "error" in result

    def test_init_database_creates_schema(self, tmp_path):
        """init_database creates database when it doesn't exist."""
        db_path = str(tmp_path / "fresh.db")
        os.environ["DB_PATH"] = db_path
        import servers.research_db as srv
        importlib.reload(srv)
        srv.DB_PATH = db_path

        result = json.loads(srv.init_database())
        assert "initialized" in result["status"]

        result = json.loads(srv.describe_entities())
        assert "entities" in result


# =============================================================================
# Invalid Operations
# =============================================================================


class TestErrorHandling:
    """Error cases that agents might encounter."""

    def test_invalid_table(self, db):
        result = parse(db["read"]("nonexistent_table"))
        assert "error" in str(result).lower() or isinstance(result, list)

    def test_query_rejects_insert(self, db):
        result = parse(db["query"]("INSERT INTO entities (id, name) VALUES ('e999', 'bad')"))
        assert "error" in result

    def test_query_rejects_delete(self, db):
        result = parse(db["query"]("DELETE FROM entities"))
        assert "error" in result

    def test_query_rejects_update(self, db):
        result = parse(db["query"]("UPDATE entities SET name = 'bad' WHERE id = 'e1'"))
        assert "error" in result

    def test_invalid_include_table(self, db):
        """Include with non-FK table raises error."""
        db["create"]("entities", {"name": "Test", "url": "https://test.com"})
        try:
            result = parse(db["read"]("entities", include=["nonexistent"]))
            assert "error" in str(result).lower()
        except ValueError:
            pass  # also acceptable

    def test_describe_invalid_table(self, db):
        result = parse(db["describe"]("nonexistent"))
        assert "error" in str(result).lower()


# =============================================================================
# Source Data
# =============================================================================


class TestSourceData:
    """Entity source data — structured key-value per source type."""

    def test_create_and_read_source_data(self, db):
        db["create"]("entities", {"name": "Test", "url": "https://test.com"})
        db["create"]("entity_source_data", [
            {"entity_id": "e1", "source_type": "github", "key": "stars", "value": "14600"},
            {"entity_id": "e1", "source_type": "github", "key": "forks", "value": "1200"},
        ])

        data = parse(db["query"](
            "SELECT key, value FROM entity_source_data WHERE entity_id = 'e1' AND source_type = 'github'"
        ))
        assert len(data) == 2
        keys = {d["key"] for d in data}
        assert "stars" in keys
        assert "forks" in keys
