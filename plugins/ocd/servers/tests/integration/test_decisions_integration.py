"""Integration tests for the decisions MCP server.

Exercises the full stack: server tool functions → skill layer → SQLite.
No mocking — uses real temp databases.
"""

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

import servers.decisions.__main__ as decisions_server


@pytest.fixture
def db(tmp_path):
    """Patch _db_path to return a temp database path."""
    db_path = str(tmp_path / "decisions.db")
    with patch.object(decisions_server, "_db_path", return_value=db_path):
        yield db_path


def _parse(result: str) -> dict:
    return json.loads(result)


class TestDecisionsLifecycle:
    """Add → list → search → get → update → get → remove."""

    def test_full_lifecycle(self, db):
        # Add without detail
        r1 = _parse(decisions_server.decisions_add("Use SQLite for storage"))
        assert r1["id"] == 1
        assert r1["has_detail"] is False

        # Add with detail
        r2 = _parse(decisions_server.decisions_add(
            "Unified verb set across all MCPs",
            detail_md="## Context\n\nEach MCP had its own naming.\n\n## Decision\n\nStandardize on add/list/search/get/update/remove.",
        ))
        assert r2["id"] == 2
        assert r2["has_detail"] is True

        # List all
        listing = _parse(decisions_server.decisions_list())
        assert listing["total"] == 2
        assert len(listing["entries"]) == 2
        assert all("detail_md" not in e for e in listing["entries"])

        # List by ids
        specific = _parse(decisions_server.decisions_list(ids=[2]))
        assert len(specific["entries"]) == 1
        assert specific["entries"][0]["id"] == 2

        # List with limit
        limited = _parse(decisions_server.decisions_list(limit=1))
        assert len(limited["entries"]) == 1

        # Search
        found = _parse(decisions_server.decisions_search("verb"))
        assert found["total"] == 1
        assert found["entries"][0]["id"] == 2

        # Search in detail_md
        found2 = _parse(decisions_server.decisions_search("naming"))
        assert found2["total"] == 1

        # Get full detail
        full = _parse(decisions_server.decisions_get([2]))
        assert len(full["entries"]) == 1
        assert "## Context" in full["entries"][0]["detail_md"]
        assert full["entries"][0]["summary"] == "Unified verb set across all MCPs"

        # Update summary
        updated = _parse(decisions_server.decisions_update(1, summary="Use SQLite with WAL for storage"))
        assert updated["summary"] == "Use SQLite with WAL for storage"
        assert updated["updated_at"] != updated["created_at"]

        # Update: add detail_md to a previously detail-less entry
        updated2 = _parse(decisions_server.decisions_update(1, detail_md="## Rationale\n\nZero-dependency."))
        assert updated2["has_detail"] is True

        # Verify via get
        full2 = _parse(decisions_server.decisions_get([1]))
        assert "Zero-dependency" in full2["entries"][0]["detail_md"]

        # Update: clear detail_md
        cleared = _parse(decisions_server.decisions_update(1, detail_md=""))
        assert cleared["has_detail"] is False

        # Remove
        removed = _parse(decisions_server.decisions_remove(1))
        assert removed["removed"]["id"] == 1
        assert removed["remaining"] == 1

        # Verify removal
        after = _parse(decisions_server.decisions_list())
        assert after["total"] == 1


class TestDecisionsErrors:

    def test_update_nonexistent(self, db):
        result = _parse(decisions_server.decisions_update(999, summary="nope"))
        assert "error" in result

    def test_remove_nonexistent(self, db):
        result = _parse(decisions_server.decisions_remove(999))
        assert "error" in result

    def test_get_nonexistent_returns_empty(self, db):
        result = _parse(decisions_server.decisions_get([999]))
        assert result["entries"] == []

    def test_search_no_match(self, db):
        result = _parse(decisions_server.decisions_search("zzzznotfound"))
        assert result["total"] == 0
