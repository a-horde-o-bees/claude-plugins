"""Tests for the decisions MCP server business logic.

Exercises the `_decisions_store` module directly — server handlers are
thin wrappers that delegate to it, so testing the store covers the
server behavior without spinning up a FastMCP process.

Each test uses a fresh tmp_path as the synthetic project root so
decisions.md round-trips do not touch the real repository.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Import the store via plugin-root-on-sys.path, matching how the server does it.
PLUGIN_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLUGIN_ROOT))

from servers import _decisions_store as store  # noqa: E402


# ===========================================================================
# Round-trip against the real repository decisions.md
# ===========================================================================


class TestRealIndexRoundtrip:
    """Parse the real decisions.md and verify round-tripping preserves entries."""

    def test_parse_real_index(self) -> None:
        project_root = PLUGIN_ROOT.parent.parent
        index = project_root / "decisions.md"
        if not index.exists():
            pytest.skip("no real decisions.md at project root")
        preamble, entries = store._parse_index(index.read_text())
        assert len(entries) > 0
        for e in entries:
            assert e.title
            assert e.summary

    def test_real_index_survives_render(self) -> None:
        project_root = PLUGIN_ROOT.parent.parent
        index = project_root / "decisions.md"
        if not index.exists():
            pytest.skip("no real decisions.md at project root")
        preamble, entries = store._parse_index(index.read_text())
        rendered = store._render_index(preamble, entries)
        preamble2, entries2 = store._parse_index(rendered)
        assert [e.title for e in entries2] == [e.title for e in entries]
        assert [e.summary for e in entries2] == [e.summary for e in entries]
        assert [e.detail_path for e in entries2] == [e.detail_path for e in entries]


# ===========================================================================
# Recording and listing
# ===========================================================================


class TestRecord:
    def test_record_creates_index(self, tmp_path: Path) -> None:
        result = store.record(tmp_path, title="First", summary="one-liner")
        assert result["action"] == "recorded"
        assert result["index"] == 1
        assert result["detail_path"] is None
        assert (tmp_path / "decisions.md").exists()
        assert "First" in (tmp_path / "decisions.md").read_text()

    def test_record_with_detail_creates_file(self, tmp_path: Path) -> None:
        result = store.record(
            tmp_path,
            title="With Detail",
            summary="summary line",
            context="the problem",
            options="A vs B",
            decision="chose A",
            consequences="enables X",
        )
        assert result["detail_path"] == "decisions/with-detail.md"
        detail_file = tmp_path / "decisions" / "with-detail.md"
        assert detail_file.exists()
        content = detail_file.read_text()
        assert "# With Detail" in content
        assert "## Context" in content
        assert "## Options Considered" in content
        assert "## Decision" in content
        assert "## Consequences" in content

    def test_record_rejects_duplicate_title(self, tmp_path: Path) -> None:
        store.record(tmp_path, title="Dup", summary="first")
        with pytest.raises(ValueError, match="already exists"):
            store.record(tmp_path, title="dup", summary="second")

    def test_record_requires_title_and_summary(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError):
            store.record(tmp_path, title="", summary="x")
        with pytest.raises(ValueError):
            store.record(tmp_path, title="x", summary="")


class TestListAndGet:
    def test_list_returns_insertion_order(self, tmp_path: Path) -> None:
        store.record(tmp_path, title="Alpha", summary="a")
        store.record(tmp_path, title="Beta", summary="b")
        store.record(tmp_path, title="Gamma", summary="c")
        result = store.list_decisions(tmp_path)
        assert result["count"] == 3
        titles = [d["title"] for d in result["decisions"]]
        assert titles == ["Alpha", "Beta", "Gamma"]

    def test_get_by_index(self, tmp_path: Path) -> None:
        store.record(tmp_path, title="Alpha", summary="a")
        store.record(tmp_path, title="Beta", summary="b")
        result = store.get(tmp_path, 2)
        assert result["title"] == "Beta"

    def test_get_by_stringified_index(self, tmp_path: Path) -> None:
        store.record(tmp_path, title="Alpha", summary="a")
        result = store.get(tmp_path, "1")
        assert result["title"] == "Alpha"

    def test_get_by_title_case_insensitive(self, tmp_path: Path) -> None:
        store.record(tmp_path, title="Alpha", summary="a")
        result = store.get(tmp_path, "alpha")
        assert result["title"] == "Alpha"

    def test_get_includes_detail(self, tmp_path: Path) -> None:
        store.record(
            tmp_path,
            title="Rich",
            summary="s",
            context="ctx",
            decision="dec",
        )
        result = store.get(tmp_path, "Rich")
        assert result["detail"] is not None
        assert result["detail"]["context"] == "ctx"
        assert result["detail"]["decision"] == "dec"
        assert result["detail"]["options"] is None

    def test_get_unknown_raises(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="No decision matches"):
            store.get(tmp_path, "nope")


# ===========================================================================
# Update and remove
# ===========================================================================


class TestUpdate:
    def test_update_summary(self, tmp_path: Path) -> None:
        store.record(tmp_path, title="T", summary="old")
        store.update(tmp_path, "T", summary="new")
        result = store.get(tmp_path, "T")
        assert result["summary"] == "new"

    def test_update_creates_detail_when_none_existed(self, tmp_path: Path) -> None:
        store.record(tmp_path, title="T", summary="s")
        store.update(tmp_path, "T", context="added later")
        result = store.get(tmp_path, "T")
        assert result["detail"]["context"] == "added later"
        assert result["detail_path"] == "decisions/t.md"

    def test_update_merges_into_existing_detail(self, tmp_path: Path) -> None:
        store.record(
            tmp_path, title="T", summary="s", context="ctx", decision="dec"
        )
        store.update(tmp_path, "T", consequences="later")
        result = store.get(tmp_path, "T")
        assert result["detail"]["context"] == "ctx"
        assert result["detail"]["decision"] == "dec"
        assert result["detail"]["consequences"] == "later"

    def test_update_renames_detail_on_title_change(self, tmp_path: Path) -> None:
        store.record(tmp_path, title="Old Name", summary="s", context="c")
        old = tmp_path / "decisions" / "old-name.md"
        assert old.exists()
        store.update(tmp_path, "Old Name", title="New Name")
        assert not old.exists()
        new = tmp_path / "decisions" / "new-name.md"
        assert new.exists()

    def test_update_unknown_raises(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="No decision matches"):
            store.update(tmp_path, "ghost", summary="x")


class TestRemove:
    def test_remove_entry_and_detail(self, tmp_path: Path) -> None:
        store.record(tmp_path, title="T", summary="s", context="c")
        detail = tmp_path / "decisions" / "t.md"
        assert detail.exists()
        result = store.remove(tmp_path, "T")
        assert result["action"] == "removed"
        assert result["detail_removed"] is True
        assert not detail.exists()
        listing = store.list_decisions(tmp_path)
        assert listing["count"] == 0

    def test_remove_index_only(self, tmp_path: Path) -> None:
        store.record(tmp_path, title="T", summary="s")
        result = store.remove(tmp_path, "T")
        assert result["detail_removed"] is False

    def test_remove_preserves_other_entries(self, tmp_path: Path) -> None:
        store.record(tmp_path, title="A", summary="a")
        store.record(tmp_path, title="B", summary="b")
        store.record(tmp_path, title="C", summary="c")
        store.remove(tmp_path, "B")
        listing = store.list_decisions(tmp_path)
        assert [d["title"] for d in listing["decisions"]] == ["A", "C"]

    def test_remove_unknown_raises(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="No decision matches"):
            store.remove(tmp_path, "ghost")


# ===========================================================================
# Slugification and file naming
# ===========================================================================


class TestSlugify:
    def test_basic(self) -> None:
        assert store.slugify("Hello World") == "hello-world"

    def test_punctuation_collapses(self) -> None:
        assert store.slugify("A/B/C — test!") == "a-b-c-test"

    def test_empty_fallback(self) -> None:
        assert store.slugify("   ") == "decision"

    def test_unique_path_avoids_collision(self, tmp_path: Path) -> None:
        (tmp_path / "decisions").mkdir()
        (tmp_path / "decisions" / "foo.md").write_text("existing")
        path = store._unique_detail_path(tmp_path, "Foo")
        assert path == "decisions/foo-2.md"


# ===========================================================================
# Server import smoke test
# ===========================================================================


class TestServerImport:
    """Smoke test: the server module imports and registers its tools."""

    def test_server_imports(self) -> None:
        from servers import decisions as server_mod
        assert server_mod.mcp is not None
        assert server_mod.mcp.name == "ocd-decisions"
