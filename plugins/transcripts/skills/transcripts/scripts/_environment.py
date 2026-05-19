"""Environment resolution for the transcripts skill.

Resolves the project directory (where the DB lives) and Claude home
(where session JSONL transcripts live). Both honor env-var overrides
so callers running outside a git checkout — or against a non-default
Claude home — can still drive the skill.

Vendored subset of the shared environment helper that the legacy
ocd-old skills imported. Only `get_project_dir` and `get_claude_home`
are kept; plugin-root resolution is dropped because the new skill
no longer composes its DB path from a plugin name.
"""

import os
import subprocess
from pathlib import Path


def get_claude_home() -> Path:
    """Resolve ~/.claude (override via CLAUDE_HOME env var)."""
    env = os.environ.get("CLAUDE_HOME")
    if env:
        return Path(env).resolve()
    return (Path.home() / ".claude").resolve()


def get_project_dir() -> Path:
    """Resolve project directory from CLAUDE_PROJECT_DIR with git fallback.

    Falls back to `git rev-parse --show-toplevel` from cwd when the env
    var is unset. Refuses any resolution that lands inside Claude home —
    plugin caches under ~/.claude/plugins/cache/ are themselves git
    checkouts; without the guard, `git rev-parse` fired from a cache
    subdirectory returns ~/.claude/ and downstream code writes to
    ~/.claude/.claude/... paths.
    """
    claude_home = get_claude_home()

    def _reject_if_inside_home(path: Path) -> Path:
        try:
            path.relative_to(claude_home)
        except ValueError:
            return path
        raise RuntimeError(
            f"resolved project directory {path} is inside Claude home "
            f"({claude_home}) — set CLAUDE_PROJECT_DIR to your project "
            "root explicitly. Common cause: invoking from a plugin "
            "cache subdirectory."
        )

    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        path = Path(env).resolve()
        if path.is_dir():
            return _reject_if_inside_home(path)
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        path = Path(result.stdout.strip()).resolve()
        if path.is_dir():
            return _reject_if_inside_home(path)
    raise RuntimeError(
        "project directory not discoverable — set CLAUDE_PROJECT_DIR or "
        "invoke from within a git checkout",
    )
