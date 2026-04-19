"""Phase 4 operations: full entity reads for implementation blueprint."""

import json


def result_text(result: str) -> str:
    """Extract result string from _ok() wrapper."""
    return json.loads(result)["result"]


class TestPhase4Blueprint:
    """Phase 4 operations: full entity reads for implementation blueprint."""

    def _seed_full_dataset(self, db):
        db["register_entity"]({"name": "Top Entity", "url": "https://top.com", "relevance": 9})
        db["set_stage"]("e1", "researched")
        db["add_notes"]("e1", [
            "Key architectural pattern: markdown-as-code",
            "Multi-agent parallel dispatch via Task tool",
        ])
        db["set_measures"]("e1", [
            {"measure": "implementation_model", "value": "markdown-only"},
            {"measure": "activation_scope", "value": "pr"},
        ])

    def test_full_entity_with_all_includes(self, db):
        """Phase 4 reads entity with notes, measures, and URLs."""
        self._seed_full_dataset(db)
        detail = result_text(db["get_entity"]("e1"))
        assert "Top Entity" in detail
        assert "Notes (2)" in detail
        assert "Measures (2)" in detail
        assert "URLs" in detail

    def test_read_all_researched_with_notes(self, db):
        """Phase 4 bulk read: all researched entities listed."""
        self._seed_full_dataset(db)
        db["register_entity"]({"name": "Second", "url": "https://second.com", "relevance": 7})
        db["set_stage"]("e2", "researched")
        db["add_notes"]("e2", ["Note for second entity"])

        text = result_text(db["list_entities"](stage="researched"))
        assert "Top Entity" in text
        assert "Second" in text
