"""Compliant runtime fixture — full readiness interface over a marker file."""

import os
from pathlib import Path

import plugin


def _marker_path() -> Path:
    return Path(os.environ["CLAUDE_PROJECT_DIR"]) / ".fixture" / "compliant_runtime" / "marker"


def ready() -> bool:
    return _marker_path().exists()


def ensure_ready() -> None:
    if not ready():
        raise plugin.NotReadyError(
            "compliant_runtime fixture is dormant — run init to initialize."
        )


def init(force: bool = False) -> dict:
    _ = force
    marker = _marker_path()
    before = "current" if marker.exists() else "absent"
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.touch()
    return {"files": [{"path": str(marker), "before": before, "after": "current"}], "extra": []}


def status() -> dict:
    marker = _marker_path()
    state = "current" if marker.exists() else "absent"
    return {"files": [{"path": str(marker), "before": state, "after": state}], "extra": []}
