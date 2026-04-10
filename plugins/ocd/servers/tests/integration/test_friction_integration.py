"""Integration tests for the friction MCP server.

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

from servers import friction as friction_server


@pytest.fixture
def db(tmp_path):
    """Patch FRICTION_DB to a temp database for the duration of the test."""
    db_path = str(tmp_path / "friction.db")
    with patch.object(friction_server, "FRICTION_DB", db_path):
        yield db_path


def _parse(result: str) -> dict:
    return json.loads(result)


# --- Full lifecycle ---


class TestFrictionLifecycle:
    """Add → list → search → get → update → get → remove."""

    def test_full_lifecycle(self, db):
        # Add
        r = _parse(friction_server.friction_add("navigator", "paths_search lacks regex"))
        assert r["id"] == 1
        assert r["system"] == "navigator"
        assert r["has_detail"] is False

        r2 = _parse(friction_server.friction_add(
            "navigator", "scope_analyze slow on large repos",
            detail_md="## Expected\n\nUnder 2 seconds.\n\n## Workaround\n\nLimit depth.",
        ))
        assert r2["id"] == 2
        assert r2["has_detail"] is True

        r3 = _parse(friction_server.friction_add("stash", "promote fails silently"))
        assert r3["id"] == 3

        # List all
        listing = _parse(friction_server.friction_list())
        assert listing["total"] == 3
        assert len(listing["entries"]) == 3
        assert all("detail_md" not in e for e in listing["entries"])

        # List by system
        nav_only = _parse(friction_server.friction_list(system="navigator"))
        assert nav_only["total"] == 2

        # List by ids
        specific = _parse(friction_server.friction_list(ids=[1, 3]))
        assert len(specific["entries"]) == 2
        ids_returned = {e["id"] for e in specific["entries"]}
        assert ids_returned == {1, 3}

        # Search
        found = _parse(friction_server.friction_search("regex"))
        assert found["total"] == 1
        assert found["entries"][0]["id"] == 1

        # Search in detail_md
        found2 = _parse(friction_server.friction_search("2 seconds"))
        assert found2["total"] == 1
        assert found2["entries"][0]["id"] == 2

        # Get full detail
        full = _parse(friction_server.friction_get([2]))
        assert len(full["entries"]) == 1
        assert "## Expected" in full["entries"][0]["detail_md"]

        # Update summary
        updated = _parse(friction_server.friction_update(1, summary="paths_search needs regex support"))
        assert updated["summary"] == "paths_search needs regex support"
        assert updated["updated_at"] != updated["created_at"]

        # Update: clear detail_md with empty string
        cleared = _parse(friction_server.friction_update(2, detail_md=""))
        assert cleared["has_detail"] is False

        # Verify cleared via get
        full2 = _parse(friction_server.friction_get([2]))
        assert full2["entries"][0]["detail_md"] is None

        # Systems list
        systems = _parse(friction_server.friction_systems_list())
        assert systems["total_systems"] == 2
        assert systems["total_entries"] == 3
        names = {s["name"] for s in systems["systems"]}
        assert names == {"navigator", "stash"}

        # Remove
        removed = _parse(friction_server.friction_remove(1))
        assert removed["removed"]["id"] == 1
        assert removed["remaining"] == 2

        # Verify removed
        after = _parse(friction_server.friction_list())
        assert after["total"] == 2


class TestFrictionErrors:
    """Error paths return JSON error responses."""

    def test_invalid_system_name(self, db):
        result = _parse(friction_server.friction_add("bad/system", "summary"))
        assert "error" in result

    def test_update_nonexistent(self, db):
        result = _parse(friction_server.friction_update(999, summary="nope"))
        assert "error" in result

    def test_remove_nonexistent(self, db):
        result = _parse(friction_server.friction_remove(999))
        assert "error" in result

    def test_get_nonexistent_returns_empty(self, db):
        result = _parse(friction_server.friction_get([999]))
        assert result["entries"] == []

    def test_search_no_match(self, db):
        result = _parse(friction_server.friction_search("zzzznotfound"))
        assert result["total"] == 0
