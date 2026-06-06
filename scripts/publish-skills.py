#!/usr/bin/env python3
"""Publish live skill sources into the committed distribution mirror.

Source of truth is ``~/.claude/skills/<name>/`` — real files, edited live.
The mirror is ``<repo>/skills/<name>/`` — generated, committed (the marketplace
serves it from GitHub), and never hand-edited. Publishing is one-way and
idempotent.

  python scripts/publish-skills.py            regenerate the mirror from source
  python scripts/publish-skills.py --check    read-only drift detector

``--check`` exits non-zero and lists skills whose mirror differs from source
(or whose source was hand-edited away). A skill whose source is absent (CI, or a
contributor who edits the mirror directly) is skipped, not failed.
"""
from __future__ import annotations

import filecmp
import json
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC_ROOT = Path.home() / ".claude" / "skills"
DST_ROOT = REPO / "skills"
MANIFEST = REPO / ".claude" / "skill-sources.json"
IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc")
_PRUNE = {"__pycache__"}


def manifest_names() -> list[str]:
    return json.loads(MANIFEST.read_text())["skills"]


def _differ(a: Path, b: Path) -> bool:
    """True if directory trees a and b differ, ignoring __pycache__/*.pyc."""
    cmp = filecmp.dircmp(a, b, ignore=list(_PRUNE))
    if cmp.left_only or cmp.right_only or cmp.diff_files or cmp.funny_files:
        return True
    for sub in cmp.common_dirs:
        if _differ(a / sub, b / sub):
            return True
    return False


def main() -> int:
    check = "--check" in sys.argv
    names = manifest_names()
    DST_ROOT.mkdir(exist_ok=True)

    drift, missing = [], []
    for name in names:
        src, dst = SRC_ROOT / name, DST_ROOT / name
        if not src.is_dir():
            missing.append(name)
            continue
        if check:
            if not dst.is_dir() or _differ(src, dst):
                drift.append(name)
        else:
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst, ignore=IGNORE)

    # Prune mirror dirs no longer in the manifest.
    declared = set(names)
    stale = [d.name for d in DST_ROOT.iterdir() if d.is_dir() and d.name not in declared]
    if check:
        drift.extend(s for s in stale if s not in drift)
    else:
        for s in stale:
            shutil.rmtree(DST_ROOT / s)

    if missing:
        print(f"skipped (source absent): {', '.join(sorted(missing))}")
    if check and drift:
        print(f"DRIFT — mirror differs from source: {', '.join(sorted(drift))}")
        print("Run: python scripts/publish-skills.py")
        return 1
    if not check:
        print(f"published {len(names) - len(missing)} skills → {DST_ROOT.relative_to(REPO)}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
