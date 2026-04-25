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


class TestSiblingPath:
    def test_resolves_to_peer_of_project_root(self, project_repo: Path):
        result = sibling_path("feature-x")
        assert result.parent == project_repo.parent

    def test_uses_double_hyphen_separator(self, project_repo: Path):
        result = sibling_path("feature-x")
        assert result.name == f"{project_repo.name}--feature-x"

    def test_resolves_identically_from_inside_a_sibling(
        self, project_repo: Path, monkeypatch
    ):
        """`sibling_path` must anchor at the main worktree, so the same
        name resolves to the same path whether the caller runs from main
        or from inside a sibling. Without anchoring, a sibling caller
        derives its sibling path from its own basename and produces
        `<project>--<sibling>--<name>` — a doubly-nested location.
        """
        sibling = worktree_add(
            "feature-a", "sandbox/feature-a", base_ref="main"
        )
        from_main = sibling_path("feature-b")
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(sibling))
        from_sibling = sibling_path("feature-b")
        assert from_main == from_sibling


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

    def test_add_from_remote_ref_does_not_auto_track(self, project_repo: Path):
        """`worktree_add` with a remote-tracking `base_ref` (e.g.
        `origin/main`) must not auto-set upstream on the new branch.

        Git's default behavior is to track the start-point when the
        start-point is a remote-tracking ref — helpful for checkouts
        meant to follow that ref, wrong for sandbox feature branches.
        If the default leaks through, a failed or deferred `git push
        -u` leaves the sandbox tracking `origin/main`, and a later
        `git pull` or defaultless `git push` from the sandbox could
        silently touch main instead of the feature branch.
        """
        worktree_add(
            "feature-x", "sandbox/feature-x", base_ref="origin/main"
        )
        sibling = sibling_path("feature-x")
        result = subprocess.run(
            [
                "git", "-C", str(sibling),
                "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0, (
            "expected no upstream on new sandbox branch "
            f"(got: {result.stdout.strip()!r})"
        )

    def test_add_from_sandbox_branch_inherits_source_history(
        self, project_repo: Path
    ):
        """`worktree_add` with `base_ref=<sandbox-branch>` produces a
        new sibling whose HEAD has the source branch's tip in its
        ancestry. This is the primitive that pack relies on when
        splitting a sub-feature off an in-flight sandbox: the new
        sandbox branches from the source's tip, inheriting whatever
        commits the source has accumulated.
        """
        source = worktree_add(
            "feature-a", "sandbox/feature-a", base_ref="main"
        )
        subprocess.run(
            ["git", "-C", str(source), "config", "user.email", "test@example.com"],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(source), "config", "user.name", "Test"],
            check=True,
        )
        (source / "feature-a-only.md").write_text("a-only\n")
        subprocess.run(
            ["git", "-C", str(source), "add", "feature-a-only.md"], check=True
        )
        subprocess.run(
            ["git", "-C", str(source), "commit", "-m", "a-only", "--quiet"],
            check=True,
        )
        source_tip = subprocess.run(
            ["git", "-C", str(source), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()

        sub = worktree_add(
            "feature-a-helpers",
            "sandbox/feature-a-helpers",
            base_ref="sandbox/feature-a",
        )
        check = subprocess.run(
            [
                "git", "-C", str(sub),
                "merge-base", "--is-ancestor", source_tip, "HEAD",
            ],
            capture_output=True,
        )
        assert check.returncode == 0, (
            f"sub-feature HEAD does not have source tip {source_tip} in ancestry"
        )
        assert (sub / "feature-a-only.md").exists(), (
            "sub-feature worktree should contain source-only file"
        )


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

    def test_status_works_from_inside_a_sibling(
        self, project_repo: Path, monkeypatch
    ):
        """`worktree_status` looks up siblings by name — that name is
        anchored at the main worktree. From inside a sibling, the same
        name must resolve to the same registered worktree as it does
        from main. Without the anchor, the sibling-cwd caller computes
        a doubly-nested path and reports `exists: false`.
        """
        sibling = worktree_add(
            "feature-x", "sandbox/feature-x", base_ref="main"
        )
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(sibling))
        status = worktree_status("feature-x")
        assert status.exists is True
        assert status.branch == "sandbox/feature-x"

    def test_list_excludes_main_when_called_from_inside_a_sibling(
        self, project_repo: Path, monkeypatch
    ):
        """`worktree_list` enumerates non-main worktrees. The "main"
        anchor must be the actual main project, not the cwd's worktree
        — otherwise listing from a sibling would exclude the sibling
        itself instead of main.
        """
        sibling = worktree_add(
            "feature-x", "sandbox/feature-x", base_ref="main"
        )
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(sibling))
        entries = worktree_list()
        names = [e.name for e in entries]
        paths = [e.path.resolve() for e in entries]
        assert "feature-x" in names
        assert project_repo.resolve() not in paths


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
