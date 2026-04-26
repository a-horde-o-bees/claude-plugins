"""Tests for project listing and current-project path resolution."""

from pathlib import Path

from systems.transcripts._transcripts import _path_encode, project_list, project_path


class TestProjectList:
    def test_returns_sorted_names(self, projects_root: Path):
        (projects_root / "-b-second").mkdir()
        (projects_root / "-a-first").mkdir()
        assert project_list() == ["-a-first", "-b-second"]

    def test_includes_dirs_only(self, projects_root: Path):
        (projects_root / "-real").mkdir()
        (projects_root / "stray.txt").write_text("x")
        assert project_list() == ["-real"]

    def test_empty_when_projects_root_missing(self, tmp_path: Path, monkeypatch):
        monkeypatch.setenv("CLAUDE_HOME", str(tmp_path / "does-not-exist"))
        assert project_list() == []


class TestProjectPath:
    def test_returns_path_when_current_project_has_transcripts(
        self, projects_root: Path, tmp_path: Path, monkeypatch
    ):
        repo = tmp_path / "repo"
        repo.mkdir()
        encoded = _path_encode(repo)
        target = projects_root / encoded
        target.mkdir()
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(repo))
        assert project_path() == target

    def test_returns_none_when_no_matching_dir(
        self, projects_root: Path, tmp_path: Path, monkeypatch
    ):
        repo = tmp_path / "repo-without-transcripts"
        repo.mkdir()
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(repo))
        assert project_path() is None

    def test_returned_path_name_is_encoded_form(
        self, projects_root: Path, tmp_path: Path, monkeypatch
    ):
        repo = tmp_path / "repo"
        repo.mkdir()
        encoded = _path_encode(repo)
        (projects_root / encoded).mkdir()
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(repo))
        result = project_path()
        assert result is not None
        assert result.name == encoded


class TestPathEncode:
    def test_absolute_slashes_become_dashes(self, tmp_path: Path):
        p = tmp_path / "sub" / "dir"
        p.mkdir(parents=True)
        encoded = _path_encode(p)
        assert "/" not in encoded
        assert encoded.startswith("-")
        assert encoded.endswith("-sub-dir")

    def test_spaces_become_dashes(self, tmp_path: Path):
        p = tmp_path / "with spaces"
        p.mkdir()
        encoded = _path_encode(p)
        assert " " not in encoded
        assert encoded.count("-") >= 1
