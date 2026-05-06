"""Legacy init facade for the rules subsystem.

Delegates to systems/rules/setup/__init__.py — the new per-system setup
shape (install/uninstall/status with scope). This file is a transitional
shim so existing setup orchestration (run_init, run_status, etc.) keeps
working while other systems migrate. Removed in a single cleanup commit
once every system has its own setup/ folder and the setup CLI dispatch
has switched over.

Interface contract: init() and status() return
{"files": [...], "extra": [...]}.
"""

from .setup import install, uninstall, status as _scoped_status


def init(force: bool = False) -> dict:
    """Legacy init — installs all rule templates at project scope."""
    return install(scope="project", target=None, force=force)


def status() -> dict:
    """Legacy status — reports project-scope deployment state."""
    return _scoped_status(scope="project")


def clean() -> dict:
    """Legacy clean — uninstalls all rule files from project scope."""
    return uninstall(scope="project", target=None)
