"""End-to-end tests for the compose workflow (new, refine, build, list, sub-ops)."""

import re

from scripts._spec import (
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
    spec = make_composed_scaffold(name=name, description="test composition")
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


def test_compose_new_emits_state_only(composer_run, isolated_env):
    """compose new emits resolved state (scope + target path) — no procedure."""
    result = composer_run("compose", "new", "--scope", "user")
    assert result.returncode == 0
    assert "scope: user" in result.stdout
    assert "target:" in result.stdout
    assert str(isolated_env["claude_home"] / "skills") in result.stdout
    # No procedure / scaffold prints — those live in _compose_new.md
    assert "Next steps for the agent" not in result.stdout
    assert "spec_version:" not in result.stdout
    # No disk ops
    assert not (isolated_env["claude_home"] / "skills").exists() or not list(
        (isolated_env["claude_home"] / "skills").iterdir()
    )


def test_compose_add_source_sparse_checks_into_sources_subdir(
    composer_run, fixture_repo, isolated_env
):
    spec_path = _seed_composition(composer_run, fixture_repo, isolated_env)
    from scripts._paths import derive_source_slug
    slug = derive_source_slug(_file_url(fixture_repo), "fixture-skill")
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


def test_compose_add_source_two_skills_same_repo_no_collision(
    composer_run, fixture_repo, isolated_env
):
    """Two skills from the same repo embed into distinct sources/ subdirs.

    Regression guard for the slug-collision bug — prior to including the
    skill name in derive_source_slug, the second add-source clobbered
    the first's SKILL.md because both resolved to the same embed dir.
    """
    import subprocess
    from scripts._paths import derive_source_slug

    # Add a second skill to the fixture repo, on the same branch.
    second_skill_dir = fixture_repo / "skills" / "second-skill"
    second_skill_dir.mkdir(parents=True)
    (second_skill_dir / "SKILL.md").write_text(
        "---\nname: second-skill\ndescription: another fixture\n---\n# second\n"
    )
    subprocess.run(["git", "add", "."], cwd=fixture_repo, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.email=test@test",
            "-c",
            "user.name=test",
            "commit",
            "-qm",
            "add second skill",
        ],
        cwd=fixture_repo,
        check=True,
    )

    _seed_composition(composer_run, fixture_repo, isolated_env)
    composer_run(
        "compose",
        "add-source",
        "my-skill",
        f"{_file_url(fixture_repo)}:second-skill",
        "--scope",
        "user",
    )

    slug_first = derive_source_slug(_file_url(fixture_repo), "fixture-skill")
    slug_second = derive_source_slug(_file_url(fixture_repo), "second-skill")
    assert slug_first != slug_second

    sources_dir = isolated_env["claude_home"] / "skills" / "my-skill" / "sources"
    assert (sources_dir / slug_first / "SKILL.md").exists()
    assert (sources_dir / slug_second / "SKILL.md").exists()


def test_compose_new_omits_type_field_from_scaffold(composer_run, isolated_env):
    """Scaffold output must not emit `type:` — discriminator was dropped in pivot-4."""
    result = composer_run("compose", "new", "--scope", "user")
    assert "type:" not in result.stdout


def test_compose_add_source_finds_skill_at_nested_depth(
    composer_run, fixture_repo, isolated_env
):
    """Probe locates a skill folder at arbitrary depth — not just `skills/<skill>/`.

    Community repos use varied layouts (`<plugin>/skills/<skill>/`,
    `plugins/<plugin>/skills/<skill>/`, etc.). The probe scans the full
    ls-tree for any `<...>/<skill>/SKILL.md` match.
    """
    import subprocess
    from scripts._paths import derive_source_slug

    # Place a skill at a deeply nested path in the fixture repo.
    nested_dir = fixture_repo / "plugins" / "some-plugin" / "skills" / "deep-skill"
    nested_dir.mkdir(parents=True)
    (nested_dir / "SKILL.md").write_text(
        "---\nname: deep-skill\ndescription: nested fixture\n---\n# deep\n"
    )
    subprocess.run(["git", "add", "."], cwd=fixture_repo, check=True)
    subprocess.run(
        [
            "git", "-c", "user.email=test@test", "-c", "user.name=test",
            "commit", "-qm", "add deeply-nested skill",
        ],
        cwd=fixture_repo,
        check=True,
    )

    _seed_composition(composer_run, fixture_repo, isolated_env)
    composer_run(
        "compose",
        "add-source",
        "my-skill",
        f"{_file_url(fixture_repo)}:deep-skill",
        "--scope",
        "user",
    )

    slug = derive_source_slug(_file_url(fixture_repo), "deep-skill")
    embed = (
        isolated_env["claude_home"]
        / "skills"
        / "my-skill"
        / "sources"
        / slug
        / "SKILL.md"
    )
    assert embed.exists()


def test_compose_add_source_rejects_ambiguous_same_depth_matches(
    composer_run, fixture_repo, isolated_env
):
    """Two `<x>/<skill>/SKILL.md` paths at the same depth — probe refuses."""
    import subprocess

    # Two skills with the same name at the same nesting depth.
    for parent in ("a", "b"):
        d = fixture_repo / parent / "ambiguous-skill"
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text(
            f"---\nname: ambiguous-skill\ndescription: under {parent}\n---\n# {parent}\n"
        )
    subprocess.run(["git", "add", "."], cwd=fixture_repo, check=True)
    subprocess.run(
        [
            "git", "-c", "user.email=test@test", "-c", "user.name=test",
            "commit", "-qm", "add ambiguous skill",
        ],
        cwd=fixture_repo,
        check=True,
    )

    _seed_composition(composer_run, fixture_repo, isolated_env)
    result = composer_run(
        "compose",
        "add-source",
        "my-skill",
        f"{_file_url(fixture_repo)}:ambiguous-skill",
        "--scope",
        "user",
        check=False,
    )
    assert result.returncode != 0
    assert "multiple paths" in result.stderr


def test_compose_remove_source_deletes_embed_and_frontmatter(
    composer_run, fixture_repo, isolated_env
):
    from scripts._paths import derive_source_slug

    spec_path = _seed_composition(composer_run, fixture_repo, isolated_env)
    slug = derive_source_slug(_file_url(fixture_repo), "fixture-skill")
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
    _seed_composition(composer_run, fixture_repo, isolated_env)
    composer_run("compose", "build", "my-skill", "--scope", "user")
    skill_md = isolated_env["claude_home"] / "skills" / "my-skill" / "SKILL.md"
    assert skill_md.exists()
    text = skill_md.read_text()
    assert "name: my-skill" in text
    assert "test composition" in text  # description carries from composition.md
    # scripts/__init__.py is the empty package marker
    assert (isolated_env["claude_home"] / "skills" / "my-skill" / "scripts" / "__init__.py").exists()


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
    spec = make_composed_scaffold(name="my-skill", description="")
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
    assert "deployed: no" in result.stdout
    assert "in sync:" in result.stdout
    assert "fixture-skill" in result.stdout
    # Procedural "Next steps" content lives in _compose_refine.md, not in script output
    assert "Next steps for the agent" not in result.stdout


def test_compose_refine_reports_deployed_after_build(
    composer_run, fixture_repo, isolated_env
):
    _seed_composition(composer_run, fixture_repo, isolated_env)
    composer_run("compose", "build", "my-skill", "--scope", "user")
    result = composer_run("compose", "refine", "my-skill", "--scope", "user")
    assert "deployed: yes" in result.stdout


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
