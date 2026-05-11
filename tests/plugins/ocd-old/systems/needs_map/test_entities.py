"""Unit tests for component and need CRUD plus validation."""

import pytest

from systems.needs_map import _entities


class TestAddComponent:
    def test_returns_auto_id(self, conn):
        cid = _entities.add_component(conn, "first")
        assert cid == "c1"

    def test_persists_description(self, conn):
        cid = _entities.add_component(conn, "first")
        row = conn.execute(
            "SELECT description FROM components WHERE id = ?", (cid,)
        ).fetchone()
        assert row[0] == "first"

    def test_sequential_ids(self, conn):
        assert _entities.add_component(conn, "a") == "c1"
        assert _entities.add_component(conn, "b") == "c2"


class TestSetComponent:
    def test_updates_description(self, conn):
        cid = _entities.add_component(conn, "first")
        _entities.set_component(conn, cid, "second")
        row = conn.execute(
            "SELECT description FROM components WHERE id = ?", (cid,)
        ).fetchone()
        assert row[0] == "second"

    def test_raises_on_unknown(self, conn):
        with pytest.raises(LookupError, match="c99"):
            _entities.set_component(conn, "c99", "x")


class TestRemoveComponent:
    def test_deletes_entity(self, conn):
        cid = _entities.add_component(conn, "first")
        _entities.remove_component(conn, cid)
        assert conn.execute(
            "SELECT COUNT(*) FROM components"
        ).fetchone()[0] == 0

    def test_raises_on_unknown(self, conn):
        with pytest.raises(LookupError, match="c99"):
            _entities.remove_component(conn, "c99")


class TestAddNeed:
    def test_creates_root(self, conn):
        nid = _entities.add_need(conn, "root")
        row = conn.execute(
            "SELECT parent_id FROM needs WHERE id = ?", (nid,)
        ).fetchone()
        assert row[0] is None


class TestRefine:
    def test_creates_child(self, conn):
        parent = _entities.add_need(conn, "root")
        child = _entities.refine(conn, parent, "child")
        row = conn.execute(
            "SELECT parent_id FROM needs WHERE id = ?", (child,)
        ).fetchone()
        assert row[0] == parent

    def test_raises_on_unknown_parent(self, conn):
        with pytest.raises(LookupError, match="n99"):
            _entities.refine(conn, "n99", "child")


class TestSetNeed:
    def test_updates_description(self, conn):
        nid = _entities.add_need(conn, "old")
        _entities.set_need(conn, nid, "new")
        row = conn.execute(
            "SELECT description FROM needs WHERE id = ?", (nid,)
        ).fetchone()
        assert row[0] == "new"

    def test_raises_on_unknown(self, conn):
        with pytest.raises(LookupError, match="n99"):
            _entities.set_need(conn, "n99", "x")


class TestSetParent:
    def test_detach_to_root(self, conn):
        parent = _entities.add_need(conn, "parent")
        child = _entities.refine(conn, parent, "child")
        _entities.set_parent(conn, child, None)
        row = conn.execute(
            "SELECT parent_id FROM needs WHERE id = ?", (child,)
        ).fetchone()
        assert row[0] is None

    def test_reparent(self, conn):
        a = _entities.add_need(conn, "a")
        b = _entities.add_need(conn, "b")
        child = _entities.refine(conn, a, "child")
        _entities.set_parent(conn, child, b)
        row = conn.execute(
            "SELECT parent_id FROM needs WHERE id = ?", (child,)
        ).fetchone()
        assert row[0] == b

    def test_self_parent_rejected(self, conn):
        nid = _entities.add_need(conn, "x")
        with pytest.raises(ValueError, match="its own parent"):
            _entities.set_parent(conn, nid, nid)

    def test_cycle_rejected(self, conn):
        a = _entities.add_need(conn, "a")
        b = _entities.refine(conn, a, "b")
        with pytest.raises(ValueError, match="cycle"):
            _entities.set_parent(conn, a, b)


class TestRemoveNeed:
    def test_removes_leaf(self, conn):
        nid = _entities.add_need(conn, "x")
        _entities.remove_need(conn, nid)
        assert conn.execute("SELECT COUNT(*) FROM needs").fetchone()[0] == 0

    def test_refuses_with_children(self, conn):
        parent = _entities.add_need(conn, "parent")
        _entities.refine(conn, parent, "child")
        with pytest.raises(ValueError, match="child"):
            _entities.remove_need(conn, parent)

    def test_raises_on_unknown(self, conn):
        with pytest.raises(LookupError, match="n99"):
            _entities.remove_need(conn, "n99")


class TestValidate:
    def test_marks_component(self, conn):
        cid = _entities.add_component(conn, "x")
        kind = _entities.validate(conn, cid)
        assert kind == "components"
        row = conn.execute(
            "SELECT validated FROM components WHERE id = ?", (cid,)
        ).fetchone()
        assert row[0] == 1

    def test_marks_need(self, conn):
        nid = _entities.add_need(conn, "x")
        kind = _entities.validate(conn, nid)
        assert kind == "needs"
        row = conn.execute(
            "SELECT validated FROM needs WHERE id = ?", (nid,)
        ).fetchone()
        assert row[0] == 1

    def test_raises_on_unknown(self, conn):
        with pytest.raises(LookupError, match="x99"):
            _entities.validate(conn, "x99")


class TestInvalidate:
    def test_clears_component_validation(self, conn):
        cid = _entities.add_component(conn, "x")
        _entities.validate(conn, cid)
        _entities.invalidate(conn, cid)
        row = conn.execute(
            "SELECT validated FROM components WHERE id = ?", (cid,)
        ).fetchone()
        assert row[0] == 0

    def test_raises_on_unknown(self, conn):
        with pytest.raises(LookupError, match="x99"):
            _entities.invalidate(conn, "x99")
