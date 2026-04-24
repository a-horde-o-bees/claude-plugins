"""Shared fixtures for integration tests."""

import subprocess
import sys
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


def _install_research_scripts_on_syspath() -> None:
    """Make `logs/research/_scripts/` importable for integration tests.

    Cross-corpus research utilities live outside any plugin package, so
    they aren't reachable through the plugin's venv import path. Tests
    that use `sample_tools` etc. depend on this sys.path insertion; it
    runs at conftest import time so test collection succeeds.
    """
    scripts_dir = _git_root() / "logs" / "research" / "_scripts"
    if scripts_dir.is_dir() and str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))


_install_research_scripts_on_syspath()


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
