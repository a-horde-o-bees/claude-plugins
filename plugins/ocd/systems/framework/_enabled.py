"""Per-project opt-in configuration for plugin systems.

Stores the list of enabled systems in `.claude/<plugin>/enabled-systems.json`
so `/ocd:setup init` and `enable`/`disable` verbs can cherry-pick which
systems deploy into the project. Systems not in the list are not
initialized and their deployed artifacts (rules, conventions, log
templates) are removed via each system's `clean()` contract.

Auto-init (scripts/auto_init.py) does not consult this file — it is the
plugin-developer bootstrap path that always force-runs every system.
This configuration is the user-onboarding path.
"""

from __future__ import annotations

import json
from pathlib import Path

from ._environment import get_project_dir
from ._metadata import get_plugin_name


def _config_path(plugin_root: Path) -> Path:
    plugin_name = get_plugin_name(plugin_root)
    return get_project_dir() / ".claude" / plugin_name / "enabled-systems.json"


def read_enabled(plugin_root: Path) -> list[str] | None:
    """Return the enabled list, or None when no config exists.

    Callers differentiate absence (first-time install, interactive
    picker should run) from an empty list (user explicitly disabled
    everything — respect that).
    """
    path = _config_path(plugin_root)
    if not path.is_file():
        return None
    data = json.loads(path.read_text())
    enabled = data.get("enabled", [])
    if not isinstance(enabled, list):
        return []
    return [name for name in enabled if isinstance(name, str)]


def write_enabled(plugin_root: Path, systems: list[str]) -> None:
    """Persist the enabled list. Creates `.claude/<plugin>/` if missing."""
    path = _config_path(plugin_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"enabled": sorted(set(systems))}, indent=2) + "\n")


def effective_enabled(plugin_root: Path, available: list[str]) -> list[str]:
    """Enabled list, clamped to currently-available systems.

    A config written in one session might reference systems that no
    longer ship; dropping them here keeps orchestration decisions from
    tripping over stale names.
    """
    enabled = read_enabled(plugin_root)
    if enabled is None:
        return list(available)
    available_set = set(available)
    return [name for name in enabled if name in available_set]
