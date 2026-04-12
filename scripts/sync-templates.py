"""Sync template files to deployed copies.

Compares plugin template files in plugins/ against their deployed
counterparts in .claude/. Copies template content to deployed location
when bytes differ. Templates are the working copies; deployed copies
are derived artifacts consumed by Claude Code at runtime.

Prints synced deployed file paths to stdout. Called by:
- git pre-commit hook (ensures deployed copies are current at commit time)
- /sync-templates skill (interactive sync for testing without committing)
"""

import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def discover_mappings() -> list[tuple[Path, Path]]:
    """Build (template, deployed) pairs from project structure.

    Scans template directories to discover all deployable files.
    Rules: plugins/<plugin>/rules/<name>.md → .claude/rules/<plugin>/<name>.md
    Conventions: plugins/<plugin>/conventions/<name>.md → .claude/conventions/<plugin>/<name>.md
    Patterns: plugins/<plugin>/patterns/<name>.md → .claude/patterns/<plugin>/<name>.md
    Logs: plugins/<plugin>/logs/routing.md → .claude/logs/routing.md
          plugins/<plugin>/logs/<type>/_template.md → .claude/logs/<type>/_template.md

    README.md and architecture.md in rules/conventions/patterns template
    directories are source-only documentation and are excluded from deployment.
    """
    mappings = []
    plugins_dir = PROJECT_ROOT / "plugins"
    source_only = {"README.md", "architecture.md"}

    def collect(
        template_dir: Path,
        deployed_dir: Path,
        exclude: set[str] | None = None,
    ) -> None:
        if not template_dir.is_dir():
            return

        skip = exclude or set()
        for template in sorted(template_dir.glob("*.md")):
            if template.name in skip:
                continue
            deployed = deployed_dir / template.name
            mappings.append((template, deployed))

    def collect_logs(
        logs_dir: Path,
        deployed_dir: Path,
    ) -> None:
        if not logs_dir.is_dir():
            return

        # Per-type _template.md files
        for type_dir in sorted(logs_dir.iterdir()):
            if not type_dir.is_dir():
                continue
            for template in sorted(type_dir.glob("_template.md")):
                deployed = deployed_dir / type_dir.name / template.name
                mappings.append((template, deployed))

    for plugin_dir in sorted(plugins_dir.iterdir()):
        if not plugin_dir.is_dir():
            continue

        collect(
            plugin_dir / "rules",
            PROJECT_ROOT / ".claude" / "rules" / plugin_dir.name,
            exclude=source_only,
        )
        collect(
            plugin_dir / "conventions",
            PROJECT_ROOT / ".claude" / "conventions" / plugin_dir.name,
            exclude=source_only,
        )
        collect(
            plugin_dir / "patterns",
            PROJECT_ROOT / ".claude" / "patterns" / plugin_dir.name,
            exclude=source_only,
        )
        collect_logs(
            plugin_dir / "logs",
            PROJECT_ROOT / ".claude" / "logs",
        )

    return mappings


def sync_pair(template: Path, deployed: Path) -> bool:
    """Copy template to deployed location if bytes differ.

    Returns True if deployed was updated, False if already current or
    template does not exist.
    """
    if not template.exists():
        return False

    if deployed.exists() and template.read_bytes() == deployed.read_bytes():
        return False

    deployed.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(template, deployed)
    return True


def main() -> int:
    mappings = discover_mappings()
    synced = []
    current_count = 0

    for template, deployed in mappings:
        rel = str(deployed.relative_to(PROJECT_ROOT))
        if sync_pair(template, deployed):
            synced.append(rel)
        else:
            current_count += 1

    if synced:
        for path in synced:
            print(path)
    else:
        print(f"sync-templates: all {current_count} deployed copies current", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
