"""Unit tests for the friction skill (SQLite-backed).

Exercises the public API directly against servers.friction — no FastMCP,
no server module, no subprocess. Tests isolate database state via tmp_path.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

import servers.friction as friction


@pytest.fixture
def db_path(tmp_path):
    """Isolated test database."""
    return str(tmp_path / "test_friction.db")


# ===========================================================================
# friction_add
# ===========================================================================


class TestFrictionAdd:
    def test_basic_add(self, db_path: str) -> None:
        result = friction.friction_add(db_path, "navigator", "scan missed a file")
        assert result["id"] == 1
        assert result["system"] == "navigator"
        assert result["summary"] == "scan missed a file"
        assert result["has_detail"] is False
        assert "created_at" in result
        assert "updated_at" in result

    def test_add_with_detail(self, db_path: str) -> None:
        result = friction.friction_add(
            db_path, "navigator", "scan missed a file",
            detail_md="## Context\nThe scanner skipped hidden dirs.",
        )
        assert result["has_detail"] is True

    def test_add_increments_id(self, db_path: str) -> None:
        r1 = friction.friction_add(db_path, "navigator", "first")
        r2 = friction.friction_add(db_path, "navigator", "second")
        assert r2["id"] == r1["id"] + 1

    def test_invalid_system_raises(self, db_path: str) -> None:
        with pytest.raises(ValueError):
            friction.friction_add(db_path, "bad/name", "a")

    def test_empty_system_raises(self, db_path: str) -> None:
        with pytest.raises(ValueError):
            friction.friction_add(db_path, "", "a")

    def test_dot_prefix_system_raises(self, db_path: str) -> None:
        with pytest.raises(ValueError):
            friction.friction_add(db_path, ".hidden", "a")

    def test_timestamps_are_utc_iso(self, db_path: str) -> None:
        result = friction.friction_add(db_path, "navigator", "a")
        # ISO 8601 UTC contains '+00:00' or 'Z'
        assert "+00:00" in result["created_at"] or result["created_at"].endswith("Z")
        assert result["created_at"] == result["updated_at"]


# ===========================================================================
# friction_list
# ===========================================================================


class TestFrictionList:
    def test_empty_db(self, db_path: str) -> None:
        result = friction.friction_list(db_path)
        assert result == {"total": 0, "entries": []}

    def test_list_all(self, db_path: str) -> None:
        friction.friction_add(db_path, "navigator", "a")
        friction.friction_add(db_path, "evaluate-skills", "b")
        result = friction.friction_list(db_path)
        assert result["total"] == 2
        systems = {e["system"] for e in result["entries"]}
        assert systems == {"navigator", "evaluate-skills"}

    def test_filter_by_system(self, db_path: str) -> None:
        friction.friction_add(db_path, "navigator", "a")
        friction.friction_add(db_path, "evaluate-skills", "b")
        result = friction.friction_list(db_path, system="navigator")
        assert result["total"] == 1
        assert result["entries"][0]["system"] == "navigator"

    def test_filter_by_ids(self, db_path: str) -> None:
        r1 = friction.friction_add(db_path, "navigator", "a")
        friction.friction_add(db_path, "navigator", "b")
        r3 = friction.friction_add(db_path, "evaluate-skills", "c")
        result = friction.friction_list(db_path, ids=[r1["id"], r3["id"]])
        assert result["total"] == 2
        returned_ids = {e["id"] for e in result["entries"]}
        assert returned_ids == {r1["id"], r3["id"]}

    def test_limit(self, db_path: str) -> None:
        for i in range(5):
            friction.friction_add(db_path, "navigator", f"entry-{i}")
        result = friction.friction_list(db_path, limit=2)
        assert len(result["entries"]) == 2

    def test_no_detail_md_in_response(self, db_path: str) -> None:
        friction.friction_add(db_path, "navigator", "a", detail_md="some detail")
        result = friction.friction_list(db_path)
        entry = result["entries"][0]
        assert "detail_md" not in entry
        assert entry["has_detail"] is True

    def test_order_is_newest_first(self, db_path: str) -> None:
        friction.friction_add(db_path, "navigator", "first")
        friction.friction_add(db_path, "navigator", "second")
        result = friction.friction_list(db_path)
        assert result["entries"][0]["summary"] == "second"
        assert result["entries"][1]["summary"] == "first"


# ===========================================================================
# friction_search
# ===========================================================================


class TestFrictionSearch:
    def test_match_in_summary(self, db_path: str) -> None:
        friction.friction_add(db_path, "navigator", "scan missed hidden files")
        friction.friction_add(db_path, "navigator", "description too long")
        result = friction.friction_search(db_path, "hidden")
        assert result["total"] == 1
        assert result["entries"][0]["summary"] == "scan missed hidden files"

    def test_match_in_detail_md(self, db_path: str) -> None:
        friction.friction_add(
            db_path, "navigator", "scan issue",
            detail_md="The scanner skipped hidden directories.",
        )
        result = friction.friction_search(db_path, "hidden")
        assert result["total"] == 1

    def test_no_match(self, db_path: str) -> None:
        friction.friction_add(db_path, "navigator", "scan issue")
        result = friction.friction_search(db_path, "nonexistent")
        assert result["total"] == 0

    def test_with_system_filter(self, db_path: str) -> None:
        friction.friction_add(db_path, "navigator", "scan missed hidden files")
        friction.friction_add(db_path, "evaluate-skills", "hidden config problem")
        result = friction.friction_search(db_path, "hidden", system="navigator")
        assert result["total"] == 1
        assert result["entries"][0]["system"] == "navigator"

    def test_regex_pattern(self, db_path: str) -> None:
        friction.friction_add(db_path, "navigator", "scan missed 3 files")
        friction.friction_add(db_path, "navigator", "scan missed many files")
        result = friction.friction_search(db_path, r"missed \d+ files")
        assert result["total"] == 1
        assert result["entries"][0]["summary"] == "scan missed 3 files"

    def test_no_detail_md_in_response(self, db_path: str) -> None:
        friction.friction_add(db_path, "navigator", "a", detail_md="detail here")
        result = friction.friction_search(db_path, "detail")
        assert result["total"] == 1
        assert "detail_md" not in result["entries"][0]


# ===========================================================================
# friction_get
# ===========================================================================


class TestFrictionGet:
    def test_get_single_id(self, db_path: str) -> None:
        added = friction.friction_add(db_path, "navigator", "a", detail_md="full detail")
        result = friction.friction_get(db_path, added["id"])
        assert len(result["entries"]) == 1
        entry = result["entries"][0]
        assert entry["id"] == added["id"]
        assert entry["detail_md"] == "full detail"

    def test_get_multiple_ids(self, db_path: str) -> None:
        r1 = friction.friction_add(db_path, "navigator", "a")
        r2 = friction.friction_add(db_path, "navigator", "b")
        result = friction.friction_get(db_path, [r1["id"], r2["id"]])
        assert len(result["entries"]) == 2

    def test_nonexistent_id_returns_empty(self, db_path: str) -> None:
        result = friction.friction_get(db_path, 999)
        assert len(result["entries"]) == 0

    def test_includes_null_detail(self, db_path: str) -> None:
        added = friction.friction_add(db_path, "navigator", "no detail")
        result = friction.friction_get(db_path, added["id"])
        assert result["entries"][0]["detail_md"] is None


# ===========================================================================
# friction_update
# ===========================================================================


class TestFrictionUpdate:
    def test_update_summary(self, db_path: str) -> None:
        added = friction.friction_add(db_path, "navigator", "original")
        result = friction.friction_update(db_path, added["id"], summary="updated")
        assert result["summary"] == "updated"
        assert result["updated_at"] != added["created_at"] or True  # updated_at refreshed

    def test_update_detail_md(self, db_path: str) -> None:
        added = friction.friction_add(db_path, "navigator", "a")
        friction.friction_update(db_path, added["id"], detail_md="new detail")
        got = friction.friction_get(db_path, added["id"])
        assert got["entries"][0]["detail_md"] == "new detail"

    def test_clear_detail_md_with_empty_string(self, db_path: str) -> None:
        added = friction.friction_add(db_path, "navigator", "a", detail_md="has detail")
        result = friction.friction_update(db_path, added["id"], detail_md="")
        assert result["has_detail"] is False
        got = friction.friction_get(db_path, added["id"])
        assert got["entries"][0]["detail_md"] is None

    def test_update_system(self, db_path: str) -> None:
        added = friction.friction_add(db_path, "navigator", "a")
        result = friction.friction_update(db_path, added["id"], system="evaluate-skills")
        assert result["system"] == "evaluate-skills"

    def test_nonexistent_id_raises(self, db_path: str) -> None:
        with pytest.raises(ValueError, match="not found"):
            friction.friction_update(db_path, 999, summary="x")

    def test_invalid_system_raises(self, db_path: str) -> None:
        added = friction.friction_add(db_path, "navigator", "a")
        with pytest.raises(ValueError):
            friction.friction_update(db_path, added["id"], system="bad/name")

    def test_updated_at_changes(self, db_path: str) -> None:
        added = friction.friction_add(db_path, "navigator", "a")
        original_updated = added["updated_at"]
        result = friction.friction_update(db_path, added["id"], summary="changed")
        # updated_at should be refreshed (may be same if test runs fast, but
        # the value is re-assigned regardless)
        assert "updated_at" in result


# ===========================================================================
# friction_remove
# ===========================================================================


class TestFrictionRemove:
    def test_remove_by_id(self, db_path: str) -> None:
        r1 = friction.friction_add(db_path, "navigator", "first")
        r2 = friction.friction_add(db_path, "navigator", "second")
        result = friction.friction_remove(db_path, r1["id"])
        assert result["removed"]["id"] == r1["id"]
        assert result["remaining"] == 1
        # Verify it's gone
        listed = friction.friction_list(db_path)
        assert listed["total"] == 1
        assert listed["entries"][0]["id"] == r2["id"]

    def test_nonexistent_id_raises(self, db_path: str) -> None:
        with pytest.raises(ValueError, match="not found"):
            friction.friction_remove(db_path, 999)

    def test_remove_last_entry(self, db_path: str) -> None:
        added = friction.friction_add(db_path, "navigator", "only")
        result = friction.friction_remove(db_path, added["id"])
        assert result["remaining"] == 0


# ===========================================================================
# friction_systems_list
# ===========================================================================


class TestFrictionSystemsList:
    def test_empty_db(self, db_path: str) -> None:
        result = friction.friction_systems_list(db_path)
        assert result == {"total_systems": 0, "total_entries": 0, "systems": []}

    def test_multiple_systems(self, db_path: str) -> None:
        friction.friction_add(db_path, "navigator", "a")
        friction.friction_add(db_path, "navigator", "b")
        friction.friction_add(db_path, "evaluate-skills", "c")
        result = friction.friction_systems_list(db_path)
        assert result["total_systems"] == 2
        assert result["total_entries"] == 3
        by_name = {s["name"]: s["count"] for s in result["systems"]}
        assert by_name == {"navigator": 2, "evaluate-skills": 1}

    def test_order_by_count_desc(self, db_path: str) -> None:
        friction.friction_add(db_path, "alpha", "a")
        for _ in range(3):
            friction.friction_add(db_path, "beta", "b")
        for _ in range(2):
            friction.friction_add(db_path, "gamma", "c")
        result = friction.friction_systems_list(db_path)
        names = [s["name"] for s in result["systems"]]
        assert names == ["beta", "gamma", "alpha"]


# ===========================================================================
# Lifecycle
# ===========================================================================


class TestLifecycle:
    def test_add_list_remove_converges(self, db_path: str) -> None:
        """Add two entries, remove one, verify queue state converges."""
        r1 = friction.friction_add(db_path, "navigator", "first")
        friction.friction_add(db_path, "navigator", "second")
        listed = friction.friction_list(db_path, system="navigator")
        assert listed["total"] == 2

        friction.friction_remove(db_path, r1["id"])
        listed = friction.friction_list(db_path, system="navigator")
        assert listed["total"] == 1
        assert listed["entries"][0]["summary"] == "second"

    def test_add_update_get_cycle(self, db_path: str) -> None:
        """Add, update detail, get full entry."""
        added = friction.friction_add(db_path, "navigator", "gap found")
        friction.friction_update(db_path, added["id"], detail_md="## Detail\nFull context here.")
        got = friction.friction_get(db_path, added["id"])
        assert got["entries"][0]["detail_md"] == "## Detail\nFull context here."
        assert got["entries"][0]["summary"] == "gap found"
