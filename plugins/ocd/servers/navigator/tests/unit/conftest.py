"""Shared fixtures for navigator unit tests.

Sets CLAUDE_PROJECT_DIR to tmp_path/project for every test and returns
both paths via the `project_dir` fixture. tmp_path stays as a
workspace for test databases and other non-project artifacts that the
scanner should not see. Tests that need their own nested project root
override CLAUDE_PROJECT_DIR in their own fixture via monkeypatch.setenv.
"""

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def project_dir(tmp_path, monkeypatch) -> Path:
    """Project root anchored inside tmp_path, isolated from test artifacts."""
    project = tmp_path / "project"
    project.mkdir(exist_ok=True)
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(project))
    return project
