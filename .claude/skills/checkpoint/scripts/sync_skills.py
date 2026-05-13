#!/usr/bin/env python3
"""Sync user-scope skills per .claude/installed-skills.json manifest.

For each skill declared in the manifest:
- Read the source plugin's current version from `plugins/<plugin>/.claude-plugin/plugin.json`
- If `installed_version` is missing or differs from current: run `npx skills add <repo> --skill <name> -g`
- Record the new `installed_version` in the manifest on successful install

Manifest shape:
{
  "skills": [
    {"name": "<skill>", "plugin": "<plugin>", "repo": "<owner>/<repo>", "installed_version": "<x.y.z>"}
  ]
}

Output: one line per skill with action taken; final summary line.
Exit code: 0 on full success; 1 if any install failed.
"""
import json
import subprocess
import sys
from pathlib import Path


def find_project_root() -> Path:
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        if (parent / ".claude-plugin" / "marketplace.json").exists():
            return parent
    raise SystemExit("error: no .claude-plugin/marketplace.json found in cwd or ancestors")


def read_plugin_version(project_root: Path, plugin: str) -> str:
    manifest = project_root / "plugins" / plugin / ".claude-plugin" / "plugin.json"
    if not manifest.exists():
        raise SystemExit(f"error: plugin manifest not found at {manifest}")
    with open(manifest) as f:
        return json.load(f)["version"]


def main() -> int:
    project_root = find_project_root()
    manifest_path = project_root / ".claude" / "installed-skills.json"
    if not manifest_path.exists():
        print(f"no manifest at {manifest_path} — nothing to sync")
        return 0

    with open(manifest_path) as f:
        manifest = json.load(f)

    skills = manifest.get("skills", [])
    if not skills:
        print(f"manifest at {manifest_path} declares no skills — nothing to sync")
        return 0

    any_failed = False
    any_changed = False
    installed_count = 0
    updated_count = 0
    uptodate_count = 0

    for entry in skills:
        name = entry["name"]
        plugin = entry["plugin"]
        repo = entry["repo"]
        current_version = read_plugin_version(project_root, plugin)
        installed_version = entry.get("installed_version")

        if installed_version == current_version:
            uptodate_count += 1
            print(f"+ {name} ({plugin} v{current_version}) — up to date")
            continue

        action = "install" if installed_version is None else "update"
        print(f"~ {name} ({plugin} v{installed_version or 'none'} → v{current_version}) — running npx skills add")
        result = subprocess.run(
            ["npx", "skills", "add", repo, "--skill", name, "-g"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            any_failed = True
            print(f"- {name} — npx skills add failed (exit {result.returncode}):")
            if result.stderr:
                print(result.stderr.rstrip())
            continue

        entry["installed_version"] = current_version
        any_changed = True
        if action == "install":
            installed_count += 1
        else:
            updated_count += 1
        print(f"+ {name} ({plugin} v{current_version}) — {action}ed")

    if any_changed:
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
            f.write("\n")
        print(f"\nmanifest updated: {manifest_path}")

    print(
        f"\nsync summary: {installed_count} installed, {updated_count} updated, "
        f"{uptodate_count} up to date, {len(skills) - installed_count - updated_count - uptodate_count} failed"
    )
    return 1 if any_failed else 0


if __name__ == "__main__":
    sys.exit(main())
