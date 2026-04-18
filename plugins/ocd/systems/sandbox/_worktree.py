"""Worktree verb — branched worktree substrate setup and teardown.

Creates a disposable branch at `sandbox/<topic>` and checks it out under
`.claude/worktrees/<topic>/`. Push is blocked via an invalid pushurl for
the duration so any accidental `git push` inside the worktree fails
loudly instead of publishing sandbox commits. Teardown removes the
worktree, deletes the branch, and restores the original pushurl.

Setup and teardown live here; interactive work between them — invoking
skills under test, driving `AskUserQuestion` flows, applying file
changes via Edit/Write — stays in the invoking session.
"""

import subprocess
from pathlib import Path

import plugin


WORKTREES_DIR = Path(".claude") / "worktrees"
PUSHURL_BLOCK = "file:///dev/null"


def worktree_setup(topic: str) -> Path:
    """Block push, create a branched worktree for the topic, return its path.

    Fails loudly if the worktree path or branch already exists.
    """
    project_root = plugin.get_project_dir()
    worktree_path = project_root / WORKTREES_DIR / topic
    branch = f"sandbox/{topic}"

    if worktree_path.exists():
        raise RuntimeError(
            f"worktree path already exists: {worktree_path} — pick a "
            "different topic or run `/ocd:sandbox cleanup` first",
        )
    if _branch_exists(project_root, branch):
        raise RuntimeError(
            f"branch already exists: {branch} — pick a different topic "
            "or run `/ocd:sandbox cleanup` first",
        )

    _block_push(project_root)
    worktree_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(project_root),
            "worktree",
            "add",
            "-b",
            branch,
            str(worktree_path),
        ],
        check=True,
    )
    return worktree_path.resolve()


def worktree_teardown(topic: str) -> None:
    """Remove the worktree, delete the branch, unblock push.

    Idempotent — absent worktree or branch is a no-op. Push is always
    unblocked on exit, even if worktree removal partially failed, so a
    crashed run doesn't leave the origin in a broken state.
    """
    project_root = plugin.get_project_dir()
    worktree_path = project_root / WORKTREES_DIR / topic
    branch = f"sandbox/{topic}"

    try:
        if worktree_path.exists():
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(project_root),
                    "worktree",
                    "remove",
                    "--force",
                    str(worktree_path),
                ],
                check=False,
            )
        if _branch_exists(project_root, branch):
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(project_root),
                    "branch",
                    "-D",
                    branch,
                ],
                check=False,
            )
    finally:
        _unblock_push(project_root)


def _branch_exists(project_root: Path, branch: str) -> bool:
    result = subprocess.run(
        [
            "git",
            "-C",
            str(project_root),
            "show-ref",
            "--verify",
            "--quiet",
            f"refs/heads/{branch}",
        ],
        capture_output=True,
    )
    return result.returncode == 0


def _block_push(project_root: Path) -> None:
    subprocess.run(
        [
            "git",
            "-C",
            str(project_root),
            "config",
            "remote.origin.pushurl",
            PUSHURL_BLOCK,
        ],
        check=True,
    )


def _unblock_push(project_root: Path) -> None:
    subprocess.run(
        [
            "git",
            "-C",
            str(project_root),
            "config",
            "--unset",
            "remote.origin.pushurl",
        ],
        check=False,
    )
