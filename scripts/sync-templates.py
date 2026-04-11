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
    Rules: plugins/<plugin>/rules/<name>.md ↔ .claude/rules/<plugin>/<name>.md
    Conventions: plugins/<plugin>/conventions/<name>.md ↔ .claude/conventions/<plugin>/<name>.md

    Plugin-rules and plugin-conventions README.md and architecture.md are
    source-only documentation and are excluded from deployment.
    """
    mappings = []
    plugins_dir = PROJECT_ROOT / "plugins"
    source_only = {"README.md", "architecture.md"}

    def collect(
        source_dir: Path,
        deployed_dir: Path,
    ) -> None:
        seen: set[str] = set()

        # From templates
        if source_dir.is_dir():
            for template in sorted(source_dir.glob("*.md")):
                if template.name in source_only:
                    continue
                deployed = deployed_dir / template.name
                mappings.append((template, deployed))
                seen.add(template.name)

        # From deployed (catch new files without templates)
        if source_dir.is_dir() and deployed_dir.is_dir():
            for deployed in sorted(deployed_dir.rglob("*.md")):
                if deployed.name not in seen:
                    template = source_dir / deployed.name
                    mappings.append((template, deployed))

    for plugin_dir in sorted(plugins_dir.iterdir()):
        if not plugin_dir.is_dir():
            continue

        collect(
            plugin_dir / "rules",
            PROJECT_ROOT / ".claude" / "rules" / plugin_dir.name,
        )
        collect(
            plugin_dir / "conventions",
            PROJECT_ROOT / ".claude" / "conventions" / plugin_dir.name,
        )

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
