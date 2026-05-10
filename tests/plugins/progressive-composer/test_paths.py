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
    "url,expected",
    [
        ("https://github.com/anthropics/skills.git", "anthropics-skills"),
        ("https://github.com/anthropics/skills", "anthropics-skills"),
        ("git@github.com:foo/bar.git", "foo-bar"),
        # last 2 path segments — keeps slugs short across deep paths
        ("https://example.com/path/with/slashes/repo.git", "slashes-repo"),
    ],
)
def test_derive_source_slug(url, expected):
    assert derive_source_slug(url) == expected


def test_derive_source_slug_falls_back_for_pathless_url():
    slug = derive_source_slug("https://example.com")
    assert slug  # non-empty
    assert all(c.isalnum() or c == "-" for c in slug)
