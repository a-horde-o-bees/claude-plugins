"""Validate marketplace and plugin manifests.

Checks every `.claude-plugin/marketplace*.json` and every plugin's
`.claude-plugin/plugin.json` under `plugins/`. Verifies JSON parses,
required fields are present, and plugin sources declare either a
relative path or a supported git source shape.

Exits 0 on clean validation, non-zero when any file fails.

Runs in CI via `.github/workflows/validate.yml` and can be invoked
locally before pushing.
"""

import json
import sys
from pathlib import Path


def _git_root() -> Path:
    import subprocess
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
    )
    return Path(result.stdout.strip()).resolve()


def _validate_marketplace(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        return [f"{path}: JSON parse error: {e}"]

    for field in ("name", "owner", "plugins"):
        if field not in data:
            errors.append(f"{path}: missing required field `{field}`")

    owner = data.get("owner", {})
    if isinstance(owner, dict) and "name" not in owner:
        errors.append(f"{path}: `owner.name` missing")

    for idx, plugin in enumerate(data.get("plugins", []) or []):
        if not isinstance(plugin, dict):
            errors.append(f"{path}: plugins[{idx}] is not an object")
            continue
        if "name" not in plugin:
            errors.append(f"{path}: plugins[{idx}] missing `name`")
        source = plugin.get("source")
        if source is None:
            errors.append(f"{path}: plugins[{idx}] missing `source`")
            continue
        if isinstance(source, str):
            if not source.startswith("./"):
                errors.append(
                    f"{path}: plugins[{idx}] relative source must start with `./`",
                )
        elif isinstance(source, dict):
            kind = source.get("source")
            if kind not in ("github", "url", "git-subdir", "npm"):
                errors.append(
                    f"{path}: plugins[{idx}] unknown source kind `{kind}`",
                )
        else:
            errors.append(f"{path}: plugins[{idx}] source has invalid type")

    return errors


def _validate_plugin(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        return [f"{path}: JSON parse error: {e}"]

    if "name" not in data:
        errors.append(f"{path}: missing required field `name`")

    name = data.get("name", "")
    if name and not all(c.isalnum() or c in "-" for c in name):
        errors.append(f"{path}: `name` must be kebab-case (letters, digits, hyphens)")

    return errors


def main() -> int:
    root = _git_root()
    marketplace_dir = root / ".claude-plugin"
    plugin_dirs = sorted((root / "plugins").glob("*/"))

    errors: list[str] = []

    if marketplace_dir.is_dir():
        for candidate in sorted(marketplace_dir.glob("marketplace*.json")):
            errors.extend(_validate_marketplace(candidate))

    for plugin_dir in plugin_dirs:
        manifest = plugin_dir / ".claude-plugin" / "plugin.json"
        if not manifest.is_file():
            # Plugin dirs without plugin.json are in-development scaffolding —
            # not yet part of any marketplace. Skip rather than fail.
            continue
        errors.extend(_validate_plugin(manifest))

    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        print(f"\nValidation failed — {len(errors)} issue(s)", file=sys.stderr)
        return 1

    print("Validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
