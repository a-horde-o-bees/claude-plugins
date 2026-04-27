"""Per-verb CLI smoke tests exercising every subcommand end-to-end."""

import sys

import pytest

from systems import setup
from tools import environment

from systems.needs_map import _init, __main__ as cli


@pytest.fixture(autouse=True)
def plugin_root_shim(project_dir, monkeypatch):
    """Stub plugin root and initialize the DB for every CLI test."""
    monkeypatch.setattr(setup, "get_plugin_name", lambda _root: "ocd")
    plugin_root = project_dir.parent / "plugin"
    plugin_root.mkdir(exist_ok=True)
    monkeypatch.setattr(environment, "get_plugin_root", lambda: plugin_root)
    _init.init()
    return plugin_root


def _run(monkeypatch, *argv) -> None:
    """Invoke the CLI with the given argv tail (after the program name)."""
    monkeypatch.setattr(sys, "argv", ["needs-map", *argv])
    cli.main()


class TestComponentVerbs:
    def test_add_component(self, monkeypatch, capsys):
        _run(monkeypatch, "add-component", "first", "component")
        out = capsys.readouterr().out
        assert "[c1]" in out and "first component" in out

    def test_set_component(self, monkeypatch, capsys):
        _run(monkeypatch, "add-component", "a")
        _run(monkeypatch, "set-component", "c1", "updated", "text")
        out = capsys.readouterr().out
        assert "updated text" in out

    def test_remove_component(self, monkeypatch, capsys):
        _run(monkeypatch, "add-component", "a")
        _run(monkeypatch, "remove-component", "c1")
        out = capsys.readouterr().out
        assert "Removed" in out


class TestNeedVerbs:
    def test_add_need(self, monkeypatch, capsys):
        _run(monkeypatch, "add-need", "root", "need")
        out = capsys.readouterr().out
        assert "[n1]" in out

    def test_refine(self, monkeypatch, capsys):
        _run(monkeypatch, "add-need", "root")
        _run(monkeypatch, "refine", "n1", "child", "need")
        out = capsys.readouterr().out
        assert "child need" in out

    def test_set_need(self, monkeypatch, capsys):
        _run(monkeypatch, "add-need", "old")
        _run(monkeypatch, "set-need", "n1", "new", "desc")
        out = capsys.readouterr().out
        assert "new desc" in out

    def test_set_parent_detach(self, monkeypatch, capsys):
        _run(monkeypatch, "add-need", "a")
        _run(monkeypatch, "add-need", "b")
        _run(monkeypatch, "refine", "n1", "child")
        _run(monkeypatch, "set-parent", "n3", "root")
        out = capsys.readouterr().out
        assert "root" in out

    def test_set_parent_to_other(self, monkeypatch, capsys):
        _run(monkeypatch, "add-need", "a")
        _run(monkeypatch, "add-need", "b")
        _run(monkeypatch, "refine", "n1", "child")
        _run(monkeypatch, "set-parent", "n3", "n2")
        out = capsys.readouterr().out
        assert "child of n2" in out

    def test_remove_need(self, monkeypatch, capsys):
        _run(monkeypatch, "add-need", "x")
        _run(monkeypatch, "remove-need", "n1")
        out = capsys.readouterr().out
        assert "Removed" in out


class TestEdgeVerbs:
    @pytest.fixture(autouse=True)
    def _seed(self, monkeypatch):
        _run(monkeypatch, "add-component", "c1-desc")
        _run(monkeypatch, "add-component", "c2-desc")
        _run(monkeypatch, "add-need", "root")
        _run(monkeypatch, "refine", "n1", "leaf")

    def test_depend(self, monkeypatch, capsys):
        _run(monkeypatch, "depend", "c1", "c2")
        out = capsys.readouterr().out
        assert "depends on c2" in out

    def test_undepend(self, monkeypatch, capsys):
        _run(monkeypatch, "depend", "c1", "c2")
        _run(monkeypatch, "undepend", "c1", "c2")
        out = capsys.readouterr().out
        assert "Removed" in out

    def test_address(self, monkeypatch, capsys):
        _run(monkeypatch, "address", "c1", "n2", "direct", "hit")
        out = capsys.readouterr().out
        assert "c1 → n2" in out
        assert "direct hit" in out

    def test_unaddress(self, monkeypatch, capsys):
        _run(monkeypatch, "address", "c1", "n2", "hit")
        _run(monkeypatch, "unaddress", "c1", "n2")
        out = capsys.readouterr().out
        assert "Removed" in out

    def test_set_rationale(self, monkeypatch, capsys):
        _run(monkeypatch, "address", "c1", "n2", "old")
        _run(monkeypatch, "set-rationale", "c1", "n2", "new", "one")
        out = capsys.readouterr().out
        assert "new one" in out

    def test_add_path(self, monkeypatch, capsys):
        _run(monkeypatch, "add-path", "c1", "src/foo.py")
        out = capsys.readouterr().out
        assert "src/foo.py" in out

    def test_remove_path(self, monkeypatch, capsys):
        _run(monkeypatch, "add-path", "c1", "src/foo.py")
        _run(monkeypatch, "remove-path", "c1", "src/foo.py")
        out = capsys.readouterr().out
        assert "Removed" in out


class TestValidationVerbs:
    @pytest.fixture(autouse=True)
    def _seed(self, monkeypatch):
        _run(monkeypatch, "add-component", "c1-desc")

    def test_validate(self, monkeypatch, capsys):
        _run(monkeypatch, "validate", "c1")
        out = capsys.readouterr().out
        assert "Validated" in out

    def test_invalidate(self, monkeypatch, capsys):
        _run(monkeypatch, "validate", "c1")
        _run(monkeypatch, "invalidate", "c1")
        out = capsys.readouterr().out
        assert "Invalidated" in out


class TestAnalysisVerbs:
    @pytest.fixture(autouse=True)
    def _seed(self, monkeypatch):
        _run(monkeypatch, "add-component", "c1-desc")
        _run(monkeypatch, "add-component", "c2-desc")
        _run(monkeypatch, "add-need", "root")
        _run(monkeypatch, "refine", "n1", "leaf")
        _run(monkeypatch, "depend", "c1", "c2")
        _run(monkeypatch, "address", "c1", "n2", "mechanism")
        _run(monkeypatch, "add-path", "c1", "src/foo.py")

    def test_dependencies(self, monkeypatch, capsys):
        capsys.readouterr()  # drop seed output
        _run(monkeypatch, "dependencies")
        out = capsys.readouterr().out
        assert "c1" in out and "c2" in out

    def test_dependencies_with_verify(self, monkeypatch, capsys):
        capsys.readouterr()
        _run(monkeypatch, "dependencies", "--verify")
        out = capsys.readouterr().out
        assert "c1" in out

    def test_dependencies_single(self, monkeypatch, capsys):
        capsys.readouterr()
        _run(monkeypatch, "dependencies", "c1")
        out = capsys.readouterr().out
        assert "c1" in out

    def test_needs(self, monkeypatch, capsys):
        capsys.readouterr()
        _run(monkeypatch, "needs")
        out = capsys.readouterr().out
        assert "root" in out and "leaf" in out

    def test_needs_rooted(self, monkeypatch, capsys):
        capsys.readouterr()
        _run(monkeypatch, "needs", "n1")
        out = capsys.readouterr().out
        assert "root" in out

    def test_addresses_all(self, monkeypatch, capsys):
        capsys.readouterr()
        _run(monkeypatch, "addresses")
        out = capsys.readouterr().out
        assert "c1" in out

    def test_addresses_gaps(self, monkeypatch, capsys):
        capsys.readouterr()
        _run(monkeypatch, "addresses", "--gaps")
        out = capsys.readouterr().out
        assert "gap" in out.lower() or "no gaps" in out.lower()

    def test_addresses_orphans(self, monkeypatch, capsys):
        capsys.readouterr()
        _run(monkeypatch, "addresses", "--orphans")
        out = capsys.readouterr().out
        assert "c2" in out  # c2 is orphan (addresses nothing)

    def test_addresses_entity(self, monkeypatch, capsys):
        capsys.readouterr()
        _run(monkeypatch, "addresses", "c1")
        out = capsys.readouterr().out
        assert "c1" in out

    def test_where(self, monkeypatch, capsys):
        capsys.readouterr()
        _run(monkeypatch, "where", "c1")
        out = capsys.readouterr().out
        assert "src/foo.py" in out

    def test_why(self, monkeypatch, capsys):
        capsys.readouterr()
        _run(monkeypatch, "why", "c1")
        out = capsys.readouterr().out
        assert "mechanism" in out

    def test_how(self, monkeypatch, capsys):
        capsys.readouterr()
        _run(monkeypatch, "how", "n2")
        out = capsys.readouterr().out
        assert "c1" in out and "mechanism" in out

    def test_compare(self, monkeypatch, capsys):
        capsys.readouterr()
        _run(monkeypatch, "compare", "c1", "c2")
        out = capsys.readouterr().out
        assert "c1" in out and "c2" in out

    def test_summary(self, monkeypatch, capsys):
        capsys.readouterr()
        _run(monkeypatch, "summary")
        out = capsys.readouterr().out
        assert "Components:" in out
        assert "Needs:" in out


class TestUncoveredVerb:
    def test_runs(self, monkeypatch, capsys, project_dir):
        import subprocess as real_subprocess
        real_run = real_subprocess.run

        def fake_run(cmd, **kwargs):
            class Result:
                def __init__(self, stdout, returncode=0, stderr=""):
                    self.stdout = stdout
                    self.returncode = returncode
                    self.stderr = stderr
            if cmd[:2] == ["git", "rev-parse"]:
                return Result(stdout=str(project_dir) + "\n")
            if cmd[:2] == ["git", "ls-files"]:
                return Result(stdout="src/a.py\n")
            return real_run(cmd, **kwargs)

        monkeypatch.setattr(
            "systems.needs_map._queries.subprocess.run", fake_run,
        )
        capsys.readouterr()
        _run(monkeypatch, "uncovered")
        out = capsys.readouterr().out
        assert "Uncovered" in out or "covered" in out


class TestErrorPaths:
    def test_unknown_component_exits_1(self, monkeypatch, capsys):
        with pytest.raises(SystemExit) as exc:
            _run(monkeypatch, "remove-component", "c99")
        assert exc.value.code == 1
        err = capsys.readouterr().err
        assert "c99" in err

    def test_wiring_rule_rejection_exits_1(self, monkeypatch, capsys):
        _run(monkeypatch, "add-component", "c1-desc")
        _run(monkeypatch, "add-need", "root")
        capsys.readouterr()
        with pytest.raises(SystemExit) as exc:
            _run(monkeypatch, "address", "c1", "n1", "hit")  # n1 is root
        assert exc.value.code == 1
        err = capsys.readouterr().err
        assert "root" in err.lower()
