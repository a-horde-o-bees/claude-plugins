"""Phase reversion: go back to Phase 1 to add more entities."""

import json


def result_text(result: str) -> str:
    """Extract result string from _ok() wrapper."""
    return json.loads(result)["result"]


class TestPhaseReversion:
    """Phase reversion: go back to Phase 1 to add more entities."""

    def _seed_post_research(self, db):
        db["register_entity"]({"name": "Entity A", "url": "https://a.com", "relevance": 9})
        db["set_stage"]("e1", "researched")
        db["add_notes"]("e1", ["Research note"])
        db["set_measures"]("e1", [{"measure": "score", "value": "95"}])

        db["register_entity"]({"name": "Entity B", "url": "https://b.com", "relevance": 7})
        db["set_stage"]("e2", "researched")
        db["set_measures"]("e2", [{"measure": "score", "value": "80"}])

    def test_reversion_clears_measures(self, db):
        """Reverting to Phase 1 clears measures but preserves entities and notes."""
        self._seed_post_research(db)

        db["clear_all_measures"]()

        text = result_text(db["list_entities"]())
        assert "Entity A" in text
        assert "Entity B" in text

        detail = result_text(db["get_entity"]("e1"))
        assert "Research note" in detail
        assert "Measures" not in detail

    def test_reversion_resets_stage(self, db):
        """Reverting to Phase 1 resets entity stage to allow re-research."""
        self._seed_post_research(db)

        db["set_stage"]("e1", "new")
        db["set_stage"]("e2", "new")

        text = result_text(db["list_entities"](stage="new"))
        assert "Entity A" in text
        assert "Entity B" in text

    def test_new_entities_after_reversion(self, db):
        """New entities added after reversion coexist with existing data."""
        self._seed_post_research(db)

        db["register_entity"]({"name": "New Discovery", "url": "https://new.com", "relevance": 8})

        text = result_text(db["list_entities"]())
        assert "Entity A" in text
        assert "Entity B" in text
        assert "New Discovery" in text

        detail = result_text(db["get_entity"]("e3"))
        assert "Stage: new" in detail
