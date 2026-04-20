"""Shared fixtures for sandbox integration tests.

Each test gets a fresh tmp git repo with one initial commit on `main`
and a bare origin remote, with `CLAUDE_PROJECT_DIR` pointing at the
working repo. Tests exercise real `git worktree` commands against
these isolated repos — no interaction with the project repository
running the test suite.
"""

import subprocess
from pathlib import Path

import pytest


@pytest.fixture
def project_repo(tmp_path, monkeypatch) -> Path:
    project = tmp_path / "claude-plugins"
    project.mkdir()
    origin = tmp_path / "claude-plugins.git"
    subprocess.run(
        ["git", "init", "--quiet", "--bare", "-b", "main", str(origin)],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(project), "init", "--quiet", "-b", "main"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(project), "config", "user.email", "test@example.com"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(project), "config", "user.name", "Test"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(project), "remote", "add", "origin", str(origin)],
        check=True,
    )
    (project / "README.md").write_text("initial\n")
    subprocess.run(
        ["git", "-C", str(project), "add", "README.md"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(project), "commit", "-m", "init", "--quiet"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(project), "push", "-u", "origin", "main", "--quiet"],
        check=True,
    )
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(project))
    return project
