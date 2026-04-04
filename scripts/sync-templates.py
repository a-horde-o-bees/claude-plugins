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

    Enumerates template files and maps each to its deployed counterpart.
    Rules: plugins/<plugin>/rules/<name>.md → .claude/rules/<name>.md
    Conventions: plugins/<plugin>/conventions/<name> → .claude/<plugin>/conventions/<name>
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

        conv_dir = plugin_dir / "conventions"
        deployed_conv_dir = (
            PROJECT_ROOT / ".claude" / plugin_name / "conventions"
        )

        # Existing templates → deployed counterparts
        if conv_dir.is_dir():
            for template in sorted(conv_dir.iterdir()):
                if not template.is_file():
                    continue
                deployed = deployed_conv_dir / template.name
                mappings.append((template, deployed))

        # Manifest: plugins/<plugin>/manifest.yaml ↔ .claude/<plugin>/manifest.yaml
        manifest_path = (
            PROJECT_ROOT / ".claude" / plugin_name / "manifest.yaml"
        )
        manifest_template = plugin_dir / "manifest.yaml"
        if manifest_path.is_file():
            mappings.append((manifest_template, manifest_path))
            existing_rule_templates = {
                f.name for f in rules_dir.iterdir() if f.is_file()
            } if rules_dir.is_dir() else set()
            existing_conv_templates = {
                f.name for f in conv_dir.iterdir() if f.is_file()
            } if conv_dir.is_dir() else set()

            for line in manifest_path.read_text().splitlines():
                stripped = line.strip()
                indent = len(line) - len(line.lstrip())
                if indent == 2 and stripped.endswith(":"):
                    entry_path = stripped[:-1]

                    rules_prefix = ".claude/rules/"
                    if entry_path.startswith(rules_prefix):
                        name = entry_path[len(rules_prefix):]
                        if name not in existing_rule_templates:
                            template = rules_dir / name
                            deployed = PROJECT_ROOT / ".claude" / "rules" / name
                            mappings.append((template, deployed))
                        continue

                    conv_prefix = f".claude/{plugin_name}/conventions/"
                    if entry_path.startswith(conv_prefix) and conv_dir.is_dir():
                        name = entry_path[len(conv_prefix):]
                        if name not in existing_conv_templates:
                            template = conv_dir / name
                            deployed = deployed_conv_dir / name
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
