"""Tests for message-text extraction and transcript filtering."""

import json
from pathlib import Path

from systems.transcripts._transcripts import _chat_extract, _extract_message_text


class TestExtractMessageText:
    def test_string(self):
        assert _extract_message_text("hello") == "hello"

    def test_list_of_text_parts_joined_with_newline(self):
        content = [
            {"type": "text", "text": "line one"},
            {"type": "text", "text": "line two"},
        ]
        assert _extract_message_text(content) == "line one\nline two"

    def test_list_skips_non_text_parts(self):
        content = [
            {"type": "text", "text": "visible"},
            {"type": "tool_use", "name": "Bash", "input": {}},
            {"type": "thinking", "thinking": "hidden"},
        ]
        assert _extract_message_text(content) == "visible"

    def test_list_of_strings(self):
        assert _extract_message_text(["a", "b"]) == "a\nb"

    def test_none(self):
        assert _extract_message_text(None) == ""

    def test_empty_list(self):
        assert _extract_message_text([]) == ""


class TestChatExtract:
    def _write(self, path: Path, entries: list[dict]) -> None:
        path.write_text("\n".join(json.dumps(e) for e in entries) + "\n")

    def test_keeps_user_and_assistant_with_text(self, tmp_path: Path):
        src = tmp_path / "t.jsonl"
        self._write(src, [
            {"type": "user", "uuid": "1", "timestamp": "t1",
             "message": {"content": "hi"}},
            {"type": "assistant", "uuid": "2", "timestamp": "t2",
             "message": {"content": "hello"}},
        ])
        msgs = _chat_extract(src)
        assert len(msgs) == 2
        assert msgs[0] == {"type": "user", "timestamp": "t1", "message": "hi"}
        assert msgs[1] == {"type": "assistant", "timestamp": "t2", "message": "hello"}

    def test_filters_tool_results(self, tmp_path: Path):
        src = tmp_path / "t.jsonl"
        self._write(src, [
            {"type": "user", "uuid": "1", "timestamp": "t1",
             "toolUseResult": {"stdout": "..."},
             "message": {"content": "result payload"}},
            {"type": "user", "uuid": "2", "timestamp": "t2",
             "message": {"content": "real prompt"}},
        ])
        msgs = _chat_extract(src)
        assert len(msgs) == 1
        assert msgs[0]["message"] == "real prompt"

    def test_filters_tool_use_and_thinking_blocks(self, tmp_path: Path):
        src = tmp_path / "t.jsonl"
        self._write(src, [
            {"type": "assistant", "uuid": "1", "timestamp": "t1",
             "message": {"content": [
                 {"type": "thinking", "thinking": "private"},
                 {"type": "tool_use", "name": "Bash", "input": {}},
                 {"type": "text", "text": "visible answer"},
             ]}},
        ])
        msgs = _chat_extract(src)
        assert len(msgs) == 1
        assert msgs[0]["message"] == "visible answer"

    def test_filters_empty_messages(self, tmp_path: Path):
        src = tmp_path / "t.jsonl"
        self._write(src, [
            {"type": "user", "uuid": "1", "timestamp": "t1",
             "message": {"content": ""}},
            {"type": "assistant", "uuid": "2", "timestamp": "t2",
             "message": {"content": [{"type": "tool_use", "name": "X"}]}},
            {"type": "user", "uuid": "3", "timestamp": "t3",
             "message": {"content": "kept"}},
        ])
        msgs = _chat_extract(src)
        assert [m["message"] for m in msgs] == ["kept"]

    def test_requires_uuid_and_valid_type(self, tmp_path: Path):
        src = tmp_path / "t.jsonl"
        self._write(src, [
            {"type": "summary", "uuid": "1", "message": {"content": "meta"}},
            {"type": "user", "message": {"content": "no uuid"}},
            {"type": "user", "uuid": "2", "timestamp": "t", "message": {"content": "kept"}},
        ])
        msgs = _chat_extract(src)
        assert [m["message"] for m in msgs] == ["kept"]

    def test_handles_malformed_and_blank_lines(self, tmp_path: Path):
        src = tmp_path / "t.jsonl"
        src.write_text(
            "\n"
            "{not valid json\n"
            + json.dumps({
                "type": "user", "uuid": "1", "timestamp": "t",
                "message": {"content": "survived"},
            }) + "\n"
        )
        msgs = _chat_extract(src)
        assert [m["message"] for m in msgs] == ["survived"]

    def test_preserves_file_order(self, tmp_path: Path):
        src = tmp_path / "t.jsonl"
        self._write(src, [
            {"type": "user", "uuid": "1", "timestamp": "t1", "message": {"content": "A"}},
            {"type": "assistant", "uuid": "2", "timestamp": "t2", "message": {"content": "B"}},
            {"type": "user", "uuid": "3", "timestamp": "t3", "message": {"content": "C"}},
        ])
        msgs = _chat_extract(src)
        assert [m["message"] for m in msgs] == ["A", "B", "C"]
