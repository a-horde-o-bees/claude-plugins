"""Unit tests for analysis queries — coverage, tree retrieval, summary, uncovered."""

import pytest

from systems.needs_map import _edges, _entities, _queries


@pytest.fixture
def seeded(conn):
    """Two components, a root need, a leaf need — basic shape for tree queries."""
    c1 = _entities.add_component(conn, "c1-desc")
    c2 = _entities.add_component(conn, "c2-desc")
    root = _entities.add_need(conn, "root")
    leaf = _entities.refine(conn, root, "leaf")
    return {"c1": c1, "c2": c2, "root": root, "leaf": leaf}


class TestCoverage:
    def test_covered_direct(self, conn, seeded):
        _edges.address(conn, seeded["c1"], seeded["leaf"], "hit")
        status, addressers = _queries.coverage(conn, seeded["leaf"])
        assert status == "covered"
        assert addressers == [seeded["c1"]]

    def test_covered_via_descendant(self, conn, seeded):
        _edges.address(conn, seeded["c1"], seeded["leaf"], "hit")
        status, _addressers = _queries.coverage(conn, seeded["root"])
        assert status == "covered"

    def test_gap_on_unaddressed_leaf(self, conn, seeded):
        status, _ = _queries.coverage(conn, seeded["leaf"])
        assert status == "gap"

    def test_unrefined_on_root_no_children(self, conn):
        nid = _entities.add_need(conn, "root")
        status, _ = _queries.coverage(conn, nid)
        assert status == "unrefined"

    def test_abstract_on_interior_no_addressed_descendant(self, conn, seeded):
        status, _ = _queries.coverage(conn, seeded["root"])
        assert status == "abstract"


class TestComponentRow:
    def test_returns_row(self, conn, seeded):
        desc, validated = _queries.component_row(conn, seeded["c1"])
        assert desc == "c1-desc"
        assert validated == 0

    def test_raises_on_unknown(self, conn):
        with pytest.raises(LookupError, match="c99"):
            _queries.component_row(conn, "c99")


class TestNeedRow:
    def test_returns_row(self, conn, seeded):
        desc, validated, parent = _queries.need_row(conn, seeded["leaf"])
        assert desc == "leaf"
        assert validated == 0
        assert parent == seeded["root"]

    def test_root_parent_is_none(self, conn, seeded):
        _desc, _validated, parent = _queries.need_row(conn, seeded["root"])
        assert parent is None

    def test_raises_on_unknown(self, conn):
        with pytest.raises(LookupError, match="n99"):
            _queries.need_row(conn, "n99")


class TestDependencyRoots:
    def test_lists_components_with_no_dependents(self, conn, seeded):
        _edges.depend(conn, seeded["c1"], seeded["c2"])
        roots = _queries.dependency_roots(conn)
        ids = [r[0] for r in roots]
        assert seeded["c2"] in ids
        assert seeded["c1"] not in ids


class TestDependentsOf:
    def test_returns_dependents(self, conn, seeded):
        _edges.depend(conn, seeded["c1"], seeded["c2"])
        dependents = _queries.dependents_of(conn, seeded["c2"])
        assert [r[0] for r in dependents] == [seeded["c1"]]


class TestNeedRoots:
    def test_filters_to_roots(self, conn, seeded):
        roots = _queries.need_roots(conn)
        assert [r[0] for r in roots] == [seeded["root"]]


class TestNeedChildren:
    def test_returns_children(self, conn, seeded):
        children = _queries.need_children(conn, seeded["root"])
        assert [r[0] for r in children] == [seeded["leaf"]]


class TestDirectAddressers:
    def test_returns_addressers(self, conn, seeded):
        _edges.address(conn, seeded["c1"], seeded["leaf"], "why")
        rows = _queries.direct_addressers(conn, seeded["leaf"])
        assert len(rows) == 1
        assert rows[0][0] == seeded["c1"]
        assert rows[0][3] == "why"


class TestAddressedNeeds:
    def test_returns_addressed_needs(self, conn, seeded):
        _edges.address(conn, seeded["c1"], seeded["leaf"], "why")
        rows = _queries.addressed_needs(conn, seeded["c1"])
        assert len(rows) == 1
        assert rows[0][0] == seeded["leaf"]


class TestLeafGaps:
    def test_lists_unaddressed_leaves(self, conn, seeded):
        gaps = _queries.leaf_gaps(conn)
        assert [g[0] for g in gaps] == [seeded["leaf"]]

    def test_excludes_addressed(self, conn, seeded):
        _edges.address(conn, seeded["c1"], seeded["leaf"], "hit")
        assert _queries.leaf_gaps(conn) == []

    def test_excludes_roots(self, conn):
        _entities.add_need(conn, "root")
        assert _queries.leaf_gaps(conn) == []


class TestOrphans:
    def test_lists_components_addressing_nothing(self, conn, seeded):
        orphans = _queries.orphans(conn)
        ids = [r[0] for r in orphans]
        assert set(ids) == {seeded["c1"], seeded["c2"]}

    def test_excludes_addressing_components(self, conn, seeded):
        _edges.address(conn, seeded["c1"], seeded["leaf"], "hit")
        ids = [r[0] for r in _queries.orphans(conn)]
        assert seeded["c1"] not in ids


class TestAllNeeds:
    def test_returns_all_need_ids(self, conn, seeded):
        rows = _queries.all_needs(conn)
        assert {r[0] for r in rows} == {seeded["root"], seeded["leaf"]}


class TestComponentPaths:
    def test_returns_paths(self, conn, seeded):
        _edges.add_path(conn, seeded["c1"], "src/a.py")
        _edges.add_path(conn, seeded["c1"], "src/b.py")
        paths = _queries.component_paths(conn, seeded["c1"])
        assert paths == ["src/a.py", "src/b.py"]


class TestSummaryCounts:
    def test_reports_counts(self, conn, seeded):
        _edges.address(conn, seeded["c1"], seeded["leaf"], "hit")
        counts = _queries.summary_counts(conn)
        assert counts["components"] == 2
        assert counts["needs"] == 2
        assert counts["roots"] == 1
        assert counts["leaves"] == 1
        assert counts["addresses"] == 1
        assert counts["gaps"] == 0


class TestDependencyAncestors:
    def test_returns_transitive(self, conn):
        c1 = _entities.add_component(conn, "c1")
        c2 = _entities.add_component(conn, "c2")
        c3 = _entities.add_component(conn, "c3")
        _edges.depend(conn, c1, c2)
        _edges.depend(conn, c2, c3)
        ancestors = _queries.dependency_ancestors(conn, c1)
        ids = {r[0] for r in ancestors}
        assert ids == {c2, c3}


class TestAllComponentIds:
    def test_returns_ids(self, conn, seeded):
        ids = _queries.all_component_ids(conn)
        assert set(ids) == {seeded["c1"], seeded["c2"]}


class TestAllComponentPaths:
    def test_returns_all_paths(self, conn, seeded):
        _edges.add_path(conn, seeded["c1"], "src/a.py")
        _edges.add_path(conn, seeded["c2"], "src/b.py")
        paths = _queries.all_component_paths(conn)
        assert set(paths) == {"src/a.py", "src/b.py"}


class TestUncoveredFiles:
    def test_surfaces_git_tracked_not_in_paths(
        self, conn, seeded, project_dir, monkeypatch,
    ):
        """With git shimmed to return one tracked file, uncovered lists it when absent from paths."""
        import subprocess as real_subprocess

        def fake_run(cmd, **kwargs):
            class Result:
                def __init__(self, stdout, returncode=0, stderr=""):
                    self.stdout = stdout
                    self.returncode = returncode
                    self.stderr = stderr
            if cmd[:2] == ["git", "rev-parse"]:
                return Result(stdout=str(project_dir) + "\n")
            if cmd[:2] == ["git", "ls-files"]:
                return Result(stdout="src/covered.py\nsrc/uncovered.py\n")
            return real_subprocess.run(cmd, **kwargs)

        monkeypatch.setattr(
            "systems.needs_map._queries.subprocess.run", fake_run,
        )
        _edges.add_path(conn, seeded["c1"], "src/covered.py")
        result = _queries.uncovered_files(conn)
        assert result == ["src/uncovered.py"]

    def test_excludes_test_files(
        self, conn, project_dir, monkeypatch,
    ):
        """tests/ and test_*.py and conftest.py are filtered out."""
        def fake_run(cmd, **kwargs):
            class Result:
                def __init__(self, stdout, returncode=0, stderr=""):
                    self.stdout = stdout
                    self.returncode = returncode
                    self.stderr = stderr
            if cmd[:2] == ["git", "rev-parse"]:
                return Result(stdout=str(project_dir) + "\n")
            if cmd[:2] == ["git", "ls-files"]:
                return Result(
                    stdout="src/real.py\ntests/test_a.py\nsrc/test_b.py\nsrc/conftest.py\n"
                )
            return None

        monkeypatch.setattr(
            "systems.needs_map._queries.subprocess.run", fake_run,
        )
        result = _queries.uncovered_files(conn)
        assert result == ["src/real.py"]
