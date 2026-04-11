"""Integration tests for the stash MCP server.

Exercises the full stack: server tool functions → skill layer → SQLite.
No mocking — uses real temp databases. Includes cross-scope promotion.
"""

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

import servers.stash.__main__ as stash_server


@pytest.fixture
def dbs(tmp_path):
    """Patch both project and user DB paths to temp databases."""
    project_db = str(tmp_path / "project_stash.db")
    user_db = str(tmp_path / "user_stash.db")
    with (
        patch.object(stash_server, "_project_db", return_value=project_db),
        patch.object(stash_server, "_user_db", return_value=user_db),
    ):
        yield {"project": project_db, "user": user_db}


def _parse(result: str) -> dict:
    return json.loads(result)


class TestStashLifecycle:
    """Add → list → search → get → update → get → remove in project scope."""

    def test_full_lifecycle(self, dbs):
        # Add
        r1 = _parse(stash_server.stash_add("Investigate caching for paths_list"))
        assert r1["id"] == 1
        assert r1["has_detail"] is False

        r2 = _parse(stash_server.stash_add(
            "Convention gate hook",
            detail_md="## Approach\n\nPreToolUse hook on Edit|Write.\n\n## Blocked by\n\nRetry loop problem.",
        ))
        assert r2["id"] == 2
        assert r2["has_detail"] is True

        # List all
        listing = _parse(stash_server.stash_list())
        assert listing["total"] == 2
        assert all("detail_md" not in e for e in listing["entries"])

        # List by ids
        specific = _parse(stash_server.stash_list(ids=[2]))
        assert len(specific["entries"]) == 1

        # Search
        found = _parse(stash_server.stash_search("caching"))
        assert found["total"] == 1
        assert found["entries"][0]["id"] == 1

        # Search in detail_md
        found2 = _parse(stash_server.stash_search("retry loop"))
        assert found2["total"] == 1
        assert found2["entries"][0]["id"] == 2

        # Get full detail
        full = _parse(stash_server.stash_get([2]))
        assert "## Approach" in full["entries"][0]["detail_md"]

        # Update summary
        updated = _parse(stash_server.stash_update(1, summary="Investigate read caching for paths_list"))
        assert "read caching" in updated["summary"]
        assert updated["updated_at"] != updated["created_at"]

        # Update: add detail
        updated2 = _parse(stash_server.stash_update(1, detail_md="Could use LRU with TTL."))
        assert updated2["has_detail"] is True

        # Update: clear detail
        cleared = _parse(stash_server.stash_update(1, detail_md=""))
        assert cleared["has_detail"] is False

        # Remove
        removed = _parse(stash_server.stash_remove(1))
        assert removed["removed"]["id"] == 1
        assert removed["remaining"] == 1

        # Verify
        after = _parse(stash_server.stash_list())
        assert after["total"] == 1


class TestStashScopes:
    """Project and user scopes are independent databases."""

    def test_scopes_are_isolated(self, dbs):
        _parse(stash_server.stash_add("project idea", scope="project"))
        _parse(stash_server.stash_add("cross-project idea", scope="user"))

        project = _parse(stash_server.stash_list(scope="project"))
        user = _parse(stash_server.stash_list(scope="user"))

        assert project["total"] == 1
        assert project["entries"][0]["summary"] == "project idea"
        assert user["total"] == 1
        assert user["entries"][0]["summary"] == "cross-project idea"

    def test_cross_scope_promotion(self, dbs):
        # Add to user scope
        added = _parse(stash_server.stash_add("idea born in user scope", scope="user"))
        user_id = added["id"]

        # Verify it's in user
        user_list = _parse(stash_server.stash_list(scope="user"))
        assert user_list["total"] == 1

        # Promote to project via update with scope="project"
        promoted = _parse(stash_server.stash_update(user_id, scope="project"))
        assert promoted["action"] == "promoted"
        assert promoted["from_scope"] == "user"
        assert promoted["to_scope"] == "project"
        assert promoted["entry"]["summary"] == "idea born in user scope"

        # Verify: gone from user, present in project
        user_after = _parse(stash_server.stash_list(scope="user"))
        assert user_after["total"] == 0
        project_after = _parse(stash_server.stash_list(scope="project"))
        assert project_after["total"] == 1

    def test_promotion_with_summary_update(self, dbs):
        added = _parse(stash_server.stash_add("vague idea", scope="user"))
        promoted = _parse(stash_server.stash_update(
            added["id"], summary="refined idea for this project", scope="project",
        ))
        assert promoted["entry"]["summary"] == "refined idea for this project"


class TestStashErrors:

    def test_update_nonexistent_either_scope(self, dbs):
        result = _parse(stash_server.stash_update(999, summary="nope"))
        assert "error" in result

    def test_remove_nonexistent(self, dbs):
        result = _parse(stash_server.stash_remove(999))
        assert "error" in result

    def test_get_nonexistent_returns_empty(self, dbs):
        result = _parse(stash_server.stash_get([999]))
        assert result["entries"] == []
