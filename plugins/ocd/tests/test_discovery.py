"""Unit tests for plugin._discovery.

Covers the deterministic scan behavior of _discover_systems (scans
`lib/*/` for `_init.py`) and _discover_workflow_skills (scans
`skills/*/` for `SKILL.md`). Both functions must return sorted lists,
skip directories that lack the sentinel file, and handle missing
parent directories gracefully.
"""

from pathlib import Path

from plugin._discovery import _discover_systems, _discover_workflow_skills


class TestDiscoverSystems:
    def test_missing_lib_dir_returns_empty_list(self, tmp_path: Path) -> None:
        assert _discover_systems(tmp_path) == []

    def test_empty_lib_dir_returns_empty_list(self, tmp_path: Path) -> None:
        (tmp_path / "lib").mkdir()
        assert _discover_systems(tmp_path) == []

    def test_discovers_libs_with_init_py(self, tmp_path: Path) -> None:
        lib = tmp_path / "lib"
        (lib / "navigator").mkdir(parents=True)
        (lib / "navigator" / "_init.py").write_text("")
        (lib / "governance").mkdir()
        (lib / "governance" / "_init.py").write_text("")

        result = _discover_systems(tmp_path)

        assert set(result) == {"navigator", "governance"}

    def test_ignores_libs_without_init_py(self, tmp_path: Path) -> None:
        lib = tmp_path / "lib"
        (lib / "with_init").mkdir(parents=True)
        (lib / "with_init" / "_init.py").write_text("")
        (lib / "without_init").mkdir()

        result = _discover_systems(tmp_path)

        assert result == ["with_init"]

    def test_returns_sorted_names(self, tmp_path: Path) -> None:
        lib = tmp_path / "lib"
        for name in ["zulu", "alpha", "mike"]:
            (lib / name).mkdir(parents=True)
            (lib / name / "_init.py").write_text("")

        result = _discover_systems(tmp_path)

        assert result == ["alpha", "mike", "zulu"]

    def test_ignores_files_that_are_not_packages(self, tmp_path: Path) -> None:
        lib = tmp_path / "lib"
        lib.mkdir()
        (lib / "loose_init.py").write_text("")

        result = _discover_systems(tmp_path)

        assert result == []


class TestDiscoverWorkflowSkills:
    def test_missing_skills_dir_returns_empty_list(self, tmp_path: Path) -> None:
        assert _discover_workflow_skills(tmp_path) == []

    def test_empty_skills_dir_returns_empty_list(self, tmp_path: Path) -> None:
        (tmp_path / "skills").mkdir()
        assert _discover_workflow_skills(tmp_path) == []

    def test_discovers_skills_with_skill_md(self, tmp_path: Path) -> None:
        skills = tmp_path / "skills"
        for name in ["commit", "push"]:
            (skills / name).mkdir(parents=True)
            (skills / name / "SKILL.md").write_text("")

        result = _discover_workflow_skills(tmp_path)

        assert set(result) == {"commit", "push"}

    def test_ignores_directories_without_skill_md(self, tmp_path: Path) -> None:
        skills = tmp_path / "skills"
        (skills / "real").mkdir(parents=True)
        (skills / "real" / "SKILL.md").write_text("")
        (skills / "stub").mkdir()

        result = _discover_workflow_skills(tmp_path)

        assert result == ["real"]

    def test_returns_sorted_names(self, tmp_path: Path) -> None:
        skills = tmp_path / "skills"
        for name in ["zebra", "apple", "mango"]:
            (skills / name).mkdir(parents=True)
            (skills / name / "SKILL.md").write_text("")

        result = _discover_workflow_skills(tmp_path)

        assert result == ["apple", "mango", "zebra"]
