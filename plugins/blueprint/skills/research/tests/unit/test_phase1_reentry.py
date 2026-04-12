"""Phase 1 re-entry: dashboard queries with existing data."""

import json


def result_text(result: str) -> str:
    """Extract result string from _ok() wrapper."""
    return json.loads(result)["result"]


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
