"""Unit tests for framework._discovery.

Covers the deterministic scan behavior of _discover_systems (scans
`systems/*/` for `_init.py`) and _discover_workflow_skills (scans
`systems/*/` for `SKILL.md`). Both functions must return sorted
lists, skip directories that lack the sentinel file, and handle
missing parent directories gracefully.
"""

from pathlib import Path

from framework._system_discovery import _discover_systems, _discover_workflow_skills


class TestDiscoverSystems:
    def test_missing_subsystems_dir_returns_empty_list(self, tmp_path: Path) -> None:
        assert _discover_systems(tmp_path) == []

    def test_empty_subsystems_dir_returns_empty_list(self, tmp_path: Path) -> None:
        (tmp_path / "systems").mkdir()
        assert _discover_systems(tmp_path) == []

    def test_discovers_subsystems_with_init_py(self, tmp_path: Path) -> None:
        systems = tmp_path / "systems"
        (systems / "navigator").mkdir(parents=True)
        (systems / "navigator" / "_init.py").write_text("")
        (systems / "governance").mkdir()
        (systems / "governance" / "_init.py").write_text("")

        result = _discover_systems(tmp_path)

        assert set(result) == {"navigator", "governance"}

    def test_ignores_subsystems_without_init_py(self, tmp_path: Path) -> None:
        systems = tmp_path / "systems"
        (systems / "with_init").mkdir(parents=True)
        (systems / "with_init" / "_init.py").write_text("")
        (systems / "without_init").mkdir()

        result = _discover_systems(tmp_path)

        assert result == ["with_init"]

    def test_returns_sorted_names(self, tmp_path: Path) -> None:
        systems = tmp_path / "systems"
        for name in ["zulu", "alpha", "mike"]:
            (systems / name).mkdir(parents=True)
            (systems / name / "_init.py").write_text("")

        result = _discover_systems(tmp_path)

        assert result == ["alpha", "mike", "zulu"]

    def test_ignores_files_that_are_not_packages(self, tmp_path: Path) -> None:
        systems = tmp_path / "systems"
        systems.mkdir()
        (systems / "loose_init.py").write_text("")

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
