"""Sync deployed copies to template files.

Compares deployed files in .claude/ against their template counterparts
in plugins/. Copies deployed content to template when bytes differ.
Prints synced file paths to stdout for the caller to stage.

Called by git pre-commit hook.
"""

import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def discover_mappings() -> list[tuple[Path, Path]]:
    """Build (template, deployed) pairs from project structure.

    Scans both template and deployed directories to discover all files.
    Rules: plugins/<plugin>/rules/<name>.md ↔ .claude/rules/<name>.md
    Conventions: plugins/<plugin>/conventions/<name> ↔ .claude/conventions/<name>
    """
    mappings = []
    plugins_dir = PROJECT_ROOT / "plugins"

    for plugin_dir in sorted(plugins_dir.iterdir()):
        if not plugin_dir.is_dir():
            continue

        rules_dir = plugin_dir / "rules"
        conv_dir = plugin_dir / "conventions"

        # Rules: template ↔ deployed
        deployed_rules = PROJECT_ROOT / ".claude" / "rules"
        seen_rules: set[str] = set()

        # From templates
        if rules_dir.is_dir():
            for template in sorted(rules_dir.glob("*.md")):
                deployed = deployed_rules / template.name
                mappings.append((template, deployed))
                seen_rules.add(template.name)

        # From deployed (catch new rules without templates)
        if rules_dir.is_dir() and deployed_rules.is_dir():
            for deployed in sorted(deployed_rules.glob("*.md")):
                if deployed.name not in seen_rules:
                    template = rules_dir / deployed.name
                    mappings.append((template, deployed))

        # Conventions: template ↔ deployed
        deployed_conv = PROJECT_ROOT / ".claude" / "conventions"
        seen_conv: set[str] = set()

        # From templates
        if conv_dir.is_dir():
            for template in sorted(conv_dir.iterdir()):
                if not template.is_file():
                    continue
                deployed = deployed_conv / template.name
                mappings.append((template, deployed))
                seen_conv.add(template.name)

        # From deployed (catch new conventions without templates)
        if conv_dir.is_dir() and deployed_conv.is_dir():
            for deployed in sorted(deployed_conv.glob("*.md")):
                if deployed.name not in seen_conv:
                    template = conv_dir / deployed.name
                    mappings.append((template, deployed))

    return mappings


def sync_pair(template: Path, deployed: Path) -> bool:
    """Compare and sync a single template/deployed pair.

    Returns True if template was updated, False if already current or
    deployed file does not exist.
    """
    if not deployed.exists():
        return False

    if template.exists() and template.read_bytes() == deployed.read_bytes():
        return False

    template.parent.mkdir(parents=True, exist_ok=True)
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
        for path in synced:
            print(path)
    else:
        print(f"sync-templates: all {current_count} templates current", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
