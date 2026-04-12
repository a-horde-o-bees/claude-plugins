"""Plugin environment resolution.

Canonical helpers for resolving project directory, plugin root, plugin
data directory, and Claude home. All return absolute canonical paths.
"""

import os
from pathlib import Path


def get_plugin_root() -> Path:
    """Resolve plugin root from CLAUDE_PLUGIN_ROOT with __file__ fallback.

    Falls back to a deterministic walk from this module's own file
    position: plugin/_environment.py always lives at plugins/<name>/plugin/
    relative to the plugin root, so the walk is correct across dev,
    install cache, and any other install location.
    """
    env = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if env:
        return Path(env).resolve()
    return Path(__file__).resolve().parent.parent


def get_project_dir() -> Path:
    """Resolve project directory from CLAUDE_PROJECT_DIR.

    Raises when unset — project identity is not inferable from working
    directory. Claude Code sets this at runtime; scripts/run-plugin.sh
    exports it; tests set it explicitly in subprocess env or via
    monkeypatch.
    """
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if not env:
        raise RuntimeError(
            "CLAUDE_PROJECT_DIR is not set. Run under Claude Code, via "
            "scripts/run-plugin.sh, or set the variable explicitly."
        )
    return Path(env).resolve()


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
