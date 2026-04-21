#!/usr/bin/env python3
"""Validate marketplace.json and referenced plugin.json manifests.

Schema-based validation chosen over `claude plugin validate` CLI invocation
because the CLI requires a working Claude Code install + authenticated
context on the CI runner. 0/54 sampled marketplace repos wire `claude plugin
validate` into CI; Anthropic's own aggregator uses a hand-rolled bun+TS
validator. This is the Python analogue — manual shape checks, no schema
library dependency.

Exits non-zero on any validation failure with GitHub-Actions-annotated
error messages (`::error::` prefix).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MARKETPLACE_PATH = REPO_ROOT / ".claude-plugin" / "marketplace.json"
KEBAB = re.compile(r"^[a-z0-9][a-z0-9-]*$")

RESERVED_MARKETPLACE_NAMES = {
    "claude-code-marketplace",
    "claude-code-plugins",
    "claude-plugins-official",
    "anthropic-marketplace",
    "anthropic-plugins",
    "agent-skills",
    "knowledge-work-plugins",
    "life-sciences",
}


def _err(errors: list[str], msg: str) -> None:
    errors.append(msg)


def _validate_marketplace(data: dict, errors: list[str]) -> None:
    for field in ("name", "owner", "plugins"):
        if field not in data:
            _err(errors, f"marketplace.json missing required field: {field}")

    name = data.get("name", "")
    if isinstance(name, str):
        if not KEBAB.fullmatch(name):
            _err(errors, f"marketplace name '{name}' is not kebab-case")
        if name in RESERVED_MARKETPLACE_NAMES:
            _err(errors, f"marketplace name '{name}' is reserved")

    owner = data.get("owner", {})
    if not isinstance(owner, dict) or not owner.get("name"):
        _err(errors, "marketplace.json owner.name is required")

    plugins = data.get("plugins")
    if not isinstance(plugins, list):
        _err(errors, "marketplace.json plugins must be an array")


def _validate_plugin_entry(entry: dict, errors: list[str]) -> None:
    name = entry.get("name", "<unnamed>")
    if not entry.get("name"):
        _err(errors, f"plugin entry missing name: {entry}")
    if not KEBAB.fullmatch(name):
        _err(errors, f"plugin name '{name}' is not kebab-case")

    source = entry.get("source")
    if source is None:
        _err(errors, f"plugin '{name}' missing source")
        return

    if isinstance(source, str):
        if not source.startswith("./"):
            _err(errors, f"plugin '{name}' relative source must start with './': {source}")
            return
        plugin_dir = REPO_ROOT / source
        if not plugin_dir.is_dir():
            _err(errors, f"plugin '{name}' source path not found: {source}")
            return
        _validate_plugin_json(name, plugin_dir, errors)


def _validate_plugin_json(name: str, plugin_dir: Path, errors: list[str]) -> None:
    pj_path = plugin_dir / ".claude-plugin" / "plugin.json"
    if not pj_path.is_file():
        return
    try:
        pj = json.loads(pj_path.read_text())
    except json.JSONDecodeError as exc:
        _err(errors, f"{pj_path.relative_to(REPO_ROOT)}: invalid JSON — {exc}")
        return

    pj_name = pj.get("name", "")
    if pj_name != name:
        _err(
            errors,
            f"plugin '{name}': plugin.json name '{pj_name}' does not match marketplace entry",
        )
    if pj_name and not KEBAB.fullmatch(pj_name):
        _err(errors, f"plugin.json name '{pj_name}' is not kebab-case")


def main() -> int:
    if not MARKETPLACE_PATH.is_file():
        print(f"::error::marketplace.json not found at {MARKETPLACE_PATH}", file=sys.stderr)
        return 1

    try:
        marketplace = json.loads(MARKETPLACE_PATH.read_text())
    except json.JSONDecodeError as exc:
        print(f"::error::marketplace.json invalid JSON — {exc}", file=sys.stderr)
        return 1

    errors: list[str] = []
    _validate_marketplace(marketplace, errors)

    for entry in marketplace.get("plugins", []) or []:
        if isinstance(entry, dict):
            _validate_plugin_entry(entry, errors)

    if errors:
        for msg in errors:
            print(f"::error::{msg}", file=sys.stderr)
        return 1

    print(f"Validation passed — marketplace + {len(marketplace.get('plugins', []))} plugin manifest(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
