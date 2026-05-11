"""Shared fixtures for setup system tests."""

import subprocess
from pathlib import Path

import pytest


@pytest.fixture
def git_project_dir(tmp_path: Path) -> Path:
    """tmp_path with `git init` so deploy-side setup verbs accept it.

    `run_init`, `run_enable`, and `run_disable` require their resolved
    project directory to be inside a git repository — see the gate in
    `_orchestration._require_git_project_dir`. Tests that exercise these
    verbs need a git-initialized project root, but do not need a full
    sandbox worktree (which the `sandbox_worktree` fixture provides for
    tests that depend on the live project's git state).
    """
    subprocess.run(
        ["git", "init", "--quiet", str(tmp_path)],
        check=True, capture_output=True,
    )
    return tmp_path
