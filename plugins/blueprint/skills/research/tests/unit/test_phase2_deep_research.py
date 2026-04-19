"""Phase 2 operations: research agents writing notes, advancing stage."""

import json
import sqlite3


def result_text(result: str) -> str:
    """Extract result string from _ok() wrapper."""
    return json.loads(result)["result"]


class TestPhase2DeepResearch:
    """Phase 2 operations: research agents writing notes, advancing stage."""

    def _seed_for_research(self, db):
        db["register_entity"]({"name": "High Priority", "url": "https://hp.com", "relevance": 9})
        db["register_entity"]({"name": "Med Priority", "url": "https://mp.com", "relevance": 7})
        db["register_entity"]({"name": "Low Priority", "url": "https://lp.com", "relevance": 5})
        db["add_notes"]("e1", ["Initial discovery observation"])

    def test_get_research_queue(self, db):
        """Phase 2 input: entities filtered for research queue."""
        self._seed_for_research(db)
        text = result_text(db["list_entities"](stage="new"))
        assert "High Priority" in text
        assert "Med Priority" in text
        assert "Low Priority" in text

    def test_research_agent_reads_entity(self, db):
        """Research agent loads entity with existing notes."""
        self._seed_for_research(db)
        detail = result_text(db["get_entity"]("e1"))
        assert "High Priority" in detail
        assert "Initial discovery observation" in detail

    def test_research_agent_writes_notes(self, db):
        """Research agent adds comprehensive notes after research."""
        self._seed_for_research(db)
        db["add_notes"]("e1", [
            "Apache 2.0 licensed, fully open source",
            "32k GitHub stars, active maintenance",
            "Supports 30+ languages via tree-sitter",
        ])
        detail = result_text(db["get_entity"]("e1"))
        assert "Apache 2.0" in detail
        assert "32k GitHub stars" in detail
        assert "tree-sitter" in detail
        # Should have 4 notes total: 1 initial + 3 new
        assert "Notes (4)" in detail

    def test_research_agent_reconciles_notes(self, db):
        """Research agent corrects outdated note during reconciliation."""
        self._seed_for_research(db)
        db["add_notes"]("e1", ["15k stars"])

        # Find the outdated note ID
        conn = sqlite3.connect(db["path"])
        conn.row_factory = sqlite3.Row
        outdated = conn.execute(
            "SELECT id FROM entity_notes WHERE entity_id = 'e1' AND note = '15k stars'"
        ).fetchone()
        conn.close()

        db["remove_notes"]("e1", [outdated["id"]])
        db["add_notes"]("e1", ["32k GitHub stars as of March 2026"])

        detail = result_text(db["get_entity"]("e1"))
        assert "32k GitHub stars as of March 2026" in detail
        assert "15k stars" not in detail

    def test_advance_stage_to_researched(self, db):
        """Research agent marks entity as researched after completing."""
        self._seed_for_research(db)
        db["set_stage"]("e1", "researched")
        detail = result_text(db["get_entity"]("e1"))
        assert "Stage: researched" in detail

    def test_verify_stage_after_completion(self, db):
        """Orchestrator verifies agent actually set stage."""
        self._seed_for_research(db)
        detail = result_text(db["get_entity"]("e1"))
        assert "Stage: new" in detail  # not advanced — needs re-spawn

    def test_adjacent_entity_discovery(self, db):
        """Research agent discovers and registers adjacent entities."""
        self._seed_for_research(db)
        text = result_text(db["register_entity"]({
            "name": "Adjacent Tool",
            "url": "https://adjacent.com",
            "source_url": "https://hp.com",
            "description": "Found while researching High Priority",
            "relevance": 6,
        }))
        assert "id: e4" in text

        detail = result_text(db["get_entity"]("e4"))
        assert "Found via" in detail
