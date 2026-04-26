"""Tests for transcript export (write, skip-if-unchanged, in-place output)."""

import json
from pathlib import Path

from systems.transcripts._transcripts import (
    _git_blob_hash,
    _transcript_export,
    chat_clean,
    chat_export,
)


def _write_jsonl(path: Path, entries: list[dict]) -> None:
    path.write_text("\n".join(json.dumps(e) for e in entries) + "\n")


def _jsonl_with_one_message(path: Path, text: str = "hi") -> None:
    _write_jsonl(path, [{
        "type": "user", "uuid": "u", "timestamp": "t",
        "message": {"content": text},
    }])


class TestTranscriptExport:
    def test_writes_sibling_chat_json(self, tmp_path: Path):
        src = tmp_path / "abc.jsonl"
        _jsonl_with_one_message(src)
        assert _transcript_export(src) is True
        assert (tmp_path / "abc_chat.json").exists()

    def test_envelope_has_only_githash_and_messages(self, tmp_path: Path):
        src = tmp_path / "abc.jsonl"
        _jsonl_with_one_message(src)
        _transcript_export(src)
        envelope = json.loads((tmp_path / "abc_chat.json").read_text())
        assert set(envelope.keys()) == {"githash", "messages"}
        assert envelope["githash"] == _git_blob_hash(src)

    def test_skips_when_hash_matches(self, tmp_path: Path):
        src = tmp_path / "abc.jsonl"
        _jsonl_with_one_message(src)
        assert _transcript_export(src) is True
        assert _transcript_export(src) is False

    def test_rewrites_when_source_changes(self, tmp_path: Path):
        src = tmp_path / "abc.jsonl"
        _jsonl_with_one_message(src, "first")
        _transcript_export(src)
        _jsonl_with_one_message(src, "second")
        assert _transcript_export(src) is True
        envelope = json.loads((tmp_path / "abc_chat.json").read_text())
        assert envelope["messages"][0]["message"] == "second"


class TestChatExport:
    def test_counts_written_and_missing(self, projects_root: Path, project_dir: Path):
        _jsonl_with_one_message(project_dir / "a.jsonl")
        _jsonl_with_one_message(project_dir / "b.jsonl")
        counts = chat_export(["-test-project", "-does-not-exist"])
        assert counts == {"written": 2, "skipped": 0, "missing": 1}

    def test_output_lands_beside_source(self, projects_root: Path, project_dir: Path):
        _jsonl_with_one_message(project_dir / "a.jsonl")
        chat_export(["-test-project"])
        assert (project_dir / "a_chat.json").exists()
        assert list(projects_root.rglob("*_chat.json")) == [project_dir / "a_chat.json"]

    def test_second_run_skips_unchanged(self, projects_root: Path, project_dir: Path):
        _jsonl_with_one_message(project_dir / "a.jsonl")
        chat_export(["-test-project"])
        counts = chat_export(["-test-project"])
        assert counts == {"written": 0, "skipped": 1, "missing": 0}

    def test_does_not_descend_into_subdirectories(
        self, projects_root: Path, project_dir: Path
    ):
        _jsonl_with_one_message(project_dir / "top.jsonl")
        sub = project_dir / "agents"
        sub.mkdir()
        _jsonl_with_one_message(sub / "nested.jsonl")
        chat_export(["-test-project"])
        assert (project_dir / "top_chat.json").exists()
        assert not (sub / "nested_chat.json").exists()

    def test_does_not_pick_up_chat_json_as_source(
        self, projects_root: Path, project_dir: Path
    ):
        _jsonl_with_one_message(project_dir / "a.jsonl")
        # Stray file with the output suffix — glob is `*.jsonl`, so this
        # must be ignored as a source candidate.
        (project_dir / "stray_chat.json").write_text("{}")
        counts = chat_export(["-test-project"])
        assert counts["written"] == 1


class TestChatClean:
    def test_removes_chat_json_siblings(self, projects_root: Path, project_dir: Path):
        _jsonl_with_one_message(project_dir / "a.jsonl")
        _jsonl_with_one_message(project_dir / "b.jsonl")
        chat_export(["-test-project"])
        counts = chat_clean(["-test-project"])
        assert counts == {"removed": 2, "missing": 0}
        assert list(project_dir.glob("*_chat.json")) == []

    def test_preserves_source_jsonl(self, projects_root: Path, project_dir: Path):
        _jsonl_with_one_message(project_dir / "a.jsonl")
        chat_export(["-test-project"])
        chat_clean(["-test-project"])
        assert (project_dir / "a.jsonl").exists()

    def test_counts_missing_project(self, projects_root: Path):
        counts = chat_clean(["-nope"])
        assert counts == {"removed": 0, "missing": 1}
