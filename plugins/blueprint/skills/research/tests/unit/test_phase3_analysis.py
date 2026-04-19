"""Phase 3 operations: analysis queries, measure extraction, incremental measures."""

import json


def result_text(result: str) -> str:
    """Extract result string from _ok() wrapper."""
    return json.loads(result)["result"]


class TestPhase3Analysis:
    """Phase 3 operations: analysis queries, measure extraction, incremental measures."""

    def _seed_for_analysis(self, db):
        for i, (name, rel) in enumerate([
            ("Code Review", 9),
            ("Semgrep", 8),
            ("Superpowers", 8),
            ("ArchUnit", 7),
        ], 1):
            db["register_entity"]({"name": name, "url": f"https://e{i}.com", "relevance": rel})
            db["set_stage"](f"e{i}", "researched")
            db["add_notes"](f"e{i}", [
                f"{name} note 1",
                f"{name} note 2",
            ])

    def test_get_researched_entities(self, db):
        """Analysis input: all researched entities."""
        self._seed_for_analysis(db)
        text = result_text(db["list_entities"](stage="researched"))
        assert "Code Review" in text
        assert "ArchUnit" in text

    def test_analysis_agent_reads_notes(self, db):
        """Analysis agent reads entity with all notes."""
        self._seed_for_analysis(db)
        detail = result_text(db["get_entity"]("e1"))
        assert "Notes (2)" in detail

    def test_measure_extraction(self, db):
        """Extract measures per entity from analysis findings."""
        self._seed_for_analysis(db)
        for i in range(1, 5):
            db["set_measures"](f"e{i}", [
                {"measure": "implementation_model", "value": "markdown-only"},
                {"measure": "activation_scope", "value": "pr"},
                {"measure": "confidence_scoring", "value": "yes"},
            ])

        summary = result_text(db["get_measure_summary"]())
        assert "implementation_model" in summary
        assert "activation_scope" in summary
        assert "confidence_scoring" in summary

    def test_measure_distribution_query(self, db):
        """Query measure distributions for findings report."""
        self._seed_for_analysis(db)
        db["set_measures"]("e1", [{"measure": "scope", "value": "pr"}])
        db["set_measures"]("e2", [{"measure": "scope", "value": "whole-project"}])
        db["set_measures"]("e3", [{"measure": "scope", "value": "pr"}])
        db["set_measures"]("e4", [{"measure": "scope", "value": "whole-project"}])

        summary = result_text(db["get_measure_summary"]())
        assert "scope" in summary

    def test_incremental_measures_new_entities_only(self, db):
        """Adding entities after initial analysis: only new entities need measures."""
        self._seed_for_analysis(db)
        for i in range(1, 5):
            db["set_measures"](f"e{i}", [{"measure": "score", "value": str(i * 10)}])

        db["register_entity"]({"name": "New Entity", "url": "https://new.com", "relevance": 6})
        db["set_stage"]("e5", "researched")

        # e5 has no measures yet — verify via get_entity
        detail = result_text(db["get_entity"]("e5"))
        assert "Measures" not in detail

        db["set_measures"]("e5", [{"measure": "score", "value": "60"}])

        detail = result_text(db["get_entity"]("e5"))
        assert "score: 60" in detail

    def test_criteria_change_clears_all_measures(self, db):
        """Effectiveness criteria change clears all measures for re-extraction."""
        self._seed_for_analysis(db)
        for i in range(1, 5):
            db["set_measures"](f"e{i}", [{"measure": "score", "value": str(i * 10)}])

        db["clear_all_measures"]()

        # Verify no measures on any entity
        for i in range(1, 5):
            detail = result_text(db["get_entity"](f"e{i}"))
            assert "Measures" not in detail
