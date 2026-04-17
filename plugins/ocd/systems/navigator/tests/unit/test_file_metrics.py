"""Unit tests for _compute_file_metrics and metrics storage via paths_upsert."""

from pathlib import Path

from systems.navigator._db import get_connection
from systems.navigator._scanner import _compute_file_metrics, _compute_git_hash
from systems.navigator import paths_upsert


class TestComputeFileMetrics:
    def test_text_file(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("line1\nline2\nline3\n")
        m = _compute_file_metrics(f)
        assert m["git_hash"] is not None
        assert len(m["git_hash"]) == 40
        assert m["line_count"] == 3
        assert m["char_count"] == len("line1\nline2\nline3\n")

    def test_file_no_trailing_newline(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("line1\nline2")
        m = _compute_file_metrics(f)
        assert m["line_count"] == 2

    def test_empty_file(self, tmp_path):
        f = tmp_path / "empty.txt"
        f.write_text("")
        m = _compute_file_metrics(f)
        assert m["git_hash"] is not None
        assert m["line_count"] == 0
        assert m["char_count"] == 0

    def test_single_newline(self, tmp_path):
        f = tmp_path / "newline.txt"
        f.write_text("\n")
        m = _compute_file_metrics(f)
        assert m["line_count"] == 1
        assert m["char_count"] == 1

    def test_directory(self, tmp_path):
        m = _compute_file_metrics(tmp_path)
        assert m["git_hash"] is None
        assert m["line_count"] is None
        assert m["char_count"] is None

    def test_nonexistent(self):
        m = _compute_file_metrics(Path("/nonexistent/file.txt"))
        assert m["git_hash"] is None
        assert m["line_count"] is None
        assert m["char_count"] is None

    def test_consistent_with_git_hash(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("content")
        m = _compute_file_metrics(f)
        h = _compute_git_hash(f)
        assert m["git_hash"] == h


class TestSetEntryMetrics:
    def test_stores_metrics_on_describe(self, db_path, tmp_path):
        f = tmp_path / "test.py"
        f.write_text("a = 1\nb = 2\n")
        paths_upsert(db_path, str(f), description="Test file")
        conn = get_connection(db_path)
        row = conn.execute(
            "SELECT line_count, char_count FROM entries WHERE path = ?",
            (str(f),),
        ).fetchone()
        assert row["line_count"] == 2
        assert row["char_count"] == len("a = 1\nb = 2\n")
        conn.close()

    def test_updates_metrics_on_redescribe(self, db_path, tmp_path):
        f = tmp_path / "test.py"
        f.write_text("a = 1\n")
        paths_upsert(db_path, str(f), description="v1")
        f.write_text("a = 1\nb = 2\nc = 3\n")
        paths_upsert(db_path, str(f), description="v2")
        conn = get_connection(db_path)
        row = conn.execute(
            "SELECT line_count FROM entries WHERE path = ?",
            (str(f),),
        ).fetchone()
        assert row["line_count"] == 3
        conn.close()
