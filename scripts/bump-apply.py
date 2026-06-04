#!/usr/bin/env python3
"""Apply the in-PR plugin-version bump — the apply-side counterpart to bump-check.py.

For each plugin with code changes versus a base ref (default `origin/main`), set
its `plugin.json` version to `z+1` of the base version — unless it is already
ahead of base, in which case it's left untouched (idempotent; respects a manual
minor/major bump). Newly-added plugins (no manifest at base) are skipped.

The bump rides in the PR atomically with the change, so there is no server-side
push-back to a protected `main` (the failure mode that retired auto-bump.yml).
bump-check.py stays as the CI belt: apply *and* verify.

Modes:
  default      changed plugins = working tree vs base (`git diff --name-only <base>`,
               includes uncommitted edits); bump the working tree. The caller commits.
               Used by the /checkpoint flow before /git-commit.
  --staged     changed plugins = the staged set (`git diff --cached --name-only`);
               bump and `git add` so the bump lands in the commit being made.
               Used by the pre-commit hook.
  --fetch      `git fetch -q origin <base-branch>` first, so the recompute is against
               the freshest base — the merge-time guarantee.

Usage: bump-apply.py [<base-ref>] [--staged] [--fetch]   (default base: origin/main)
Prints one line per bump applied; exit 0 always (nothing to bump is success).
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

MANIFEST = ".claude-plugin/plugin.json"
VERSION_RE = re.compile(r'("version"\s*:\s*")(\d+)\.(\d+)\.(\d+)(")')


def _run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(args, capture_output=True, text=True)


def _ver(s: str) -> tuple[int, int, int]:
    a, b, c = s.split(".")
    return int(a), int(b), int(c)


def _version_at_ref(ref: str, path: str) -> str | None:
    r = _run(["git", "show", f"{ref}:{path}"])
    if r.returncode != 0:
        return None
    m = VERSION_RE.search(r.stdout)
    return f"{m.group(2)}.{m.group(3)}.{m.group(4)}" if m else None


def _version_file(path: Path) -> str | None:
    if not path.exists():
        return None
    m = VERSION_RE.search(path.read_text())
    return f"{m.group(2)}.{m.group(3)}.{m.group(4)}" if m else None


def _set_version(path: Path, new: str) -> None:
    text = path.read_text()
    path.write_text(VERSION_RE.sub(lambda m: f"{m.group(1)}{new}{m.group(5)}", text, count=1))


def _changed_plugins(files: list[str]) -> set[str]:
    names: set[str] = set()
    for f in files:
        parts = f.split("/")
        if len(parts) >= 2 and parts[0] == "plugins" and not f.endswith(MANIFEST):
            names.add(parts[1])
    return names


def apply_bumps(base: str, staged: bool, paths: list[str] | None = None) -> list[str]:
    cmd = ["git", "diff", "--cached", "--name-only"] if staged \
        else ["git", "diff", "--name-only", base]
    if paths:
        cmd += ["--", *paths]
    files = _run(cmd).stdout.splitlines()

    bumped: list[str] = []
    for name in sorted(_changed_plugins([f for f in files if f])):
        manifest = Path("plugins") / name / MANIFEST
        base_ver = _version_at_ref(base, f"plugins/{name}/{MANIFEST}")
        if base_ver is None:
            continue  # newly added plugin — no prior version to bump from
        cur = _version_file(manifest)
        if cur is None:
            continue
        if _ver(cur) <= _ver(base_ver):
            x, y, z = base_ver.split(".")
            target = f"{x}.{y}.{int(z) + 1}"
            _set_version(manifest, target)
            if staged:
                _run(["git", "add", str(manifest)])
            bumped.append(f"{name}: {cur} -> {target} (base {base} = {base_ver})")
    return bumped


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Apply the in-PR plugin-version bump")
    ap.add_argument("base", nargs="?", default="origin/main", help="base ref (default origin/main)")
    ap.add_argument("--staged", action="store_true", help="bump the staged set and git-add (pre-commit)")
    ap.add_argument("--fetch", action="store_true", help="fetch the base branch first (merge-time freshness)")
    ap.add_argument("--paths", nargs="*", metavar="PATHSPEC",
                    help="scope the bump to plugins under these paths (scoped checkpoint)")
    a = ap.parse_args(argv)

    if a.fetch:
        branch = a.base.split("/", 1)[1] if "/" in a.base else a.base
        remote = a.base.split("/", 1)[0] if "/" in a.base else "origin"
        _run(["git", "fetch", "-q", remote, branch])

    for line in apply_bumps(a.base, a.staged, a.paths):
        print(f"bump-apply: {line}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
