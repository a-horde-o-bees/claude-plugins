"""Unit tests for _compute_git_hash."""

from pathlib import Path

from lib.navigator._scanner import _compute_git_hash


class TestComputeGitHash:
    def test_file_hash(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello\n")
        h = _compute_git_hash(f)
        assert h is not None
        assert len(h) == 40

    def test_same_content_same_hash(self, tmp_path):
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_text("content")
        f2.write_text("content")
        assert _compute_git_hash(f1) == _compute_git_hash(f2)

    def test_different_content_different_hash(self, tmp_path):
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_text("content1")
        f2.write_text("content2")
        assert _compute_git_hash(f1) != _compute_git_hash(f2)

    def test_nonexistent_file(self):
        assert _compute_git_hash(Path("/nonexistent/file.txt")) is None

    def test_directory(self, tmp_path):
        assert _compute_git_hash(tmp_path) is None
