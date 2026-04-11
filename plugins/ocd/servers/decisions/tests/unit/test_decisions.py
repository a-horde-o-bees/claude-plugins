"""Unit tests for decisions business logic.

Exercises the `servers.decisions` package directly — the MCP server
(`servers/decisions/__main__.py`) is a thin wrapper that delegates here, so
testing the skill covers the business logic without spinning up a
FastMCP process. Server import is covered separately by
`tests/test_invocation.py::TestServerInvocation::test_decisions_loads`.

Each test uses a fresh tmp_path-based SQLite database so tests are
fully isolated from each other and from the real project.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

import servers.decisions as decisions


@pytest.fixture
def db_path(tmp_path: Path) -> str:
    """Isolated database path scoped to a single test."""
    return str(tmp_path / "test_decisions.db")


# ===========================================================================
# decisions_add
# ===========================================================================


class TestAdd:
    def test_add_basic(self, db_path: str) -> None:
        result = decisions.decisions_add(db_path, summary="Use SQLite for storage")
        assert result["id"] == 1
        assert result["summary"] == "Use SQLite for storage"
        assert result["has_detail"] is False
        assert result["created_at"] is not None
        assert result["updated_at"] is not None

    def test_add_with_detail(self, db_path: str) -> None:
        detail = "## Context\nWe needed persistent storage.\n## Decision\nSQLite."
        result = decisions.decisions_add(db_path, summary="Storage choice", detail_md=detail)
        assert result["id"] == 1
        assert result["has_detail"] is True

    def test_add_timestamps_are_iso_utc(self, db_path: str) -> None:
        result = decisions.decisions_add(db_path, summary="Timestamp check")
        # ISO 8601 with timezone offset
        assert re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", result["created_at"])
        assert result["created_at"] == result["updated_at"]

    def test_add_auto_increments_id(self, db_path: str) -> None:
        r1 = decisions.decisions_add(db_path, summary="First")
        r2 = decisions.decisions_add(db_path, summary="Second")
        assert r1["id"] == 1
        assert r2["id"] == 2

    def test_add_duplicate_summary_allowed(self, db_path: str) -> None:
        """No unique constraint on summary — duplicates are permitted."""
        decisions.decisions_add(db_path, summary="Same text")
        result = decisions.decisions_add(db_path, summary="Same text")
        assert result["id"] == 2


# ===========================================================================
# decisions_list
# ===========================================================================


class TestList:
    def test_list_empty_db(self, db_path: str) -> None:
        result = decisions.decisions_list(db_path)
        assert result["total"] == 0
        assert result["entries"] == []

    def test_list_all_insertion_order(self, db_path: str) -> None:
        decisions.decisions_add(db_path, summary="Alpha")
        decisions.decisions_add(db_path, summary="Beta")
        decisions.decisions_add(db_path, summary="Gamma")
        result = decisions.decisions_list(db_path)
        assert result["total"] == 3
        summaries = [e["summary"] for e in result["entries"]]
        assert summaries == ["Alpha", "Beta", "Gamma"]

    def test_list_by_ids(self, db_path: str) -> None:
        decisions.decisions_add(db_path, summary="A")
        decisions.decisions_add(db_path, summary="B")
        decisions.decisions_add(db_path, summary="C")
        result = decisions.decisions_list(db_path, ids=[1, 3])
        assert len(result["entries"]) == 2
        assert result["entries"][0]["summary"] == "A"
        assert result["entries"][1]["summary"] == "C"
        # total reflects the full table, not filtered count
        assert result["total"] == 3

    def test_list_with_limit(self, db_path: str) -> None:
        decisions.decisions_add(db_path, summary="A")
        decisions.decisions_add(db_path, summary="B")
        decisions.decisions_add(db_path, summary="C")
        result = decisions.decisions_list(db_path, limit=2)
        assert len(result["entries"]) == 2
        assert result["total"] == 3

    def test_list_has_detail_flag(self, db_path: str) -> None:
        decisions.decisions_add(db_path, summary="No detail")
        decisions.decisions_add(db_path, summary="With detail", detail_md="Some content")
        decisions.decisions_add(db_path, summary="Empty detail", detail_md="")
        result = decisions.decisions_list(db_path)
        assert result["entries"][0]["has_detail"] is False
        assert result["entries"][1]["has_detail"] is True
        assert result["entries"][2]["has_detail"] is False

    def test_list_excludes_detail_md(self, db_path: str) -> None:
        decisions.decisions_add(db_path, summary="Test", detail_md="Long content")
        result = decisions.decisions_list(db_path)
        assert "detail_md" not in result["entries"][0]


# ===========================================================================
# decisions_search
# ===========================================================================


class TestSearch:
    def test_search_match_in_summary(self, db_path: str) -> None:
        decisions.decisions_add(db_path, summary="Use SQLite for storage")
        decisions.decisions_add(db_path, summary="Use markdown for docs")
        result = decisions.decisions_search(db_path, "SQLite")
        assert result["total"] == 1
        assert result["entries"][0]["summary"] == "Use SQLite for storage"

    def test_search_match_in_detail_md(self, db_path: str) -> None:
        decisions.decisions_add(
            db_path, summary="Storage choice", detail_md="We evaluated PostgreSQL and SQLite"
        )
        decisions.decisions_add(db_path, summary="Unrelated")
        result = decisions.decisions_search(db_path, "PostgreSQL")
        assert result["total"] == 1
        assert result["entries"][0]["summary"] == "Storage choice"

    def test_search_no_match(self, db_path: str) -> None:
        decisions.decisions_add(db_path, summary="Something")
        result = decisions.decisions_search(db_path, "nonexistent")
        assert result["total"] == 0
        assert result["entries"] == []

    def test_search_regex_pattern(self, db_path: str) -> None:
        decisions.decisions_add(db_path, summary="Use v1.2 API")
        decisions.decisions_add(db_path, summary="Use v2.0 API")
        result = decisions.decisions_search(db_path, r"v\d+\.\d+")
        assert result["total"] == 2


# ===========================================================================
# decisions_get
# ===========================================================================


class TestGet:
    def test_get_single_id(self, db_path: str) -> None:
        decisions.decisions_add(db_path, summary="Test", detail_md="Full detail here")
        result = decisions.decisions_get(db_path, 1)
        assert len(result["entries"]) == 1
        entry = result["entries"][0]
        assert entry["id"] == 1
        assert entry["summary"] == "Test"
        assert entry["detail_md"] == "Full detail here"

    def test_get_multiple_ids(self, db_path: str) -> None:
        decisions.decisions_add(db_path, summary="A")
        decisions.decisions_add(db_path, summary="B")
        decisions.decisions_add(db_path, summary="C")
        result = decisions.decisions_get(db_path, [1, 3])
        assert len(result["entries"]) == 2
        assert result["entries"][0]["summary"] == "A"
        assert result["entries"][1]["summary"] == "C"

    def test_get_nonexistent_returns_empty(self, db_path: str) -> None:
        result = decisions.decisions_get(db_path, 999)
        assert result["entries"] == []

    def test_get_includes_detail_md(self, db_path: str) -> None:
        decisions.decisions_add(db_path, summary="Test", detail_md="Content")
        result = decisions.decisions_get(db_path, 1)
        assert "detail_md" in result["entries"][0]
        assert result["entries"][0]["detail_md"] == "Content"

    def test_get_null_detail_md(self, db_path: str) -> None:
        decisions.decisions_add(db_path, summary="No detail")
        result = decisions.decisions_get(db_path, 1)
        assert result["entries"][0]["detail_md"] is None


# ===========================================================================
# decisions_update
# ===========================================================================


class TestUpdate:
    def test_update_summary(self, db_path: str) -> None:
        decisions.decisions_add(db_path, summary="Old summary")
        result = decisions.decisions_update(db_path, id=1, summary="New summary")
        assert result["summary"] == "New summary"
        assert result["id"] == 1

    def test_update_detail_md(self, db_path: str) -> None:
        decisions.decisions_add(db_path, summary="Test")
        result = decisions.decisions_update(db_path, id=1, detail_md="Added detail")
        assert result["has_detail"] is True
        # Verify via get
        full = decisions.decisions_get(db_path, 1)
        assert full["entries"][0]["detail_md"] == "Added detail"

    def test_update_clear_detail_md_with_empty_string(self, db_path: str) -> None:
        decisions.decisions_add(db_path, summary="Test", detail_md="Some detail")
        result = decisions.decisions_update(db_path, id=1, detail_md="")
        assert result["has_detail"] is False
        full = decisions.decisions_get(db_path, 1)
        assert full["entries"][0]["detail_md"] is None

    def test_update_none_leaves_fields_unchanged(self, db_path: str) -> None:
        decisions.decisions_add(db_path, summary="Original", detail_md="Detail")
        result = decisions.decisions_update(db_path, id=1)
        assert result["summary"] == "Original"
        assert result["has_detail"] is True

    def test_update_bumps_updated_at(self, db_path: str) -> None:
        added = decisions.decisions_add(db_path, summary="Test")
        updated = decisions.decisions_update(db_path, id=1, summary="Changed")
        assert updated["updated_at"] >= added["updated_at"]
        assert updated["created_at"] == added["created_at"]

    def test_update_nonexistent_raises(self, db_path: str) -> None:
        with pytest.raises(ValueError, match="No decision with id 999"):
            decisions.decisions_update(db_path, id=999, summary="Ghost")


# ===========================================================================
# decisions_remove
# ===========================================================================


class TestRemove:
    def test_remove_returns_metadata(self, db_path: str) -> None:
        decisions.decisions_add(db_path, summary="To remove")
        result = decisions.decisions_remove(db_path, id=1)
        assert result["removed"]["id"] == 1
        assert result["removed"]["summary"] == "To remove"
        assert result["remaining"] == 0

    def test_remove_remaining_count(self, db_path: str) -> None:
        decisions.decisions_add(db_path, summary="A")
        decisions.decisions_add(db_path, summary="B")
        decisions.decisions_add(db_path, summary="C")
        result = decisions.decisions_remove(db_path, id=2)
        assert result["remaining"] == 2

    def test_remove_nonexistent_raises(self, db_path: str) -> None:
        with pytest.raises(ValueError, match="No decision with id 999"):
            decisions.decisions_remove(db_path, id=999)

    def test_remove_actually_deletes(self, db_path: str) -> None:
        decisions.decisions_add(db_path, summary="Gone")
        decisions.decisions_remove(db_path, id=1)
        result = decisions.decisions_list(db_path)
        assert result["total"] == 0
        assert result["entries"] == []
