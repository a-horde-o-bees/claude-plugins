"""Non-sequential workflow flows — scope refinement, re-entry, resumption, reversion, merge.

Tests cover scenarios where the agent revisits earlier phases, resumes
interrupted work, or resolves duplicates discovered during research.
"""

import json


def parse(result: str):
    return json.loads(result)


# =============================================================================
# Phase 1: Scope Refinement Loops
# =============================================================================


class TestPhase1ScopeRefinement:
    """Non-sequential Phase 1: criteria changes, relevance reassessment, hardline filters."""

    def _seed_entities(self, db):
        db["create"]("entities", {"name": "High Rel", "url": "https://high.com", "relevance": 9, "role": "example"})
        db["create"]("entities", {"name": "Mid Rel", "url": "https://mid.com", "relevance": 5, "role": "example"})
        db["create"]("entities", {"name": "Low Rel", "url": "https://low.com", "relevance": 2, "role": "example"})
        db["create"]("entities", {"name": "Context Source", "url": "https://ctx.com", "relevance": 7, "role": "context"})

    def test_relevance_reassessment(self, db):
        """Criteria change triggers relevance rescore on existing entities."""
        self._seed_entities(db)

        db["update"]("entities", "e1", {"relevance": 6})
        db["update"]("entities", "e2", {"relevance": 8})

        e1 = parse(db["read"]("entities", {"id": "e1"}))
        e2 = parse(db["read"]("entities", {"id": "e2"}))
        assert e1[0]["relevance"] == 6
        assert e2[0]["relevance"] == 8

    def test_retroactive_hardline_filter(self, db):
        """New hardline criterion rejects existing entities."""
        self._seed_entities(db)

        low_rel = parse(db["read"]("entities", {"relevance__lt": 3}))
        for entity in low_rel:
            db["update"]("entities", entity["id"], {"stage": "rejected"})
            db["create"]("entity_notes", {"entity_id": entity["id"], "note": "Rejected: below new relevance threshold"})

        rejected = parse(db["read"]("entities", {"stage": "rejected"}))
        assert len(rejected) == 1
        assert rejected[0]["name"] == "Low Rel"

    def test_criteria_change_clears_measures(self, db):
        """Criteria change invalidates existing measures."""
        self._seed_entities(db)

        db["create"]("entity_measures", {"entity_id": "e1", "measure": "score", "value": "95"})
        db["create"]("entity_measures", {"entity_id": "e2", "measure": "score", "value": "70"})

        db["delete"]("entity_measures", all=True)

        measures = parse(db["query"]("SELECT COUNT(*) as count FROM entity_measures"))
        assert measures[0]["count"] == 0

    def test_add_entities_from_new_source(self, db):
        """User discovers new directory mid-phase, adds entities."""
        self._seed_entities(db)

        db["create"]("entities", {"name": "New Directory", "url": "https://newdir.com", "role": "directory", "relevance": 6})
        db["create"]("entities", {
            "name": "Newly Found Tool",
            "url": "https://newtool.com",
            "source_url": "https://newdir.com",
            "relevance": 7,
        })

        prov = parse(db["query"]("SELECT * FROM url_provenance WHERE source_url LIKE '%newdir%'"))
        assert len(prov) == 1


# =============================================================================
# Phase 1 Re-Entry
# =============================================================================


class TestPhase1ReEntry:
    """Phase 1 re-entry: dashboard queries with existing data."""

    def _seed_full_landscape(self, db):
        for i, (name, role, rel, stage) in enumerate([
            ("Researched Tool", "example", 9, "researched"),
            ("New Tool A", "example", 7, "new"),
            ("New Tool B", "example", 5, "new"),
            ("Rejected Tool", "example", 0, "rejected"),
            ("Context Source", "context", 8, "researched"),
            ("Directory", "directory", 6, "new"),
        ], 1):
            db["create"]("entities", {"name": name, "url": f"https://e{i}.com", "role": role, "relevance": rel})
            if stage != "new":
                db["update"]("entities", f"e{i}", {"stage": stage})

        db["create"]("entity_notes", [
            {"entity_id": "e1", "note": "Note 1 for researched tool"},
            {"entity_id": "e1", "note": "Note 2 for researched tool"},
        ])
        db["create"]("entity_notes", {"entity_id": "e2", "note": "Single note for new tool"})

    def test_dashboard_stats_query(self, db):
        """Re-entry dashboard: entity counts by role and stage."""
        self._seed_full_landscape(db)

        stats = parse(db["query"](
            "SELECT stage, COUNT(*) as count FROM entities GROUP BY stage ORDER BY stage"
        ))
        stage_counts = {s["stage"]: s["count"] for s in stats}
        assert stage_counts["new"] == 3
        assert stage_counts["researched"] == 2

    def test_dashboard_examples_by_relevance(self, db):
        """Re-entry dashboard: examples with relevance values."""
        self._seed_full_landscape(db)

        examples = parse(db["read"]("entities", {"role": "example"}))
        assert len(examples) == 4
        relevances = {e["name"]: e["relevance"] for e in examples}
        assert relevances["Researched Tool"] == 9

    def test_dashboard_provenance(self, db):
        """Re-entry dashboard: provenance source counts."""
        self._seed_full_landscape(db)
        prov = parse(db["query"]("SELECT source_url, COUNT(entity_id) as entity_count FROM url_provenance GROUP BY source_url"))
        assert isinstance(prov, list)

    def test_dashboard_multi_source_entities(self, db):
        """Re-entry dashboard: entities found via multiple sources."""
        self._seed_full_landscape(db)
        reach = parse(db["query"](
            "SELECT entity_id, COUNT(source_url) as source_count FROM url_provenance GROUP BY entity_id HAVING source_count >= 2"
        ))
        assert isinstance(reach, list)


# =============================================================================
# Phase 2: Interrupted Research and Resumption
# =============================================================================


class TestPhase2Resumption:
    """Phase 2 re-entry: research interrupted, resume from checkpoint."""

    def _seed_partial_research(self, db):
        db["create"]("entities", {"name": "Done", "url": "https://done.com", "relevance": 9})
        db["update"]("entities", "e1", {"stage": "researched"})
        db["create"]("entity_notes", [
            {"entity_id": "e1", "note": "Fully researched note 1"},
            {"entity_id": "e1", "note": "Fully researched note 2"},
        ])

        db["create"]("entities", {"name": "Partial", "url": "https://partial.com", "relevance": 8})
        db["create"]("entity_notes", {"entity_id": "e2", "note": "Agent wrote this before interruption"})

        db["create"]("entities", {"name": "Not Started", "url": "https://notstarted.com", "relevance": 7})

    def test_find_resume_point(self, db):
        """Identify unresearched entities for resumption."""
        self._seed_partial_research(db)
        pending = parse(db["read"]("entities", {"stage": "new"}))
        assert len(pending) == 2
        names = {e["name"] for e in pending}
        assert "Partial" in names
        assert "Not Started" in names

    def test_interrupted_agent_reconciles(self, db):
        """Re-spawned agent reads existing notes and continues."""
        self._seed_partial_research(db)
        entity = parse(db["read"]("entities", {"id": "e2"}, include=["entity_notes"]))
        assert len(entity[0]["entity_notes"]) == 1

        db["create"]("entity_notes", [
            {"entity_id": "e2", "note": "Additional research after resumption"},
            {"entity_id": "e2", "note": "Final observation before stage advance"},
        ])
        db["update"]("entities", "e2", {"stage": "researched"})

        entity = parse(db["read"]("entities", {"id": "e2"}, include=["entity_notes"]))
        assert entity[0]["stage"] == "researched"
        assert len(entity[0]["entity_notes"]) == 3


# =============================================================================
# Phase Reversion
# =============================================================================


class TestPhaseReversion:
    """Phase reversion: go back to Phase 1 to add more entities."""

    def _seed_post_research(self, db):
        db["create"]("entities", {"name": "Entity A", "url": "https://a.com", "relevance": 9})
        db["update"]("entities", "e1", {"stage": "researched"})
        db["create"]("entity_notes", {"entity_id": "e1", "note": "Research note"})
        db["create"]("entity_measures", {"entity_id": "e1", "measure": "score", "value": "95"})

        db["create"]("entities", {"name": "Entity B", "url": "https://b.com", "relevance": 7})
        db["update"]("entities", "e2", {"stage": "researched"})
        db["create"]("entity_measures", {"entity_id": "e2", "measure": "score", "value": "80"})

    def test_reversion_clears_measures(self, db):
        """Reverting to Phase 1 clears measures but preserves entities and notes."""
        self._seed_post_research(db)

        db["delete"]("entity_measures", all=True)

        entities = parse(db["read"]("entities"))
        assert len(entities) == 2

        entity = parse(db["read"]("entities", {"id": "e1"}, include=["entity_notes"]))
        assert len(entity[0]["entity_notes"]) == 1

        measures = parse(db["query"]("SELECT COUNT(*) as count FROM entity_measures"))
        assert measures[0]["count"] == 0

    def test_reversion_resets_stage(self, db):
        """Reverting to Phase 1 resets entity stage to allow re-research."""
        self._seed_post_research(db)

        db["update"]("entities", "e1", {"stage": "new"})
        db["update"]("entities", "e2", {"stage": "new"})

        entities = parse(db["read"]("entities", {"stage": "new"}))
        assert len(entities) == 2

    def test_new_entities_after_reversion(self, db):
        """New entities added after reversion coexist with existing data."""
        self._seed_post_research(db)

        db["create"]("entities", {"name": "New Discovery", "url": "https://new.com", "relevance": 8})

        all_entities = parse(db["read"]("entities"))
        assert len(all_entities) == 3

        new = parse(db["read"]("entities", {"id": "e3"}))
        assert new[0]["stage"] == "new"


# =============================================================================
# Duplicate Resolution
# =============================================================================


class TestDuplicateResolution:
    """Duplicate detection and merge — happens during deep research."""

    def test_merge_entities(self, db):
        """Merge duplicate entities into survivor."""
        db["create"]("entities", {"name": "Entity A", "url": "https://a.com", "relevance": 8, "description": "First description"})
        db["create"]("entities", {"name": "Entity A (dupe)", "url": "https://a-alt.com", "relevance": 6, "description": "Second description"})
        db["create"]("entity_notes", {"entity_id": "e1", "note": "Note on original"})
        db["create"]("entity_notes", {"entity_id": "e2", "note": "Note on duplicate"})

        db["merge"](["e1", "e2"])

        survivor = parse(db["read"]("entities", {"id": "e1"}, include=["entity_notes"]))
        assert len(survivor) == 1
        assert len(survivor[0]["entity_notes"]) == 2

        merged = parse(db["read"]("entities", {"id": "e2"}))
        assert len(merged) == 0 or merged[0]["stage"] == "merged"
