"""End-to-end agent tests for sandbox skill orchestration.

The Python primitives in `_worktree.py` are covered by the unit-style
integration tests in `test_worktree.py`. These tests add the layer
above: spawn `claude -p` to run a real `/sandbox` verb invocation
through the markdown skill, then assert observable git/filesystem
side effects.

Marked `pytest.mark.agent` so they only run with `--run-agent`. They
require the user's installed plugin cache to reflect the branch under
test — run `/checkpoint` before invoking so the cached SKILL.md /
component files match the working tree, then:
`bin/project-run tests --plugin ocd --run-agent`.
"""

import shutil
import subprocess
from pathlib import Path

import pytest

from systems.sandbox._worktree import worktree_add


pytestmark = pytest.mark.agent

SPAWN_TIMEOUT_SEC = 300


@pytest.fixture(scope="session")
def claude_cli() -> str:
    cli = shutil.which("claude")
    if not cli:
        pytest.skip("claude CLI not on PATH")
    return cli


def _spawn_in(cli: str, cwd: Path, prompt: str) -> subprocess.CompletedProcess:
    """Run `claude -p <prompt>` with cwd set; return CompletedProcess."""
    return subprocess.run(
        [cli, "-p", prompt],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=False,
        timeout=SPAWN_TIMEOUT_SEC,
    )


def _commit_in(worktree: Path, filename: str, content: str) -> None:
    """Commit `filename` with `content` to `worktree`. Configures
    git identity locally so the test does not depend on user globals."""
    subprocess.run(
        ["git", "-C", str(worktree), "config", "user.email", "test@example.com"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(worktree), "config", "user.name", "Test"],
        check=True,
    )
    (worktree / filename).write_text(content)
    subprocess.run(
        ["git", "-C", str(worktree), "add", filename], check=True
    )
    subprocess.run(
        ["git", "-C", str(worktree), "commit", "-m", filename, "--quiet"],
        check=True,
    )


class TestUpdateFromSibling:
    """`/sandbox update` invoked from inside a sibling worktree —
    cwd-fallback derives the feature-id from the branch, all git
    operations target the sibling explicitly, branch lands on origin.
    """

    def test_no_arg_from_sibling_pushes_branch(
        self, project_repo: Path, claude_cli: str
    ):
        sibling = worktree_add(
            "feature-x", "sandbox/feature-x", base_ref="main"
        )
        _commit_in(sibling, "x.md", "feature-x work\n")

        result = _spawn_in(claude_cli, sibling, "/sandbox update")

        assert result.returncode == 0, (
            f"claude -p exited {result.returncode}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
        check = subprocess.run(
            [
                "git", "-C", str(sibling),
                "rev-parse", "--verify", "refs/remotes/origin/sandbox/feature-x",
            ],
            capture_output=True, text=True,
        )
        assert check.returncode == 0, (
            "sandbox/feature-x was not pushed to origin\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
