"""Shared fixtures for rules unit tests.

Sets CLAUDE_PROJECT_DIR and CLAUDE_HOME to scratch paths under tmp_path
so install/uninstall at user and project scope land in isolated
directories. Returns both roots via the `scopes` fixture.
"""

from dataclasses import dataclass
from pathlib import Path

import pytest


@dataclass
class Scopes:
    project: Path
    user: Path


@pytest.fixture(autouse=True)
def scopes(tmp_path, monkeypatch) -> Scopes:
    """Project and user roots anchored inside tmp_path."""
    project = tmp_path / "project"
    user = tmp_path / "user"
    project.mkdir()
    user.mkdir()
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(project))
    monkeypatch.setenv("CLAUDE_HOME", str(user))
    return Scopes(project=project, user=user)
