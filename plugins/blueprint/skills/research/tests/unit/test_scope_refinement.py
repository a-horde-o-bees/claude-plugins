"""Non-sequential Phase 1: criteria changes, relevance reassessment, hardline filters."""

import json


def result_text(result: str) -> str:
    """Extract result string from _ok() wrapper."""
    return json.loads(result)["result"]


class TestPhase1ScopeRefinement:
    """Non-sequential Phase 1: criteria changes, relevance reassessment, hardline filters."""

    def _seed_entities(self, db):
        db["register_entity"]({"name": "High Rel", "url": "https://high.com", "relevance": 9, "modes": ["example"]})
        db["register_entity"]({"name": "Mid Rel", "url": "https://mid.com", "relevance": 5, "modes": ["example"]})
        db["register_entity"]({"name": "Low Rel", "url": "https://low.com", "relevance": 2, "modes": ["example"]})
        db["register_entity"]({"name": "Context Source", "url": "https://ctx.com", "relevance": 7, "modes": ["context"]})

    def test_relevance_reassessment(self, db):
        """Criteria change triggers relevance rescore on existing entities."""
        self._seed_entities(db)

        db["set_relevance"]("e1", 6)
        db["set_relevance"]("e2", 8)

        detail_e1 = result_text(db["get_entity"]("e1"))
        detail_e2 = result_text(db["get_entity"]("e2"))
        assert "Relevance: 6" in detail_e1
        assert "Relevance: 8" in detail_e2

    def test_retroactive_hardline_filter(self, db):
        """New hardline criterion rejects existing entities."""
        self._seed_entities(db)

        # Low Rel has relevance 2 — reject it
        db["reject_entity"]("e3", "below new relevance threshold")

        detail = result_text(db["get_entity"]("e3"))
        assert "Stage: rejected" in detail
        assert "Relevance: -1" in detail
        assert "below new relevance threshold" in detail

    def test_criteria_change_clears_measures(self, db):
        """Criteria change invalidates existing measures."""
        self._seed_entities(db)

        db["set_measures"]("e1", [{"measure": "score", "value": "95"}])
        db["set_measures"]("e2", [{"measure": "score", "value": "70"}])

        db["clear_all_measures"]()

        detail_e1 = result_text(db["get_entity"]("e1"))
        detail_e2 = result_text(db["get_entity"]("e2"))
        assert "Measures" not in detail_e1
        assert "Measures" not in detail_e2

    def test_add_entities_from_new_source(self, db):
        """User discovers new directory mid-phase, adds entities."""
        self._seed_entities(db)

        db["register_entity"]({"name": "New Directory", "url": "https://newdir.com", "modes": ["directory"], "relevance": 6})
        db["register_entity"]({
            "name": "Newly Found Tool",
            "url": "https://newtool.com",
            "source_url": "https://newdir.com",
            "relevance": 7,
        })

        detail = result_text(db["get_entity"]("e6"))
        assert "newdir.com" in detail
