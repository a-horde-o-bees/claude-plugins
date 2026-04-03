"""Tests for coverage computation and domain/goal management."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent.parent))

from skills.research._db import init_db
from skills.research._coverage import (
    add_domain,
    add_goal,
    get_coverage,
    get_domains,
    get_goals,
    link_domain_criterion,
    link_goal_domain,
    register_domains,
    register_goals,
    remove_domain,
    remove_goal,
    unlink_domain_criterion,
)
from skills.research._entities import register_entity
from skills.research._criteria import register_criteria, link_criterion_note
from skills.research._notes import upsert_notes as add_notes
from skills.research._db import get_connection


def _setup(tmp_path):
    db_path = str(tmp_path / "test.db")
    init_db(db_path)
    return db_path


class TestDomainCRUD:
    def test_add_and_list(self, tmp_path):
        db = _setup(tmp_path)
        add_domain(db, "Loop Patterns", "Autonomous iteration structures")
        add_domain(db, "Convergence", "Stopping criteria")
        result = get_domains(db)
        assert "Loop Patterns" in result
        assert "Convergence" in result
        assert "2 criteria" not in result  # no criteria linked yet

    def test_register_replaces_all(self, tmp_path):
        db = _setup(tmp_path)
        add_domain(db, "Old Domain")
        register_domains(db, [{"name": "New A"}, {"name": "New B"}])
        result = get_domains(db)
        assert "Old Domain" not in result
        assert "New A" in result
        assert "New B" in result

    def test_remove(self, tmp_path):
        db = _setup(tmp_path)
        result = add_domain(db, "Temporary")
        domain_id = result.split("id: ")[1].rstrip(")")
        remove_domain(db, domain_id)
        result = get_domains(db)
        assert "Temporary" not in result


class TestGoalCRUD:
    def test_add_and_list(self, tmp_path):
        db = _setup(tmp_path)
        add_goal(db, "Cycle-level autonomy", "Run without human gating")
        result = get_goals(db)
        assert "Cycle-level autonomy" in result

    def test_register_replaces_all(self, tmp_path):
        db = _setup(tmp_path)
        add_goal(db, "Old Goal")
        register_goals(db, [{"name": "Goal A"}, {"name": "Goal B"}])
        result = get_goals(db)
        assert "Old Goal" not in result
        assert "Goal A" in result

    def test_remove(self, tmp_path):
        db = _setup(tmp_path)
        result = add_goal(db, "Temporary")
        goal_id = result.split("id: ")[1].rstrip(")")
        remove_goal(db, goal_id)
        result = get_goals(db)
        assert "Temporary" not in result


class TestJunctions:
    def test_link_domain_criterion(self, tmp_path):
        db = _setup(tmp_path)
        add_domain(db, "Test Domain")
        register_criteria(db, [{"type": "relevancy", "name": "Has loops", "gate": "System iterates"}])
        link_domain_criterion(db, "d1", "c1")
        result = get_domains(db)
        assert "1 criteria" in result

    def test_unlink_domain_criterion(self, tmp_path):
        db = _setup(tmp_path)
        add_domain(db, "Test Domain")
        register_criteria(db, [{"type": "relevancy", "name": "Has loops", "gate": "System iterates"}])
        link_domain_criterion(db, "d1", "c1")
        unlink_domain_criterion(db, "d1", "c1")
        result = get_domains(db)
        assert "0 criteria" in result

    def test_link_goal_domain(self, tmp_path):
        db = _setup(tmp_path)
        add_goal(db, "Autonomy")
        add_domain(db, "Loop Patterns")
        link_goal_domain(db, "g1", "d1")
        result = get_goals(db)
        assert "1 domains" in result

    def test_cascade_delete_domain(self, tmp_path):
        """Removing domain cascades to junction tables."""
        db = _setup(tmp_path)
        add_domain(db, "Doomed")
        add_goal(db, "Goal")
        register_criteria(db, [{"type": "relevancy", "name": "C1", "gate": "test"}])
        link_domain_criterion(db, "d1", "c1")
        link_goal_domain(db, "g1", "d1")
        remove_domain(db, "d1")
        # Goal should show 0 domains
        result = get_goals(db)
        assert "0 domains" in result

    def test_cascade_delete_goal(self, tmp_path):
        """Removing goal cascades to goal_domains junction."""
        db = _setup(tmp_path)
        add_goal(db, "Doomed")
        add_domain(db, "Domain")
        link_goal_domain(db, "g1", "d1")
        remove_goal(db, "g1")
        # Verify junction is clean
        conn = get_connection(db)
        count = conn.execute("SELECT COUNT(*) as c FROM goal_domains").fetchone()["c"]
        conn.close()
        assert count == 0


class TestCoverage:
    def _seed(self, db):
        """Create domains, criteria, entities, notes, and links for coverage testing."""
        # Domains
        add_domain(db, "Loop Patterns")
        add_domain(db, "Convergence")

        # Criteria
        register_criteria(db, [
            {"type": "relevancy", "name": "Has loops", "gate": "System iterates"},
            {"type": "relevancy", "name": "Detects convergence", "gate": "Stops when done"},
        ])

        # Link domains to criteria
        link_domain_criterion(db, "d1", "c1")  # Loop Patterns → Has loops
        link_domain_criterion(db, "d2", "c2")  # Convergence → Detects convergence

        # Entity with notes
        register_entity(db, "Tool A", url="https://tool-a.dev", modes=["example"])
        add_notes(db, "e1", ["Implements iterative loop", "Uses keep/discard pattern"])

        # Link criterion to note (pass)
        link_criterion_note(db, "c1", "n1", "pass")

        # Advance to researched
        conn = get_connection(db)
        conn.execute("UPDATE entities SET stage = 'researched' WHERE id = 'e1'")
        conn.commit()
        conn.close()

    def test_coverage_with_data(self, tmp_path):
        db = _setup(tmp_path)
        self._seed(db)
        result = get_coverage(db)
        assert "Loop Patterns: 1 researched" in result
        assert "Convergence: 0 researched" in result

    def test_coverage_empty(self, tmp_path):
        db = _setup(tmp_path)
        result = get_coverage(db)
        assert "No domains" not in result  # returns header even with no domains
        # Actually with no domains, the query returns empty
        assert "Coverage by domain:" in result

    def test_entity_pool(self, tmp_path):
        db = _setup(tmp_path)
        self._seed(db)
        # Add an unresearched entity
        register_entity(db, "Tool B", url="https://tool-b.dev", modes=["example"])
        result = get_coverage(db)
        assert "Unresearched: 1" in result
        assert "Researched: 1" in result

    def test_distinct_counts(self, tmp_path):
        """Entity linked through multiple criteria in same domain counted once."""
        db = _setup(tmp_path)
        add_domain(db, "Multi-Criteria Domain")
        register_criteria(db, [
            {"type": "relevancy", "name": "C1", "gate": "test1"},
            {"type": "relevancy", "name": "C2", "gate": "test2"},
        ])
        link_domain_criterion(db, "d1", "c1")
        link_domain_criterion(db, "d1", "c2")

        register_entity(db, "Tool", url="https://tool.dev", modes=["example"])
        add_notes(db, "e1", ["Fact about C1", "Fact about C2"])
        link_criterion_note(db, "c1", "n1", "pass")
        link_criterion_note(db, "c2", "n2", "pass")

        conn = get_connection(db)
        conn.execute("UPDATE entities SET stage = 'researched' WHERE id = 'e1'")
        conn.commit()
        conn.close()

        result = get_coverage(db)
        # Should say 1 entity, not 2
        assert "1 researched entities" in result
