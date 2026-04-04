"""Manifest parser for governance data.

Reads manifest.yaml to load governance entries (conventions and rules)
with their patterns and dependencies. No PyYAML dependency — custom
parser for the specific manifest structure.
"""

from __future__ import annotations

from pathlib import Path


def load_manifest(manifest_path: Path) -> dict[str, dict]:
    """Load manifest.yaml. Returns {relative_path: {pattern, dependencies}} map.

    Simple parser for specific manifest structure — no PyYAML dependency.
    Raises FileNotFoundError if manifest does not exist.
    """
    content = manifest_path.read_text()
    result: dict[str, dict] = {}

    current_path = None
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped or stripped == "conventions:":
            continue

        # Entry key: "  .claude/rules/ocd-auth.md:"
        indent = len(line) - len(line.lstrip())
        if indent == 2 and stripped.endswith(":"):
            current_path = stripped[:-1]
            result[current_path] = {"pattern": "", "dependencies": []}
            continue

        if current_path is None:
            continue

        # Pattern: '    pattern: "*.py"'
        if stripped.startswith("pattern:"):
            value = stripped[len("pattern:"):].strip()
            result[current_path]["pattern"] = value.strip('"').strip("'")

        # Dependencies: '    dependencies: [.claude/rules/ocd-auth.md, ...]'
        elif stripped.startswith("dependencies:"):
            value = stripped[len("dependencies:"):].strip()
            value = value.strip("[]")
            if value:
                result[current_path]["dependencies"] = [
                    item.strip().strip('"').strip("'") for item in value.split(",")
                ]

    return result


def load_settings(manifest_path: Path) -> dict:
    """Load settings section from manifest.yaml. Returns {key: value} map.

    Settings are optional. Returns empty dict if no settings section exists
    or manifest file is missing.
    """
    try:
        content = manifest_path.read_text()
    except FileNotFoundError:
        return {}

    result: dict = {}
    in_settings = False

    for line in content.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        indent = len(line) - len(line.lstrip())

        if indent == 0 and stripped == "settings:":
            in_settings = True
            continue
        elif indent == 0 and stripped.endswith(":"):
            in_settings = False
            continue

        if not in_settings:
            continue

        if indent == 2 and ":" in stripped:
            key, _, value = stripped.partition(":")
            value = value.strip()
            try:
                result[key.strip()] = int(value)
            except ValueError:
                result[key.strip()] = value

    return result
