"""Shared fixtures for integration tests."""

import subprocess
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent.parent


@pytest.fixture(scope="session")
def worktree():
    """Disposable git worktree for integration tests.

    Tests that interact with git state (staging, hooks) run in an
    isolated worktree so they cannot affect the main working tree.
    Session-scoped — one worktree shared across all integration tests.
    """
    with tempfile.TemporaryDirectory() as tmp:
        wt_path = Path(tmp) / "integration-worktree"
        subprocess.run(
            ["git", "worktree", "add", str(wt_path), "HEAD", "--detach"],
            cwd=ROOT,
            capture_output=True,
            check=True,
        )
        yield wt_path
        subprocess.run(
            ["git", "worktree", "remove", str(wt_path), "--force"],
            cwd=ROOT,
            capture_output=True,
        )
