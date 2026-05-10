"""End-to-end tests for the compose workflow (new, refine, build, list, sub-ops)."""

import re

from scripts._spec import (
    BUILD_STATUS_BUILT,
    parse,
)


def _file_url(path) -> str:
    return f"file://{path}"


def _seed_composition(composer_run, fixture_repo, isolated_env, name="my-skill", scope="user"):
    """Walk through compose new + composition.md write + add-source.

    Returns the composition.md path. The agent's normal flow uses Write
    tool to create the scaffold; tests do the equivalent via plain file
    write so they can drive subsequent verbs.
    """
    from scripts._paths import composition_path
    from scripts._spec import make_composed_scaffold, write as write_spec

    spec_path = composition_path(name, scope)
    spec = make_composed_scaffold(name=name, scope=scope, description="test composition")
    spec.goal_summary = "demonstrate end-to-end compose flow"
    spec_path.parent.mkdir(parents=True, exist_ok=True)
    write_spec(spec_path, spec)

    composer_run(
        "compose",
        "add-source",
        name,
        f"{_file_url(fixture_repo)}:fixture-skill",
        "--scope",
        scope,
    )
    return spec_path


def test_compose_new_prints_orchestration(composer_run, isolated_env):
    """compose new is workflow entry — outputs orchestration, no disk ops."""
    result = composer_run("compose", "new", "--scope", "user")
    assert result.returncode == 0
    assert "compose new started" in result.stdout
    assert "Next steps for the agent" in result.stdout
    assert "spec_version: 1" in result.stdout
    # No skill folder created
    assert not (isolated_env["claude_home"] / "skills").exists() or not list(
        (isolated_env["claude_home"] / "skills").iterdir()
    )


def test_compose_add_source_sparse_checks_into_sources_subdir(
    composer_run, fixture_repo, isolated_env
):
    spec_path = _seed_composition(composer_run, fixture_repo, isolated_env)
    from scripts._paths import derive_source_slug
    slug = derive_source_slug(_file_url(fixture_repo))
    embed = (
        isolated_env["claude_home"]
        / "skills"
        / "my-skill"
        / "sources"
        / slug
        / "SKILL.md"
    )
    assert embed.exists()

    spec = parse(spec_path.read_text())
    assert len(spec.sources) == 1
    assert spec.sources[0].skill == "fixture-skill"
    assert re.fullmatch(r"[0-9a-f]{40}", spec.sources[0].commit)


def test_compose_remove_source_deletes_embed_and_frontmatter(
    composer_run, fixture_repo, isolated_env
):
    from scripts._paths import derive_source_slug

    spec_path = _seed_composition(composer_run, fixture_repo, isolated_env)
    slug = derive_source_slug(_file_url(fixture_repo))
    embed = isolated_env["claude_home"] / "skills" / "my-skill" / "sources" / slug
    assert embed.exists()

    composer_run(
        "compose",
        "remove-source",
        "my-skill",
        slug,
        "--scope",
        "user",
    )
    assert not embed.exists()
    spec = parse(spec_path.read_text())
    assert spec.sources == []


def test_compose_update_sources_rerolls_commit(
    composer_run, fixture_repo, commit_to_fixture, isolated_env
):
    spec_path = _seed_composition(composer_run, fixture_repo, isolated_env)
    initial = parse(spec_path.read_text())
    initial_commit = initial.sources[0].commit

    commit_to_fixture(
        "skills/fixture-skill/extra.md",
        "drift content\n",
        message="upstream change",
    )
    composer_run(
        "compose",
        "update-sources",
        "my-skill",
        "--scope",
        "user",
    )
    after = parse(spec_path.read_text())
    assert after.sources[0].commit != initial_commit


def test_compose_purge_sources_deletes_subfolder(
    composer_run, fixture_repo, isolated_env
):
    _seed_composition(composer_run, fixture_repo, isolated_env)
    sources_dir = isolated_env["claude_home"] / "skills" / "my-skill" / "sources"
    assert sources_dir.exists()

    composer_run("compose", "purge-sources", "my-skill", "--scope", "user")
    assert not sources_dir.exists()


def test_compose_build_writes_skill_md(composer_run, fixture_repo, isolated_env):
    spec_path = _seed_composition(composer_run, fixture_repo, isolated_env)
    composer_run("compose", "build", "my-skill", "--scope", "user")
    skill_md = isolated_env["claude_home"] / "skills" / "my-skill" / "SKILL.md"
    assert skill_md.exists()
    assert "my-skill" in skill_md.read_text()
    assert "demonstrate end-to-end compose flow" in skill_md.read_text()

    spec = parse(spec_path.read_text())
    assert spec.build_status == BUILD_STATUS_BUILT
    assert spec.last_build is not None


def test_compose_build_refuses_overwrite_without_force(
    composer_run, fixture_repo, isolated_env
):
    _seed_composition(composer_run, fixture_repo, isolated_env)
    composer_run("compose", "build", "my-skill", "--scope", "user")
    result = composer_run(
        "compose", "build", "my-skill", "--scope", "user", check=False
    )
    assert result.returncode != 0
    assert "already exists" in result.stderr


def test_compose_build_force_overwrites(composer_run, fixture_repo, isolated_env):
    _seed_composition(composer_run, fixture_repo, isolated_env)
    composer_run("compose", "build", "my-skill", "--scope", "user")
    skill_md = isolated_env["claude_home"] / "skills" / "my-skill" / "SKILL.md"
    skill_md.write_text("# user refinements\n")

    composer_run(
        "compose", "build", "my-skill", "--scope", "user", "--force"
    )
    assert "user refinements" not in skill_md.read_text()




def test_compose_build_rejects_empty_description(composer_run, fixture_repo, isolated_env):
    from scripts._paths import composition_path
    from scripts._spec import make_composed_scaffold, write as write_spec

    spec_path = composition_path("my-skill", "user")
    spec = make_composed_scaffold(name="my-skill", scope="user", description="")
    spec.goal_summary = "summary"
    spec_path.parent.mkdir(parents=True, exist_ok=True)
    write_spec(spec_path, spec)

    composer_run(
        "compose",
        "add-source",
        "my-skill",
        f"{_file_url(fixture_repo)}:fixture-skill",
        "--scope",
        "user",
    )

    result = composer_run(
        "compose", "build", "my-skill", "--scope", "user", check=False
    )
    assert result.returncode != 0
    assert "description" in result.stderr


def test_compose_refine_reads_spec_and_reports_in_sync(
    composer_run, fixture_repo, isolated_env
):
    _seed_composition(composer_run, fixture_repo, isolated_env)
    result = composer_run("compose", "refine", "my-skill", "--scope", "user")
    assert "spec:" in result.stdout
    assert "in sync:" in result.stdout
    assert "fixture-skill" in result.stdout


def test_compose_refine_detects_drift(
    composer_run, fixture_repo, commit_to_fixture, isolated_env
):
    _seed_composition(composer_run, fixture_repo, isolated_env)
    commit_to_fixture(
        "skills/fixture-skill/extra.md",
        "new content\n",
        message="upstream changed",
    )
    result = composer_run("compose", "refine", "my-skill", "--scope", "user")
    assert "drift detected" in result.stdout
    assert "fixture-skill" in result.stdout


def test_compose_refine_missing_spec_exits_nonzero(composer_run, isolated_env):
    result = composer_run(
        "compose", "refine", "absent", "--scope", "user", check=False
    )
    assert result.returncode != 0
    assert "no composition" in result.stderr


def test_compose_list_empty(composer_run, isolated_env):
    result = composer_run("compose", "list")
    assert "no skills deployed" in result.stdout


def test_compose_list_shows_composition(
    composer_run, fixture_repo, isolated_env
):
    _seed_composition(composer_run, fixture_repo, isolated_env)
    result = composer_run("compose", "list", "--scope", "user")
    assert "my-skill" in result.stdout
    assert "draft" in result.stdout


def test_compose_list_drift_runs_ls_remote(
    composer_run, fixture_repo, commit_to_fixture, isolated_env
):
    _seed_composition(composer_run, fixture_repo, isolated_env)
    composer_run("compose", "build", "my-skill", "--scope", "user")
    commit_to_fixture(
        "skills/fixture-skill/extra.md",
        "drift\n",
        message="drift",
    )
    result = composer_run("compose", "list", "--scope", "user", "--drift")
    assert "drift:" in result.stdout
    assert "fixture-skill" in result.stdout
