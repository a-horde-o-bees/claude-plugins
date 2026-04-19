"""Tests for criteria effectiveness computation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent.parent))

from skills.research._db import init_db, get_connection
from skills.research._effectiveness import get_criteria_effectiveness
from skills.research._entities import register_entity
from skills.research._criteria import register_criteria, link_criterion_note
from skills.research._notes import upsert_notes as add_notes


def _setup(tmp_path):
    db_path = str(tmp_path / "test.db")
    init_db(db_path)
    return db_path


def _seed(db):
    """Create criteria, entities, notes, and links for effectiveness testing."""
    register_criteria(db, [
        {"type": "hardline", "name": "Open source", "gate": "Source code publicly available"},
        {"type": "hardline", "name": "Consumer feasible", "gate": "Runs on consumer hardware"},
        {"type": "relevancy", "name": "Has loops", "gate": "System iterates"},
        {"type": "relevancy", "name": "Has convergence", "gate": "Detects when done"},
        {"type": "relevancy", "name": "Untriggered", "gate": "No entity should match this"},
    ])

    # Entity 1: passes everything, high relevance
    register_entity(db, "Good Tool", url="https://good.dev", modes=["example"], relevance=5)
    add_notes(db, "e1", ["Open source MIT", "Runs locally", "Has iterative loop", "Detects convergence"])
    link_criterion_note(db, "c1", "n1", "pass")  # open source
    link_criterion_note(db, "c2", "n2", "pass")  # consumer feasible
    link_criterion_note(db, "c3", "n3", "pass")  # has loops
    link_criterion_note(db, "c4", "n4", "pass")  # has convergence

    # Entity 2: fails consumer feasible, rejected
    register_entity(db, "Heavy Tool", url="https://heavy.dev", modes=["example"], relevance=-1)
    add_notes(db, "e2", ["Open source", "Requires 4 GPUs"])
    link_criterion_note(db, "c1", "n5", "pass")  # open source
    link_criterion_note(db, "c2", "n6", "fail")  # consumer feasible fails

    conn = get_connection(db)
    conn.execute("UPDATE entities SET stage = 'researched' WHERE id = 'e1'")
    conn.execute("UPDATE entities SET stage = 'rejected' WHERE id = 'e2'")
    conn.commit()
    conn.close()


class TestEffectiveness:
    def test_basic_output(self, tmp_path):
        db = _setup(tmp_path)
        _seed(db)
        result = get_criteria_effectiveness(db)
        assert "5 criteria" in result
        assert "Has loops" in result
        assert "Has convergence" in result

    def test_pass_fail_counts(self, tmp_path):
        db = _setup(tmp_path)
        _seed(db)
        result = get_criteria_effectiveness(db)
        # Open source: 2 passes (e1 and e2)
        assert "Open source: pass=2" in result
        # Consumer feasible: 1 pass (e1), 1 fail (e2)
        assert "Consumer feasible: pass=1, fail=1" in result

    def test_untriggered(self, tmp_path):
        db = _setup(tmp_path)
        _seed(db)
        result = get_criteria_effectiveness(db)
        assert "Untriggered criteria" in result
        assert "Untriggered" in result.split("Untriggered criteria")[1]

    def test_hardline_rejection_distribution(self, tmp_path):
        db = _setup(tmp_path)
        _seed(db)
        result = get_criteria_effectiveness(db)
        assert "Hardline rejection distribution" in result
        assert "Consumer feasible" in result.split("Hardline rejection")[1]

    def test_no_criteria(self, tmp_path):
        db = _setup(tmp_path)
        result = get_criteria_effectiveness(db)
        assert "No criteria defined" in result

    def test_discrimination(self, tmp_path):
        db = _setup(tmp_path)
        _seed(db)
        result = get_criteria_effectiveness(db)
        assert "Discrimination" in result
