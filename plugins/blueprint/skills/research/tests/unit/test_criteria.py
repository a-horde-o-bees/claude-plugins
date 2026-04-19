"""Tests for criteria definitions, note links, assessment, and cascade behavior."""

import json
import sqlite3

import pytest


def parse(result):
    """Parse JSON tool result, handling wrapped and unwrapped formats."""
    if isinstance(result, str):
        data = json.loads(result)
        if isinstance(data, dict) and "result" in data:
            inner = data["result"]
            if isinstance(inner, str):
                try:
                    return json.loads(inner)
                except json.JSONDecodeError:
                    return inner
            return inner
        return data
    return result


class TestCriteriaDefinitions:
    """CRUD operations on criteria definitions."""

    def test_add_single_criterion(self, db):
        result = db["add_criterion"](type="hardline", name="Open source", gate="OSI-approved license")
        assert "Added criterion c1" in parse(result)

    def test_set_criteria_replaces_all(self, db):
        db["add_criterion"](type="hardline", name="Old criterion", gate="old gate")
        db["set_criteria"](criteria=[
            {"type": "hardline", "name": "New hardline", "gate": "new gate 1"},
            {"type": "relevancy", "name": "New relevancy", "gate": "new gate 2"},
        ])
        result = parse(db["get_criteria"]())
        assert "New hardline" in result
        assert "New relevancy" in result
        assert "Old criterion" not in result

    def test_remove_criterion(self, db):
        db["add_criterion"](type="relevancy", name="Adoption", gate=">=50 stars")
        db["remove_criterion"](criterion_id="c1")
        result = parse(db["get_criteria"]())
        assert "No criteria defined" in result

    def test_get_criteria_lists_all(self, db):
        db["set_criteria"](criteria=[
            {"type": "hardline", "name": "Open source", "gate": "OSI license"},
            {"type": "relevancy", "name": "Adoption", "gate": ">=50 stars"},
            {"type": "relevancy", "name": "Stable", "gate": "Versioned releases"},
        ])
        result = parse(db["get_criteria"]())
        assert "Criteria (3)" in result
        assert "[H]" in result  # hardline
        assert "[R]" in result  # relevancy

    def test_criterion_type_check_constraint(self, db):
        result = parse(db["add_criterion"](type="optional", name="bad", gate="bad"))
        assert "error" in result or "CHECK" in str(result)

    def test_set_criteria_cascades_links(self, db):
        """Replacing criteria removes all old criterion-note links."""
        db["add_criterion"](type="relevancy", name="Old", gate="old gate")
        db["register_entity"](data={"name": "Test", "url": "https://test.com", "modes": ["example"]})
        db["add_notes"](entity_id="e1", notes=["Has 100 stars"])
        db["link_criterion_note"](criterion_id="c1", note_id="n1", quality="pass")

        # Replace all criteria — old links should cascade delete
        db["set_criteria"](criteria=[
            {"type": "relevancy", "name": "New", "gate": "new gate"},
        ])

        # The old link should be gone (c1 was deleted and replaced by new c1)
        conn = sqlite3.connect(db["path"])
        links = conn.execute("SELECT COUNT(*) FROM criteria_notes").fetchone()[0]
        conn.close()
        assert links == 0


class TestCriteriaNoteLinks:
    """Linking criteria to entity notes with quality."""

    def _seed(self, db):
        db["add_criterion"](type="relevancy", name="Adoption", gate=">=50 stars")
        db["add_criterion"](type="hardline", name="Open source", gate="OSI license")
        db["register_entity"](data={"name": "Tool A", "url": "https://a.com", "modes": ["example"]})
        db["add_notes"](entity_id="e1", notes=["Has 200 stars on GitHub", "MIT license"])

    def test_link_criterion_note(self, db):
        self._seed(db)
        result = parse(db["link_criterion_note"](criterion_id="c1", note_id="n1", quality="pass"))
        assert "Linked c1 to n1" in result

    def test_link_quality_check_constraint(self, db):
        self._seed(db)
        result = parse(db["link_criterion_note"](criterion_id="c1", note_id="n1", quality="maybe"))
        assert "error" in result or "CHECK" in str(result)

    def test_unlink_criterion_note(self, db):
        self._seed(db)
        db["link_criterion_note"](criterion_id="c1", note_id="n1", quality="pass")
        result = parse(db["unlink_criterion_note"](criterion_id="c1", note_id="n1"))
        assert "Unlinked" in result

    def test_clear_criterion_links(self, db):
        self._seed(db)
        db["link_criterion_note"](criterion_id="c1", note_id="n1", quality="pass")
        db["link_criterion_note"](criterion_id="c1", note_id="n2", quality="pass")
        result = parse(db["clear_criterion_links"](criterion_id="c1"))
        assert "Cleared 2 links" in result

    def test_link_replaces_existing_quality(self, db):
        """INSERT OR REPLACE updates quality on same criterion-note pair."""
        self._seed(db)
        db["link_criterion_note"](criterion_id="c1", note_id="n1", quality="fail")
        db["link_criterion_note"](criterion_id="c1", note_id="n1", quality="pass")

        conn = sqlite3.connect(db["path"])
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT quality FROM criteria_notes WHERE criterion_id='c1' AND note_id='n1'"
        ).fetchone()
        conn.close()
        assert row["quality"] == "pass"


class TestCascadeBehavior:
    """ON DELETE CASCADE from criteria and entity_notes to criteria_notes."""

    def _seed(self, db):
        db["add_criterion"](type="relevancy", name="Adoption", gate=">=50 stars")
        db["register_entity"](data={"name": "Tool", "url": "https://tool.com", "modes": ["example"]})
        db["add_notes"](entity_id="e1", notes=["Has 200 stars"])
        db["link_criterion_note"](criterion_id="c1", note_id="n1", quality="pass")

    def _count_links(self, db):
        conn = sqlite3.connect(db["path"])
        count = conn.execute("SELECT COUNT(*) FROM criteria_notes").fetchone()[0]
        conn.close()
        return count

    def test_delete_criterion_cascades_links(self, db):
        self._seed(db)
        assert self._count_links(db) == 1
        db["remove_criterion"](criterion_id="c1")
        assert self._count_links(db) == 0

    def test_delete_note_cascades_links(self, db):
        self._seed(db)
        assert self._count_links(db) == 1
        db["remove_notes"](entity_id="e1", note_ids=["n1"])
        assert self._count_links(db) == 0

    def test_clear_notes_cascades_links(self, db):
        self._seed(db)
        db["add_notes"](entity_id="e1", notes=["Second note"])
        db["link_criterion_note"](criterion_id="c1", note_id="n2", quality="fail")
        assert self._count_links(db) == 2
        db["clear_notes"](entity_id="e1")
        assert self._count_links(db) == 0

    def test_stage_downgrade_cascades_through_notes(self, db):
        """Stage downgrade from researched deletes notes, which cascades to criteria links."""
        self._seed(db)
        db["set_stage"](entity_id="e1", stage="researched")
        assert self._count_links(db) == 1

        # Downgrade to new — _enforce_stage deletes notes
        db["set_stage"](entity_id="e1", stage="new")
        assert self._count_links(db) == 0


class TestAssessment:
    """Computed assessment from criterion-note links."""

    def _seed_criteria(self, db):
        db["set_criteria"](criteria=[
            {"type": "hardline", "name": "Open source", "gate": "OSI license"},
            {"type": "relevancy", "name": "Adoption", "gate": ">=50 stars"},
            {"type": "relevancy", "name": "Stable", "gate": "Versioned releases"},
            {"type": "relevancy", "name": "Lifecycle", "gate": "Launch, stop, or resume"},
        ])
        db["register_entity"](data={"name": "Tool", "url": "https://tool.com", "modes": ["example"]})
        db["add_notes"](entity_id="e1", notes=[
            "MIT license",
            "1800 stars on GitHub",
            "v2.1.0 released last week",
            "Supports launch and resume",
        ])

    def test_get_assessment_no_criteria(self, db):
        db["register_entity"](data={"name": "Tool", "url": "https://tool.com"})
        result = parse(db["get_assessment"](entity_id="e1"))
        assert "No criteria defined" in result

    def test_get_assessment_no_links(self, db):
        self._seed_criteria(db)
        result = parse(db["get_assessment"](entity_id="e1"))
        assert "No linked notes" in result
        assert "Relevancy: 0/3" in result

    def test_assessment_pass(self, db):
        self._seed_criteria(db)
        db["link_criterion_note"](criterion_id="c2", note_id="n2", quality="pass")
        result = parse(db["get_assessment"](entity_id="e1"))
        assert "PASS" in result
        assert "Relevancy: 1/3" in result

    def test_assessment_fail(self, db):
        self._seed_criteria(db)
        db["link_criterion_note"](criterion_id="c2", note_id="n2", quality="fail")
        result = parse(db["get_assessment"](entity_id="e1"))
        assert "[x]" in result  # fail icon for c2
        assert "[fail] n2" in result

    def test_pass_supersedes_fail(self, db):
        """Same criterion has both pass and fail links for entity — pass wins."""
        self._seed_criteria(db)
        db["link_criterion_note"](criterion_id="c2", note_id="n1", quality="fail")
        db["link_criterion_note"](criterion_id="c2", note_id="n2", quality="pass")
        result = parse(db["get_assessment"](entity_id="e1"))
        # c2 should show as PASS despite having a fail link too
        assert "Relevancy: 1/3" in result

    def test_hardline_failure(self, db):
        self._seed_criteria(db)
        db["link_criterion_note"](criterion_id="c1", note_id="n1", quality="fail")
        result = parse(db["get_assessment"](entity_id="e1"))
        assert "Hardline: FAIL" in result
        assert "Open source" in result

    def test_relevancy_count(self, db):
        self._seed_criteria(db)
        db["link_criterion_note"](criterion_id="c2", note_id="n2", quality="pass")
        db["link_criterion_note"](criterion_id="c3", note_id="n3", quality="pass")
        db["link_criterion_note"](criterion_id="c4", note_id="n4", quality="pass")
        result = parse(db["get_assessment"](entity_id="e1"))
        assert "Relevancy: 3/3" in result

    def test_compute_relevance_updates_entity(self, db):
        self._seed_criteria(db)
        db["link_criterion_note"](criterion_id="c2", note_id="n2", quality="pass")
        db["link_criterion_note"](criterion_id="c3", note_id="n3", quality="pass")

        result = parse(db["compute_relevance"](entity_id="e1"))
        assert "→ 2" in result or "= 2" in result

        # Verify the entity's cached relevance was updated
        entity = parse(db["get_entity"](entity_id="e1"))
        assert "Relevance: 2" in entity


class TestMergeInteraction:
    """Criteria links survive entity merge (notes change owner, keep ID)."""

    def test_merge_preserves_criteria_links(self, db):
        db["add_criterion"](type="relevancy", name="Adoption", gate=">=50 stars")

        db["register_entity"](data={"name": "Tool A", "url": "https://a.com", "modes": ["example"]})
        db["register_entity"](data={"name": "Tool B", "url": "https://b.com", "modes": ["example"]})
        db["add_notes"](entity_id="e1", notes=["A has 100 stars"])
        db["add_notes"](entity_id="e2", notes=["B has 200 stars"])
        db["link_criterion_note"](criterion_id="c1", note_id="n1", quality="pass")
        db["link_criterion_note"](criterion_id="c1", note_id="n2", quality="pass")

        # Merge e2 into e1 — notes move to e1, note IDs unchanged
        db["merge_entities"](entity_ids=["e1", "e2"])

        # Both criterion links should survive
        conn = sqlite3.connect(db["path"])
        links = conn.execute("SELECT COUNT(*) FROM criteria_notes WHERE criterion_id='c1'").fetchone()[0]
        conn.close()
        assert links == 2
