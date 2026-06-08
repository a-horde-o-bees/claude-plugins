#!/usr/bin/env python3
"""Reconcile the project skill manifest against the live source reality.

Precursor to ``sync_skills``: compares ``.claude/skill-manifest.json`` against the
skills actually present in ``~/.claude/skills/``, so the manifest is curated
deliberately — nothing ships implicitly. A new live skill is surfaced as a
candidate, not auto-added; the human decides what the plugin exposes.

  reconcile_manifest.py             report new / removed / changed (human)
  reconcile_manifest.py --json      machine-readable report
  reconcile_manifest.py --add a,b   add skills to the manifest (must be live)
  reconcile_manifest.py --remove a  drop skills from the manifest

  new           — live skills (with SKILL.md) absent from the manifest (add to publish)
  removed       — manifest entries with no live source (drop, or restore the source)
  changed       — manifested skills whose live source differs from the repo mirror
  project_newer — CHANGED skills whose mirror is MORE RECENT than live (see below)

Project-newer is the red flag: the repo mirror holds newer, differing content than
the source of truth. A plain ``sync_skills`` refuses to overwrite these. Shared
config/helpers live in ``_mirror``.
"""
from __future__ import annotations

import argparse
import json

import _mirror as m


def report() -> dict:
    manifest = m.manifest_load()
    live = m.live_skills()
    mset = set(manifest)
    new = sorted(live - mset)
    removed = sorted(mset - live)
    changed = sorted(
        name for name in manifest
        if name in live and (not (m.DST_ROOT / name).is_dir() or m.differ(m.SRC_ROOT / name, m.DST_ROOT / name))
    )
    project_newer = sorted(name for name in changed if m.project_newer(name))
    return {"new": new, "removed": removed, "changed": changed,
            "project_newer": project_newer,
            "manifest_count": len(manifest), "live_count": len(live)}


def main() -> int:
    ap = argparse.ArgumentParser(description="Reconcile the skill manifest against live sources.")
    ap.add_argument("--json", action="store_true", help="machine-readable report")
    ap.add_argument("--add", default="", help="comma-separated skills to add (must be live)")
    ap.add_argument("--remove", default="", help="comma-separated skills to drop")
    a = ap.parse_args()

    if a.add or a.remove:
        manifest = m.manifest_load()
        live = m.live_skills()
        add = [x.strip() for x in a.add.split(",") if x.strip()]
        rm = {x.strip() for x in a.remove.split(",") if x.strip()}
        bad = [x for x in add if x not in live]
        if bad:
            print(f"refusing — not live skills: {', '.join(bad)}")
            return 1
        out = [x for x in manifest if x not in rm] + [x for x in add if x not in manifest]
        m.manifest_save(out)
        print(f"manifest: {len(manifest)} -> {len(out)} skills")
        return 0

    r = report()
    if a.json:
        print(json.dumps(r, indent=2))
        return 3 if r["project_newer"] else 0
    print(f"manifest {r['manifest_count']} skills | live {r['live_count']} skills")
    for label, key in (("NEW (live, not manifested)", "new"),
                       ("REMOVED (manifested, no source)", "removed"),
                       ("CHANGED (source differs from mirror)", "changed")):
        items = r[key]
        print(f"  {label}: {', '.join(items) if items else '—'}")
    if r["project_newer"]:
        m.warn_project_newer(r["project_newer"])
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
