#!/usr/bin/env python3
"""Fail a PR that changes plugin code without bumping the plugin's version.

The in-PR counterpart to `.githooks/pre-commit`: where the hook bumps on
direct-to-main commits, this gate enforces the bump in the PR itself so merge
yields one `main` commit carrying both change and bump — the deployment signal
for `claude plugins update` via /checkpoint.

A plugin "changed" when any file under `plugins/<name>/` other than its own
`.claude-plugin/plugin.json` differs base→head. For each such plugin, the
version in `.claude-plugin/plugin.json` must be strictly greater at head than
at base. A newly-added plugin (no manifest at base) is exempt.

Usage: bump-check.py <base-ref>   (head is the working tree / current HEAD)
"""

import json
import subprocess
import sys
from pathlib import Path

MANIFEST = ".claude-plugin/plugin.json"


def _run(args: list[str]) -> str:
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout


def changed_files(base: str) -> list[str]:
    out = _run(["git", "diff", "--name-only", f"{base}...HEAD"])
    return [line for line in out.splitlines() if line]


def plugins_with_code_changes(files: list[str]) -> set[str]:
    """Plugin names whose non-manifest files changed."""
    names: set[str] = set()
    for f in files:
        parts = f.split("/")
        if len(parts) >= 2 and parts[0] == "plugins" and not f.endswith(MANIFEST):
            names.add(parts[1])
    return names


def _version_at(ref: str, path: str) -> str | None:
    """Version string at a git ref, or None if the manifest doesn't exist there."""
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True)
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)["version"]
    except (json.JSONDecodeError, KeyError):
        return None


def _version_head(path: str) -> str | None:
    p = Path(path)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())["version"]
    except (json.JSONDecodeError, KeyError):
        return None


def _semver(v: str) -> tuple[int, ...]:
    return tuple(int(x) for x in v.split("."))


def missing_bumps(base: str) -> list[str]:
    """Plugin names that changed code but did not increment their version."""
    failures: list[str] = []
    for name in sorted(plugins_with_code_changes(changed_files(base))):
        manifest = f"plugins/{name}/{MANIFEST}"
        old = _version_at(base, manifest)
        if old is None:
            continue  # newly added plugin — no prior version to bump
        new = _version_head(manifest)
        if new is None or _semver(new) <= _semver(old):
            failures.append(f"{name}: {old} → {new or '(missing)'} (must increment)")
    return failures


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: bump-check.py <base-ref>", file=sys.stderr)
        return 2
    base = argv[0]
    failures = missing_bumps(base)
    if failures:
        print("Plugin code changed without a version bump:")
        for f in failures:
            print(f"  - {f}")
        print("\nBump the patch version in each plugin's .claude-plugin/plugin.json.")
        return 1
    print("bump-check: all changed plugins carry a version increment.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
