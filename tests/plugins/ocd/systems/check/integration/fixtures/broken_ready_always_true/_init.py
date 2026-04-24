"""Broken fixture — predicate lies and does not reflect state."""

from tools.errors import NotReadyError


def ready() -> bool:
    return True


def ensure_ready() -> None:
    if not ready():
        raise NotReadyError("broken_ready_always_true is dormant.")


def init(force: bool = False) -> dict:
    _ = force
    return {"files": [], "extra": []}


def status() -> dict:
    return {"files": [], "extra": []}
