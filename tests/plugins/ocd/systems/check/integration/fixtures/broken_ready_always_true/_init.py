"""Broken fixture — predicate lies and does not reflect state."""

import framework


def ready() -> bool:
    return True


def ensure_ready() -> None:
    if not ready():
        raise framework.NotReadyError("broken_ready_always_true is dormant.")


def init(force: bool = False) -> dict:
    _ = force
    return {"files": [], "extra": []}


def status() -> dict:
    return {"files": [], "extra": []}
