"""Unit tests for plugin._discovery.

Covers the deterministic scan behavior of _discover_systems (scans
`subsystems/*/` for `_init.py`) and _discover_workflow_skills (scans
`subsystems/*/` for `SKILL.md`). Both functions must return sorted
lists, skip directories that lack the sentinel file, and handle
missing parent directories gracefully.
"""

from pathlib import Path

from plugin._discovery import _discover_systems, _discover_workflow_skills


class TestDiscoverSystems:
    def test_missing_subsystems_dir_returns_empty_list(self, tmp_path: Path) -> None:
        assert _discover_systems(tmp_path) == []

    def test_empty_subsystems_dir_returns_empty_list(self, tmp_path: Path) -> None:
        (tmp_path / "subsystems").mkdir()
        assert _discover_systems(tmp_path) == []

    def test_discovers_subsystems_with_init_py(self, tmp_path: Path) -> None:
        subsystems = tmp_path / "subsystems"
        (subsystems / "navigator").mkdir(parents=True)
        (subsystems / "navigator" / "_init.py").write_text("")
        (subsystems / "governance").mkdir()
        (subsystems / "governance" / "_init.py").write_text("")

        result = _discover_systems(tmp_path)

        assert set(result) == {"navigator", "governance"}

    def test_ignores_subsystems_without_init_py(self, tmp_path: Path) -> None:
        subsystems = tmp_path / "subsystems"
        (subsystems / "with_init").mkdir(parents=True)
        (subsystems / "with_init" / "_init.py").write_text("")
        (subsystems / "without_init").mkdir()

        result = _discover_systems(tmp_path)

        assert result == ["with_init"]

    def test_returns_sorted_names(self, tmp_path: Path) -> None:
        subsystems = tmp_path / "subsystems"
        for name in ["zulu", "alpha", "mike"]:
            (subsystems / name).mkdir(parents=True)
            (subsystems / name / "_init.py").write_text("")

        result = _discover_systems(tmp_path)

        assert result == ["alpha", "mike", "zulu"]

    def test_ignores_files_that_are_not_packages(self, tmp_path: Path) -> None:
        subsystems = tmp_path / "subsystems"
        subsystems.mkdir()
        (subsystems / "loose_init.py").write_text("")

        result = _discover_systems(tmp_path)

        assert result == []


class TestDiscoverWorkflowSkills:
    def test_missing_subsystems_dir_for_skills_returns_empty_list(self, tmp_path: Path) -> None:
        assert _discover_workflow_skills(tmp_path) == []

    def test_empty_subsystems_dir_for_skills_returns_empty_list(self, tmp_path: Path) -> None:
        (tmp_path / "subsystems").mkdir()
        assert _discover_workflow_skills(tmp_path) == []

    def test_discovers_skills_with_skill_md(self, tmp_path: Path) -> None:
        subsystems = tmp_path / "subsystems"
        for name in ["commit", "push"]:
            (subsystems / name).mkdir(parents=True)
            (subsystems / name / "SKILL.md").write_text("")

        result = _discover_workflow_skills(tmp_path)

        assert set(result) == {"commit", "push"}

    def test_ignores_directories_without_skill_md(self, tmp_path: Path) -> None:
        subsystems = tmp_path / "subsystems"
        (subsystems / "real").mkdir(parents=True)
        (subsystems / "real" / "SKILL.md").write_text("")
        (subsystems / "stub").mkdir()

        result = _discover_workflow_skills(tmp_path)

        assert result == ["real"]

    def test_returns_sorted_names(self, tmp_path: Path) -> None:
        subsystems = tmp_path / "subsystems"
        for name in ["zebra", "apple", "mango"]:
            (subsystems / name).mkdir(parents=True)
            (subsystems / name / "SKILL.md").write_text("")

        result = _discover_workflow_skills(tmp_path)

        assert result == ["apple", "mango", "zebra"]
