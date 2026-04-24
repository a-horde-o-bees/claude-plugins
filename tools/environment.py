"""Environment resolution for project and plugin directories.

Canonical source for `get_project_dir`, `get_plugin_root`,
`get_plugin_data_dir`, `get_claude_home`, and `get_git_root_for`. All
return absolute canonical paths.

Single source of truth — every plugin ships a vendored copy under
`<plugin>/tools/` propagated by `.githooks/pre-commit`. Drift is caught
by the content-equality contract test in
`tests/integration/test_shared_file_sync.py`.
"""

import os
import subprocess
from pathlib import Path


def get_plugin_root() -> Path:
    """Resolve plugin root from CLAUDE_PLUGIN_ROOT with a marker-anchor fallback.

    Walks ancestors of this module's `__file__` upward until one contains
    `.claude-plugin/plugin.json` — the file that exists only at the
    plugin root. Depth-independent: any future relocation of this module
    inside the plugin tree continues to resolve correctly without code
    changes.
    """
    env = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if env:
        return Path(env).resolve()
    here = Path(__file__).resolve()
    for ancestor in here.parents:
        if (ancestor / ".claude-plugin" / "plugin.json").exists():
            return ancestor
    raise RuntimeError(
        f"plugin root not found walking up from {here} — no ancestor "
        "contains .claude-plugin/plugin.json; set CLAUDE_PLUGIN_ROOT "
        "explicitly if running outside a plugin tree",
    )


def get_project_dir() -> Path:
    """Resolve project directory from CLAUDE_PROJECT_DIR with git fallback.

    Falls back to `git rev-parse --show-toplevel` from cwd when the env
    var is unset — deterministic within any checkout or worktree of the
    same repo, and correct for linked worktrees where `.git` is a file
    pointer rather than a directory. Raises when neither the env var is
    set nor git root is discoverable.
    """
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        path = Path(env).resolve()
        if path.is_dir():
            return path
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        path = Path(result.stdout.strip()).resolve()
        if path.is_dir():
            return path
    raise RuntimeError(
        "project directory not discoverable — set CLAUDE_PROJECT_DIR or "
        "invoke from within a git checkout",
    )


def get_git_root_for(path: Path) -> Path:
    """Resolve the git repository root containing `path`.

    Shells to `git -C <path> rev-parse --show-toplevel` — correct for
    linked worktrees (where `.git` is a file pointer, not a directory)
    and for paths that live outside `get_project_dir()`'s current
    resolution. Use when the caller has a concrete input path whose
    owning repo it needs, rather than the ambient project directory.
    """
    path = Path(path).resolve()
    anchor = path if path.is_dir() else path.parent
    result = subprocess.run(
        ["git", "-C", str(anchor), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        root = Path(result.stdout.strip()).resolve()
        if root.is_dir():
            return root
    raise RuntimeError(
        f"git root not discoverable for {path} — not inside a git checkout",
    )


def get_plugin_data_dir() -> Path:
    """Resolve plugin data directory from CLAUDE_PLUGIN_DATA.

    Raises when unset — this is Claude Code-managed per-plugin persistent
    storage (venv, cached state) that survives plugin version upgrades
    and is not inferable from the install directory, the project, or
    the working directory.
    """
    env = os.environ.get("CLAUDE_PLUGIN_DATA")
    if not env:
        raise RuntimeError(
            "CLAUDE_PLUGIN_DATA is not set. Required for plugin venv and "
            "persistent state — must run under Claude Code plugin context."
        )
    return Path(env).resolve()


def get_claude_home() -> Path:
    """Resolve ~/.claude (override via CLAUDE_HOME env var)."""
    env = os.environ.get("CLAUDE_HOME")
    if env:
        return Path(env).resolve()
    return (Path.home() / ".claude").resolve()
