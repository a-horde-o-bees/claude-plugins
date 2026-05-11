"""Integration tests for cleanup — inventory filter and remove execution."""

from pathlib import Path

from systems.sandbox._cleanup import cleanup_inventory, cleanup_remove
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


class TestCleanupRemove:
    def test_removes_sibling_path(
        self, project_repo: Path, tmp_path: Path,
    ):
        sibling = tmp_path / f"{project_repo.name}--tmp-orphan"
        sibling.mkdir()
        (sibling / "leftover.txt").write_text("junk\n")
        cleanup_remove([sibling], [])
        assert not sibling.exists()

    def test_removes_worktree_path(self, project_repo: Path):
        worktree_path = worktree_setup("inspect-x")
        assert worktree_path.exists()
        cleanup_remove([], [worktree_path])
        assert not worktree_path.exists()
        # Branch remains — cleanup_remove removes the worktree, not the branch
        inventory = cleanup_inventory()
        worktree_paths = [entry.path for entry in inventory.worktrees]
        assert str(worktree_path) not in worktree_paths

    def test_no_op_on_absent_sibling(
        self, project_repo: Path, tmp_path: Path,
    ):
        """Absent sibling path is silently skipped — a crashed setup can leave
        the inventory listing something that was already removed by hand."""
        absent = tmp_path / f"{project_repo.name}--tmp-never-existed"
        cleanup_remove([absent], [])  # must not raise
        assert not absent.exists()

    def test_mixed_siblings_and_worktrees(
        self, project_repo: Path, tmp_path: Path,
    ):
        sibling = tmp_path / f"{project_repo.name}--tmp-mixed"
        sibling.mkdir()
        worktree_path = worktree_setup("mixed-wt")

        cleanup_remove([sibling], [worktree_path])

        assert not sibling.exists()
        assert not worktree_path.exists()
