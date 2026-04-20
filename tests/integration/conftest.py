"""Shared fixtures for integration tests."""

import subprocess
import tempfile
from pathlib import Path

import pytest


def _git_root() -> Path:
    """Anchor at the enclosing git root rather than walking __file__ parents.

    Mirrors framework.get_project_dir()'s fallback. The project venv
    has no access to the plugin framework module, so tests at project
    level invoke git directly instead of importing the helper.
    """
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
    )
    return Path(result.stdout.strip()).resolve()


@pytest.fixture(scope="session")
def worktree():
    """Disposable git worktree for integration tests.

    Tests that interact with git state (staging, hooks) run in an
    isolated worktree so they cannot affect the main working tree.
    Session-scoped — one worktree shared across all integration tests.
    """
    root = _git_root()
    with tempfile.TemporaryDirectory() as tmp:
        wt_path = Path(tmp) / "integration-worktree"
        subprocess.run(
            ["git", "worktree", "add", str(wt_path), "HEAD", "--detach"],
            cwd=root,
            capture_output=True,
            check=True,
        )
        yield wt_path
        subprocess.run(
            ["git", "worktree", "remove", str(wt_path), "--force"],
            cwd=root,
            capture_output=True,
        )
