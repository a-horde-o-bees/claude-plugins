#!/usr/bin/env python3
"""Project skill-delivery sync — the `on-main` augmentation for /git-checkpoint.

Runs after new content lands on main (a feature merge or a base-mode push) to
refresh how this repo's plugins reach a running session. Two modes:

  marketplace  Refresh the marketplace cache and run `claude plugins update`
               for each plugin whose code changed in the just-landed commit.
               Recommends a session restart (the plugin install is cached and
               only re-reads at session start).
  installed    Reinstall any user-scope skill in .claude/installed-skills.json
               whose source plugin version changed, via `npx skills add`. No
               restart needed (npx symlinks into ~/.claude/skills and the
               registry refreshes mid-session).

Usage: checkpoint-sync.py [marketplace|installed]   (default: marketplace)
Changed plugins are detected from the last landed commit (HEAD~1..HEAD), which
is the squash-merge or base-mode push. Side-effecting (runs claude/npx); not a
classification helper. Exit 0 on success, 1 if any per-plugin action failed.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def _project_root() -> Path:
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        if (parent / ".claude-plugin" / "marketplace.json").exists():
            return parent
    raise SystemExit("error: no .claude-plugin/marketplace.json found in cwd or ancestors")


def _last_landed_files() -> list[str]:
    """Files changed by the commit that just landed on main (HEAD~1..HEAD)."""
    r = subprocess.run(["git", "diff", "--name-only", "HEAD~1", "HEAD"],
                       capture_output=True, text=True)
    return [f for f in r.stdout.splitlines() if f] if r.returncode == 0 else []


def _changed_plugins(files: list[str]) -> list[str]:
    names: list[str] = []
    for f in files:
        parts = f.split("/")
        if len(parts) >= 2 and parts[0] == "plugins" and parts[1] not in names:
            names.append(parts[1])
    return names


def _marketplace(root: Path) -> int:
    files = _last_landed_files()
    changed = _changed_plugins(files)
    marketplace_changed = ".claude-plugin/marketplace.json" in files
    if not changed and not marketplace_changed:
        print("sync (marketplace): skipped — no plugin code or marketplace manifest in the last commit")
        print("Restart: not needed")
        return 0

    name = json.loads((root / ".claude-plugin" / "marketplace.json").read_text())["name"]
    failed = False
    print(f"sync (marketplace): refreshing `{name}`")
    r = subprocess.run(["claude", "plugins", "marketplace", "update", name],
                       capture_output=True, text=True)
    if r.returncode != 0:
        failed = True
        print(f"  - marketplace update failed: {r.stderr.rstrip()}")
    for plugin in changed:
        r = subprocess.run(["claude", "plugins", "update", f"{plugin}@{name}"],
                           capture_output=True, text=True)
        status = "updated" if r.returncode == 0 else f"FAILED: {r.stderr.rstrip()}"
        failed = failed or r.returncode != 0
        print(f"  {'+' if r.returncode == 0 else '-'} {plugin}@{name} — {status}")

    print(f"Plugins updated: {', '.join(changed) or '(none)'}")
    print("Restart: recommended (`/exit` then `claude --continue`) — the cached plugin install only re-reads at session start")
    return 1 if failed else 0


def _installed(root: Path) -> int:
    manifest_path = root / ".claude" / "installed-skills.json"
    if not manifest_path.exists():
        print(f"sync (installed): no manifest at {manifest_path} — nothing to sync")
        return 0
    manifest = json.loads(manifest_path.read_text())
    skills = manifest.get("skills", [])
    if not skills:
        print("sync (installed): manifest declares no skills — nothing to sync")
        return 0

    failed = changed = False
    counts = {"installed": 0, "updated": 0, "uptodate": 0, "failed": 0}
    for entry in skills:
        name, plugin, repo = entry["name"], entry["plugin"], entry["repo"]
        pj = root / "plugins" / plugin / ".claude-plugin" / "plugin.json"
        current = json.loads(pj.read_text())["version"]
        installed = entry.get("installed_version")
        if installed == current:
            counts["uptodate"] += 1
            print(f"+ {name} ({plugin} v{current}) — up to date")
            continue
        action = "install" if installed is None else "update"
        print(f"~ {name} ({plugin} v{installed or 'none'} → v{current}) — npx skills add")
        r = subprocess.run(["npx", "skills", "add", repo, "--skill", name, "-g"],
                           capture_output=True, text=True)
        if r.returncode != 0:
            failed = True
            counts["failed"] += 1
            print(f"- {name} — npx skills add failed (exit {r.returncode}): {r.stderr.rstrip()}")
            continue
        entry["installed_version"] = current
        changed = True
        counts["installed" if action == "install" else "updated"] += 1
        print(f"+ {name} ({plugin} v{current}) — {action}ed")

    if changed:
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
        print(f"\nmanifest updated: {manifest_path}")
    print(f"\nsync summary: {counts['installed']} installed, {counts['updated']} updated, "
          f"{counts['uptodate']} up to date, {counts['failed']} failed")
    print("Restart: not needed — npx symlinks the new artifacts; the registry refreshes mid-session")
    return 1 if failed else 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Project skill-delivery sync")
    ap.add_argument("mode", nargs="?", default="marketplace", choices=["marketplace", "installed"])
    a = ap.parse_args(argv)
    root = _project_root()
    return _marketplace(root) if a.mode == "marketplace" else _installed(root)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
