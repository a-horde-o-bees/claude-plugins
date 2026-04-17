"""Permissions subsystem.

Reports auto-approve pattern coverage at project and user scopes.
Install is a no-op at this layer because deploying recommended
patterns requires an interactive scope choice — the /ocd:setup
guided flow drives that via run_permissions_deploy() directly.

Interface contract: init() and status() return
{"files": [...], "extra": [...]}.
"""

from . import _operations


def init(force: bool = False) -> dict:
    """Report permissions coverage.

    Deployment is interactive and lives in the guided skill flow, not
    the standard subsystem install loop. This entry satisfies the
    contract so the subsystem participates in `plugin install` output
    alongside its siblings. `force` has no effect — retained for
    contract conformance.
    """
    _ = force
    return {"files": [], "extra": _operations.status_extra()}


def status() -> dict:
    """Report permissions coverage across project and user scopes."""
    return {"files": [], "extra": _operations.status_extra()}
