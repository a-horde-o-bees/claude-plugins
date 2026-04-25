"""Shared fixtures for integration tests."""

import subprocess
import tempfile
from pathlib import Path

import pytest


def _git_root() -> Path:
    """Resolve the enclosing git root anchored at this conftest's directory.

    Using `git -C <dir>` instead of relying on the subprocess's CWD
    keeps the helper correct regardless of where pytest is invoked.
    Anchoring to `Path(__file__).parent` (rather than walking multiple
    `.parent` levels) is legitimate here — conftest.py is the blessed
    anchor per the Python-check allowlist (`**/conftest.py`).
    """
    conftest_dir = Path(__file__).parent
    result = subprocess.run(
        ["git", "-C", str(conftest_dir), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
    )
    return Path(result.stdout.strip()).resolve()


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Absolute path to the project's main working tree.

    Tests that need to read the project's current files (e.g. to copy
    the working-tree pre-commit hook into the disposable worktree
    before exercising it) use this rather than walking `__file__`
    themselves — conftest.py is the blessed anchor per the python-check
    allowlist.
    """
    return _git_root()


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
