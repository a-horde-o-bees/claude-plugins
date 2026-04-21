"""Project-directory and claude-home resolution.

Mirrors the plugin framework's environment helpers but scoped to
project-level tooling: no plugin-root resolution, no plugin-data
directory. Project-level tools operate on the repo and on `~/.claude/`
for per-plugin data lookups.
"""

import os
import subprocess
from pathlib import Path


def get_project_dir() -> Path:
    """Resolve project root. CLAUDE_PROJECT_DIR env var wins; falls back
    to `git rev-parse --show-toplevel` from cwd. Raises RuntimeError if
    neither source produces a valid path — project-level tools have no
    other way to locate the repo deterministically.
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


def get_claude_home() -> Path:
    """Resolve ~/.claude (override via CLAUDE_HOME env var)."""
    env = os.environ.get("CLAUDE_HOME")
    if env:
        return Path(env).resolve()
    return (Path.home() / ".claude").resolve()
