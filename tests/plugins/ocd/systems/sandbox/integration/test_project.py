"""Integration tests for sandbox._project — setup and teardown of the sibling
project substrate. Uses the shared project_repo fixture for a real git
repo root and writes the sibling into tmp_path."""

from pathlib import Path

import pytest

from systems.sandbox._project import project_setup, project_teardown


class TestProjectSetup:
    def test_creates_sibling_dir_and_git_init(
        self, project_repo: Path, tmp_path: Path,
    ) -> None:
        """setup creates the directory, initializes git, returns resolved path."""
        sandbox = tmp_path / f"{project_repo.name}--tmp-probe"
        result = project_setup(sandbox)
        assert result == sandbox.resolve()
        assert sandbox.is_dir()
        assert (sandbox / ".git").is_dir()

    def test_raises_when_path_already_exists(
        self, project_repo: Path, tmp_path: Path,
    ) -> None:
        """setup must not overwrite an existing sibling — caller picks a new topic."""
        sandbox = tmp_path / f"{project_repo.name}--tmp-collide"
        sandbox.mkdir()
        with pytest.raises(RuntimeError, match="already exists"):
            project_setup(sandbox)


class TestProjectTeardown:
    def test_removes_sibling_dir(
        self, project_repo: Path, tmp_path: Path,
    ) -> None:
        sandbox = tmp_path / f"{project_repo.name}--tmp-remove"
        project_setup(sandbox)
        assert sandbox.is_dir()
        project_teardown(sandbox)
        assert not sandbox.exists()

    def test_idempotent_on_absent_path(
        self, project_repo: Path, tmp_path: Path,
    ) -> None:
        """teardown on a never-created path is a no-op, not an error —
        crashed setup can leave nothing to remove."""
        absent = tmp_path / f"{project_repo.name}--tmp-nonexistent"
        project_teardown(absent)  # must not raise
        assert not absent.exists()
