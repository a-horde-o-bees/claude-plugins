#!/usr/bin/env python3
"""Atomic file-backed work queue for apply-over-queue.

  queue.py --dir D seed [<item>...]  initialize the pending list (empty for feeder mode)
  queue.py --dir D push <item>       append one item to pending, keeping claimed/done
  queue.py --dir D next              atomically claim + print the next item (or NONE)
  queue.py --dir D done <item>       record an item as complete
  queue.py --dir D status            print pending/claimed/done counts

State lives in D/{pending,claimed,done}.txt; an exclusive lock serializes claims
so concurrent spawns never grab the same item. A static run seeds the full list
up front; a dynamic run seeds empty and `push`es one item per feeder iteration.
"""
import argparse
import fcntl
from pathlib import Path


def _lines(p: Path):
    return [l for l in p.read_text().splitlines() if l.strip()] if p.exists() else []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sd = sub.add_parser("seed"); sd.add_argument("items", nargs="*")
    sub.add_parser("next"); sub.add_parser("status")
    dn = sub.add_parser("done"); dn.add_argument("item")
    pu = sub.add_parser("push"); pu.add_argument("item")
    a = ap.parse_args()

    D = Path(a.dir); D.mkdir(parents=True, exist_ok=True)
    pend, claim, done = D / "pending.txt", D / "claimed.txt", D / "done.txt"
    with open(D / "lock", "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        if a.cmd == "seed":
            pend.write_text("\n".join(a.items) + ("\n" if a.items else ""))
            claim.write_text(""); done.write_text("")
            print(f"seeded {len(a.items)}")
        elif a.cmd == "push":
            with open(pend, "a") as f:
                f.write(a.item + "\n")
            print("pushed")
        elif a.cmd == "next":
            items = _lines(pend)
            if not items:
                print("NONE"); return
            it, rest = items[0], items[1:]
            pend.write_text("\n".join(rest) + ("\n" if rest else ""))
            with open(claim, "a") as f:
                f.write(it + "\n")
            print(it)
        elif a.cmd == "done":
            with open(done, "a") as f:
                f.write(a.item + "\n")
            print("ok")
        elif a.cmd == "status":
            print(f"pending={len(_lines(pend))} claimed={len(_lines(claim))} done={len(_lines(done))}")


if __name__ == "__main__":
    main()
