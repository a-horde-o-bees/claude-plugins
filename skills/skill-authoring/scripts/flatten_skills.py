#!/usr/bin/env python3
"""Materialize skill dependencies into marker-delimited generated regions.

This docstring is the source of truth for what the script does.

A SKILL.md may contain at most one flatten region, placeable anywhere:

    <!-- flatten-skills START {"deps": ["<skill-folder-name>", ...]} -->
    ...generated content...
    <!-- flatten-skills STOP -->

The source layer of a file is everything outside the region plus the two
marker lines; everything between them is generated. Refresh rewrites each
region in full: a `## Dependencies` heading followed by the flat,
deduplicated transitive closure of the declared dependencies (breadth-first
from declaration order), each unit exactly once.

A unit is the dependency's SKILL.md minus frontmatter and minus its own
flatten region (marker lines included) — closure is over sources, never
over generated content — with headings demoted two levels (H1 -> H3,
H2 -> H4) and `${CLAUDE_SKILL_DIR}` rewritten to
`${CLAUDE_SKILL_DIR}/../<dep-folder>` so bundled-file references resolve
to the sibling-installed dependency from inside the host.

Dependencies resolve as sibling folders of the declaring skill. Marker-
shaped lines inside fenced code blocks are literal text in every mode.

Errors (nothing is written if any occurs):
  - more than one region in a file
  - START-line payload not a JSON object with a `deps` list of strings
  - declared dependency has no sibling SKILL.md
  - dependency cycle (named)
  - a unit would emit `-->` or a marker-shaped line outside a fence,
    corrupting the region boundary

Usage: flatten_skills.py [--check] <skills-root|skill-dir|SKILL.md> ...
  refresh (default): rewrite every region from source layers; idempotent
  --check: recompute and byte-compare; exit nonzero naming each stale or
           malformed skill, writing nothing
"""
import json
import re
import sys
from pathlib import Path

START_RE = re.compile(r"^<!-- flatten-skills START (.*) -->\s*$")
STOP_RE = re.compile(r"^<!-- flatten-skills STOP -->\s*$")
MARKER_RE = re.compile(r"^\s*<!--\s*flatten-skills\b")
FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")


def iter_lines(lines):
    """Yield (index, line, in_fence); fence delimiter lines count as fenced."""
    fence = None  # (char, min_len) while inside a fenced block
    for i, ln in enumerate(lines):
        m = FENCE_RE.match(ln)
        if fence:
            yield i, ln, True
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= fence[1] \
                    and not m.group(2).strip():
                fence = None
        elif m:
            fence = (m.group(1)[0], len(m.group(1)))
            yield i, ln, True
        else:
            yield i, ln, False


class Skill:
    def __init__(self, path: Path):
        self.path = path
        self.name = path.resolve().parent.name
        self.text = path.read_text(encoding="utf-8")
        self.lines = self.text.split("\n")
        self.start = self.stop = None  # region marker line indices
        self.deps = []
        self.errors = []
        self._parse()

    def _parse(self):
        starts, stops = [], []
        for i, ln, fenced in iter_lines(self.lines):
            if fenced:
                continue
            if START_RE.match(ln):
                starts.append(i)
            elif STOP_RE.match(ln):
                stops.append(i)
        if not starts and not stops:
            return
        if len(starts) > 1 or len(stops) > 1:
            self.errors.append("multiple flatten regions")
            return
        if len(starts) != len(stops) or starts[0] > stops[0]:
            self.errors.append("unpaired flatten markers")
            return
        self.start, self.stop = starts[0], stops[0]
        m = START_RE.match(self.lines[self.start])
        assert m is not None
        payload = m.group(1)
        if "-->" in payload:
            self.errors.append(f"declaration payload contains '-->': {payload}")
            return
        try:
            decl = json.loads(payload)
        except ValueError:
            self.errors.append(f"declaration is not valid JSON: {payload}")
            return
        if not isinstance(decl, dict) or not isinstance(decl.get("deps"), list) \
                or not all(isinstance(d, str) for d in decl["deps"]):
            self.errors.append(f"declaration lacks a 'deps' list: {payload}")
            return
        self.deps = decl["deps"]

    def component(self) -> str:
        """Source body: frontmatter and own region (markers included) removed."""
        lines = self.lines
        if self.start is not None and self.stop is not None:
            lines = lines[: self.start] + lines[self.stop + 1:]
        src = "\n".join(lines)
        src = re.sub(r"\A---\n.*?\n---\n", "", src, flags=re.S)
        return src.strip()


def demote(md: str) -> str:
    out = []
    for _, ln, fenced in iter_lines(md.split("\n")):
        out.append("##" + ln if not fenced and re.match(r"^#{1,4} ", ln) else ln)
    return "\n".join(out)


def build_unit(dep: Skill, errors) -> str:
    unit = demote(dep.component())
    unit = unit.replace("${CLAUDE_SKILL_DIR}", "${CLAUDE_SKILL_DIR}/../" + dep.name)
    for _, ln, fenced in iter_lines(unit.split("\n")):
        if fenced:
            continue
        if "-->" in ln:
            errors.append(f"{dep.path}: component contains '-->' outside a fence: {ln.strip()}")
        elif MARKER_RE.match(ln):
            errors.append(f"{dep.path}: component contains a marker-shaped line: {ln.strip()}")
    return unit


def load(path: Path, cache: dict, errors) -> Skill:
    key = path.resolve()
    if key not in cache:
        s = Skill(path)
        cache[key] = s
        errors.extend(f"{s.path}: {e}" for e in s.errors)
    return cache[key]


def resolve_dep(skill: Skill, dep: str) -> Path:
    return skill.path.resolve().parent.parent / dep / "SKILL.md"


def find_cycle(roots, get_deps):
    color, stack = {}, []

    def dfs(n):
        color[n] = 1
        stack.append(n)
        for d in get_deps(n):
            if color.get(d) == 1:
                return stack[stack.index(d):] + [d]
            if d not in color:
                cyc = dfs(d)
                if cyc:
                    return cyc
        color[n] = 2
        stack.pop()
        return None

    for r in roots:
        if r not in color:
            cyc = dfs(r)
            if cyc:
                return cyc
    return None


def main(argv):
    check = "--check" in argv
    args = [a for a in argv if a != "--check"]
    files = []
    for a in args:
        p = Path(a)
        if p.is_dir():
            own = p / "SKILL.md"
            files.extend([own] if own.exists() else sorted(p.glob("*/SKILL.md")))
        else:
            files.append(p)
    if not files:
        print("no SKILL.md files found", file=sys.stderr)
        return 2

    errors, cache = [], {}
    targets = [load(f, cache, errors) for f in files]

    # Pull the whole graph into the cache: every dep, transitively.
    queue = list(targets)
    while queue:
        s = queue.pop(0)
        for d in s.deps:
            dp = resolve_dep(s, d)
            if not dp.exists():
                errors.append(f"{s.path}: dependency '{d}' has no SKILL.md at {dp}")
                continue
            if dp.resolve() not in cache:
                queue.append(load(dp, cache, errors))
    if errors:
        for e in errors:
            print(f"ERROR {e}", file=sys.stderr)
        return 1

    graph = {k: [resolve_dep(s, d) for d in s.deps] for k, s in cache.items()}
    cyc = find_cycle([s.path.resolve() for s in targets], graph.get)
    if cyc:
        names = " -> ".join(cache[k].name for k in cyc)
        print(f"ERROR dependency cycle: {names}", file=sys.stderr)
        return 1

    # Compute every region before writing anything.
    results, stale = [], []
    for s in targets:
        if s.start is None:
            continue
        seen, order = set(), []
        bfs = [resolve_dep(s, d) for d in s.deps]
        while bfs:
            k = bfs.pop(0).resolve()
            if k in seen:
                continue
            seen.add(k)
            order.append(k)
            bfs.extend(graph[k])
        units = [build_unit(cache[k], errors) for k in order]
        content = "\n\n".join(["## Dependencies"] + units)
        # blank lines inside the boundary keep the generated markdown valid:
        # a heading or list item butted against a marker comment trips
        # blanks-around / one-line-items in the suite's markdown linter
        new_lines = (s.lines[: s.start + 1] + [""] + content.split("\n")
                     + [""] + s.lines[s.stop:])
        results.append((s, "\n".join(new_lines)))
    if errors:
        for e in errors:
            print(f"ERROR {e}", file=sys.stderr)
        return 1

    changed = 0
    for s, new_text in results:
        if new_text == s.text:
            continue
        changed += 1
        if check:
            stale.append(s)
            print(f"{s.path}: STALE region")
        else:
            s.path.write_text(new_text, encoding="utf-8")
            print(f"{s.path}: refreshed")
    n = len(results)
    if check:
        print(f"{n} region(s): {changed} stale")
        return 1 if stale else 0
    print(f"{n} region(s): {changed} refreshed, {n - changed} fresh")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
