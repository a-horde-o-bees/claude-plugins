"""Tests for systems.log.__main__.

Covers `_resolve_samples_dir` subtopic discovery — single-subtopic
auto-resolution, multi-subtopic disambiguation via `--subtopic`, error
paths with corrective messages.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from systems.log.__main__ import _SubtopicResolutionError, _resolve_samples_dir


def _make_args(**kwargs) -> argparse.Namespace:
    """Build a Namespace populated with the locator args; missing keys default to None."""
    defaults = {"subject": None, "subtopic": None, "dir": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _make_subject_tree(project_dir: Path, subject: str, subtopics: list[str]) -> Path:
    """Create logs/research/<subject>/<subtopic>-samples/ directories under project_dir."""
    subject_dir = project_dir / "logs" / "research" / subject
    subject_dir.mkdir(parents=True)
    for subtopic in subtopics:
        (subject_dir / f"{subtopic}-samples").mkdir()
    return subject_dir


@pytest.fixture
def project(tmp_path, monkeypatch):
    """Isolate `environment.get_project_dir()` to a tmp_path-rooted scratch project."""
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    return tmp_path


class TestSubtopicDiscovery:
    def test_single_subtopic_auto_resolves(self, project):
        _make_subject_tree(project, "mcp", ["repos"])
        result = _resolve_samples_dir(_make_args(subject="mcp"))
        assert result.name == "repos-samples"
        assert result.parent.name == "mcp"

    def test_multi_subtopic_without_flag_raises_with_corrective_message(self, project):
        _make_subject_tree(project, "mcp", ["repos", "tutorials"])
        with pytest.raises(_SubtopicResolutionError) as excinfo:
            _resolve_samples_dir(_make_args(subject="mcp"))
        msg = str(excinfo.value)
        assert "--subtopic" in msg
        assert "repos" in msg
        assert "tutorials" in msg

    def test_multi_subtopic_with_explicit_flag_resolves(self, project):
        _make_subject_tree(project, "mcp", ["repos", "tutorials"])
        result = _resolve_samples_dir(_make_args(subject="mcp", subtopic="tutorials"))
        assert result.name == "tutorials-samples"

    def test_invalid_subtopic_raises_with_available_list(self, project):
        _make_subject_tree(project, "mcp", ["repos", "tutorials"])
        with pytest.raises(_SubtopicResolutionError) as excinfo:
            _resolve_samples_dir(_make_args(subject="mcp", subtopic="missing"))
        msg = str(excinfo.value)
        assert "'missing'" in msg
        assert "repos" in msg
        assert "tutorials" in msg

    def test_no_subtopic_samples_folders_raises(self, project):
        # Subject dir exists but has no <subtopic>-samples/ children
        (project / "logs" / "research" / "mcp").mkdir(parents=True)
        with pytest.raises(_SubtopicResolutionError) as excinfo:
            _resolve_samples_dir(_make_args(subject="mcp"))
        assert "No <subtopic>-samples/" in str(excinfo.value)

    def test_subject_directory_missing_raises(self, project):
        with pytest.raises(_SubtopicResolutionError) as excinfo:
            _resolve_samples_dir(_make_args(subject="nonexistent"))
        assert "Subject directory not found" in str(excinfo.value)

    def test_dir_branch_returns_resolved_path(self, project):
        target = project / "explicit"
        target.mkdir()
        result = _resolve_samples_dir(_make_args(dir=str(target)))
        assert result == target.resolve()

    def test_dir_branch_validates_existence(self, project):
        with pytest.raises(_SubtopicResolutionError) as excinfo:
            _resolve_samples_dir(_make_args(dir=str(project / "missing")))
        assert "Directory not found" in str(excinfo.value)

    def test_subtopic_flag_ignored_when_dir_used(self, project):
        """`--subtopic` is only meaningful with `--subject`; with `--dir`, dir wins."""
        target = project / "explicit"
        target.mkdir()
        result = _resolve_samples_dir(_make_args(dir=str(target), subtopic="ignored"))
        assert result == target.resolve()
