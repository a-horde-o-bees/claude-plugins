"""Shared pytest fixtures for the progressive-composer plugin test suite.

Tests run scripts in two modes:

- **In-process** — tests import `scripts.<module>` directly to exercise
  internal helpers (path resolution, registry I/O). The skill folder is
  added to `sys.path` once at conftest import time so `from scripts._paths
  import ...` resolves.

- **Subprocess** — tests invoke `python3 -m scripts.<verb>` via subprocess
  to exercise the full CLI-dispatch path (argparse, exit codes, stdout).
  The `composer_run` fixture wraps the invocation, sets cwd at the skill
  folder, and threads `CLAUDE_PLUGIN_DATA`/`CLAUDE_HOME`/`CLAUDE_PROJECT_DIR`
  env vars into the subprocess so writes land in the test's tmp_path.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SKILL_DIR = (
    PROJECT_ROOT
    / "plugins"
    / "progressive-composer"
    / "skills"
    / "progressive-composer"
)


sys.path.insert(0, str(SKILL_DIR))


@pytest.fixture
def isolated_env(tmp_path, monkeypatch):
    """Point plugin data dir, claude home, and project dir at tmp_path subdirs.

    Returns a dict with the resolved paths so tests can assert on file
    layouts directly.
    """
    plugin_data = tmp_path / "plugin_data"
    claude_home = tmp_path / "claude_home"
    project_dir = tmp_path / "project"
    for path in (plugin_data, claude_home, project_dir):
        path.mkdir(parents=True, exist_ok=True)

    monkeypatch.setenv("CLAUDE_PLUGIN_DATA", str(plugin_data))
    monkeypatch.setenv("CLAUDE_HOME", str(claude_home))
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(project_dir))

    return {
        "plugin_data": plugin_data,
        "claude_home": claude_home,
        "project_dir": project_dir,
    }


@pytest.fixture
def composer_run(isolated_env):
    """Subprocess invocation of `uv run -m scripts.<verb> [args...]`.

    Returns a callable that takes the verb plus argv and returns the
    completed-process result. Cwd defaults to the skill folder; env is
    inherited from `isolated_env` so writes land under tmp_path. Uses
    `uv run` to match SKILL.md's documented invocation form, so tests
    exercise the same path the agent would.
    """

    def _run(verb: str, *args: str, check: bool = True) -> subprocess.CompletedProcess:
        result = subprocess.run(
            ["uv", "run", "-m", f"scripts.{verb}", *args],
            cwd=SKILL_DIR,
            env=os.environ.copy(),
            capture_output=True,
            text=True,
        )
        if check and result.returncode != 0:
            raise AssertionError(
                f"composer-run {verb} {args} exited {result.returncode}\n"
                f"stdout: {result.stdout}\nstderr: {result.stderr}"
            )
        return result

    return _run


@pytest.fixture
def fixture_repo(tmp_path):
    """Bare-bones git repo containing a fake skill folder.

    Created at `tmp_path/fixture-source/` with one skill at
    `skills/fixture-skill/SKILL.md`. Suitable as a `track` target for
    tests that don't want to hit a real upstream.
    """
    repo = tmp_path / "fixture-source"
    repo.mkdir()
    skill = repo / "skills" / "fixture-skill"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: fixture-skill\ndescription: a fixture\n---\n# fixture\n"
    )
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(
        ["git", "-c", "user.email=test@test", "-c", "user.name=test", "commit", "-qm", "init"],
        cwd=repo,
        check=True,
    )
    return repo


@pytest.fixture
def commit_to_fixture(fixture_repo):
    """Commit a change to the fixture repo. Returns a callable.

    Usage in tests:
        commit_to_fixture("skills/fixture-skill/extra.md", "new content")
        commit_to_fixture("skills/another-skill/SKILL.md", "...", message="add another skill")

    The callable creates parent directories as needed, writes the file,
    stages it, and commits. Caller's drift-detection assertions can rely
    on the new commit existing on the tracked branch.
    """

    def _commit(rel_path: str, content: str, message: str = "update") -> None:
        target = fixture_repo / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
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
                message,
            ],
            cwd=fixture_repo,
            check=True,
        )

    return _commit
