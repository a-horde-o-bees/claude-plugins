"""Project verb — sibling project substrate setup and teardown.

The project substrate creates a sibling directory alongside the current
project at `<parent-dir>/<parent-project>-test-<topic>/` with a fresh
git repo. The sandbox skill's planning phase (draft plan, confirm with
user, execute plan) stays in `SKILL.md`; setup and teardown delegate
here so the mechanical filesystem + git init operations are a single
allowed CLI call each.

Setup returns the absolute sandbox path. Teardown accepts the path and
removes it. Fixture copies and the `claude -p` invocation itself are
the skill executor's responsibility — those happen between setup and
teardown in the skill workflow.
"""

import shutil
import subprocess
from pathlib import Path


def project_setup(sandbox_path: Path) -> Path:
    """Create the sibling sandbox directory and initialize a git repo.

    Fails loudly if the path already exists — the caller should
    disambiguate with a different topic slug rather than overwriting
    an unrelated in-flight sandbox.
    """
    if sandbox_path.exists():
        raise RuntimeError(
            f"sandbox path already exists: {sandbox_path} — pick a different "
            "topic or run `/ocd:sandbox cleanup` first",
        )
    sandbox_path.mkdir(parents=True)
    subprocess.run(
        ["git", "-C", str(sandbox_path), "init", "--quiet"],
        check=True,
    )
    return sandbox_path.resolve()


def project_teardown(sandbox_path: Path) -> None:
    """Remove the sibling sandbox directory.

    Idempotent — absent path is a no-op, since teardown may be invoked
    after a crashed run where setup partially succeeded.
    """
    if not sandbox_path.exists():
        return
    shutil.rmtree(sandbox_path)
