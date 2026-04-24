"""Top-level setup entry point.

Runs every project-local setup step in sequence. Idempotent — each
step reports whether it made a change; steps that have already been
applied skip silently.
"""

from ..testing import _environment
from ._hookspath import set_hookspath


def setup_project() -> int:
    """Run all project-local setup steps. Returns 0 on success."""
    project_dir = _environment.get_project_dir()

    print(f"project-run setup — {project_dir}")
    print()

    if set_hookspath(project_dir):
        print("Git hookspath set to .githooks")
    else:
        print("Git hookspath already configured (or .githooks absent)")

    print()
    print("Done.")
    return 0
