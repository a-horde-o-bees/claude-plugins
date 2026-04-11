"""Unit tests for stash operations.

Exercises the ``servers.stash`` facade directly — all functions take a
db_path and return structured dicts. The server layer handles scope
resolution; skill tests use a single tmp-path database and are unaware
of project vs user scope.
"""

from __future__ import annotations

import os

import pytest

import servers.stash as store


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def db_path(tmp_path) -> str:
    """Return a temporary database path for test isolation."""
    return str(tmp_path / "stash.db")


# ---------------------------------------------------------------------------
# stash_add
# ---------------------------------------------------------------------------


class TestStashAdd:
    def test_basic_add(self, db_path: str) -> None:
        result = store.stash_add(db_path, summary="Idea one")
        assert result["id"] == 1
        assert result["summary"] == "Idea one"
        assert result["has_detail"] is False
        assert "created_at" in result
        assert "updated_at" in result

    def test_add_with_detail(self, db_path: str) -> None:
        result = store.stash_add(
            db_path, summary="Rich idea", detail_md="## Context\n\nLots of detail."
        )
        assert result["has_detail"] is True

    def test_timestamps_are_iso_utc(self, db_path: str) -> None:
        result = store.stash_add(db_path, summary="Timestamped")
        assert result["created_at"].endswith("+00:00")
        assert result["created_at"] == result["updated_at"]

    def test_sequential_ids(self, db_path: str) -> None:
        r1 = store.stash_add(db_path, summary="First")
        r2 = store.stash_add(db_path, summary="Second")
        assert r2["id"] == r1["id"] + 1


# ---------------------------------------------------------------------------
# stash_list
# ---------------------------------------------------------------------------


class TestStashList:
    def test_list_all(self, db_path: str) -> None:
        store.stash_add(db_path, summary="A")
        store.stash_add(db_path, summary="B")
        store.stash_add(db_path, summary="C")
        result = store.stash_list(db_path)
        assert result["total"] == 3
        assert len(result["entries"]) == 3
        assert [e["summary"] for e in result["entries"]] == ["A", "B", "C"]

    def test_list_by_ids(self, db_path: str) -> None:
        store.stash_add(db_path, summary="A")
        store.stash_add(db_path, summary="B")
        store.stash_add(db_path, summary="C")
        result = store.stash_list(db_path, ids=[1, 3])
        assert result["total"] == 3  # total is full count
        assert len(result["entries"]) == 2
        assert [e["summary"] for e in result["entries"]] == ["A", "C"]

    def test_list_with_limit(self, db_path: str) -> None:
        store.stash_add(db_path, summary="A")
        store.stash_add(db_path, summary="B")
        store.stash_add(db_path, summary="C")
        result = store.stash_list(db_path, limit=2)
        assert result["total"] == 3
        assert len(result["entries"]) == 2

    def test_list_empty_db(self, db_path: str) -> None:
        result = store.stash_list(db_path)
        assert result["total"] == 0
        assert result["entries"] == []

    def test_list_has_detail_correct(self, db_path: str) -> None:
        store.stash_add(db_path, summary="No detail")
        store.stash_add(db_path, summary="With detail", detail_md="body")
        result = store.stash_list(db_path)
        assert result["entries"][0]["has_detail"] is False
        assert result["entries"][1]["has_detail"] is True

    def test_list_excludes_detail_md(self, db_path: str) -> None:
        store.stash_add(db_path, summary="X", detail_md="secret body")
        result = store.stash_list(db_path)
        assert "detail_md" not in result["entries"][0]


# ---------------------------------------------------------------------------
# stash_search
# ---------------------------------------------------------------------------


class TestStashSearch:
    def test_match_in_summary(self, db_path: str) -> None:
        store.stash_add(db_path, summary="refactor the widget layer")
        store.stash_add(db_path, summary="unrelated idea")
        result = store.stash_search(db_path, pattern="widget")
        assert result["total"] == 1
        assert result["entries"][0]["summary"] == "refactor the widget layer"

    def test_match_in_detail_md(self, db_path: str) -> None:
        store.stash_add(db_path, summary="vague idea", detail_md="involves widget refactor")
        result = store.stash_search(db_path, pattern="widget")
        assert result["total"] == 1

    def test_no_match(self, db_path: str) -> None:
        store.stash_add(db_path, summary="something else")
        result = store.stash_search(db_path, pattern="nonexistent")
        assert result["total"] == 0
        assert result["entries"] == []

    def test_regex_pattern(self, db_path: str) -> None:
        store.stash_add(db_path, summary="add feature-123")
        store.stash_add(db_path, summary="add feature-456")
        store.stash_add(db_path, summary="remove old code")
        result = store.stash_search(db_path, pattern=r"feature-\d+")
        assert result["total"] == 2


# ---------------------------------------------------------------------------
# stash_get
# ---------------------------------------------------------------------------


class TestStashGet:
    def test_get_single_id(self, db_path: str) -> None:
        store.stash_add(db_path, summary="Target", detail_md="full body")
        result = store.stash_get(db_path, ids=1)
        assert len(result["entries"]) == 1
        assert result["entries"][0]["summary"] == "Target"
        assert result["entries"][0]["detail_md"] == "full body"

    def test_get_multiple_ids(self, db_path: str) -> None:
        store.stash_add(db_path, summary="A")
        store.stash_add(db_path, summary="B")
        store.stash_add(db_path, summary="C")
        result = store.stash_get(db_path, ids=[1, 3])
        assert len(result["entries"]) == 2
        assert [e["summary"] for e in result["entries"]] == ["A", "C"]

    def test_get_nonexistent_returns_empty(self, db_path: str) -> None:
        result = store.stash_get(db_path, ids=[999])
        assert result["entries"] == []


# ---------------------------------------------------------------------------
# stash_update
# ---------------------------------------------------------------------------


class TestStashUpdate:
    def test_update_summary(self, db_path: str) -> None:
        store.stash_add(db_path, summary="Original")
        result = store.stash_update(db_path, id=1, summary="Updated")
        assert result["summary"] == "Updated"
        assert result["updated_at"] != result["created_at"]

    def test_update_detail_md(self, db_path: str) -> None:
        store.stash_add(db_path, summary="Entry")
        result = store.stash_update(db_path, id=1, detail_md="new detail")
        assert result["has_detail"] is True
        full = store.stash_get(db_path, ids=1)
        assert full["entries"][0]["detail_md"] == "new detail"

    def test_clear_detail_md_with_empty_string(self, db_path: str) -> None:
        store.stash_add(db_path, summary="Entry", detail_md="has content")
        result = store.stash_update(db_path, id=1, detail_md="")
        assert result["has_detail"] is False
        full = store.stash_get(db_path, ids=1)
        assert full["entries"][0]["detail_md"] is None

    def test_update_none_leaves_unchanged(self, db_path: str) -> None:
        store.stash_add(db_path, summary="Original", detail_md="keep me")
        result = store.stash_update(db_path, id=1)
        assert result["summary"] == "Original"
        assert result["has_detail"] is True

    def test_update_nonexistent_raises(self, db_path: str) -> None:
        with pytest.raises(ValueError, match="No stash entry with id 999"):
            store.stash_update(db_path, id=999, summary="Nope")


# ---------------------------------------------------------------------------
# stash_remove
# ---------------------------------------------------------------------------


class TestStashRemove:
    def test_remove_entry(self, db_path: str) -> None:
        store.stash_add(db_path, summary="Doomed")
        result = store.stash_remove(db_path, id=1)
        assert result["removed"]["summary"] == "Doomed"
        assert result["remaining"] == 0

    def test_remove_returns_remaining_count(self, db_path: str) -> None:
        store.stash_add(db_path, summary="A")
        store.stash_add(db_path, summary="B")
        store.stash_add(db_path, summary="C")
        result = store.stash_remove(db_path, id=2)
        assert result["remaining"] == 2

    def test_remove_nonexistent_raises(self, db_path: str) -> None:
        with pytest.raises(ValueError, match="No stash entry with id 42"):
            store.stash_remove(db_path, id=42)

    def test_remove_preserves_other_entries(self, db_path: str) -> None:
        store.stash_add(db_path, summary="A")
        store.stash_add(db_path, summary="B")
        store.stash_add(db_path, summary="C")
        store.stash_remove(db_path, id=2)
        result = store.stash_list(db_path)
        assert [e["summary"] for e in result["entries"]] == ["A", "C"]
