"""Deploy-only fixture — init/status without a readiness interface."""

import os
from pathlib import Path


def init(force: bool = False) -> dict:
    _ = force
    target = Path(os.environ["CLAUDE_PROJECT_DIR"]) / ".fixture" / "deploy_only"
    target.mkdir(parents=True, exist_ok=True)
    return {"files": [], "extra": []}


def status() -> dict:
    return {"files": [], "extra": []}
