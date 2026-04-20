"""Unit tests for sibling-path resolution."""

from pathlib import Path

import pytest

from systems.sandbox._worktree import sibling_path


@pytest.fixture(autouse=True)
def project_dir(tmp_path, monkeypatch) -> Path:
    project = tmp_path / "claude-plugins"
    project.mkdir()
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(project))
    return project


class TestSiblingPath:
    def test_resolves_to_peer_of_project_root(self, project_dir):
        result = sibling_path("feature-x")
        assert result.parent == project_dir.parent

    def test_uses_double_hyphen_separator(self, project_dir):
        result = sibling_path("feature-x")
        assert result.name == f"{project_dir.name}--feature-x"
