"""Unit tests for skill resolution."""

from __future__ import annotations

import json
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest

from skills.navigator import _skills
from skills.navigator._skills import (
    _parse_frontmatter_name,
    _search_skills_dir,
    resolve_skill,
    list_skills,
)


@pytest.fixture
def tmp_env(monkeypatch: pytest.MonkeyPatch) -> Generator[dict[str, Path], None, None]:
    """Create temp directory tree simulating skill discovery locations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        home = root / "home"
        project = root / "project"
        plugin = root / "plugin"
        marketplace_cache = home / ".claude" / "plugins"

        for d in [home / ".claude" / "skills", project / ".claude" / "skills",
                   plugin / "skills", marketplace_cache]:
            d.mkdir(parents=True)

        monkeypatch.setattr(_skills, "_get_claude_home", lambda: home / ".claude")
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(project))
        monkeypatch.setenv("CLAUDE_PLUGIN_ROOT", str(plugin))

        yield {
            "root": root,
            "home": home,
            "project": project,
            "plugin": plugin,
            "marketplace_cache": marketplace_cache,
        }


def _write_skill(base_dir: Path, dir_name: str, name: str) -> Path:
    """Create a SKILL.md with frontmatter name in a skill directory."""
    skill_dir = base_dir / dir_name
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(f"---\nname: {name}\ndescription: Test skill\n---\n\n# /{name}\n")
    return skill_md


def _write_installed_plugins(cache_dir: Path, plugins: dict[str, str]) -> None:
    """Write installed_plugins.json with plugin entries."""
    data = {"version": 2, "plugins": {}}
    for plugin_key, install_path in plugins.items():
        data["plugins"][plugin_key] = [{
            "scope": "user",
            "installPath": install_path,
            "version": "1.0.0",
            "installedAt": "2026-01-01T00:00:00.000Z",
            "lastUpdated": "2026-01-01T00:00:00.000Z",
        }]
    (cache_dir / "installed_plugins.json").write_text(json.dumps(data))


# =========================================================================
# Frontmatter parsing
# =========================================================================


class TestParseFrontmatterName:
    def test_extracts_name(self, tmp_path: Path) -> None:
        skill_md = tmp_path / "SKILL.md"
        skill_md.write_text("---\nname: my-skill\ndescription: test\n---\n")
        assert _parse_frontmatter_name(skill_md) == "my-skill"

    def test_quoted_name(self, tmp_path: Path) -> None:
        skill_md = tmp_path / "SKILL.md"
        skill_md.write_text('---\nname: "my-skill"\ndescription: test\n---\n')
        assert _parse_frontmatter_name(skill_md) == "my-skill"

    def test_no_frontmatter(self, tmp_path: Path) -> None:
        skill_md = tmp_path / "SKILL.md"
        skill_md.write_text("# No frontmatter\n")
        assert _parse_frontmatter_name(skill_md) is None

    def test_missing_file(self, tmp_path: Path) -> None:
        skill_md = tmp_path / "nonexistent.md"
        assert _parse_frontmatter_name(skill_md) is None

    def test_no_name_field(self, tmp_path: Path) -> None:
        skill_md = tmp_path / "SKILL.md"
        skill_md.write_text("---\ndescription: test\n---\n")
        assert _parse_frontmatter_name(skill_md) is None


# =========================================================================
# Directory search
# =========================================================================


class TestSearchSkillsDir:
    def test_finds_by_name(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        _write_skill(skills_dir, "conventions", "ocd-conventions")
        result = _search_skills_dir(skills_dir, "ocd-conventions")
        assert result is not None
        assert result.name == "SKILL.md"

    def test_not_found(self, tmp_path: Path) -> None:
        skills_dir = tmp_path / "skills"
        _write_skill(skills_dir, "conventions", "ocd-conventions")
        assert _search_skills_dir(skills_dir, "nonexistent") is None

    def test_missing_directory(self, tmp_path: Path) -> None:
        assert _search_skills_dir(tmp_path / "nonexistent", "any") is None


# =========================================================================
# Priority resolution
# =========================================================================


class TestResolveSkill:
    def test_finds_in_plugin_dir(self, tmp_env: dict[str, Path]) -> None:
        _write_skill(tmp_env["plugin"] / "skills", "conventions", "ocd-conventions")
        result = resolve_skill("ocd-conventions")
        assert result is not None
        assert "plugin" in str(result)

    def test_project_shadows_plugin(self, tmp_env: dict[str, Path]) -> None:
        _write_skill(tmp_env["plugin"] / "skills", "my-skill", "my-skill")
        _write_skill(tmp_env["project"] / ".claude" / "skills", "my-skill", "my-skill")
        result = resolve_skill("my-skill")
        assert result is not None
        assert "project" in str(result)

    def test_personal_shadows_project(self, tmp_env: dict[str, Path]) -> None:
        _write_skill(tmp_env["project"] / ".claude" / "skills", "my-skill", "my-skill")
        _write_skill(tmp_env["home"] / ".claude" / "skills", "my-skill", "my-skill")
        result = resolve_skill("my-skill")
        assert result is not None
        assert "home" in str(result)

    def test_plugin_dir_shadows_marketplace(self, tmp_env: dict[str, Path]) -> None:
        # Create marketplace plugin with same skill name
        mp_dir = tmp_env["root"] / "marketplace_plugin"
        _write_skill(mp_dir / "skills", "my-skill", "my-skill")
        _write_installed_plugins(
            tmp_env["marketplace_cache"],
            {"my-plugin@marketplace": str(mp_dir)},
        )
        # Create plugin-dir skill with same name
        _write_skill(tmp_env["plugin"] / "skills", "my-skill", "my-skill")
        result = resolve_skill("my-skill")
        assert result is not None
        assert "plugin" in str(result)

    def test_falls_through_to_marketplace(self, tmp_env: dict[str, Path]) -> None:
        mp_dir = tmp_env["root"] / "marketplace_plugin"
        _write_skill(mp_dir / "skills", "other-skill", "other-skill")
        _write_installed_plugins(
            tmp_env["marketplace_cache"],
            {"other-plugin@marketplace": str(mp_dir)},
        )
        result = resolve_skill("other-skill")
        assert result is not None
        assert "marketplace_plugin" in str(result)

    def test_not_found(self, tmp_env: dict[str, Path]) -> None:
        assert resolve_skill("nonexistent") is None


# =========================================================================
# List skills
# =========================================================================


class TestListSkills:
    def test_lists_from_plugin_dir(self, tmp_env: dict[str, Path]) -> None:
        _write_skill(tmp_env["plugin"] / "skills", "conv", "ocd-conventions")
        _write_skill(tmp_env["plugin"] / "skills", "nav", "ocd-navigator")
        skills = list_skills()
        assert len(skills) == 2
        assert all(s["source"] == "plugin-dir" for s in skills)

    def test_higher_priority_shadows(self, tmp_env: dict[str, Path]) -> None:
        _write_skill(tmp_env["plugin"] / "skills", "my-skill", "my-skill")
        _write_skill(tmp_env["project"] / ".claude" / "skills", "my-skill", "my-skill")
        skills = list_skills()
        assert len(skills) == 1
        assert skills[0]["source"] == "project"

    def test_empty_when_no_skills(self, tmp_env: dict[str, Path]) -> None:
        assert list_skills() == []
