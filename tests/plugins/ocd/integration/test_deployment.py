"""Integration tests for per-system deployment layout.

Each plugin system's `_init.py` declares where its templates deploy
under `.claude/`. These tests exercise `init(force=True)` against a
disposable tmp project dir and assert the resulting layout matches the
canonical shape:

- Project-wide rules  → .claude/rules/<plugin>/<rule>.md           (flat)
- System-scoped rules → .claude/rules/<plugin>/systems/<system>.md (nested one level)
- Conventions         → .claude/conventions/<plugin>/<conv>.md     (flat)
- Patterns            → .claude/patterns/<plugin>/<pattern>.md     (flat)
- Log templates       → .claude/logs/<type>/_template.md           (by log type)

The separation between flat project-wide rules and `systems/`-nested
system-scoped rules prevents filename collisions while keeping the
source→deployed mapping intuitive — source `systems/<s>/rules/<s>.md`
lands at deployed `.claude/rules/<plugin>/systems/<s>.md`.
"""

import importlib
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest

import framework

OCD_PLUGIN_DIR = framework.get_plugin_root()


def _clear_plugin_modules() -> None:
    """Drop cached plugin-scoped imports so a fresh plugin context loads cleanly.

    Excludes `framework` — its classes (NotReadyError, etc.) are referenced
    by modules that may have been imported during pytest collection by
    other tests. Reloading framework creates a new class object, breaking
    `isinstance` checks in the held references.
    """
    prefixes = ("plugin", "systems")
    for key in list(sys.modules):
        root = key.split(".", 1)[0]
        if root in prefixes:
            del sys.modules[key]


def _run_all_inits(plugin_dir: Path) -> None:
    """Import and invoke every `systems/*/_init.py` with force=True."""
    _clear_plugin_modules()
    systems_dir = plugin_dir / "systems"
    added = [str(systems_dir), str(plugin_dir)]
    for entry in added:
        sys.path.insert(0, entry)
    try:
        for init_file in sorted(systems_dir.glob("*/_init.py")):
            system_name = init_file.parent.name
            mod = importlib.import_module(f"systems.{system_name}._init")
            if hasattr(mod, "init"):
                mod.init(force=True)
    finally:
        for entry in added:
            sys.path.remove(entry)
        _clear_plugin_modules()


@pytest.fixture
def deployed_tree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    """Run every ocd system init against a fresh tmp project dir."""
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    monkeypatch.setenv("CLAUDE_PLUGIN_ROOT", str(OCD_PLUGIN_DIR))
    _run_all_inits(OCD_PLUGIN_DIR)
    yield tmp_path


class TestProjectWideRules:
    """Foundational rules deploy flat under .claude/rules/<plugin>/."""

    def test_design_principles_deployed_flat(self, deployed_tree: Path) -> None:
        assert (deployed_tree / ".claude/rules/ocd/design-principles.md").is_file()

    def test_markdown_deployed_flat(self, deployed_tree: Path) -> None:
        assert (deployed_tree / ".claude/rules/ocd/markdown.md").is_file()

    def test_process_flow_notation_deployed_flat(self, deployed_tree: Path) -> None:
        assert (deployed_tree / ".claude/rules/ocd/process-flow-notation.md").is_file()

    def test_system_docs_deployed_flat(self, deployed_tree: Path) -> None:
        assert (deployed_tree / ".claude/rules/ocd/system-docs.md").is_file()

    def test_workflow_deployed_flat(self, deployed_tree: Path) -> None:
        assert (deployed_tree / ".claude/rules/ocd/workflow.md").is_file()


class TestSystemScopedRules:
    """System-contributed rules deploy under .claude/rules/<plugin>/systems/ flat."""

    def test_navigator_rule_under_systems(self, deployed_tree: Path) -> None:
        assert (deployed_tree / ".claude/rules/ocd/systems/navigator.md").is_file()

    def test_log_rule_under_systems(self, deployed_tree: Path) -> None:
        assert (deployed_tree / ".claude/rules/ocd/systems/log.md").is_file()

    def test_refactor_rule_under_systems(self, deployed_tree: Path) -> None:
        assert (deployed_tree / ".claude/rules/ocd/systems/refactor.md").is_file()

    def test_no_nested_navigator_subdir(self, deployed_tree: Path) -> None:
        assert not (deployed_tree / ".claude/rules/ocd/navigator").exists()

    def test_no_nested_log_subdir(self, deployed_tree: Path) -> None:
        assert not (deployed_tree / ".claude/rules/ocd/log").exists()


class TestConventions:
    """Conventions deploy flat under .claude/conventions/<plugin>/."""

    def test_python_convention_deployed(self, deployed_tree: Path) -> None:
        assert (deployed_tree / ".claude/conventions/ocd/python.md").is_file()

    def test_testing_convention_deployed(self, deployed_tree: Path) -> None:
        assert (deployed_tree / ".claude/conventions/ocd/testing.md").is_file()


class TestPatterns:
    """Patterns deploy flat under .claude/patterns/<plugin>/."""

    def test_mass_rename_pattern_deployed(self, deployed_tree: Path) -> None:
        assert (deployed_tree / ".claude/patterns/ocd/mass-rename.md").is_file()

    def test_worktree_isolation_pattern_deployed(self, deployed_tree: Path) -> None:
        assert (deployed_tree / ".claude/patterns/ocd/worktree-isolation.md").is_file()


class TestLogTemplates:
    """Log-type templates deploy under .claude/logs/<type>/."""

    @pytest.mark.parametrize("log_type", ["decision", "friction", "idea", "problem"])
    def test_log_template_deployed(self, deployed_tree: Path, log_type: str) -> None:
        assert (deployed_tree / f".claude/logs/{log_type}/_template.md").is_file()
