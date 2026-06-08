#!/usr/bin/env python3
"""Sync live skill sources into this project's distribution mirror.

Project-local tool: skills are authored in ``~/.claude/skills/`` (the source of
truth); this regenerates the repo's ``skills/`` mirror from them, per the
allowlist in ``.claude/skill-manifest.json``. The mirror is what the marketplace
plugin ships — never edit ``skills/`` directly; edit the live source and sync.

  sync_skills.py            regenerate the mirror from source (per manifest)
  sync_skills.py --check    read-only drift detector (exit 1 drift, 3 project-newer)
  sync_skills.py --force    overwrite even a project-newer mirror (see below)

**Project-newer guard.** If a mirrored skill's content differs from live AND the
mirror is more recent, the live source is no longer the latest — the project may
hold changes that aren't in ``~/.claude/skills/``. Sync refuses to overwrite such
a skill (it would destroy the newer version), flags it loudly, and continues with
the rest. Back-port the change to the live source, or pass ``--force``.

Shared config/helpers (paths, manifest, .gitignore-derived exclusions) live in
``_mirror``. Run ``reconcile_manifest.py`` first to curate the manifest.
"""
from __future__ import annotations

import argparse
import shutil

import _mirror as m


def main() -> int:
    ap = argparse.ArgumentParser(description="Mirror ~/.claude/skills into repo skills/ per the manifest.")
    ap.add_argument("--check", action="store_true", help="read-only drift detector")
    ap.add_argument("--force", action="store_true", help="overwrite even a project-newer mirror")
    a = ap.parse_args()

    names = m.manifest_load()
    declared = set(names)
    m.DST_ROOT.mkdir(exist_ok=True)

    missing = sorted(n for n in names if not (m.SRC_ROOT / n).is_dir())
    present = [n for n in names if (m.SRC_ROOT / n).is_dir()]
    newer = sorted(n for n in present if m.project_newer(n))
    stale = sorted(d.name for d in m.DST_ROOT.iterdir() if d.is_dir() and d.name not in declared)

    if a.check:
        drift = sorted(
            {n for n in present if not (m.DST_ROOT / n).is_dir() or m.differ(m.SRC_ROOT / n, m.DST_ROOT / n)}
            | set(stale)
        )
        if missing:
            print(f"skipped (source absent): {', '.join(missing)}")
        if newer:
            m.warn_project_newer(newer)
        if drift:
            print(f"DRIFT — mirror differs from manifest source: {', '.join(drift)}")
        return 3 if newer else (1 if drift else 0)

    if newer and not a.force:
        m.warn_project_newer(newer)
        print(f"skipped (project-newer, not overwritten): {', '.join(newer)}")

    to_sync = [n for n in present if a.force or n not in newer]
    for n in to_sync:
        dst = m.DST_ROOT / n
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(m.SRC_ROOT / n, dst, ignore=m.IGNORE)
    for stale_name in stale:
        shutil.rmtree(m.DST_ROOT / stale_name)

    if missing:
        print(f"skipped (source absent): {', '.join(missing)}")
    print(f"synced {len(to_sync)} skills -> {m.DST_ROOT}")
    return 3 if (newer and not a.force) else 0


if __name__ == "__main__":
    raise SystemExit(main())
