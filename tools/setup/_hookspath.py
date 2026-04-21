"""Git `core.hookspath` configuration.

This project tracks version-controlled git hooks under `.githooks/`.
Configuring `core.hookspath=.githooks` makes git use those hooks
instead of the default `.git/hooks/` directory. The plugin framework
used to auto-wire this on plugin install, which was inappropriate —
that decision should be explicit per project, not imposed by an
installed plugin on whichever downstream repo hosts it.
"""

import subprocess
from pathlib import Path


def set_hookspath(project_dir: Path) -> bool:
    """Configure git to use .githooks/ when that directory exists.

    Returns True if hookspath was newly set, False if already set or absent.
    """
    githooks_dir = project_dir / ".githooks"
    if not githooks_dir.is_dir():
        return False
    current = subprocess.run(
        ["git", "-C", str(project_dir), "config", "--get", "core.hookspath"],
        capture_output=True,
        text=True,
    )
    if current.returncode == 0 and current.stdout.strip() == ".githooks":
        return False
    subprocess.run(
        ["git", "-C", str(project_dir), "config", "core.hookspath", ".githooks"],
        capture_output=True,
    )
    return True
