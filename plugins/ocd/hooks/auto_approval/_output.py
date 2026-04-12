"""Hook response helpers for PreToolUse permission decisions."""

from __future__ import annotations

import json
import sys


def approve() -> None:
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow",
            }
        },
        sys.stdout,
    )


def block(reason: str) -> None:
    json.dump({"decision": "block", "reason": reason}, sys.stdout)
