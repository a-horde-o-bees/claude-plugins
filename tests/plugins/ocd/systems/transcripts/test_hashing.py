"""Tests for git-compatible blob hash and existing-hash lookup."""

import json
from pathlib import Path

from systems.transcripts._transcripts import _existing_githash, _git_blob_hash


class TestGitBlobHash:
    def test_matches_git_hash_object(self, tmp_path: Path):
        # sha1('blob 6\x00hello\n') is the canonical git hash for 'hello\n'.
        f = tmp_path / "t"
        f.write_bytes(b"hello\n")
        assert _git_blob_hash(f) == "ce013625030ba8dba906f756967f9e9ca394464a"

    def test_same_content_same_hash(self, tmp_path: Path):
        a = tmp_path / "a"
        b = tmp_path / "b"
        a.write_bytes(b"same")
        b.write_bytes(b"same")
        assert _git_blob_hash(a) == _git_blob_hash(b)

    def test_different_content_different_hash(self, tmp_path: Path):
        a = tmp_path / "a"
        b = tmp_path / "b"
        a.write_bytes(b"one")
        b.write_bytes(b"two")
        assert _git_blob_hash(a) != _git_blob_hash(b)


class TestExistingGithash:
    def test_none_for_missing_file(self, tmp_path: Path):
        assert _existing_githash(tmp_path / "nope.json") is None

    def test_returns_hash_from_valid_envelope(self, tmp_path: Path):
        p = tmp_path / "x_chat.json"
        p.write_text(json.dumps({"githash": "abc123", "messages": []}))
        assert _existing_githash(p) == "abc123"

    def test_none_for_malformed_json(self, tmp_path: Path):
        p = tmp_path / "x_chat.json"
        p.write_text("{not json")
        assert _existing_githash(p) is None

    def test_none_for_non_dict_payload(self, tmp_path: Path):
        p = tmp_path / "x_chat.json"
        p.write_text(json.dumps(["a", "b"]))
        assert _existing_githash(p) is None

    def test_none_when_field_missing(self, tmp_path: Path):
        p = tmp_path / "x_chat.json"
        p.write_text(json.dumps({"messages": []}))
        assert _existing_githash(p) is None
