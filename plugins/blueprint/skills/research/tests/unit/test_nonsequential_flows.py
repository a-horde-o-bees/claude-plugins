"""Non-sequential workflow flows — scope refinement, re-entry, resumption, reversion, merge.

Tests cover scenarios where the agent revisits earlier phases, resumes
interrupted work, or resolves duplicates discovered during research.
"""

import json
import sqlite3

import pytest


def parse(result: str):
    return json.loads(result)


def result_text(result: str) -> str:
    """Extract result string from _ok() wrapper."""
    return json.loads(result)["result"]


# =============================================================================
# Phase 1: Scope Refinement Loops
# =============================================================================


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


# =============================================================================
# Phase 1 Re-Entry
# =============================================================================


class TestPhase1ReEntry:
    """Phase 1 re-entry: dashboard queries with existing data."""

    def _seed_full_landscape(self, db):
        for i, (name, modes, rel, stage) in enumerate([
            ("Researched Tool", ["example"], 9, "researched"),
            ("New Tool A", ["example"], 7, "new"),
            ("New Tool B", ["example"], 5, "new"),
            ("Rejected Tool", ["example"], 0, "rejected"),
            ("Context Source", ["context"], 8, "researched"),
            ("Directory", ["directory"], 6, "new"),
        ], 1):
            db["register_entity"]({"name": name, "url": f"https://e{i}.com", "modes": modes, "relevance": rel})
            if stage != "new":
                db["set_stage"](f"e{i}", stage)

        db["add_notes"]("e1", [
            "Note 1 for researched tool",
            "Note 2 for researched tool",
        ])
        db["add_notes"]("e2", ["Single note for new tool"])

    def test_dashboard_stats_query(self, db):
        """Re-entry dashboard: entity counts by stage."""
        self._seed_full_landscape(db)

        dashboard = result_text(db["get_dashboard"]())
        assert "3 new" in dashboard
        assert "2 researched" in dashboard

    def test_dashboard_examples_by_relevance(self, db):
        """Re-entry dashboard: examples visible via mode filter."""
        self._seed_full_landscape(db)

        text = result_text(db["list_entities"](mode="example"))
        assert "Researched Tool" in text
        assert "New Tool A" in text

    def test_dashboard_provenance(self, db):
        """Re-entry dashboard: provenance information available."""
        self._seed_full_landscape(db)
        dashboard = result_text(db["get_dashboard"]())
        assert "Provenance" in dashboard

    def test_dashboard_multi_source_entities(self, db):
        """Re-entry dashboard: entities found via multiple sources tracked."""
        self._seed_full_landscape(db)
        # Add provenance to entity e1 from two sources
        db["add_provenance"]("e1", "https://source1.com")
        db["add_provenance"]("e1", "https://source2.com")

        detail = result_text(db["get_entity"]("e1"))
        assert "source1.com" in detail
        assert "source2.com" in detail


# =============================================================================
# Phase 2: Interrupted Research and Resumption
# =============================================================================


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


# =============================================================================
# Phase Reversion
# =============================================================================


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


# =============================================================================
# Duplicate Resolution
# =============================================================================


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
