"""Shared fixtures for navigator unit tests.

Sets CLAUDE_PROJECT_DIR to tmp_path/project for every test and returns
both paths via the `project_dir` fixture. tmp_path stays as a
workspace for test databases and other non-project artifacts that the
scanner should not see. Tests that need their own nested project root
override CLAUDE_PROJECT_DIR in their own fixture via monkeypatch.setenv.
"""

from pathlib import Path

import pytest

from lib.navigator._db import get_connection, SCHEMA


@pytest.fixture(autouse=True)
def project_dir(tmp_path, monkeypatch) -> Path:
    """Project root anchored inside tmp_path, isolated from test artifacts."""
    project = tmp_path / "project"
    project.mkdir(exist_ok=True)
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(project))
    return project


@pytest.fixture
def db_path(tmp_path):
    """Create a temporary database with schema at tmp_path root.

    Lives outside the per-test CLAUDE_PROJECT_DIR (tmp_path/project) so
    the scanner doesn't index the database file as a project entry.
    """
    path = str(tmp_path / "test.db")
    conn = get_connection(path)
    conn.executescript(SCHEMA)
    conn.close()
    return path


@pytest.fixture
def populated_db(db_path, project_dir):
    """Database with sample entries and real files on disk matching them.

    Files are created under the project_dir so the scanner's reconciliation
    leaves the fixture entries in place instead of deleting them.
    """
    files = {
        "src/lib/utils.py": "utils",
        "src/lib/core.py": "core",
        "src/main.py": "main",
        "src/config.py": "",
    }
    for rel, content in files.items():
        target = project_dir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)

    conn = get_connection(db_path)
    entries = [
        ("src", None, "directory", 0, 1, "Source code", None),
        ("src/lib", "src", "directory", 0, 1, "Library modules", None),
        ("src/lib/utils.py", "src/lib", "file", 0, 1, "Utility functions", None),
        ("src/lib/core.py", "src/lib", "file", 0, 1, None, None),
        ("src/main.py", "src", "file", 0, 1, "Application entry point", None),
        ("src/config.py", "src", "file", 0, 1, "", None),
    ]
    for e in entries:
        conn.execute(
            "INSERT INTO entries (path, parent_path, entry_type, exclude, traverse, description, git_hash) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)", e,
        )
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def db_with_patterns(db_path):
    """Database with glob patterns in the patterns table."""
    conn = get_connection(db_path)
    pats = [
        ("**/__pycache__", None, 1, 0, None),
        ("**/tests", None, 0, 0, "Test suites"),
        ("**/__init__.py", None, 0, 1, "Package marker"),
    ]
    for p in pats:
        conn.execute(
            "INSERT INTO patterns (pattern, entry_type, exclude, traverse, description) "
            "VALUES (?, ?, ?, ?, ?)", p,
        )
    conn.commit()
    conn.close()
    return db_path
