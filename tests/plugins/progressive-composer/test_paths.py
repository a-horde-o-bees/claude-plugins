"""Path-resolution unit tests for the new self-contained skill folder model."""

import pytest

from scripts._paths import (
    composition_path,
    compositions_in_scope,
    derive_source_slug,
    scope_skills_dir,
    skill_folder,
    skill_md_path,
    source_embed_path,
    sources_subdir,
)


def test_scope_skills_dir_user(isolated_env):
    assert scope_skills_dir("user") == isolated_env["claude_home"] / "skills"


def test_scope_skills_dir_project(isolated_env):
    assert scope_skills_dir("project") == isolated_env["project_dir"] / ".claude" / "skills"


def test_scope_skills_dir_rejects_unknown(isolated_env):
    with pytest.raises(ValueError, match="unknown scope"):
        scope_skills_dir("global")


def test_skill_folder_user(isolated_env):
    assert (
        skill_folder("my-skill", "user")
        == isolated_env["claude_home"] / "skills" / "my-skill"
    )


def test_composition_path_user(isolated_env):
    assert (
        composition_path("my-skill", "user")
        == isolated_env["claude_home"] / "skills" / "my-skill" / "composition.md"
    )


def test_skill_md_path_user(isolated_env):
    assert (
        skill_md_path("my-skill", "user")
        == isolated_env["claude_home"] / "skills" / "my-skill" / "SKILL.md"
    )


def test_sources_subdir_user(isolated_env):
    assert (
        sources_subdir("my-skill", "user")
        == isolated_env["claude_home"] / "skills" / "my-skill" / "sources"
    )


def test_source_embed_path_user(isolated_env):
    assert (
        source_embed_path("my-skill", "anthropics-skills", "user")
        == isolated_env["claude_home"]
        / "skills"
        / "my-skill"
        / "sources"
        / "anthropics-skills"
    )


def test_compositions_in_scope_empty(isolated_env):
    assert compositions_in_scope("user") == []


def test_compositions_in_scope_skips_folders_without_composition(isolated_env):
    skills_dir = isolated_env["claude_home"] / "skills"
    skills_dir.mkdir(parents=True)
    (skills_dir / "naked-skill").mkdir()
    (skills_dir / "naked-skill" / "SKILL.md").write_text("# without composition\n")
    assert compositions_in_scope("user") == []


def test_compositions_in_scope_returns_skills_with_composition(isolated_env):
    skills_dir = isolated_env["claude_home"] / "skills"
    skills_dir.mkdir(parents=True)
    for name in ("a-skill", "b-skill"):
        folder = skills_dir / name
        folder.mkdir()
        (folder / "composition.md").write_text("---\nname: x\nscope: user\n---\n")
    paths = compositions_in_scope("user")
    assert len(paths) == 2
    assert paths[0].parent.name == "a-skill"
    assert paths[1].parent.name == "b-skill"


@pytest.mark.parametrize(
    "url,skill,expected",
    [
        (
            "https://github.com/anthropics/skills.git",
            "pdf",
            "anthropics-skills--pdf",
        ),
        (
            "https://github.com/anthropics/skills",
            "pdf",
            "anthropics-skills--pdf",
        ),
        (
            "git@github.com:foo/bar.git",
            "my-skill",
            "foo-bar--my-skill",
        ),
        # last 2 path segments of repo — keeps slugs short across deep paths
        (
            "https://example.com/path/with/slashes/repo.git",
            "thing",
            "slashes-repo--thing",
        ),
    ],
)
def test_derive_source_slug(url, skill, expected):
    assert derive_source_slug(url, skill) == expected


def test_derive_source_slug_includes_skill_to_avoid_collision():
    """Two skills from the same repo must produce distinct slugs."""
    url = "https://github.com/affaan-m/everything-claude-code.git"
    patterns_slug = derive_source_slug(url, "python-patterns")
    testing_slug = derive_source_slug(url, "python-testing")
    assert patterns_slug != testing_slug


def test_derive_source_slug_falls_back_for_pathless_url():
    slug = derive_source_slug("https://example.com", "thing")
    assert slug  # non-empty
    assert all(c.isalnum() or c == "-" for c in slug)
    assert slug.endswith("--thing")


def test_get_project_dir_rejects_path_inside_claude_home(
    tmp_path, monkeypatch
):
    """Refuse a project_dir resolution that lands inside CLAUDE_HOME.

    Caches and home-dir git checkouts can shadow real projects when the
    script falls back to `git rev-parse --show-toplevel`. Detect that
    case and tell the caller to set CLAUDE_PROJECT_DIR explicitly.
    """
    from scripts._paths import get_project_dir

    claude_home = tmp_path / "claude_home"
    bad_project = claude_home / "plugins" / "cache" / "x" / "y" / "z"
    bad_project.mkdir(parents=True)
    monkeypatch.setenv("CLAUDE_HOME", str(claude_home))
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(bad_project))

    with pytest.raises(RuntimeError, match="CLAUDE_PROJECT_DIR"):
        get_project_dir()
