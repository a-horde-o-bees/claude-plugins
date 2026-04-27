"""Shared fixtures for needs_map tests.

Per-test CLAUDE_PROJECT_DIR anchored inside tmp_path, plus a ready-to-use
connection against a freshly-initialized schema. Tests that seed entities
use the `conn` fixture directly; tests that exercise init() or status()
through the plugin helpers rely on the env-var isolation.
"""

from pathlib import Path

import pytest

from systems.needs_map._db import get_connection, init_db


@pytest.fixture(autouse=True)
def project_dir(tmp_path, monkeypatch) -> Path:
    """Project root inside tmp_path with CLAUDE_PROJECT_DIR set."""
    project = tmp_path / "project"
    project.mkdir(exist_ok=True)
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(project))
    return project


@pytest.fixture
def db_path(tmp_path) -> str:
    """Path to a freshly-initialized DB file outside the project root."""
    path = str(tmp_path / "test.db")
    init_db(path)
    return path


@pytest.fixture
def conn(db_path):
    """Open SQLite connection against the initialized schema."""
    connection = get_connection(db_path)
    try:
        yield connection
    finally:
        connection.close()
