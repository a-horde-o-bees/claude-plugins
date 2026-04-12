"""Duplicate detection and merge — happens during deep research."""

import json


def parse(result: str):
    return json.loads(result)


def result_text(result: str) -> str:
    """Extract result string from _ok() wrapper."""
    return json.loads(result)["result"]


class TestDuplicateResolution:
    """Duplicate detection and merge — happens during deep research."""

    def test_merge_entities(self, db):
        """Merge duplicate entities into survivor."""
        db["register_entity"]({"name": "Entity A", "url": "https://a.com", "relevance": 8, "description": "First description"})
        db["register_entity"]({"name": "Entity A (dupe)", "url": "https://a-alt.com", "relevance": 6, "description": "Second description"})
        db["add_notes"]("e1", ["Note on original"])
        db["add_notes"]("e2", ["Note on duplicate"])

        db["merge_entities"](["e1", "e2"])

        detail = result_text(db["get_entity"]("e1"))
        assert "Note on original" in detail
        assert "Note on duplicate" in detail

        # e2 should be gone (deleted by merge)
        result = parse(db["get_entity"]("e2"))
        assert "error" in result
