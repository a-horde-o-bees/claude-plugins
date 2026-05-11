"""Unit tests for edges — depends_on, addresses, component_paths — plus wiring rules."""

import pytest

from systems.needs_map import _edges, _entities


@pytest.fixture
def seeded(conn):
    """Two components and a refined need for basic edge tests."""
    c1 = _entities.add_component(conn, "c1-desc")
    c2 = _entities.add_component(conn, "c2-desc")
    root = _entities.add_need(conn, "root")
    leaf = _entities.refine(conn, root, "leaf")
    return {"c1": c1, "c2": c2, "root": root, "leaf": leaf}


class TestDepend:
    def test_records_edge(self, conn, seeded):
        _edges.depend(conn, seeded["c1"], seeded["c2"])
        row = conn.execute(
            "SELECT COUNT(*) FROM depends_on"
        ).fetchone()[0]
        assert row == 1

    def test_rejects_self_loop(self, conn, seeded):
        with pytest.raises(ValueError, match="itself"):
            _edges.depend(conn, seeded["c1"], seeded["c1"])

    def test_rejects_cycle(self, conn, seeded):
        _edges.depend(conn, seeded["c1"], seeded["c2"])
        with pytest.raises(ValueError, match="cycle"):
            _edges.depend(conn, seeded["c2"], seeded["c1"])

    def test_rejects_duplicate(self, conn, seeded):
        _edges.depend(conn, seeded["c1"], seeded["c2"])
        with pytest.raises(ValueError, match="already exists"):
            _edges.depend(conn, seeded["c1"], seeded["c2"])

    def test_rejects_unknown_component(self, conn, seeded):
        with pytest.raises(LookupError, match="c99"):
            _edges.depend(conn, "c99", seeded["c1"])


class TestUndepend:
    def test_removes_edge(self, conn, seeded):
        _edges.depend(conn, seeded["c1"], seeded["c2"])
        _edges.undepend(conn, seeded["c1"], seeded["c2"])
        assert conn.execute(
            "SELECT COUNT(*) FROM depends_on"
        ).fetchone()[0] == 0

    def test_raises_on_missing(self, conn, seeded):
        with pytest.raises(LookupError, match="dependency"):
            _edges.undepend(conn, seeded["c1"], seeded["c2"])


class TestAddress:
    def test_records_edge(self, conn, seeded):
        _edges.address(conn, seeded["c1"], seeded["leaf"], "direct hit")
        row = conn.execute(
            "SELECT rationale FROM addresses"
        ).fetchone()
        assert row[0] == "direct hit"

    def test_strips_rationale(self, conn, seeded):
        _edges.address(conn, seeded["c1"], seeded["leaf"], "  hit  ")
        row = conn.execute(
            "SELECT rationale FROM addresses"
        ).fetchone()
        assert row[0] == "hit"

    def test_refuses_root(self, conn, seeded):
        with pytest.raises(ValueError, match="root"):
            _edges.address(conn, seeded["c1"], seeded["root"], "hit")

    def test_refuses_empty_rationale(self, conn, seeded):
        with pytest.raises(ValueError, match="rationale"):
            _edges.address(conn, seeded["c1"], seeded["leaf"], "")

    def test_refuses_whitespace_rationale(self, conn, seeded):
        with pytest.raises(ValueError, match="rationale"):
            _edges.address(conn, seeded["c1"], seeded["leaf"], "   ")

    def test_refuses_ancestor_conflict(self, conn, seeded):
        grandchild = _entities.refine(conn, seeded["leaf"], "grandchild")
        _edges.address(conn, seeded["c1"], seeded["leaf"], "hit")
        with pytest.raises(ValueError, match="ancestor"):
            _edges.address(conn, seeded["c1"], grandchild, "hit2")

    def test_refuses_descendant_conflict(self, conn, seeded):
        grandchild = _entities.refine(conn, seeded["leaf"], "grandchild")
        _edges.address(conn, seeded["c1"], grandchild, "hit")
        with pytest.raises(ValueError, match="descendant"):
            _edges.address(conn, seeded["c1"], seeded["leaf"], "hit2")

    def test_allows_cross_component_same_need(self, conn, seeded):
        """Different components can address the same need through different mechanisms."""
        _edges.address(conn, seeded["c1"], seeded["leaf"], "mechanism A")
        _edges.address(conn, seeded["c2"], seeded["leaf"], "mechanism B")
        assert conn.execute(
            "SELECT COUNT(*) FROM addresses"
        ).fetchone()[0] == 2

    def test_refuses_duplicate(self, conn, seeded):
        _edges.address(conn, seeded["c1"], seeded["leaf"], "hit")
        with pytest.raises(ValueError, match="already exists"):
            _edges.address(conn, seeded["c1"], seeded["leaf"], "hit again")


class TestUnaddress:
    def test_removes_edge(self, conn, seeded):
        _edges.address(conn, seeded["c1"], seeded["leaf"], "hit")
        _edges.unaddress(conn, seeded["c1"], seeded["leaf"])
        assert conn.execute(
            "SELECT COUNT(*) FROM addresses"
        ).fetchone()[0] == 0

    def test_raises_on_missing(self, conn, seeded):
        with pytest.raises(LookupError, match="addressing"):
            _edges.unaddress(conn, seeded["c1"], seeded["leaf"])


class TestSetRationale:
    def test_updates(self, conn, seeded):
        _edges.address(conn, seeded["c1"], seeded["leaf"], "old")
        _edges.set_rationale(conn, seeded["c1"], seeded["leaf"], "new")
        row = conn.execute(
            "SELECT rationale FROM addresses"
        ).fetchone()
        assert row[0] == "new"

    def test_refuses_empty(self, conn, seeded):
        _edges.address(conn, seeded["c1"], seeded["leaf"], "old")
        with pytest.raises(ValueError, match="empty"):
            _edges.set_rationale(conn, seeded["c1"], seeded["leaf"], "")

    def test_raises_on_missing_edge(self, conn, seeded):
        with pytest.raises(LookupError, match="not found"):
            _edges.set_rationale(conn, seeded["c1"], seeded["leaf"], "x")


class TestAddPath:
    def test_records(self, conn, seeded):
        _edges.add_path(conn, seeded["c1"], "src/foo.py")
        row = conn.execute(
            "SELECT path FROM component_paths"
        ).fetchone()
        assert row[0] == "src/foo.py"

    def test_rejects_duplicate(self, conn, seeded):
        _edges.add_path(conn, seeded["c1"], "src/foo.py")
        with pytest.raises(ValueError, match="already"):
            _edges.add_path(conn, seeded["c1"], "src/foo.py")

    def test_rejects_unknown_component(self, conn):
        with pytest.raises(LookupError, match="c99"):
            _edges.add_path(conn, "c99", "src/foo.py")


class TestRemovePath:
    def test_deletes(self, conn, seeded):
        _edges.add_path(conn, seeded["c1"], "src/foo.py")
        _edges.remove_path(conn, seeded["c1"], "src/foo.py")
        assert conn.execute(
            "SELECT COUNT(*) FROM component_paths"
        ).fetchone()[0] == 0

    def test_raises_on_missing(self, conn, seeded):
        with pytest.raises(LookupError, match="path"):
            _edges.remove_path(conn, seeded["c1"], "src/foo.py")
