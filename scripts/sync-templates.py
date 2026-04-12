"""Sync template files to deployed copies.

Discovers plugin directories under plugins/ and calls the plugin
framework's deploy_* functions with force=True to sync templates
to their deployed locations in .claude/. Clears orphaned deployed
files when templates are removed.

Prints synced deployed file paths to stdout. Called by:
- SessionEnd hook (ensures deployed copies are current for next session)
- /sync-templates skill (interactive sync for testing without committing)
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Add the ocd plugin to sys.path — it is the canonical source of the
# plugin framework. Other plugins receive a copy via pre-commit hook.
sys.path.insert(0, str(PROJECT_ROOT / "plugins" / "ocd"))

from plugin import (  # noqa: E402
    deploy_conventions,
    deploy_logs,
    deploy_patterns,
    deploy_rules,
)


def main() -> int:
    plugins_dir = PROJECT_ROOT / "plugins"
    synced: list[str] = []

    for plugin_dir in sorted(plugins_dir.iterdir()):
        if not plugin_dir.is_dir():
            continue

        for deploy_fn in (deploy_rules, deploy_conventions, deploy_patterns, deploy_logs):
            results = deploy_fn(plugin_dir, PROJECT_ROOT, force=True)
            for r in results:
                if r["before"] != r["after"]:
                    synced.append(r["path"])

    if synced:
        for path in synced:
            print(path)
    else:
        print("sync-templates: all deployed copies current", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
