"""Worktree substrate — path resolution and lifecycle primitives.

Sibling-path convention places each worktree at `<parent>/<project>--<name>/`:

- The main session's filesystem walks do not descend into worktree copies
- A single `<project>--*` permission glob covers every substrate
- New Claude sessions started in a sibling bind their own `CLAUDE_PROJECT_DIR`,
  enabling true parallel operation without tool or state leakage

Callers choose the branch name and whether to create a new branch from
a base ref or attach to an existing branch; primitives do not hardcode
a branch namespace. Push-blocking is a caller-opt-in policy — callers
that block on `worktree_add` must unblock on `worktree_remove`.

Ephemeral sandboxes created by `worktree_setup` / `worktree_teardown`
use sibling name `tmp-<topic>` and branch `sandbox/tmp/<topic>` — the
`tmp-*` prefix distinguishes disposable sandboxes from durable feature
boxes in both the sibling listing and the branch namespace.
"""

import subprocess
from dataclasses import dataclass
from pathlib import Path

from tools import environment


PUSHURL_BLOCK = "file:///dev/null"
EPHEMERAL_NAME_PREFIX = "tmp-"
EPHEMERAL_BRANCH_PREFIX = "sandbox/tmp/"


@dataclass
class WorktreeStatus:
    """State snapshot of a single worktree.

    `clean` and the push-state fields are None for detached worktrees
    or when the worktree path is absent.
    """

    name: str
    path: Path
    exists: bool
    branch: str | None
    detached: bool
    clean: bool | None
    pushed: bool | None
    ahead_of_main: int | None


def sibling_path(name: str) -> Path:
    """Resolve `<parent>/<project>--<name>/` for the current project."""
    project_root = environment.get_project_dir()
    return project_root.parent / f"{project_root.name}--{name}"


def worktree_add(
    name: str,
    branch: str,
    *,
    base_ref: str | None = None,
    block_push: bool = False,
) -> Path:
    """Create a sibling worktree on `branch`.

    When `base_ref` is given, creates `branch` from it. When None,
    attaches to an existing local or origin branch (fetches origin
    if the branch is remote-only).

    When `block_push`, sets an invalid pushurl on the project's origin
    so accidental pushes from the worktree fail loudly. Pair with
    `worktree_remove(..., unblock_push=True)`.
    """
    project_root = environment.get_project_dir()
    path = sibling_path(name)

    if path.exists():
        raise RuntimeError(
            f"worktree path already exists: {path} — pick a different name "
            "or remove the existing worktree first",
        )

    if base_ref is not None:
        if _branch_exists(project_root, branch):
            raise RuntimeError(
                f"branch already exists: {branch} — pick a different name "
                "or attach to the existing branch with base_ref=None",
            )
        # `--no-track` suppresses git's default "track the start-point"
        # behavior, which fires when `base_ref` is a remote-tracking ref
        # (e.g. `origin/main`). Sandbox branches should have no upstream
        # until an explicit `git push -u` sets it to the feature branch's
        # own remote — otherwise a deferred or failed push leaves the
        # sandbox tracking origin/main silently.
        git_args = [
            "worktree", "add", "--no-track", "-b", branch, str(path), base_ref,
        ]
    else:
        if not _branch_exists_anywhere(project_root, branch):
            raise RuntimeError(
                f"branch not found locally or on origin: {branch}",
            )
        git_args = ["worktree", "add", str(path), branch]

    if block_push:
        _block_push(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "-C", str(project_root), *git_args],
        check=True,
    )
    return path.resolve()


def worktree_remove(
    name: str,
    *,
    delete_branch: bool = False,
    unblock_push: bool = False,
) -> None:
    """Remove a sibling worktree. Idempotent.

    When `delete_branch`, deletes the worktree's branch after removal.
    When `unblock_push`, clears the invalid pushurl set by
    `worktree_add(..., block_push=True)`. Push is always unblocked
    even if worktree removal fails, so a crashed caller cannot leave
    origin in a broken state.
    """
    project_root = environment.get_project_dir()
    path = sibling_path(name)
    branch = _worktree_branch(path) if delete_branch else None

    try:
        if path.exists():
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(project_root),
                    "worktree",
                    "remove",
                    "--force",
                    str(path),
                ],
                check=False,
            )
        if delete_branch and branch and _branch_exists(project_root, branch):
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
        if unblock_push:
            _unblock_push(project_root)


def worktree_list() -> list[WorktreeStatus]:
    """Enumerate every worktree on this project, main tree excluded."""
    project_root = environment.get_project_dir()
    raw = _list_raw(project_root)
    entries = []
    for path, branch, detached in raw:
        path_obj = Path(path)
        if path_obj.resolve() == project_root:
            continue
        name = _name_from_path(path_obj, project_root)
        clean = _is_clean(path_obj) if path_obj.exists() else None
        pushed, ahead = (
            _push_state(path_obj, branch)
            if branch and path_obj.exists()
            else (None, None)
        )
        entries.append(
            WorktreeStatus(
                name=name,
                path=path_obj,
                exists=path_obj.exists(),
                branch=branch,
                detached=detached,
                clean=clean,
                pushed=pushed,
                ahead_of_main=ahead,
            ),
        )
    return entries


def worktree_status(name: str) -> WorktreeStatus:
    """Return detailed state of a single sibling worktree by name."""
    path = sibling_path(name)
    if not path.exists():
        return WorktreeStatus(
            name=name,
            path=path,
            exists=False,
            branch=None,
            detached=False,
            clean=None,
            pushed=None,
            ahead_of_main=None,
        )

    branch = _worktree_branch(path)
    detached = branch is None
    clean = _is_clean(path)
    pushed, ahead = _push_state(path, branch) if branch else (None, None)
    return WorktreeStatus(
        name=name,
        path=path,
        exists=True,
        branch=branch,
        detached=detached,
        clean=clean,
        pushed=pushed,
        ahead_of_main=ahead,
    )


def worktree_setup(topic: str) -> Path:
    """Create an ephemeral sandbox worktree at `<parent>/<project>--tmp-<topic>/`.

    Branch `sandbox/tmp/<topic>` is created from `main`. Push is
    blocked via invalid pushurl for the duration so accidental pushes
    fail loudly.
    """
    return worktree_add(
        f"{EPHEMERAL_NAME_PREFIX}{topic}",
        f"{EPHEMERAL_BRANCH_PREFIX}{topic}",
        base_ref="main",
        block_push=True,
    )


def worktree_teardown(topic: str) -> None:
    """Remove the ephemeral sandbox worktree and unblock push."""
    worktree_remove(
        f"{EPHEMERAL_NAME_PREFIX}{topic}",
        delete_branch=True,
        unblock_push=True,
    )


def _list_raw(project_root: Path) -> list[tuple[str, str | None, bool]]:
    result = subprocess.run(
        ["git", "-C", str(project_root), "worktree", "list", "--porcelain"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return []

    entries: list[tuple[str, str | None, bool]] = []
    path: str | None = None
    branch: str | None = None
    detached = False

    def flush() -> None:
        if path is not None:
            entries.append((path, branch, detached))

    for line in result.stdout.splitlines():
        if line.startswith("worktree "):
            flush()
            path = line[len("worktree ") :]
            branch = None
            detached = False
        elif line.startswith("branch "):
            branch = line[len("branch refs/heads/") :]
        elif line == "detached":
            detached = True

    flush()
    return entries


def _name_from_path(path: Path, project_root: Path) -> str:
    prefix = f"{project_root.name}--"
    if path.parent == project_root.parent and path.name.startswith(prefix):
        return path.name[len(prefix) :]
    return path.name


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


def _branch_exists_anywhere(project_root: Path, branch: str) -> bool:
    if _branch_exists(project_root, branch):
        return True
    if _remote_branch_exists(project_root, branch):
        return True
    subprocess.run(
        ["git", "-C", str(project_root), "fetch", "origin", branch],
        capture_output=True,
    )
    return _remote_branch_exists(project_root, branch)


def _remote_branch_exists(project_root: Path, branch: str) -> bool:
    result = subprocess.run(
        [
            "git",
            "-C",
            str(project_root),
            "show-ref",
            "--verify",
            "--quiet",
            f"refs/remotes/origin/{branch}",
        ],
        capture_output=True,
    )
    return result.returncode == 0


def _worktree_branch(path: Path) -> str | None:
    if not path.exists():
        return None
    result = subprocess.run(
        ["git", "-C", str(path), "symbolic-ref", "--short", "HEAD"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def _is_clean(path: Path) -> bool:
    result = subprocess.run(
        ["git", "-C", str(path), "status", "--porcelain"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return False
    return result.stdout.strip() == ""


def _push_state(path: Path, branch: str) -> tuple[bool | None, int | None]:
    subprocess.run(
        ["git", "-C", str(path), "fetch", "origin", branch],
        capture_output=True,
    )
    local = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
    )
    remote = subprocess.run(
        ["git", "-C", str(path), "rev-parse", f"origin/{branch}"],
        capture_output=True,
        text=True,
    )
    if local.returncode != 0 or remote.returncode != 0:
        return (None, None)
    pushed = local.stdout.strip() == remote.stdout.strip()
    ahead_result = subprocess.run(
        [
            "git",
            "-C",
            str(path),
            "rev-list",
            "--count",
            f"origin/{branch}..HEAD",
        ],
        capture_output=True,
        text=True,
    )
    ahead = int(ahead_result.stdout.strip() or "0")
    return (pushed, ahead)


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
