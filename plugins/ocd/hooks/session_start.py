"""SessionStart hook: persist plugin root for agent Bash commands.

Writes CLAUDE_PLUGIN_ROOT to .claude/ocd/.plugin_root so scripts
can resolve the plugin directory when the environment variable is
not available (agent Bash commands only receive hook execution context).
"""

import os

import plugin


def main() -> None:
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if not plugin_root:
        return

    ocd_dir = plugin.get_project_dir() / ".claude" / "ocd"
    ocd_dir.mkdir(parents=True, exist_ok=True)

    plugin_root_file = ocd_dir / ".plugin_root"
    plugin_root_file.write_text(plugin_root)


if __name__ == "__main__":
    main()
