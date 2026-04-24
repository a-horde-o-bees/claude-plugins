"""Settings loader: read and merge global/project settings.json files."""

from __future__ import annotations

import json
from pathlib import Path


def load_settings_file(path: Path) -> dict:
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def merge_settings(global_settings: dict, project_settings: dict) -> dict:
    """Merge global and project settings. Union of allow/deny lists and
    additionalDirectories. Project values appear after global values."""
    global_perms = global_settings.get("permissions", {})
    project_perms = project_settings.get("permissions", {})

    merged_allow = list(global_perms.get("allow", []))
    for rule in project_perms.get("allow", []):
        if rule not in merged_allow:
            merged_allow.append(rule)

    merged_deny = list(global_perms.get("deny", []))
    for rule in project_perms.get("deny", []):
        if rule not in merged_deny:
            merged_deny.append(rule)

    merged_dirs = list(global_perms.get("additionalDirectories", []))
    for d in project_perms.get("additionalDirectories", []):
        if d not in merged_dirs:
            merged_dirs.append(d)

    return {
        "permissions": {
            "allow": merged_allow,
            "deny": merged_deny,
            "additionalDirectories": merged_dirs,
        }
    }


def load_merged_settings(project_dir: Path) -> dict:
    global_path = Path.home() / ".claude" / "settings.json"
    project_path = project_dir / ".claude" / "settings.json"
    return merge_settings(
        load_settings_file(global_path),
        load_settings_file(project_path),
    )
