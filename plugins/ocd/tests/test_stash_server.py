"""Tests for the stash MCP server business logic.

Exercises the ``_stash_store`` module directly — server handlers are
thin wrappers that delegate to it, so testing the store covers the
server behavior without spinning up a FastMCP process.

Each test uses ``tmp_path`` for the synthetic project root and the
``OCD_STASH_USER_DIR`` environment variable for the user-level stash,
so round-trips never touch the real filesystem.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Import the store via plugin-root-on-sys.path, matching how the server does it.
PLUGIN_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLUGIN_ROOT))

from servers import _stash_store as store  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    """Synthetic project root with a .claude directory."""
    (tmp_path / ".claude").mkdir()
    return tmp_path


@pytest.fixture
def user_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect the user-level stash into tmp_path."""
    user = tmp_path / "user-home" / ".claude" / "stash"
    monkeypatch.setenv("OCD_STASH_USER_DIR", str(user))
    return user


# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------


class TestPaths:
    def test_project_stash_path(self, project_root: Path) -> None:
        path = store.project_stash_path(project_root)
        assert path == project_root / ".claude" / "stash" / "stash.md"

    def test_user_stash_path_honors_env(self, user_dir: Path) -> None:
        assert store.user_stash_path() == user_dir / "stash.md"


# ---------------------------------------------------------------------------
# Slugification
# ---------------------------------------------------------------------------


class TestSlugify:
    def test_basic(self) -> None:
        assert store.slugify("Hello World") == "hello-world"

    def test_punctuation_collapses(self) -> None:
        assert store.slugify("A/B/C — test!") == "a-b-c-test"

    def test_empty_fallback(self) -> None:
        assert store.slugify("   ") == "entry"


# ---------------------------------------------------------------------------
# Entry parsing and round-trip
# ---------------------------------------------------------------------------


class TestEntryFormat:
    def test_simple_entry_line(self) -> None:
        entry = store.StashEntry(title="Alpha", summary="one-liner")
        line = entry.to_line()
        assert line == "- **[Alpha]** — one-liner"

    def test_entry_with_detail_line(self) -> None:
        entry = store.StashEntry(
            title="Alpha", summary="one-liner", detail_file="alpha.md"
        )
        line = entry.to_line()
        assert line == "- **[Alpha]** — one-liner → [detail](alpha.md)"

    def test_parse_simple_entry(self) -> None:
        text = "# Stash\n\n- **[Alpha]** — one-liner\n"
        _, sections = store._parse(text)
        top = [s for s in sections if not s.heading][0]
        assert len(top.entries) == 1
        assert top.entries[0].title == "Alpha"
        assert top.entries[0].summary == "one-liner"
        assert top.entries[0].detail_file is None

    def test_parse_entry_with_detail(self) -> None:
        text = (
            "# Stash\n\n- **[Beta]** — summary text → [detail](beta.md)\n"
        )
        _, sections = store._parse(text)
        entries = sections[0].entries
        assert entries[0].title == "Beta"
        assert entries[0].summary == "summary text"
        assert entries[0].detail_file == "beta.md"

    def test_parse_with_unattached_section(self) -> None:
        text = (
            "# Stash\n"
            "\n"
            "preamble line\n"
            "\n"
            "## Unattached\n"
            "\n"
            "- **[Cross-project]** — idea\n"
        )
        _, sections = store._parse(text)
        unattached = [s for s in sections if s.heading == "## Unattached"]
        assert len(unattached) == 1
        assert len(unattached[0].entries) == 1
        assert unattached[0].entries[0].title == "Cross-project"


# ---------------------------------------------------------------------------
# add
# ---------------------------------------------------------------------------


class TestAdd:
    def test_project_add_creates_stash_file(self, project_root: Path) -> None:
        result = store.add(project_root, title="Alpha", summary="one-liner")
        assert result["action"] == "added"
        assert result["scope"] == "project"
        assert result["section"] == "(top)"
        stash_file = project_root / ".claude" / "stash" / "stash.md"
        assert stash_file.exists()
        text = stash_file.read_text()
        assert "# Stash" in text
        assert "- **[Alpha]** — one-liner" in text

    def test_project_add_appends_to_existing(self, project_root: Path) -> None:
        store.add(project_root, title="Alpha", summary="first")
        store.add(project_root, title="Beta", summary="second")
        listing = store.review(project_root, scope="project")
        entries = listing["results"][0]["sections"][0]["entries"]
        assert [e["title"] for e in entries] == ["Alpha", "Beta"]

    def test_unattached_add_writes_user_stash(
        self, project_root: Path, user_dir: Path
    ) -> None:
        result = store.add(
            project_root,
            title="Cross",
            summary="cross-project idea",
            unattached=True,
        )
        assert result["scope"] == "user"
        assert result["section"] == "## Unattached"
        user_stash = user_dir / "stash.md"
        assert user_stash.exists()
        text = user_stash.read_text()
        assert "## Unattached" in text
        assert "- **[Cross]** — cross-project idea" in text

    def test_add_with_detail_creates_companion_file(
        self, project_root: Path
    ) -> None:
        result = store.add(
            project_root,
            title="Complex",
            summary="one-line",
            detail="## Goal\n\nReally long content here.",
        )
        assert result["detail_file"] is not None
        detail_path = Path(result["detail_file"])
        assert detail_path.exists()
        content = detail_path.read_text()
        assert content.startswith("# Complex")
        assert "Really long content here." in content

        stash_text = (
            project_root / ".claude" / "stash" / "stash.md"
        ).read_text()
        assert "[detail](complex.md)" in stash_text

    def test_add_rejects_duplicate_title(self, project_root: Path) -> None:
        store.add(project_root, title="Dup", summary="first")
        with pytest.raises(ValueError, match="already exists"):
            store.add(project_root, title="Dup", summary="second")

    def test_add_requires_title_and_summary(self, project_root: Path) -> None:
        with pytest.raises(ValueError):
            store.add(project_root, title="", summary="x")
        with pytest.raises(ValueError):
            store.add(project_root, title="x", summary="")


# ---------------------------------------------------------------------------
# review
# ---------------------------------------------------------------------------


class TestReview:
    def test_review_project_only(self, project_root: Path, user_dir: Path) -> None:
        store.add(project_root, title="P1", summary="p1")
        store.add(project_root, title="U1", summary="u1", unattached=True)
        result = store.review(project_root, scope="project")
        assert len(result["results"]) == 1
        assert result["results"][0]["scope"] == "project"
        assert result["results"][0]["total"] == 1

    def test_review_user_only(self, project_root: Path, user_dir: Path) -> None:
        store.add(project_root, title="P1", summary="p1")
        store.add(project_root, title="U1", summary="u1", unattached=True)
        result = store.review(project_root, scope="user")
        assert len(result["results"]) == 1
        assert result["results"][0]["scope"] == "user"
        assert result["results"][0]["total"] == 1

    def test_review_all_returns_both(
        self, project_root: Path, user_dir: Path
    ) -> None:
        store.add(project_root, title="P1", summary="p1")
        store.add(project_root, title="U1", summary="u1", unattached=True)
        result = store.review(project_root, scope="all")
        scopes = [r["scope"] for r in result["results"]]
        assert scopes == ["project", "user"]

    def test_review_missing_file_returns_empty(
        self, project_root: Path
    ) -> None:
        result = store.review(project_root, scope="project")
        r = result["results"][0]
        assert r["exists"] is False
        assert r["total"] == 0
        assert r["sections"] == []

    def test_review_inlines_detail_content(self, project_root: Path) -> None:
        store.add(
            project_root,
            title="Rich",
            summary="s",
            detail="Really important context.",
        )
        result = store.review(project_root, scope="project")
        entry = result["results"][0]["sections"][0]["entries"][0]
        assert entry["detail_file"] == "rich.md"
        assert "Really important context." in entry["detail_content"]

    def test_review_rejects_invalid_scope(self, project_root: Path) -> None:
        with pytest.raises(ValueError, match="invalid scope"):
            store.review(project_root, scope="nonsense")


# ---------------------------------------------------------------------------
# remove
# ---------------------------------------------------------------------------


class TestRemove:
    def test_remove_project_entry(self, project_root: Path) -> None:
        store.add(project_root, title="Alpha", summary="one")
        result = store.remove(project_root, title="Alpha")
        assert result["action"] == "removed"
        assert result["scope"] == "project"
        listing = store.review(project_root, scope="project")
        assert listing["results"][0]["total"] == 0

    def test_remove_also_deletes_detail(self, project_root: Path) -> None:
        store.add(
            project_root, title="Complex", summary="s", detail="body"
        )
        detail = project_root / ".claude" / "stash" / "complex.md"
        assert detail.exists()
        result = store.remove(project_root, title="Complex")
        assert result["detail_deleted"] is not None
        assert not detail.exists()

    def test_remove_user_entry(
        self, project_root: Path, user_dir: Path
    ) -> None:
        store.add(
            project_root, title="Cross", summary="c", unattached=True
        )
        result = store.remove(project_root, title="Cross", scope="user")
        assert result["action"] == "removed"
        assert result["scope"] == "user"

    def test_remove_scope_all_searches_both(
        self, project_root: Path, user_dir: Path
    ) -> None:
        store.add(
            project_root, title="Cross", summary="c", unattached=True
        )
        result = store.remove(project_root, title="Cross", scope="all")
        assert result["action"] == "removed"
        assert result["scope"] == "user"

    def test_remove_not_found(self, project_root: Path) -> None:
        result = store.remove(project_root, title="Ghost")
        assert result["action"] == "not_found"

    def test_remove_preserves_other_entries(
        self, project_root: Path
    ) -> None:
        store.add(project_root, title="A", summary="a")
        store.add(project_root, title="B", summary="b")
        store.add(project_root, title="C", summary="c")
        store.remove(project_root, title="B")
        listing = store.review(project_root, scope="project")
        titles = [
            e["title"]
            for s in listing["results"][0]["sections"]
            for e in s["entries"]
        ]
        assert titles == ["A", "C"]


# ---------------------------------------------------------------------------
# promote
# ---------------------------------------------------------------------------


class TestPromote:
    def test_promote_unattached_to_project(
        self, project_root: Path, user_dir: Path
    ) -> None:
        store.add(
            project_root, title="Cross", summary="c", unattached=True
        )
        result = store.promote(project_root, title="Cross")
        assert result["action"] == "promoted"

        user_listing = store.review(project_root, scope="user")
        assert user_listing["results"][0]["total"] == 0

        project_listing = store.review(project_root, scope="project")
        titles = [
            e["title"]
            for s in project_listing["results"][0]["sections"]
            for e in s["entries"]
        ]
        assert "Cross" in titles

    def test_promote_moves_detail_file(
        self, project_root: Path, user_dir: Path
    ) -> None:
        store.add(
            project_root,
            title="Cross",
            summary="c",
            detail="substantial context",
            unattached=True,
        )
        user_detail = user_dir / "cross.md"
        assert user_detail.exists()

        store.promote(project_root, title="Cross")

        project_detail = (
            project_root / ".claude" / "stash" / "cross.md"
        )
        assert project_detail.exists()
        assert not user_detail.exists()

    def test_promote_conflict_raises(
        self, project_root: Path, user_dir: Path
    ) -> None:
        store.add(project_root, title="Same", summary="p")
        store.add(
            project_root, title="Same", summary="u", unattached=True
        )
        with pytest.raises(ValueError, match="already exists in project stash"):
            store.promote(project_root, title="Same")

    def test_promote_not_found(
        self, project_root: Path, user_dir: Path
    ) -> None:
        result = store.promote(project_root, title="Ghost")
        assert result["action"] == "not_found"


# ---------------------------------------------------------------------------
# Round-trip
# ---------------------------------------------------------------------------


class TestRoundTrip:
    def test_add_write_read_cycle(self, project_root: Path) -> None:
        store.add(project_root, title="A", summary="a")
        store.add(project_root, title="B", summary="b", detail="with body")
        store.add(project_root, title="C", summary="c")

        path = project_root / ".claude" / "stash" / "stash.md"
        text = path.read_text()
        _, sections = store._parse(text)
        entries = [e for s in sections for e in s.entries]
        titles = [e.title for e in entries]
        assert titles == ["A", "B", "C"]

        b_entry = next(e for e in entries if e.title == "B")
        assert b_entry.detail_file == "b.md"

    def test_user_stash_keeps_unattached_heading(
        self, project_root: Path, user_dir: Path
    ) -> None:
        store.add(
            project_root, title="X", summary="x", unattached=True
        )
        text = (user_dir / "stash.md").read_text()
        assert "## Unattached" in text
        assert "# Stash" in text


# ---------------------------------------------------------------------------
# Server import smoke test
# ---------------------------------------------------------------------------


class TestServerImport:
    """Smoke test: the server module imports and registers its tools."""

    def test_server_imports(self) -> None:
        from servers import stash as server_mod
        assert server_mod.mcp is not None
        assert server_mod.mcp.name == "ocd-stash"
