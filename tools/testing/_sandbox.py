"""Detached-worktree test execution.

Creates an ephemeral sibling worktree at a given ref, invokes the
project-level test runner inside it, and cleans up before returning.
Single-call lifecycle: setup, execution, and teardown all happen in
one invocation — the worktree is always removed before return.

Sibling convention mirrors the ocd:sandbox plugin's scheme:
`<parent>/<project>--tmp-test-<short-sha>/` so all ephemeral substrates
share one permission glob.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

from . import _environment


TEST_NAME_PREFIX = "tmp-test-"


def sandbox_tests_run(
    ref: str = "main",
    plugin_filter: str | None = None,
    project_only: bool = False,
) -> int:
    """Run the tests CLI inside a detached sibling worktree at ref.

    Returns the tests CLI's exit code (0 pass, non-zero fail). Worktree
    is always removed before return.
    """
    project_root = _environment.get_project_dir()
    ref_sha = _resolve_ref(project_root, ref)
    short_sha = ref_sha[:7]
    worktree = _sibling_path(project_root, f"{TEST_NAME_PREFIX}{short_sha}")

    if worktree.exists():
        raise RuntimeError(
            f"worktree path already in use: {worktree} — run "
            "`/ocd:sandbox cleanup` first or pick a different ref",
        )

    _create_worktree(project_root, worktree, ref_sha)
    try:
        return _invoke_tests(project_root, worktree, plugin_filter, project_only)
    finally:
        _remove_worktree(project_root, worktree)


def _sibling_path(project_root: Path, name: str) -> Path:
    return project_root.parent / f"{project_root.name}--{name}"


def _resolve_ref(project_root: Path, ref: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(project_root), "rev-parse", ref],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"could not resolve ref `{ref}`: {result.stderr.strip()}",
        )
    return result.stdout.strip()


def _create_worktree(project_root: Path, worktree: Path, ref_sha: str) -> None:
    worktree.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(project_root),
            "worktree",
            "add",
            "--detach",
            str(worktree),
            ref_sha,
        ],
        check=True,
    )


def _remove_worktree(project_root: Path, worktree: Path) -> None:
    if not worktree.exists():
        return
    subprocess.run(
        [
            "git",
            "-C",
            str(project_root),
            "worktree",
            "remove",
            "--force",
            str(worktree),
        ],
        check=False,
    )
    if worktree.exists():
        shutil.rmtree(worktree, ignore_errors=True)


def _invoke_tests(
    project_root: Path,
    worktree: Path,
    plugin_filter: str | None,
    project_only: bool,
) -> int:
    args = [
        str(project_root / "bin" / "plugins-run"),
        "tests",
    ]
    if plugin_filter is not None:
        args.extend(["--plugin", plugin_filter])
    elif project_only:
        args.append("--project")

    # Point the tests runner at the parent project's venv. Inside the
    # worktree, `git rev-parse --show-toplevel` resolves to the worktree
    # itself, which has no .venv. The parent project owns the .venv and
    # the plugin venvs both, so CLAUDE_PROJECT_DIR must reference the
    # parent explicitly while pytest still discovers tests from cwd.
    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = str(project_root)

    result = subprocess.run(
        args,
        cwd=worktree,
        env=env,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    return result.returncode
