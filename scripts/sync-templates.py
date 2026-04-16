"""Sync template files to deployed copies.

Discovers plugin directories under plugins/ and invokes each content
subsystem's init() with force=True to sync templates to their deployed
locations in .claude/. Clears orphaned deployed files when templates
are removed.

Content subsystems are the template-based lib packages (rules,
conventions, patterns, logs) — infrastructure subsystems like
navigator and permissions are excluded because their init has side
effects beyond template deployment.

Prints synced deployed file paths to stdout. Called by:
- Git pre-commit hook (ensures deployed copies track template edits)
- /sync-templates skill (interactive sync for testing without committing)
"""

import importlib
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CONTENT_SUBSYSTEMS = ("rules", "conventions", "patterns", "logs")


def _sync_plugin(plugin_dir: Path) -> list[str]:
    """Run each content subsystem's init for one plugin. Returns paths touched."""
    synced: list[str] = []

    # Each plugin's sys.path is isolated so its `lib.*` and `plugin` resolve
    # to its own copies. Unload modules from any prior plugin first.
    for key in list(sys.modules):
        if key == "plugin" or key.startswith("plugin.") or key == "lib" or key.startswith("lib."):
            del sys.modules[key]

    sys.path.insert(0, str(plugin_dir))
    os.environ["CLAUDE_PLUGIN_ROOT"] = str(plugin_dir)
    os.environ["CLAUDE_PROJECT_DIR"] = str(PROJECT_ROOT)

    try:
        for subsystem in CONTENT_SUBSYSTEMS:
            try:
                mod = importlib.import_module(f"lib.{subsystem}._init")
            except ModuleNotFoundError:
                continue
            result = mod.init(force=True)
            for r in result["files"]:
                if r["before"] != r["after"]:
                    synced.append(r["path"])
    finally:
        sys.path.remove(str(plugin_dir))

    return synced


def main() -> int:
    plugins_dir = PROJECT_ROOT / "plugins"
    all_synced: list[str] = []

    for plugin_dir in sorted(plugins_dir.iterdir()):
        if not plugin_dir.is_dir():
            continue
        all_synced.extend(_sync_plugin(plugin_dir))

    if all_synced:
        for path in all_synced:
            print(path)
    else:
        print("sync-templates: all deployed copies current", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
