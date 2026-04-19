"""Integration tests for cleanup inventory — ephemeral-only filter."""

from pathlib import Path

from systems.sandbox._cleanup import cleanup_inventory
from systems.sandbox._worktree import worktree_add, worktree_setup


class TestCleanupEphemeralFilter:
    def test_inventory_excludes_durable_worktree(self, project_repo: Path):
        worktree_add("feature-x", "sandbox/feature-x", base_ref="main")
        inventory = cleanup_inventory()
        worktree_paths = [entry.path for entry in inventory.worktrees]
        sibling = (project_repo.parent / f"{project_repo.name}--feature-x").resolve()
        assert str(sibling) not in worktree_paths

    def test_inventory_includes_ephemeral_worktree(self, project_repo: Path):
        worktree_setup("inspect-x")
        inventory = cleanup_inventory()
        worktree_branches = [entry.branch for entry in inventory.worktrees]
        assert "sandbox/tmp/inspect-x" in worktree_branches

    def test_inventory_includes_ephemeral_sibling_dir(
        self, project_repo: Path, tmp_path: Path,
    ):
        # Simulate a leftover ephemeral sibling directory (no worktree attached)
        leftover = tmp_path / f"{project_repo.name}--tmp-orphan"
        leftover.mkdir()
        (leftover / "readme.md").write_text("leftover\n")
        inventory = cleanup_inventory()
        sibling_paths = [entry.path for entry in inventory.siblings]
        assert str(leftover.resolve()) in sibling_paths

    def test_inventory_excludes_durable_sibling_dir(
        self, project_repo: Path, tmp_path: Path,
    ):
        # Durable siblings (no --tmp- prefix) must not surface in cleanup
        durable = tmp_path / f"{project_repo.name}--feature-x"
        durable.mkdir()
        inventory = cleanup_inventory()
        sibling_paths = [entry.path for entry in inventory.siblings]
        assert str(durable.resolve()) not in sibling_paths
