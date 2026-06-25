#!/usr/bin/env python3
"""Stage file/dir targets into one central workspace for apply-over-queue's `staged` mode.

Targets may live anywhere. Staging copies each origin into one run-local workspace so every
spawn operates with an IDENTICAL fixed cwd (the workspace) — the prompt prefix then stays
byte-identical no matter where the origins live, which is exactly what the prompt cache needs.
The origin<->stage map drives a formal end-of-run diff and copy-back-on-approval, so review is
a real `diff` (reliable even after repeated modification, e.g. a convergence feeder) rather than
the editor's per-edit diff.

  stage.py --dir D add <origin>   copy origin -> workspace slot (idempotent); print the stage path
  stage.py --dir D diff           formal `git diff --no-index` of every staged copy vs its origin;
                                  write D/diff.patch; print a changed/total summary
  stage.py --dir D apply          copy every CHANGED staged copy back over its origin
  stage.py --dir D discard        remove the workspace (the map + diff.patch are kept as a record)
  stage.py --dir D map            print the origin<->stage map as JSON

The map lives in D/stage_map.json. A slot is D/work/<hash8(origin)>/<basename>, so re-adding the
same origin (a convergence feeder re-yielding it) resolves to the SAME slot and never clobbers
in-progress edits.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path


def _map_path(D):
    return D / "stage_map.json"


def _load(D):
    p = _map_path(D)
    return json.loads(p.read_text()) if p.exists() else []


def _save(D, m):
    _map_path(D).write_text(json.dumps(m, indent=2))


def _slot(D, origin):
    h = hashlib.sha256(str(origin).encode()).hexdigest()[:8]
    return D / "work" / h / Path(origin).name


def _diff_one(origin, stage):
    # git diff --no-index emits a clean unified patch for files and trees alike; a nonzero exit
    # just means "they differ", so the captured stdout is the signal.
    return subprocess.run(["git", "diff", "--no-index", "--", str(origin), str(stage)],
                          text=True, capture_output=True).stdout


def add(D, origin):
    origin = Path(origin).expanduser().resolve()
    if not origin.exists():
        sys.exit(f"stage add: origin does not exist: {origin}")
    m = _load(D)
    for e in m:
        if e["origin"] == str(origin):
            print(e["stage"])           # already staged — preserve the working copy
            return
    stage = _slot(D, origin)
    stage.parent.mkdir(parents=True, exist_ok=True)
    if origin.is_dir():
        shutil.copytree(origin, stage)
    else:
        shutil.copy2(origin, stage)
    m.append({"origin": str(origin), "stage": str(stage), "is_dir": origin.is_dir()})
    _save(D, m)
    print(str(stage))


def diff(D):
    m = _load(D)
    patch, changed = [], []
    for e in m:
        d = _diff_one(e["origin"], e["stage"])
        if d.strip():
            patch.append(d)
            changed.append(e["origin"])
    (D / "diff.patch").write_text("\n".join(patch))
    print(f"changed={len(changed)} of {len(m)}")
    for o in changed:
        print(f"  M {o}")
    if not changed:
        print("  (no targets changed)")


def apply(D):
    m, n = _load(D), 0
    for e in m:
        if not _diff_one(e["origin"], e["stage"]).strip():
            continue
        origin, stage = Path(e["origin"]), Path(e["stage"])
        if e["is_dir"]:
            shutil.rmtree(origin)
            shutil.copytree(stage, origin)
        else:
            shutil.copy2(stage, origin)
        n += 1
        print(f"  applied -> {origin}")
    print(f"applied {n} changed target(s)")


def discard(D):
    w = D / "work"
    if w.exists():
        shutil.rmtree(w)
    print(f"discarded workspace {w}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a_add = sub.add_parser("add")
    a_add.add_argument("origin")
    sub.add_parser("diff")
    sub.add_parser("apply")
    sub.add_parser("discard")
    sub.add_parser("map")
    a = ap.parse_args()

    D = Path(a.dir)
    D.mkdir(parents=True, exist_ok=True)
    {"add": lambda: add(D, a.origin), "diff": lambda: diff(D), "apply": lambda: apply(D),
     "discard": lambda: discard(D), "map": lambda: print(json.dumps(_load(D), indent=2))}[a.cmd]()


if __name__ == "__main__":
    main()
