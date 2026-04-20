"""Integration tests for the navigator MCP server.

Exercises the server tool functions through the full stack: server → skill → SQLite.
Scan is mocked (tested extensively in skill unit tests) to isolate server behavior.
"""

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

import framework

PLUGIN_ROOT = framework.get_plugin_root()
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from systems.navigator._db import get_connection, SCHEMA
import systems.navigator as nav_lib
import systems.navigator.server as nav_server


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
            "INSERT INTO paths (path, parent_path, entry_type, exclude, traverse, purpose) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (path, parent, etype, excl, trav, desc),
        )
    conn.commit()
    conn.close()

    with (
        patch.object(nav_server, "DB_PATH", db_path),
        patch.object(nav_lib, "_ensure_scanned", return_value=None),
    ):
        yield db_path


def _parse(result: str) -> dict:
    return json.loads(result)


class TestPathsGet:
    """paths_get — renamed from paths_describe, now accepts single or multiple paths."""

    def test_single_file(self, db):
        result = _parse(nav_server.paths_get("src/main.py"))
        assert result["path"] == "src/main.py"
        assert result["purpose"] == "Application entry point"
        assert result["type"] == "file"

    def test_single_directory_has_children(self, db):
        result = _parse(nav_server.paths_get("src"))
        assert result["path"] == "src/"
        assert result["type"] == "directory"
        assert "children" in result
        child_paths = {c["path"] for c in result["children"]}
        assert "src/main.py" in child_paths
        assert "src/utils.py" in child_paths

    def test_multi_path_returns_paths_list(self, db):
        result = _parse(nav_server.paths_get(["src/main.py", "docs/README.md"]))
        assert "paths" in result
        assert len(result["paths"]) == 2
        paths = {e["path"] for e in result["paths"]}
        assert paths == {"src/main.py", "docs/README.md"}

    def test_not_found(self, db):
        result = _parse(nav_server.paths_get("nonexistent.py"))
        assert "not_found" in result or result.get("purpose") is None

    def test_list_input_single_element(self, db):
        result = _parse(nav_server.paths_get(["src/main.py"]))
        assert "paths" in result
        assert len(result["paths"]) == 1


class TestPathsUpsert:
    """paths_upsert — renamed from paths_set, create-or-update semantics."""

    def test_update_existing_description(self, db):
        result = _parse(nav_server.paths_upsert("src/main.py", purpose="CLI entry point"))
        assert result["action"] == "updated"
        assert result["path"] == "src/main.py"

        # Verify via get
        entry = _parse(nav_server.paths_get("src/main.py"))
        assert entry["purpose"] == "CLI entry point"

    def test_describe_previously_null(self, db):
        result = _parse(nav_server.paths_upsert("src/config.py", purpose="Runtime configuration"))
        assert result["action"] == "updated"

        entry = _parse(nav_server.paths_get("src/config.py"))
        assert entry["purpose"] == "Runtime configuration"

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
    """Server wraps facade exceptions in JSON error responses."""

    def test_facade_raises_is_wrapped(self, db):
        result = _parse(nav_server.paths_remove("anything", mode="badmode"))
        assert "error" in result
        assert "mode must be one of" in result["error"]


class TestReady:
    """ready() is the dormancy predicate — file presence plus schema subset check."""

    def test_absent_db_returns_false(self, tmp_path):
        assert nav_lib.ready(tmp_path / "missing.db") is False

    def test_valid_schema_returns_true(self, tmp_path):
        db_path = tmp_path / "valid.db"
        conn = get_connection(str(db_path))
        conn.executescript(SCHEMA)
        conn.close()
        assert nav_lib.ready(db_path) is True

    def test_divergent_schema_returns_false(self, tmp_path):
        db_path = tmp_path / "divergent.db"
        conn = get_connection(str(db_path))
        conn.executescript("CREATE TABLE unrelated (x INTEGER)")
        conn.close()
        assert nav_lib.ready(db_path) is False


class TestEnsureReady:
    """ensure_ready() raises NotReadyError with an actionable message when not operational."""

    def test_absent_db_raises(self, tmp_path, monkeypatch):
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
        with pytest.raises(framework.NotReadyError) as exc:
            nav_lib.ensure_ready()
        assert "dormant" in str(exc.value).lower()
        assert "/ocd:setup" in str(exc.value)

    def test_valid_schema_does_not_raise(self, tmp_path, monkeypatch):
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
        db_path = tmp_path / ".claude" / "ocd" / "navigator" / "navigator.db"
        db_path.parent.mkdir(parents=True)
        conn = get_connection(str(db_path))
        conn.executescript(SCHEMA)
        conn.close()
        nav_lib.ensure_ready()  # should not raise
