"""Phase 2 re-entry: research interrupted, resume from checkpoint."""

import json


def result_text(result: str) -> str:
    """Extract result string from _ok() wrapper."""
    return json.loads(result)["result"]


class TestPhase2Resumption:
    """Phase 2 re-entry: research interrupted, resume from checkpoint."""

    def _seed_partial_research(self, db):
        db["register_entity"]({"name": "Done", "url": "https://done.com", "relevance": 9})
        db["set_stage"]("e1", "researched")
        db["add_notes"]("e1", [
            "Fully researched note 1",
            "Fully researched note 2",
        ])

        db["register_entity"]({"name": "Partial", "url": "https://partial.com", "relevance": 8})
        db["add_notes"]("e2", ["Agent wrote this before interruption"])

        db["register_entity"]({"name": "Not Started", "url": "https://notstarted.com", "relevance": 7})

    def test_find_resume_point(self, db):
        """Identify unresearched entities for resumption."""
        self._seed_partial_research(db)
        text = result_text(db["list_entities"](stage="new"))
        assert "Partial" in text
        assert "Not Started" in text

    def test_interrupted_agent_reconciles(self, db):
        """Re-spawned agent reads existing notes and continues."""
        self._seed_partial_research(db)
        detail = result_text(db["get_entity"]("e2"))
        assert "Agent wrote this before interruption" in detail
        assert "Notes (1)" in detail

        db["add_notes"]("e2", [
            "Additional research after resumption",
            "Final observation before stage advance",
        ])
        db["set_stage"]("e2", "researched")

        detail = result_text(db["get_entity"]("e2"))
        assert "Stage: researched" in detail
        assert "Notes (3)" in detail
