"""Sync deployed copies to template files.

Compares deployed files in .claude/ against their template counterparts
in plugins/. Copies deployed content to template when bytes differ.
Stages updated templates for the in-progress commit.

Called by git pre-commit hook.
"""

import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def discover_mappings() -> list[tuple[Path, Path]]:
    """Build (template, deployed) pairs from project structure.

    Enumerates template files and maps each to its deployed counterpart.
    Rules: plugins/<plugin>/rules/<name>.md → .claude/rules/<name>.md
    Conventions: plugins/<plugin>/templates/conventions/<name> → .claude/<plugin>/conventions/<name>
    """
    mappings = []
    plugins_dir = PROJECT_ROOT / "plugins"

    for plugin_dir in sorted(plugins_dir.iterdir()):
        if not plugin_dir.is_dir():
            continue
        plugin_name = plugin_dir.name

        rules_dir = plugin_dir / "rules"
        if rules_dir.is_dir():
            for template in sorted(rules_dir.glob("*.md")):
                deployed = PROJECT_ROOT / ".claude" / "rules" / template.name
                mappings.append((template, deployed))

        conv_dir = plugin_dir / "templates" / "conventions"
        if conv_dir.is_dir():
            for template in sorted(conv_dir.iterdir()):
                if not template.is_file():
                    continue
                deployed = (
                    PROJECT_ROOT
                    / ".claude"
                    / plugin_name
                    / "conventions"
                    / template.name
                )
                mappings.append((template, deployed))

    return mappings


def sync_pair(template: Path, deployed: Path) -> bool:
    """Compare and sync a single template/deployed pair.

    Returns True if template was updated, False if already current or
    deployed file does not exist.
    """
    if not deployed.exists():
        return False

    if template.read_bytes() == deployed.read_bytes():
        return False

    shutil.copy2(deployed, template)
    return True


def main() -> int:
    mappings = discover_mappings()
    synced = []
    current_count = 0

    for template, deployed in mappings:
        rel = str(template.relative_to(PROJECT_ROOT))
        if sync_pair(template, deployed):
            synced.append(rel)
        else:
            current_count += 1

    if synced:
        subprocess.run(
            ["git", "add"] + synced,
            cwd=PROJECT_ROOT,
            check=True,
        )
        print(f"sync-templates: {len(synced)} synced, {current_count} current")
        for path in synced:
            print(f"  synced: {path}")
    else:
        print(f"sync-templates: all {current_count} templates current")

    return 0


if __name__ == "__main__":
    sys.exit(main())
