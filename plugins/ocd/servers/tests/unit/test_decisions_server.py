"""Server wiring tests for decisions MCP server.

Verifies that the thin server layer correctly delegates to
servers.decisions and wraps results with _ok/_err. Does not spin up
FastMCP — tests the tool functions directly with a real temp database.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

import servers.decisions.__main__ as server


@pytest.fixture
def db_path(tmp_path: Path) -> str:
    """Isolated database path, patched into the server's _db_path."""
    path = str(tmp_path / "test_decisions.db")
    with patch.object(server, "_db_path", return_value=path):
        yield path


class TestServerDelegation:
    """Verify server tools delegate to skill functions and wrap responses."""

    def test_add_delegates_and_wraps(self, db_path: str) -> None:
        raw = server.decisions_add(summary="Test decision")
        result = json.loads(raw)
        assert result["id"] == 1
        assert result["summary"] == "Test decision"
        assert result["has_detail"] is False

    def test_list_returns_json(self, db_path: str) -> None:
        server.decisions_add(summary="A")
        server.decisions_add(summary="B")
        raw = server.decisions_list()
        result = json.loads(raw)
        assert result["total"] == 2
        assert len(result["entries"]) == 2

    def test_get_returns_full_content(self, db_path: str) -> None:
        server.decisions_add(summary="Rich", detail_md="Full detail")
        raw = server.decisions_get(ids=[1])
        result = json.loads(raw)
        assert result["entries"][0]["detail_md"] == "Full detail"

    def test_error_wrapping(self, db_path: str) -> None:
        raw = server.decisions_update(id=999, summary="Ghost")
        result = json.loads(raw)
        assert "error" in result
        assert "999" in result["error"]

    def test_remove_delegates(self, db_path: str) -> None:
        server.decisions_add(summary="To remove")
        raw = server.decisions_remove(id=1)
        result = json.loads(raw)
        assert result["removed"]["id"] == 1
        assert result["remaining"] == 0
