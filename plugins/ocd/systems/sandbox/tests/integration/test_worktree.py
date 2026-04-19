"""Integration tests for sibling-worktree primitives.

Exercises real `git worktree` commands against fresh tmp git repos
provided by the `project_repo` fixture.
"""

import subprocess
from pathlib import Path

import pytest

from systems.sandbox._worktree import (
    sibling_path,
    worktree_add,
    worktree_list,
    worktree_remove,
    worktree_setup,
    worktree_status,
    worktree_teardown,
)


class TestWorktreeAddRemove:
    def test_add_creates_sibling_on_new_branch(self, project_repo: Path):
        path = worktree_add("feature-x", "sandbox/feature-x", base_ref="main")
        assert path.exists()
        assert path == sibling_path("feature-x").resolve()
        result = subprocess.run(
            ["git", "-C", str(project_repo), "branch", "--list", "sandbox/feature-x"],
            capture_output=True,
            text=True,
            check=True,
        )
        assert "sandbox/feature-x" in result.stdout

    def test_add_refuses_duplicate_path(self, project_repo: Path):
        worktree_add("feature-x", "sandbox/feature-x", base_ref="main")
        with pytest.raises(RuntimeError, match="already exists"):
            worktree_add("feature-x", "sandbox/feature-x", base_ref="main")

    def test_remove_idempotent_on_absent_worktree(self, project_repo: Path):
        worktree_remove("never-created")

    def test_remove_with_delete_branch_removes_branch(self, project_repo: Path):
        worktree_add("feature-x", "sandbox/feature-x", base_ref="main")
        worktree_remove("feature-x", delete_branch=True)
        result = subprocess.run(
            ["git", "-C", str(project_repo), "branch", "--list", "sandbox/feature-x"],
            capture_output=True,
            text=True,
            check=True,
        )
        assert result.stdout.strip() == ""


class TestWorktreeListStatus:
    def test_list_surfaces_added_worktree(self, project_repo: Path):
        worktree_add("feature-x", "sandbox/feature-x", base_ref="main")
        entries = worktree_list()
        names = [e.name for e in entries]
        assert "feature-x" in names

    def test_list_excludes_main_tree(self, project_repo: Path):
        entries = worktree_list()
        paths = [e.path.resolve() for e in entries]
        assert project_repo.resolve() not in paths

    def test_status_absent_worktree_reports_nonexistent(self, project_repo: Path):
        status = worktree_status("never-created")
        assert status.exists is False
        assert status.branch is None

    def test_status_present_worktree_reports_branch_and_clean(self, project_repo: Path):
        worktree_add("feature-x", "sandbox/feature-x", base_ref="main")
        status = worktree_status("feature-x")
        assert status.exists is True
        assert status.branch == "sandbox/feature-x"
        assert status.clean is True


class TestEphemeralSetupTeardown:
    def test_setup_places_sibling_with_tmp_prefix(self, project_repo: Path):
        path = worktree_setup("inspect-x")
        assert path == sibling_path("tmp-inspect-x").resolve()
        assert path.name == f"{project_repo.name}--tmp-inspect-x"

    def test_setup_creates_branch_under_tmp_namespace(self, project_repo: Path):
        worktree_setup("inspect-x")
        result = subprocess.run(
            [
                "git",
                "-C",
                str(project_repo),
                "branch",
                "--list",
                "sandbox/tmp/inspect-x",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        assert "sandbox/tmp/inspect-x" in result.stdout

    def test_teardown_removes_worktree_and_branch(self, project_repo: Path):
        worktree_setup("inspect-x")
        worktree_teardown("inspect-x")
        assert not sibling_path("tmp-inspect-x").exists()
        result = subprocess.run(
            [
                "git",
                "-C",
                str(project_repo),
                "branch",
                "--list",
                "sandbox/tmp/inspect-x",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        assert result.stdout.strip() == ""
