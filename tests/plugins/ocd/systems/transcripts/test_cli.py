"""Tests for CLI argument parsing and dispatch.

Covers the four verbs (project_list, project_path, chat_export, chat_clean),
the leading-dash project-name workaround, default-current-project resolution,
and mutual-exclusion of --all with named projects.
"""

import json
from pathlib import Path

import pytest

from systems.transcripts import __main__ as cli
from systems.transcripts._transcripts import _path_encode


def _jsonl_with_one_message(path: Path, text: str = "hi") -> None:
    path.write_text(json.dumps({
        "type": "user", "uuid": "u", "timestamp": "t",
        "message": {"content": text},
    }) + "\n")


class TestParser:
    def test_help_does_not_raise(self):
        with pytest.raises(SystemExit) as exc:
            cli.main(["--help"])
        assert exc.value.code == 0

    def test_chat_export_help(self, capsys: pytest.CaptureFixture[str]):
        with pytest.raises(SystemExit) as exc:
            cli.main(["chat_export", "--help"])
        assert exc.value.code == 0
        out = capsys.readouterr().out
        assert "--all" in out

    def test_chat_clean_help(self):
        with pytest.raises(SystemExit) as exc:
            cli.main(["chat_clean", "--help"])
        assert exc.value.code == 0

    def test_unknown_long_flag_errors(self, capsys: pytest.CaptureFixture[str]):
        with pytest.raises(SystemExit):
            cli.main(["chat_export", "--does-not-exist"])
        err = capsys.readouterr().err
        assert "unrecognized argument" in err


class TestProjectListVerb:
    def test_prints_each_project(
        self, projects_root: Path, capsys: pytest.CaptureFixture[str]
    ):
        (projects_root / "-a").mkdir()
        (projects_root / "-b").mkdir()
        assert cli.main(["project_list"]) == 0
        out = capsys.readouterr().out
        assert out.splitlines() == ["-a", "-b"]


class TestProjectPathVerb:
    def test_prints_path_when_current_project_has_transcripts(
        self,
        projects_root: Path,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ):
        repo = tmp_path / "repo"
        repo.mkdir()
        encoded = _path_encode(repo)
        target = projects_root / encoded
        target.mkdir()
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(repo))
        assert cli.main(["project_path"]) == 0
        out = capsys.readouterr().out.strip()
        assert out == str(target)

    def test_exits_nonzero_when_no_transcripts(
        self,
        projects_root: Path,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ):
        repo = tmp_path / "repo"
        repo.mkdir()
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(repo))
        assert cli.main(["project_path"]) == 1
        err = capsys.readouterr().err
        assert "no transcripts" in err


class TestLeadingDashProjectName:
    def test_chat_export_forwards_dash_name_to_positional(self, projects_root: Path):
        encoded = "-home-fake-proj"
        (projects_root / encoded).mkdir()
        _jsonl_with_one_message(projects_root / encoded / "a.jsonl")
        exit_code = cli.main(["chat_export", encoded])
        assert exit_code == 0
        assert (projects_root / encoded / "a_chat.json").exists()

    def test_chat_clean_forwards_dash_name(self, projects_root: Path):
        encoded = "-home-fake-proj"
        p = projects_root / encoded
        p.mkdir()
        (p / "a_chat.json").write_text(json.dumps({"githash": "x", "messages": []}))
        assert cli.main(["chat_clean", encoded]) == 0
        assert list(p.glob("*_chat.json")) == []


class TestMutuallyExclusive:
    def test_all_with_names_errors(
        self, projects_root: Path, capsys: pytest.CaptureFixture[str]
    ):
        (projects_root / "-x").mkdir()
        assert cli.main(["chat_export", "--all", "-x"]) == 1
        err = capsys.readouterr().err
        assert "--all" in err


class TestDefaultCurrentProject:
    def test_chat_export_defaults_to_current_project(
        self,
        projects_root: Path,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ):
        repo = tmp_path / "repo"
        repo.mkdir()
        encoded = _path_encode(repo)
        target = projects_root / encoded
        target.mkdir()
        _jsonl_with_one_message(target / "a.jsonl")
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(repo))
        assert cli.main(["chat_export"]) == 0
        assert (target / "a_chat.json").exists()

    def test_chat_export_errors_when_no_current_transcripts(
        self,
        projects_root: Path,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ):
        repo = tmp_path / "repo"
        repo.mkdir()
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(repo))
        assert cli.main(["chat_export"]) == 1
        err = capsys.readouterr().err
        assert "Could not resolve current project" in err
