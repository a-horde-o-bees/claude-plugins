"""Unit tests for the friction MCP server.

Exercises the entry parsing, storage helpers, and tool handlers directly —
no subprocess, no MCP protocol layer. Tests isolate filesystem state via
tmp_path and monkeypatch.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from servers import friction  # noqa: E402


@pytest.fixture
def friction_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Isolated friction directory scoped to a single test."""
    target = tmp_path / "friction"
    monkeypatch.setattr(friction, "FRICTION_DIR", target)
    return target


# ===========================================================================
# Parsing and formatting
# ===========================================================================


class TestEntryParsing:
    """Round-trip parsing of the canonical entry format."""

    def test_parse_canonical_line(self) -> None:
        line = (
            "- 2026-04-05 — tool X missing capability Y; "
            "expected Y to be present; workaround: none — blocked"
        )
        entries = friction._parse_entries(line)
        assert len(entries) == 1
        entry = entries[0]
        assert entry.logged_on == "2026-04-05"
        assert entry.what_happened == "tool X missing capability Y"
        assert entry.expected == "Y to be present"
        assert entry.workaround == "none — blocked"

    def test_format_round_trips(self) -> None:
        original = friction.Entry(
            logged_on="2026-04-05",
            what_happened="tool X missing capability Y",
            expected="Y to be present",
            workaround="none — blocked",
        )
        reparsed = friction._parse_entries(original.format())
        assert len(reparsed) == 1
        assert reparsed[0] == original

    def test_parse_ignores_blank_and_non_matching_lines(self) -> None:
        content = (
            "\n"
            "Some heading text\n"
            "- 2026-04-05 — a; expected b; workaround: c\n"
            "\n"
            "- 2026-04-06 — d; expected e; workaround: f\n"
        )
        entries = friction._parse_entries(content)
        assert [e.logged_on for e in entries] == ["2026-04-05", "2026-04-06"]

    def test_real_existing_file_round_trips(self) -> None:
        """The existing evaluate-skills.md in the repo must parse and
        re-serialize to the same content — byte-identical after strip."""
        existing = Path(".claude/ocd/friction/evaluate-skills.md")
        if not existing.exists():
            pytest.skip("no existing friction file to round-trip")
        content = existing.read_text()
        entries = friction._parse_entries(content)
        assert len(entries) > 0
        reformatted = "\n".join(e.format() for e in entries) + "\n"
        assert reformatted.strip() == content.strip()


# ===========================================================================
# System name validation
# ===========================================================================


class TestSystemValidation:
    def test_valid_names_accepted(self) -> None:
        for name in ["navigator", "evaluate-skills", "plugin_framework", "a1", "A_B-c"]:
            friction._validate_system(name)  # no raise

    def test_path_separator_rejected(self) -> None:
        with pytest.raises(ValueError):
            friction._validate_system("foo/bar")

    def test_empty_rejected(self) -> None:
        with pytest.raises(ValueError):
            friction._validate_system("")

    def test_dot_prefix_rejected(self) -> None:
        with pytest.raises(ValueError):
            friction._validate_system(".hidden")


# ===========================================================================
# friction_log
# ===========================================================================


class TestFrictionLog:
    def test_creates_file_on_first_log(self, friction_dir: Path) -> None:
        result = json.loads(friction.friction_log(
            system="navigator",
            what_happened="scan missed a file",
            expected="scan picks up all files",
            workaround="manual scan",
        ))
        assert result["system"] == "navigator"
        assert result["index"] == 0
        assert (friction_dir / "navigator.md").exists()

    def test_appends_to_existing_file(self, friction_dir: Path) -> None:
        friction.friction_log("navigator", "a", "b", "c")
        result = json.loads(friction.friction_log("navigator", "d", "e", "f"))
        assert result["index"] == 1
        content = (friction_dir / "navigator.md").read_text()
        assert content.count("\n") == 2

    def test_invalid_system_returns_error(self, friction_dir: Path) -> None:
        result = json.loads(friction.friction_log(
            "bad/name", "a", "b", "c",
        ))
        assert "error" in result

    def test_entries_use_today(self, friction_dir: Path) -> None:
        from datetime import date
        result = json.loads(friction.friction_log("navigator", "a", "b", "c"))
        assert result["logged_on"] == date.today().isoformat()


# ===========================================================================
# friction_list
# ===========================================================================


class TestFrictionList:
    def test_empty_dir_returns_zero(self, friction_dir: Path) -> None:
        result = json.loads(friction.friction_list())
        assert result == {"total": 0, "entries": []}

    def test_lists_across_systems(self, friction_dir: Path) -> None:
        friction.friction_log("navigator", "a", "b", "c")
        friction.friction_log("evaluate-skills", "d", "e", "f")
        result = json.loads(friction.friction_list())
        assert result["total"] == 2
        systems = {e["system"] for e in result["entries"]}
        assert systems == {"navigator", "evaluate-skills"}

    def test_filter_by_system(self, friction_dir: Path) -> None:
        friction.friction_log("navigator", "a", "b", "c")
        friction.friction_log("evaluate-skills", "d", "e", "f")
        result = json.loads(friction.friction_list(system="navigator"))
        assert result["total"] == 1
        assert result["entries"][0]["system"] == "navigator"

    def test_limit_applied(self, friction_dir: Path) -> None:
        for i in range(5):
            friction.friction_log("navigator", f"entry-{i}", "b", "c")
        result = json.loads(friction.friction_list(limit=2))
        assert len(result["entries"]) == 2

    def test_entries_carry_index_within_system(self, friction_dir: Path) -> None:
        friction.friction_log("navigator", "first", "b", "c")
        friction.friction_log("navigator", "second", "b", "c")
        result = json.loads(friction.friction_list(system="navigator"))
        indices = {e["index"] for e in result["entries"]}
        assert indices == {0, 1}


# ===========================================================================
# friction_resolve
# ===========================================================================


class TestFrictionResolve:
    def test_removes_entry(self, friction_dir: Path) -> None:
        friction.friction_log("navigator", "first", "b", "c")
        friction.friction_log("navigator", "second", "b", "c")
        result = json.loads(friction.friction_resolve("navigator", 0))
        assert result["removed"]["what_happened"] == "first"
        assert result["remaining"] == 1

    def test_out_of_range_returns_error(self, friction_dir: Path) -> None:
        friction.friction_log("navigator", "only", "b", "c")
        result = json.loads(friction.friction_resolve("navigator", 5))
        assert "error" in result

    def test_last_entry_deletes_file(self, friction_dir: Path) -> None:
        friction.friction_log("navigator", "only", "b", "c")
        friction.friction_resolve("navigator", 0)
        assert not (friction_dir / "navigator.md").exists()

    def test_invalid_system_returns_error(self, friction_dir: Path) -> None:
        result = json.loads(friction.friction_resolve("bad/sys", 0))
        assert "error" in result


# ===========================================================================
# friction_systems
# ===========================================================================


class TestFrictionSystems:
    def test_empty_when_no_logs(self, friction_dir: Path) -> None:
        result = json.loads(friction.friction_systems())
        assert result == {"total_systems": 0, "total_entries": 0, "systems": []}

    def test_counts_per_system(self, friction_dir: Path) -> None:
        friction.friction_log("navigator", "a", "b", "c")
        friction.friction_log("navigator", "d", "e", "f")
        friction.friction_log("evaluate-skills", "g", "h", "i")
        result = json.loads(friction.friction_systems())
        assert result["total_systems"] == 2
        assert result["total_entries"] == 3
        by_name = {row["system"]: row["count"] for row in result["systems"]}
        assert by_name == {"navigator": 2, "evaluate-skills": 1}


# ===========================================================================
# End-to-end lifecycle
# ===========================================================================


class TestLifecycle:
    def test_log_list_resolve_converges(self, friction_dir: Path) -> None:
        """Log two entries, resolve one, verify queue state converges."""
        friction.friction_log("navigator", "first", "exp", "wa")
        friction.friction_log("navigator", "second", "exp", "wa")
        listed = json.loads(friction.friction_list(system="navigator"))
        assert listed["total"] == 2

        friction.friction_resolve("navigator", 0)
        listed = json.loads(friction.friction_list(system="navigator"))
        assert listed["total"] == 1
        assert listed["entries"][0]["what_happened"] == "second"
