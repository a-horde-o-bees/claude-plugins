"""Cleanup verb — inventory ephemeral sandbox artifacts and remove selected ones.

Two phases, separated because the skill needs to present the inventory
and collect per-item user decisions via `AskUserQuestion`:

- `inventory` emits machine-readable JSON listing ephemeral sibling
  projects (`<project>--tmp-*`) and disposable worktrees. The skill
  parses, presents, collects choices.
- `remove` accepts the filtered list (sibling paths + worktree paths)
  and actually deletes them.

Durable feature boxes (siblings at `<project>--<feature>` with
`sandbox/<feature>` branches) are excluded — only cleanup via explicit
`unpack` on the durable verb surface removes those.
"""

import json
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from tools import environment


EPHEMERAL_SIBLING_PREFIX = "--tmp-"
EPHEMERAL_BRANCH_PREFIX = "sandbox/tmp/"


@dataclass
class SiblingEntry:
    path: str
    size_bytes: int


@dataclass
class WorktreeEntry:
    path: str
    branch: str | None
    detached: bool


@dataclass
class Inventory:
    siblings: list[SiblingEntry]
    worktrees: list[WorktreeEntry]


def cleanup_inventory() -> Inventory:
    """Gather ephemeral sandbox artifacts in the parent project's namespace."""
    project_root = environment.get_project_dir()
    parent_dir = project_root.parent
    parent_name = project_root.name

    siblings = _find_siblings(parent_dir, parent_name)
    worktrees = _find_worktrees(project_root)
    return Inventory(siblings=siblings, worktrees=worktrees)


def cleanup_print_inventory_json() -> None:
    """Emit inventory as JSON to stdout for the skill to parse."""
    inv = cleanup_inventory()
    sys.stdout.write(json.dumps(asdict(inv), indent=2))
    sys.stdout.write("\n")


def cleanup_remove(sibling_paths: list[Path], worktree_paths: list[Path]) -> None:
    """Remove the named siblings and worktrees."""
    project_root = environment.get_project_dir()

    for sibling in sibling_paths:
        if sibling.exists():
            shutil.rmtree(sibling)

    for worktree_path in worktree_paths:
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

    subprocess.run(
        [
            "git",
            "-C",
            str(project_root),
            "worktree",
            "prune",
        ],
        check=False,
    )


def _find_siblings(parent_dir: Path, parent_name: str) -> list[SiblingEntry]:
    if not parent_dir.is_dir():
        return []
    prefix = f"{parent_name}{EPHEMERAL_SIBLING_PREFIX}"
    entries = []
    for candidate in sorted(parent_dir.iterdir()):
        if not candidate.is_dir():
            continue
        if not candidate.name.startswith(prefix):
            continue
        entries.append(
            SiblingEntry(
                path=str(candidate.resolve()),
                size_bytes=_dir_size(candidate),
            ),
        )
    return entries


def _find_worktrees(project_root: Path) -> list[WorktreeEntry]:
    """Find ephemeral worktrees — branches under `sandbox/tmp/` plus
    any detached worktrees (test runs use detached refs).
    """
    result = subprocess.run(
        ["git", "-C", str(project_root), "worktree", "list", "--porcelain"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return []

    entries: list[WorktreeEntry] = []
    path: str | None = None
    branch: str | None = None
    detached: bool = False

    def flush() -> None:
        if path is None or path == str(project_root):
            return
        is_ephemeral = detached or (
            branch is not None and branch.startswith(EPHEMERAL_BRANCH_PREFIX)
        )
        if not is_ephemeral:
            return
        entries.append(
            WorktreeEntry(path=path, branch=branch, detached=detached),
        )

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


def _dir_size(path: Path) -> int:
    total = 0
    for item in path.rglob("*"):
        if item.is_file():
            try:
                total += item.stat().st_size
            except OSError:
                continue
    return total
