"""Integration tests for the navigator MCP server.

Exercises the server tool functions through the full stack: server → skill → SQLite.
Scan is mocked (tested extensively in skill unit tests) to isolate server behavior.
"""

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from servers.navigator._db import get_connection, SCHEMA
import servers.navigator as nav_skill
import servers.navigator.__main__ as nav_server


@pytest.fixture
def db(tmp_path, monkeypatch):
    """Create a temp DB with schema and seed entries, patch server to use it.

    The facade's _ensure_scanned is mocked out — scan behavior is tested
    extensively in skill unit tests, and integration tests here isolate
    server behavior from filesystem reconciliation.
    """
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    db_path = str(tmp_path / "nav.db")
    conn = get_connection(db_path)
    conn.executescript(SCHEMA)

    entries = [
        ("src", None, "directory", 0, 1, "Source code"),
        ("src/main.py", "src", "file", 0, 1, "Application entry point"),
        ("src/utils.py", "src", "file", 0, 1, "Shared utility functions"),
        ("src/config.py", "src", "file", 0, 1, None),
        ("docs", None, "directory", 0, 1, "Project documentation"),
        ("docs/README.md", "docs", "file", 0, 1, "User-facing overview"),
    ]
    for path, parent, etype, excl, trav, desc in entries:
        conn.execute(
            "INSERT INTO entries (path, parent_path, entry_type, exclude, traverse, description) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (path, parent, etype, excl, trav, desc),
        )
    conn.commit()
    conn.close()

    with (
        patch.object(nav_server, "DB_PATH", db_path),
        patch.object(nav_skill, "_ensure_scanned", return_value=None),
        patch.object(nav_server, "_check_db", return_value=None),
    ):
        yield db_path


def _parse(result: str) -> dict:
    return json.loads(result)


class TestPathsGet:
    """paths_get — renamed from paths_describe, now accepts single or multiple paths."""

    def test_single_file(self, db):
        result = _parse(nav_server.paths_get("src/main.py"))
        assert result["path"] == "src/main.py"
        assert result["description"] == "Application entry point"
        assert result["type"] == "file"

    def test_single_directory_has_children(self, db):
        result = _parse(nav_server.paths_get("src"))
        assert result["path"] == "src/"
        assert result["type"] == "directory"
        assert "children" in result
        child_paths = {c["path"] for c in result["children"]}
        assert "src/main.py" in child_paths
        assert "src/utils.py" in child_paths

    def test_multi_path_returns_entries_list(self, db):
        result = _parse(nav_server.paths_get(["src/main.py", "docs/README.md"]))
        assert "entries" in result
        assert len(result["entries"]) == 2
        paths = {e["path"] for e in result["entries"]}
        assert paths == {"src/main.py", "docs/README.md"}

    def test_not_found(self, db):
        result = _parse(nav_server.paths_get("nonexistent.py"))
        assert "not_found" in result or result.get("description") is None

    def test_list_input_single_element(self, db):
        result = _parse(nav_server.paths_get(["src/main.py"]))
        assert "entries" in result
        assert len(result["entries"]) == 1


class TestPathsUpsert:
    """paths_upsert — renamed from paths_set, create-or-update semantics."""

    def test_update_existing_description(self, db):
        result = _parse(nav_server.paths_upsert("src/main.py", description="CLI entry point"))
        assert result["action"] == "updated"
        assert result["path"] == "src/main.py"

        # Verify via get
        entry = _parse(nav_server.paths_get("src/main.py"))
        assert entry["description"] == "CLI entry point"

    def test_describe_previously_null(self, db):
        result = _parse(nav_server.paths_upsert("src/config.py", description="Runtime configuration"))
        assert result["action"] == "updated"

        entry = _parse(nav_server.paths_get("src/config.py"))
        assert entry["description"] == "Runtime configuration"

    def test_no_changes(self, db):
        result = _parse(nav_server.paths_upsert("src/main.py"))
        assert result["action"] == "none"

    def test_set_exclude_flag(self, db):
        result = _parse(nav_server.paths_upsert("src/config.py", exclude=1))
        assert result["action"] == "updated"


class TestPathsList:
    """paths_list — directory file listing with optional filters.

    paths_list queries the DB for non-excluded file entries under a path.
    It filters by traverse/exclude flags and parent_path relationships.
    """

    def test_list_returns_list(self, db):
        result = _parse(nav_server.paths_list("."))
        assert isinstance(result, list)


class TestPathsSearch:
    """paths_search — description keyword search."""

    def test_finds_by_description(self, db):
        result = _parse(nav_server.paths_search("utility"))
        assert len(result["results"]) >= 1
        assert any(r["path"] == "src/utils.py" for r in result["results"])

    def test_case_insensitive(self, db):
        result = _parse(nav_server.paths_search("APPLICATION"))
        assert len(result["results"]) >= 1

    def test_no_match(self, db):
        result = _parse(nav_server.paths_search("zzzznotfound"))
        assert len(result["results"]) == 0


class TestPathsRemove:
    """paths_remove — delete entries."""

    def test_remove_single(self, db):
        result = _parse(nav_server.paths_remove("src/config.py"))
        assert result["action"] == "removed"
        assert result["path"] == "src/config.py"

    def test_remove_not_found(self, db):
        result = _parse(nav_server.paths_remove("nonexistent.py"))
        assert result["action"] == "not_found"


class TestErrorWrapping:
    """Server wraps exceptions in JSON error responses."""

    def test_db_missing(self, db):
        """When _check_db returns error, tool functions return it."""
        with patch.object(nav_server, "_check_db", return_value='{"error": "no db"}'):
            result = _parse(nav_server.paths_get("src"))
            assert result["error"] == "no db"
