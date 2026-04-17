"""Unit tests for paths_search (search_entries)."""

from subsystems.navigator import paths_search


class TestSearchEntries:
    def test_finds_matching(self, populated_db):
        result = paths_search(populated_db, "Utility")
        assert len(result["results"]) == 1
        assert "utils.py" in result["results"][0]["path"]

    def test_case_insensitive(self, populated_db):
        result = paths_search(populated_db, "utility")
        assert len(result["results"]) == 1

    def test_no_match(self, populated_db):
        result = paths_search(populated_db, "nonexistent")
        assert result["results"] == []

    def test_excludes_patterns(self, db_with_patterns):
        """Patterns live in a separate table — search only hits entries."""
        result = paths_search(db_with_patterns, "Package")
        assert result["results"] == []
