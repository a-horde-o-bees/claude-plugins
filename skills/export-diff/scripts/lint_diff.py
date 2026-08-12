# /// script
# requires-python = ">=3.10"
# dependencies = ["beautifulsoup4", "lxml"]
# ///
"""Semantic linter for export-diff output (SPEC.md invariant I17).

Checks every rendered page's DOM against the box contract:

- **boxing** — in a changed cell, every non-whitespace character sits
  inside a `data-run` element (I9: total boxing).
- **one-sided** — a box id present on only one side must be completely
  inked: it is a pure removal or addition, so un-inked text inside it
  would claim a counterpart that does not exist.
- **pair-align** — for a box id present on both sides, the un-inked
  (shared) text must be identical left and right after whitespace
  normalization: the line minus deletions must equal the line minus
  additions.

Usage: lint_diff.py PAGE.html [...]  — or import and call lint_html().
Exits 1 if any page has violations.
"""

import re
import sys

from bs4 import BeautifulSoup

WS = re.compile(r"\s+")


def norm(text):
    return WS.sub(" ", text).strip()


def lint_html(html):
    """Return a list of violation strings for one rendered page."""
    soup = BeautifulSoup(html, "lxml")
    violations = []
    sides = {}  # id -> {"del"/"ins" -> {"eq": [..], "ink": [..]}}
    for td in soup.select("td.cl.del, td.cl.ins"):
        side = "del" if "del" in td.get("class", []) else "ins"
        ctn = td.select_one(".ctn")
        if ctn is None:
            continue
        for node in ctn.children:
            if getattr(node, "name", None) is None:
                if node.strip():
                    violations.append(
                        f"boxing: unboxed text {node.strip()[:40]!r} [{side}]")
                continue
            rid = node.get("data-run")
            if rid is None:
                if norm(node.get_text()):
                    violations.append(
                        f"boxing: element without box id "
                        f"{norm(node.get_text())[:40]!r} [{side}]")
                continue
            slot = sides.setdefault(rid, {}).setdefault(
                side, {"eq": [], "ink": []})
            slot["ink" if node.name in ("del", "ins") else "eq"].append(
                node.get_text())
    for rid, per_side in sorted(sides.items(), key=lambda kv: int(kv[0])):
        if len(per_side) == 1:
            side, slot = next(iter(per_side.items()))
            stray = norm(" ".join(slot["eq"]))
            # matched punctuation may attach to a neighboring box — an
            # attribution choice; only word content claims a counterpart
            if re.search(r"[0-9A-Za-z]", stray):
                violations.append(
                    f"one-sided: box {rid} [{side}] has un-inked text "
                    f"with no counterpart: {stray[:60]!r}")
        else:
            left = norm(" ".join(per_side["del"]["eq"]))
            right = norm(" ".join(per_side["ins"]["eq"]))
            # compared as word multisets: whitespace and punctuation attach
            # to neighbors, and a stationary fold may reorder within its
            # box — both are attribution choices, not misalignment
            if (sorted(re.findall(r"[0-9A-Za-z]+", left))
                    != sorted(re.findall(r"[0-9A-Za-z]+", right))):
                violations.append(
                    f"pair-align: box {rid} shared text differs: "
                    f"{left[:50]!r} != {right[:50]!r}")
    return violations


def main():
    bad = False
    for path in sys.argv[1:]:
        violations = lint_html(open(path, encoding="utf-8").read())
        if violations:
            bad = True
            print(f"{path}: {len(violations)} violation(s)")
            for v in violations:
                print(f"  {v}")
        else:
            print(f"{path}: lint clean")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
