"""Unit tests for setup._system_discovery.

Covers the deterministic scan behavior of _discover_systems (scans
`systems/*/setup/__init__.py`) and _discover_workflow_skills (scans
`systems/*/SKILL.md`). Both functions must return sorted lists, skip
directories that lack the sentinel file, and handle missing parent
directories gracefully.
"""

from pathlib import Path

from systems.setup._system_discovery import _discover_systems, _discover_workflow_skills


def _make_setup_pkg(systems_dir: Path, name: str) -> None:
    pkg = systems_dir / name / "setup"
    pkg.mkdir(parents=True)
    (pkg / "__init__.py").write_text("")


class TestDiscoverSystems:
    def test_missing_subsystems_dir_returns_empty_list(self, tmp_path: Path) -> None:
        assert _discover_systems(tmp_path) == []

    def test_empty_subsystems_dir_returns_empty_list(self, tmp_path: Path) -> None:
        (tmp_path / "systems").mkdir()
        assert _discover_systems(tmp_path) == []

    def test_discovers_subsystems_with_setup_pkg(self, tmp_path: Path) -> None:
        systems = tmp_path / "systems"
        _make_setup_pkg(systems, "navigator")
        _make_setup_pkg(systems, "governance")

        result = _discover_systems(tmp_path)

        assert set(result) == {"navigator", "governance"}

    def test_ignores_subsystems_without_setup_pkg(self, tmp_path: Path) -> None:
        systems = tmp_path / "systems"
        _make_setup_pkg(systems, "with_setup")
        (systems / "without_setup").mkdir()

        result = _discover_systems(tmp_path)

        assert result == ["with_setup"]

    def test_returns_sorted_names(self, tmp_path: Path) -> None:
        systems = tmp_path / "systems"
        for name in ["zulu", "alpha", "mike"]:
            _make_setup_pkg(systems, name)

        result = _discover_systems(tmp_path)

        assert result == ["alpha", "mike", "zulu"]

    def test_ignores_loose_setup_pkg_at_systems_root(self, tmp_path: Path) -> None:
        systems = tmp_path / "systems"
        # A bare `systems/setup/__init__.py` is the orchestrator package, not a system.
        (systems / "setup").mkdir(parents=True)
        (systems / "setup" / "__init__.py").write_text("")

        result = _discover_systems(tmp_path)

        assert result == []


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
