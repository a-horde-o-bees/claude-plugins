"""Integration tests for project-level tooling under tools/.

Covers the callable surface behind `bin/plugins-run`:
- `setup` verb — set_hookspath + setup_project end-to-end
- `sandbox-tests` verb — worktree-collision guard (happy-path run is
  covered transitively by every CI invocation)
- `tests` verb — covered transitively by every test run; not re-tested
  here to avoid subprocess recursion into the project's own suite
"""

import subprocess
from pathlib import Path

import pytest

from tools.setup._hookspath import set_hookspath
from tools.setup._orchestration import setup_project
from tools.testing._sandbox import sandbox_tests_run


@pytest.fixture
def tmp_git_project(tmp_path: Path, monkeypatch) -> Path:
    """A throwaway git repo with a parent dir so worktree siblings can land."""
    parent = tmp_path / "projects"
    parent.mkdir()
    project = parent / "plugins-under-test"
    project.mkdir()
    subprocess.run(
        ["git", "-C", str(project), "init", "--quiet", "-b", "main"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(project), "config", "user.email", "test@example.com"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(project), "config", "user.name", "Test"],
        check=True,
    )
    (project / "README.md").write_text("initial\n")
    subprocess.run(
        ["git", "-C", str(project), "add", "README.md"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(project), "commit", "-m", "init", "--quiet"],
        check=True,
    )
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(project))
    return project


class TestSetHookspath:
    def test_sets_when_githooks_dir_exists_and_unset(self, tmp_git_project: Path):
        (tmp_git_project / ".githooks").mkdir()

        assert set_hookspath(tmp_git_project) is True

        result = subprocess.run(
            ["git", "-C", str(tmp_git_project), "config", "--get", "core.hookspath"],
            capture_output=True, text=True,
        )
        assert result.stdout.strip() == ".githooks"

    def test_skips_when_already_set(self, tmp_git_project: Path):
        (tmp_git_project / ".githooks").mkdir()
        set_hookspath(tmp_git_project)

        # Re-run — already configured, no change
        assert set_hookspath(tmp_git_project) is False

    def test_skips_when_githooks_dir_absent(self, tmp_git_project: Path):
        """No .githooks/ directory — hook path stays default, return False."""
        assert set_hookspath(tmp_git_project) is False

        result = subprocess.run(
            ["git", "-C", str(tmp_git_project), "config", "--get", "core.hookspath"],
            capture_output=True, text=True,
        )
        assert result.stdout.strip() == ""


class TestSetupProject:
    def test_end_to_end_configures_hookspath(
        self, tmp_git_project: Path, capsys,
    ):
        (tmp_git_project / ".githooks").mkdir()

        exit_code = setup_project()

        assert exit_code == 0
        out = capsys.readouterr().out
        assert "Git hookspath set to .githooks" in out
        assert "Done." in out

    def test_idempotent_on_second_run(
        self, tmp_git_project: Path, capsys,
    ):
        (tmp_git_project / ".githooks").mkdir()
        setup_project()
        capsys.readouterr()  # drain

        exit_code = setup_project()

        assert exit_code == 0
        assert "already configured" in capsys.readouterr().out


class TestSandboxTestsCollisionGuard:
    def test_raises_when_worktree_path_exists(self, tmp_git_project: Path):
        """Pre-existing sibling at the derived worktree path must surface
        as a RuntimeError — don't silently overwrite or reuse."""
        head = subprocess.run(
            ["git", "-C", str(tmp_git_project), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        short_sha = head[:7]
        collision = tmp_git_project.parent / (
            f"{tmp_git_project.name}--tmp-test-{short_sha}"
        )
        collision.mkdir()

        with pytest.raises(RuntimeError, match="already in use"):
            sandbox_tests_run(ref="HEAD")
