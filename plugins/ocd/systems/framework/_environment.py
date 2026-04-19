"""Plugin environment resolution.

Canonical helpers for resolving project directory, plugin root, plugin
data directory, and Claude home. All return absolute canonical paths.
"""

import os
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

    Falls back to git repository root when the env var is unset —
    deterministic within any checkout or worktree of the same repo.
    Raises when neither the env var is set nor git root is discoverable.
    """
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        return Path(env).resolve()
    import subprocess

    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return Path(result.stdout.strip()).resolve()
    raise RuntimeError(
        "CLAUDE_PROJECT_DIR is not set and git root is not discoverable. "
        "Run under Claude Code, via scripts/run-framework.sh, or set the "
        "variable explicitly."
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
    return Path.home() / ".claude"
