"""Unit tests for the log facade.

Covers the deterministic skeleton: schema invariants, CRUD contract shape,
cascade correctness, idempotency of init-like operations, type and tag
management semantics. Tests use a tmp_path SQLite database per test.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from servers.log import (
    log_add,
    log_get,
    log_list,
    log_remove,
    log_search,
    log_update,
    tag_add,
    tag_list,
    tag_remove,
    tag_update,
    type_add,
    type_list,
    type_remove,
    type_update,
)
from servers.log._db import get_connection


@pytest.fixture
def db(tmp_path: Path) -> str:
    """Fresh database with the four canonical types registered."""
    db_path = str(tmp_path / "log.db")
    type_add(db_path, name="decision", instructions="decision type")
    type_add(db_path, name="friction", instructions="friction type")
    type_add(db_path, name="problem", instructions="problem type")
    type_add(db_path, name="idea", instructions="idea type")
    return db_path


# --- Schema ---


class TestSchema:
    def test_schema_creates_four_tables(self, tmp_path: Path) -> None:
        db_path = str(tmp_path / "log.db")
        conn = get_connection(db_path)
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
        conn.close()
        names = {r[0] for r in rows}
        assert {"types", "records", "tags", "record_tags"}.issubset(names)

    def test_foreign_keys_enabled(self, tmp_path: Path) -> None:
        conn = get_connection(str(tmp_path / "log.db"))
        result = conn.execute("PRAGMA foreign_keys").fetchone()[0]
        conn.close()
        assert result == 1


# --- Records ---


class TestLogAdd:
    def test_add_with_detail_and_tags(self, db: str) -> None:
        result = log_add(
            db,
            log_type="decision",
            summary="picked sqlite",
            detail_md="## Context\nneeded embedded DB",
            tags=["storage", "core"],
        )
        assert result["id"] is not None
        assert result["log_type"] == "decision"
        assert result["summary"] == "picked sqlite"
        assert result["has_detail"] is True
        assert result["tags"] == ["core", "storage"]

    def test_add_without_detail(self, db: str) -> None:
        result = log_add(db, log_type="idea", summary="try rewriting")
        assert result["has_detail"] is False
        assert result["tags"] == []

    def test_add_unknown_type_raises_with_guidance(self, db: str) -> None:
        with pytest.raises(ValueError, match="Unknown log_type"):
            log_add(db, log_type="bogus", summary="x")

    def test_add_implicitly_creates_tags(self, db: str) -> None:
        log_add(db, log_type="friction", summary="a", tags=["new-tag"])
        tags = tag_list(db, log_type="friction")["tags"]
        assert any(t["name"] == "new-tag" and t["record_count"] == 1 for t in tags)


class TestLogList:
    def test_list_returns_metadata_only(self, db: str) -> None:
        log_add(db, log_type="idea", summary="a", detail_md="secret")
        result = log_list(db)
        assert result["total"] == 1
        entry = result["entries"][0]
        assert entry["has_detail"] is True
        assert "detail_md" not in entry

    def test_list_filter_by_type(self, db: str) -> None:
        log_add(db, log_type="idea", summary="i")
        log_add(db, log_type="friction", summary="f")
        result = log_list(db, log_type="idea")
        assert result["total"] == 1
        assert result["entries"][0]["log_type"] == "idea"

    def test_list_filter_by_tags_requires_all(self, db: str) -> None:
        log_add(db, log_type="idea", summary="a", tags=["x", "y"])
        log_add(db, log_type="idea", summary="b", tags=["x"])
        result = log_list(db, tags=["x", "y"])
        assert result["total"] == 1
        assert result["entries"][0]["summary"] == "a"

    def test_list_by_ids_ignores_other_filters(self, db: str) -> None:
        a = log_add(db, log_type="idea", summary="a")["id"]
        log_add(db, log_type="friction", summary="b")
        result = log_list(db, ids=[a], log_type="friction")
        assert result["total"] == 1
        assert result["entries"][0]["id"] == a


class TestLogSearch:
    def test_search_matches_summary(self, db: str) -> None:
        log_add(db, log_type="decision", summary="use sqlite for embedded store")
        log_add(db, log_type="decision", summary="use postgres for shared store")
        result = log_search(db, pattern="sqlite")
        assert result["total"] == 1

    def test_search_matches_detail(self, db: str) -> None:
        log_add(
            db,
            log_type="idea",
            summary="s",
            detail_md="explore tokio for async runtime",
        )
        result = log_search(db, pattern="tokio")
        assert result["total"] == 1

    def test_search_scoped_by_type(self, db: str) -> None:
        log_add(db, log_type="idea", summary="cache layer")
        log_add(db, log_type="friction", summary="cache layer")
        result = log_search(db, pattern="cache", log_type="idea")
        assert result["total"] == 1
        assert result["entries"][0]["log_type"] == "idea"


class TestLogGetUpdateRemove:
    def test_get_returns_full_content(self, db: str) -> None:
        created = log_add(
            db, log_type="decision", summary="s", detail_md="d", tags=["a"],
        )
        result = log_get(db, ids=created["id"])
        entry = result["entries"][0]
        assert entry["detail_md"] == "d"
        assert entry["tags"] == ["a"]

    def test_update_none_preserves_fields(self, db: str) -> None:
        created = log_add(db, log_type="idea", summary="orig", detail_md="keep")
        updated = log_update(db, id=created["id"], summary="new")
        # summary changed; detail_md untouched
        full = log_get(db, ids=updated["id"])["entries"][0]
        assert full["summary"] == "new"
        assert full["detail_md"] == "keep"

    def test_update_empty_string_clears_detail(self, db: str) -> None:
        created = log_add(db, log_type="idea", summary="s", detail_md="gone")
        log_update(db, id=created["id"], detail_md="")
        full = log_get(db, ids=created["id"])["entries"][0]
        assert full["detail_md"] is None

    def test_update_tags_replaces_full_set(self, db: str) -> None:
        created = log_add(db, log_type="idea", summary="s", tags=["a", "b"])
        log_update(db, id=created["id"], tags=["c"])
        full = log_get(db, ids=created["id"])["entries"][0]
        assert full["tags"] == ["c"]

    def test_remove_cascades_to_record_tags(self, db: str) -> None:
        created = log_add(db, log_type="idea", summary="s", tags=["x"])
        log_remove(db, id=created["id"])
        conn = get_connection(db)
        rows = conn.execute(
            "SELECT COUNT(*) FROM record_tags WHERE record_id = ?", (created["id"],)
        ).fetchone()[0]
        conn.close()
        assert rows == 0

    def test_remove_unknown_id_raises(self, db: str) -> None:
        with pytest.raises(ValueError, match="No record"):
            log_remove(db, id=9999)


# --- Types ---


class TestTypeAdd:
    def test_add_duplicate_raises(self, db: str) -> None:
        with pytest.raises(ValueError, match="already exists"):
            type_add(db, name="decision", instructions="x")


class TestTypeList:
    def test_list_shows_record_and_tag_counts(self, db: str) -> None:
        log_add(db, log_type="idea", summary="a", tags=["x", "y"])
        log_add(db, log_type="idea", summary="b", tags=["x"])
        result = type_list(db)
        idea = next(t for t in result["types"] if t["name"] == "idea")
        assert idea["record_count"] == 2
        assert idea["tag_count"] == 2


class TestTypeUpdate:
    def test_update_instructions(self, db: str) -> None:
        type_update(db, name="idea", instructions="new text")
        types = {t["name"]: t for t in type_list(db)["types"]}
        assert types["idea"]["instructions"] == "new text"

    def test_rename_cascades_to_records_and_tags(self, db: str) -> None:
        log_add(db, log_type="idea", summary="s", tags=["x"])
        type_update(db, name="idea", rename="proposal")
        names = {t["name"] for t in type_list(db)["types"]}
        assert "proposal" in names and "idea" not in names
        # Record and tag moved to new type name
        records = log_list(db, log_type="proposal")
        assert records["total"] == 1
        tags = tag_list(db, log_type="proposal")["tags"]
        assert any(t["name"] == "x" for t in tags)

    def test_rename_collision_raises(self, db: str) -> None:
        with pytest.raises(ValueError, match="already exists"):
            type_update(db, name="idea", rename="friction")


class TestTypeRemove:
    def test_remove_empty_type(self, db: str) -> None:
        result = type_remove(db, name="problem")
        assert result["records_deleted"] == 0
        names = {t["name"] for t in type_list(db)["types"]}
        assert "problem" not in names

    def test_remove_with_records_refuses_without_force(self, db: str) -> None:
        log_add(db, log_type="idea", summary="s")
        with pytest.raises(ValueError, match="force=True"):
            type_remove(db, name="idea")

    def test_remove_with_force_cascades(self, db: str) -> None:
        log_add(db, log_type="idea", summary="a", tags=["x"])
        log_add(db, log_type="idea", summary="b", tags=["y"])
        result = type_remove(db, name="idea", force=True)
        assert result["records_deleted"] == 2
        assert result["tags_deleted"] == 2
        # Records and tags are both gone
        remaining = log_list(db)["total"]
        assert remaining == 0


# --- Tags ---


class TestTagAdd:
    def test_add_idempotent(self, db: str) -> None:
        tag_add(db, log_type="idea", name="canonical")
        tag_add(db, log_type="idea", name="canonical")  # should not raise
        tags = tag_list(db, log_type="idea")["tags"]
        assert sum(1 for t in tags if t["name"] == "canonical") == 1

    def test_add_unknown_type_raises(self, db: str) -> None:
        with pytest.raises(ValueError, match="Unknown log_type"):
            tag_add(db, log_type="bogus", name="x")


class TestTagList:
    def test_list_scoped_sorted_by_count_desc(self, db: str) -> None:
        log_add(db, log_type="idea", summary="a", tags=["common"])
        log_add(db, log_type="idea", summary="b", tags=["common"])
        log_add(db, log_type="idea", summary="c", tags=["rare"])
        tags = tag_list(db, log_type="idea")["tags"]
        assert tags[0]["name"] == "common"
        assert tags[0]["record_count"] == 2
        assert tags[1]["name"] == "rare"

    def test_list_grouped_includes_all_types(self, db: str) -> None:
        log_add(db, log_type="idea", summary="s", tags=["x"])
        result = tag_list(db)
        assert set(result["by_type"].keys()) == {"decision", "friction", "problem", "idea"}
        assert result["by_type"]["idea"][0]["name"] == "x"
        assert result["by_type"]["friction"] == []


class TestTagUpdate:
    def test_pure_rename(self, db: str) -> None:
        log_add(db, log_type="idea", summary="a", tags=["old"])
        result = tag_update(db, log_type="idea", old="old", new="new")
        assert result["records_affected"] == 1
        tags = {t["name"] for t in tag_list(db, log_type="idea")["tags"]}
        assert "new" in tags and "old" not in tags

    def test_merge_into_existing(self, db: str) -> None:
        log_add(db, log_type="idea", summary="a", tags=["naviator"])
        log_add(db, log_type="idea", summary="b", tags=["navigator"])
        log_add(db, log_type="idea", summary="c", tags=["naviator", "navigator"])
        result = tag_update(db, log_type="idea", old="naviator", new="navigator")
        assert result["records_affected"] == 2
        # Only navigator survives; naviator is gone
        tags = {t["name"] for t in tag_list(db, log_type="idea")["tags"]}
        assert tags == {"navigator"}
        # Every record that had naviator now has navigator, deduplicated
        navigator_count = next(
            t["record_count"]
            for t in tag_list(db, log_type="idea")["tags"]
            if t["name"] == "navigator"
        )
        assert navigator_count == 3


class TestTagRemove:
    def test_remove_strips_without_deleting_records(self, db: str) -> None:
        a = log_add(db, log_type="idea", summary="a", tags=["x", "y"])["id"]
        b = log_add(db, log_type="idea", summary="b", tags=["x"])["id"]
        result = tag_remove(db, log_type="idea", name="x")
        assert result["records_affected"] == 2
        assert log_list(db)["total"] == 2
        # Record a still has y; record b has no tags
        full_a = log_get(db, ids=a)["entries"][0]
        full_b = log_get(db, ids=b)["entries"][0]
        assert full_a["tags"] == ["y"]
        assert full_b["tags"] == []

    def test_remove_unknown_tag_raises(self, db: str) -> None:
        with pytest.raises(ValueError, match="Unknown tag"):
            tag_remove(db, log_type="idea", name="bogus")
