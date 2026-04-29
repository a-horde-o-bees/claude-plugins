"""Tests for _ingest: JSONL parsing, sync, idempotency."""

from systems.transcripts import _ingest

from .conftest import make_assistant_text, make_user_msg


class TestEventLabel:
    def test_user_msg_top_level(self):
        e = make_user_msg("2026-04-28T10:00:00Z", "hello")
        label, ref = _ingest.event_label(e)
        assert label == "user_msg"
        assert ref is None

    def test_user_msg_sidechain(self):
        e = make_user_msg("2026-04-28T10:00:00Z", "hello")
        e["isSidechain"] = True
        label, _ = _ingest.event_label(e)
        assert label == "sidechain_user_msg"

    def test_assistant_text(self):
        e = make_assistant_text("2026-04-28T10:00:01Z", "ok")
        label, ref = _ingest.event_label(e)
        assert label.startswith("assistant[")
        assert "text" in label
        assert ref is None

    def test_tool_use_extracts_id_and_name(self):
        e = {
            "type": "assistant",
            "timestamp": "2026-04-28T10:00:01Z",
            "message": {
                "role": "assistant",
                "content": [{"type": "tool_use", "id": "toolu_x", "name": "Bash"}],
            },
        }
        label, ref = _ingest.event_label(e)
        assert label == "tool_use:Bash"
        assert ref == "toolu_x"

    def test_tool_result_links_back_via_ref(self):
        e = {
            "type": "user",
            "timestamp": "2026-04-28T10:00:02Z",
            "toolUseResult": {"stdout": "ok", "interrupted": False},
            "message": {
                "content": [{"type": "tool_result", "tool_use_id": "toolu_x"}],
            },
        }
        label, ref = _ingest.event_label(e)
        assert label == "tool_result"
        assert ref == "toolu_x"

    def test_interrupted_tool_result(self):
        e = {
            "type": "user",
            "timestamp": "2026-04-28T10:00:02Z",
            "toolUseResult": {"interrupted": True},
            "message": {"content": [{"type": "tool_result", "tool_use_id": "x"}]},
        }
        label, _ = _ingest.event_label(e)
        assert label == "tool_result_interrupted"

    def test_system_event_with_subtype(self):
        e = {
            "type": "system",
            "timestamp": "2026-04-28T10:00:03Z",
            "subtype": "turn_duration",
        }
        label, _ = _ingest.event_label(e)
        assert label == "system:turn_duration"


class TestExtractText:
    def test_string_content(self):
        e = {"message": {"content": "hello world"}}
        assert _ingest.extract_text(e) == "hello world"

    def test_list_content_with_text_block(self):
        e = {
            "message": {
                "content": [
                    {"type": "text", "text": "first"},
                    {"type": "tool_use", "name": "Bash"},
                    {"type": "text", "text": "second"},
                ],
            },
        }
        assert _ingest.extract_text(e) == "first\nsecond"

    def test_no_content_returns_none(self):
        assert _ingest.extract_text({"message": {}}) is None
        assert _ingest.extract_text({}) is None
        assert _ingest.extract_text({"message": {"content": "   "}}) is None


class TestSync:
    def test_ingests_synthetic_transcript(self, conn, seeded_project):
        seeded_project("-test-proj", {
            "sess1": [
                make_user_msg("2026-04-28T10:00:00Z", "hello", uuid="u1"),
                make_assistant_text("2026-04-28T10:00:05Z", "hi", uuid="a1"),
                make_user_msg("2026-04-28T10:01:00Z", "again", uuid="u2"),
            ],
        })
        added = _ingest.sync(conn)
        assert added == 3

    def test_sync_idempotent_on_unchanged(self, conn, seeded_project):
        seeded_project("-test-proj", {
            "sess1": [
                make_user_msg("2026-04-28T10:00:00Z", "hello", uuid="u1"),
                make_assistant_text("2026-04-28T10:00:05Z", "hi", uuid="a1"),
            ],
        })
        first = _ingest.sync(conn)
        second = _ingest.sync(conn)
        assert first == 2
        assert second == 0
        # No duplicates introduced.
        n = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        assert n == 2

    def test_sync_picks_up_appended_lines(self, conn, claude_home, seeded_project):
        # Initial transcript: 1 event.
        seeded_project("-proj", {
            "s1": [make_user_msg("2026-04-28T10:00:00Z", "a", uuid="u1")],
        })
        first = _ingest.sync(conn)
        assert first == 1

        # Append a second event to the same JSONL file.
        path = claude_home / "projects" / "-proj" / "s1.jsonl"
        with open(path, "a") as f:
            import json as _json
            f.write(_json.dumps(
                make_assistant_text("2026-04-28T10:00:05Z", "b", uuid="a1")
            ) + "\n")

        second = _ingest.sync(conn)
        assert second == 1  # only the new line inserted
        n = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        assert n == 2

    def test_sync_filters_by_project_name(self, conn, seeded_project):
        seeded_project("-proj-a", {
            "sa1": [make_user_msg("2026-04-28T10:00:00Z", "a")],
        })
        seeded_project("-proj-b", {
            "sb1": [make_user_msg("2026-04-28T10:00:00Z", "b")],
        })
        _ingest.sync(conn, project_filter="proj-a")
        rows = conn.execute(
            "SELECT DISTINCT project_name FROM events"
        ).fetchall()
        assert {r[0] for r in rows} == {"-proj-a"}

    def test_sync_uppercase_pk_uniqueness(self, conn, seeded_project):
        seeded_project("-proj", {
            "s1": [
                make_user_msg("2026-04-28T10:00:00Z", "a", uuid="u1"),
                make_assistant_text("2026-04-28T10:00:01Z", "b", uuid="a1"),
            ],
        })
        _ingest.sync(conn)
        _ingest.sync(conn)
        # PK is (file, line); duplicates must be impossible.
        total = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        distinct = conn.execute(
            "SELECT COUNT(*) FROM (SELECT 1 FROM events GROUP BY file, line)"
        ).fetchone()[0]
        assert total == distinct
