"""Project-level tooling for this claude-plugins repository.

Operations tied to THIS project's development infrastructure — test
orchestration, project setup — live here rather than inside any plugin.
End users of the plugins never install or import from this package; it
exists solely for maintainers working in this repo.

Path resolution helpers are defined locally rather than imported from
`shared.scripts._environment` (which is canonical storage for skill
propagation, not a runtime module). The logic is a slimmer subset of
the canonical — no defensive-against-plugin-cache guard, since
project-internal tools never run from one.
"""

import os
import subprocess
from pathlib import Path


def get_project_dir() -> Path:
    """Resolve the active project root.

    Honors CLAUDE_PROJECT_DIR (set by test fixtures and plugin
    contexts), falls back to `git rev-parse --show-toplevel` from cwd.
    Raises when neither yields a directory.
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
