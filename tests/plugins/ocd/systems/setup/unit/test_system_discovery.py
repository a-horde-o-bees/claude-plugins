"""Unit tests for setup._system_discovery.

Covers the deterministic scan behavior of _discover_systems (scans
`systems/*/__init__.py` for the per-system facade contract) and
_discover_workflow_skills (scans `systems/*/SKILL.md`). Both functions
must return sorted lists, skip directories that lack the sentinel
file, and handle missing parent directories gracefully.
"""

from pathlib import Path

from systems.setup._system_discovery import _discover_systems, _discover_workflow_skills


_FACADE_STUB = "def purpose(): pass\n"


def _make_system(systems_dir: Path, name: str, with_facade: bool = True) -> None:
    pkg = systems_dir / name
    pkg.mkdir(parents=True)
    if with_facade:
        (pkg / "__init__.py").write_text(_FACADE_STUB)


class TestDiscoverSystems:
    def test_missing_subsystems_dir_returns_empty_list(self, tmp_path: Path) -> None:
        assert _discover_systems(tmp_path) == []

    def test_empty_subsystems_dir_returns_empty_list(self, tmp_path: Path) -> None:
        (tmp_path / "systems").mkdir()
        assert _discover_systems(tmp_path) == []

    def test_discovers_subsystems_with_facade(self, tmp_path: Path) -> None:
        systems = tmp_path / "systems"
        _make_system(systems, "navigator")
        _make_system(systems, "governance")

        result = _discover_systems(tmp_path)

        assert set(result) == {"navigator", "governance"}

    def test_ignores_subsystems_without_facade(self, tmp_path: Path) -> None:
        systems = tmp_path / "systems"
        _make_system(systems, "with_facade")
        # Package present but no __init__.py — not migrated.
        (systems / "without_facade").mkdir()

        result = _discover_systems(tmp_path)

        assert result == ["with_facade"]

    def test_ignores_subsystems_missing_purpose(self, tmp_path: Path) -> None:
        systems = tmp_path / "systems"
        _make_system(systems, "complete")
        no_purpose = systems / "no_purpose"
        no_purpose.mkdir(parents=True)
        # Has __init__.py but no purpose() — not migrated.
        (no_purpose / "__init__.py").write_text("def status(): pass\n")

        result = _discover_systems(tmp_path)

        assert result == ["complete"]

    def test_returns_sorted_names(self, tmp_path: Path) -> None:
        systems = tmp_path / "systems"
        for name in ["zulu", "alpha", "mike"]:
            _make_system(systems, name)

        result = _discover_systems(tmp_path)

        assert result == ["alpha", "mike", "zulu"]

    def test_ignores_setup_orchestrator_system(self, tmp_path: Path) -> None:
        # `systems/setup/__init__.py` is the orchestrator, not a managed system.
        systems = tmp_path / "systems"
        _make_system(systems, "setup")
        _make_system(systems, "rules")

        result = _discover_systems(tmp_path)

        assert result == ["rules"]


class TestDiscoverWorkflowSkills:
    def test_missing_subsystems_dir_for_skills_returns_empty_list(self, tmp_path: Path) -> None:
        assert _discover_workflow_skills(tmp_path) == []

    def test_empty_subsystems_dir_for_skills_returns_empty_list(self, tmp_path: Path) -> None:
        (tmp_path / "systems").mkdir()
        assert _discover_workflow_skills(tmp_path) == []

    def test_discovers_skills_with_skill_md(self, tmp_path: Path) -> None:
        systems = tmp_path / "systems"
        for name in ["commit", "push"]:
            (systems / name).mkdir(parents=True)
            (systems / name / "SKILL.md").write_text("")

        result = _discover_workflow_skills(tmp_path)

        assert set(result) == {"commit", "push"}

    def test_ignores_directories_without_skill_md(self, tmp_path: Path) -> None:
        systems = tmp_path / "systems"
        (systems / "real").mkdir(parents=True)
        (systems / "real" / "SKILL.md").write_text("")
        (systems / "stub").mkdir()

        result = _discover_workflow_skills(tmp_path)

        assert result == ["real"]

    def test_returns_sorted_names(self, tmp_path: Path) -> None:
        systems = tmp_path / "systems"
        for name in ["zebra", "apple", "mango"]:
            (systems / name).mkdir(parents=True)
            (systems / name / "SKILL.md").write_text("")

        result = _discover_workflow_skills(tmp_path)

        assert result == ["apple", "mango", "zebra"]
