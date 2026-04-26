"""Fixtures for transcripts tests.

Redirects ~/.claude/projects/ to a tmp directory via the CLAUDE_HOME env
var so tests never touch the real Claude Code projects directory. Pairs
with CLAUDE_PROJECT_DIR for tests that exercise `project_path()`.
"""

from pathlib import Path

import pytest


@pytest.fixture
def projects_root(tmp_path, monkeypatch) -> Path:
    """Redirect ~/.claude/projects/ to `tmp_path / .claude / projects`.

    `tools.environment.get_claude_home()` honors CLAUDE_HOME; the system's
    `_user_dir()` is `get_claude_home() / "projects"`, so setting
    CLAUDE_HOME points the projects root at the tmp directory transparently.
    """
    claude_home = tmp_path / ".claude"
    root = claude_home / "projects"
    root.mkdir(parents=True)
    monkeypatch.setenv("CLAUDE_HOME", str(claude_home))
    return root


@pytest.fixture
def project_dir(projects_root) -> Path:
    """Create a single project dir with a standard encoded name."""
    p = projects_root / "-test-project"
    p.mkdir()
    return p
