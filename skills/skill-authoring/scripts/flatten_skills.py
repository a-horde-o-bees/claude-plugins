#!/usr/bin/env python3
"""Materialize skill dependencies declared by /skill-name references.

This docstring is the source of truth for what the script does.

A skill declares a dependency by referencing a sibling skill as
/skill-name in its SKILL.md source — in prose at the point of use
("Apply /concise-prose to the commit summaries") or as a list item under
## Dependencies for a dependency that stacks without scoping. A linked
reference may target any anchor in the flattened unit, e.g.
[/concise-prose](#anti-staleness). Refresh:

  - verifies every reference names a sibling skill folder; a
    reference-shaped token that resolves to no sibling is an error.
    Self-references (the skill's own invocation surface) are exempt and
    left untouched; fenced blocks and inline code spans are definitional
    example text, never references.
  - links every bare reference in place — /name becomes [/name](#name),
    targeting the flattened unit's heading. Already-linked references
    are left byte-identical, so refresh converges after one pass.
  - ensures a ## Dependencies section exists as the LAST section,
    holding the marker-delimited generated region:

        ## Dependencies

        <!-- flatten-skills START -->
        ...generated units...
        <!-- flatten-skills STOP -->

    The section is appended when references exist and no region does,
    and relocated to the end when other sections follow it. Hand lines
    between the heading and START (the ambient reference list) are
    source; so are lines after STOP inside the section.
  - regenerates the region in full: the deduplicated transitive closure
    of the referenced skills, ordered topologically — every unit above
    every unit it references, ties broken by first-reference appearance
    — so referenced content always sits further down.

A unit is the dependency's SKILL.md minus frontmatter and minus its
entire ## Dependencies section, with headings demoted two levels
(H1 -> H3, H2 -> H4), its own closure references linked the same way,
and ${CLAUDE_SKILL_DIR} rewritten to ${CLAUDE_SKILL_DIR}/../<dep> so
bundled-file references resolve to the sibling-installed dependency
from inside the host.

Any markdown file can be a host, and in a non-skill host
${CLAUDE_SKILL_DIR} rewrites to the dependency's absolute folder — no
dispatcher binds the variable outside a skill invocation. Hosts are
declared in settings.skill-authoring.json under a "hosts" list, read
from the user scope (~/.claude/) and the project scope (the nearest
.claude/ at or above cwd; relative entries resolve against the project
root), unioned and deduplicated. Declared hosts join every invocation
that targets this script's own suite root — the gates get them with no
flag — while invocations naming other paths process only what they
name. A malformed settings file is an error, never a skipped read.
--skills-root overrides sibling resolution for explicitly named
out-of-suite hosts.

After computing a file, every in-file anchor link must resolve to a
heading in the materialized text.

Errors (nothing is written if any occurs):
  - more than one region, unpaired markers, or a START line carrying a
    payload
  - a region outside a ## Dependencies section
  - an unresolved reference-shaped token
  - a dependency cycle (named)
  - a unit would emit `-->` or a marker-shaped line outside a fence
  - an anchor link that resolves to no heading in the materialized file

Usage: flatten_skills.py [--check] [--skills-root DIR] <skills-root|skill-dir|SKILL.md|host.md> ...
  refresh (default): rewrite every file to its normalized form; idempotent
  --check: recompute and byte-compare; exit nonzero naming each stale or
           malformed skill, writing nothing
"""
import json
import os
import re
import sys
from pathlib import Path

OWN_ROOT = Path(__file__).resolve().parent.parent.parent
SETTINGS_NAME = "settings.skill-authoring.json"


def declared_hosts(errors) -> list:
    """Union of hosts from the user and project settings files, deduplicated
    by resolved path; relative project entries resolve against the project
    root (the directory holding .claude/)."""
    sources = [(Path.home() / ".claude" / SETTINGS_NAME, Path.home())]
    proj = os.environ.get("CLAUDE_PROJECT_DIR")
    candidates = [Path(proj)] if proj else [Path.cwd(), *Path.cwd().parents]
    for p in candidates:
        if (p / ".claude" / SETTINGS_NAME).is_file():
            sources.append((p / ".claude" / SETTINGS_NAME, p))
            break
    hosts, seen = [], set()
    for f, base in sources:
        if not f.is_file():
            continue
        try:
            decl = json.loads(f.read_text(encoding="utf-8"))
            entries = decl.get("hosts", [])
            assert isinstance(entries, list) \
                and all(isinstance(h, str) for h in entries)
        except (ValueError, AssertionError):
            errors.append(f"{f}: malformed — expected a JSON object with a"
                          " 'hosts' list of strings")
            continue
        for h in entries:
            hp = (base / Path(h).expanduser()).resolve() \
                if not Path(h).expanduser().is_absolute() \
                else Path(h).expanduser().resolve()
            if hp not in seen:
                seen.add(hp)
                hosts.append(hp)
    return hosts

START_RE = re.compile(r"^<!-- flatten-skills START -->\s*$")
START_ANY_RE = re.compile(r"^\s*<!--\s*flatten-skills START\b")
STOP_RE = re.compile(r"^<!-- flatten-skills STOP -->\s*$")
MARKER_RE = re.compile(r"^\s*<!--\s*flatten-skills\b")
FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
HEADING_RE = re.compile(r"^(#{1,6}) (.+?)\s*$")
DEPS_HEAD_RE = re.compile(r"^## Dependencies\s*$")
SPAN_RE = re.compile(r"`[^`\n]+`")
# linked form first so the bare alternative never fires inside a link
REF_RE = re.compile(
    r"\[/([\w][\w-]*)\]\(#([\w-]+)\)|(?<![\w./}-])/([\w][\w-]*)\b(?!/)")
ANCHOR_RE = re.compile(r"\]\(#([^)\s]+)\)")


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


def blank_spans(line: str) -> str:
    """Inline code spans replaced by same-length padding: positions survive."""
    return SPAN_RE.sub(lambda m: " " * len(m.group()), line)


def refs_in(line: str):
    """Yield (name, linked) for reference-shaped tokens outside code spans."""
    for m in REF_RE.finditer(blank_spans(line)):
        yield (m.group(1) or m.group(3)), m.group(1) is not None


def link_refs(line: str, targets) -> str:
    """Rewrite bare /name -> [/name](#name) for names in targets."""
    out, last = [], 0
    for m in REF_RE.finditer(blank_spans(line)):
        name = m.group(3)
        if name and name in targets:
            out.append(line[last:m.start()])
            out.append(f"[/{name}](#{name})")
            last = m.end()
    out.append(line[last:])
    return "".join(out)


def slug(heading: str) -> str:
    s = re.sub(r"[^\w\s-]", "", heading.strip().lower())
    return re.sub(r"\s+", "-", s)


class Skill:
    def __init__(self, path: Path, root: Path | None = None):
        self.path = path
        self.root = (root or path.resolve().parent.parent).resolve()
        self.name = path.resolve().parent.name
        self.in_suite = path.name == "SKILL.md" \
            and path.resolve().parent.parent == self.root
        self.siblings = {d.name for d in self.root.iterdir()
                         if (d / "SKILL.md").exists()}
        self.text = path.read_text(encoding="utf-8")
        self.lines = self.text.split("\n")
        self.fenced = {i: f for i, _, f in iter_lines(self.lines)}
        self.errors = []
        self.head = self.start = self.stop = self.section_end = None
        self.deps = []
        self._parse()
        if not self.errors:
            self._scan_refs()

    def _parse(self):
        starts, stops, heads, h2s = [], [], [], []
        for i, ln, fenced in iter_lines(self.lines):
            if fenced:
                continue
            if START_RE.match(ln):
                starts.append(i)
            elif START_ANY_RE.match(ln):
                self.errors.append(f"line {i + 1}: START line carries a payload"
                                   " — the marker is bare")
            elif STOP_RE.match(ln):
                stops.append(i)
            elif MARKER_RE.match(ln):
                self.errors.append(f"line {i + 1}: stray flatten marker line")
            elif DEPS_HEAD_RE.match(ln):
                heads.append(i)
            elif HEADING_RE.match(ln) and ln.startswith("## "):
                h2s.append(i)
        if self.errors:
            return
        if len(starts) > 1 or len(stops) > 1 or len(heads) > 1:
            self.errors.append("multiple flatten regions or Dependencies sections")
            return
        if len(starts) != len(stops) or (starts and starts[0] > stops[0]):
            self.errors.append("unpaired flatten markers")
            return
        self.head = heads[0] if heads else None
        if starts:
            self.start, self.stop = starts[0], stops[0]
            if self.head is None or self.start < self.head \
                    or any(self.head < j < self.start for j in h2s):
                self.errors.append("flatten region outside the"
                                   " ## Dependencies section")
                return
        if self.head is not None:
            after = [j for j in h2s if j > self.head]
            self.section_end = after[0] if after else len(self.lines)
            if self.stop is not None and self.stop > self.section_end:
                self.errors.append("flatten region crosses a section boundary")

    def _source_idx(self):
        """Line indices of the source layer, in original order."""
        if self.start is None or self.stop is None:
            return list(range(len(self.lines)))
        gen = range(self.start + 1, self.stop)
        return [i for i in range(len(self.lines)) if i not in gen]

    def _scan_refs(self):
        """Derive deps (first-appearance order) and verify every reference."""
        seen = set()
        for i in self._source_idx():
            if self.fenced[i]:
                continue
            for name, _ in refs_in(self.lines[i]):
                if name == self.name:
                    continue
                if name not in self.siblings:
                    self.errors.append(
                        f"line {i + 1}: unresolved reference /{name}")
                elif name not in seen:
                    seen.add(name)
                    self.deps.append(name)

    def split(self):
        """(rest, hand_before, hand_after): source line-index groups."""
        if self.head is None:
            return self._source_idx(), [], []
        end = self.section_end if self.section_end is not None else len(self.lines)
        rest = list(range(self.head)) + list(range(end, len(self.lines)))
        if self.start is None or self.stop is None:
            return rest, list(range(self.head + 1, end)), []
        return rest, list(range(self.head + 1, self.start)), \
            list(range(self.stop + 1, end))

    def component(self) -> str:
        """Unit source: frontmatter and the Dependencies section removed."""
        rest, _, _ = self.split()
        src = "\n".join(self.lines[i] for i in rest)
        src = re.sub(r"\A---\n.*?\n---\n", "", src, flags=re.S)
        return src.strip()


def demote(md: str) -> str:
    out = []
    for _, ln, fenced in iter_lines(md.split("\n")):
        out.append("##" + ln if not fenced and re.match(r"^#{1,4} ", ln) else ln)
    return "\n".join(out)


def build_unit(dep: Skill, targets, errors, host: Skill) -> str:
    unit = demote(dep.component())
    sub = "${CLAUDE_SKILL_DIR}/../" + dep.name if host.in_suite \
        else str(dep.root / dep.name)
    unit = unit.replace("${CLAUDE_SKILL_DIR}", sub)
    out = []
    for _, ln, fenced in iter_lines(unit.split("\n")):
        if fenced:
            out.append(ln)
            continue
        if "-->" in ln:
            errors.append(f"{dep.path}: component contains '-->' outside a fence: {ln.strip()}")
        elif MARKER_RE.match(ln):
            errors.append(f"{dep.path}: component contains a marker-shaped line: {ln.strip()}")
        out.append(link_refs(ln, targets))
    return "\n".join(out)


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


def closure_of(s: Skill, cache) -> list:
    """Topological unit order: every unit above every unit it references,
    ties broken by breadth-first discovery from the host's references."""
    discovered, queue = [], list(s.deps)
    while queue:
        n = queue.pop(0)
        if n in discovered:
            continue
        discovered.append(n)
        queue.extend(cache[n].deps)
    priority = {n: i for i, n in enumerate(discovered)}
    indeg = {n: 0 for n in discovered}
    for n in discovered:
        for d in cache[n].deps:
            indeg[d] += 1
    order, ready = [], sorted((n for n in discovered if indeg[n] == 0),
                              key=lambda n: priority[n])
    while ready:
        n = ready.pop(0)
        order.append(n)
        for d in cache[n].deps:
            indeg[d] -= 1
            if indeg[d] == 0:
                ready.append(d)
        ready.sort(key=lambda n: priority[n])
    return order


def trim(lines):
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


def assemble(s: Skill, units, targets) -> str:
    rest_idx, before_idx, after_idx = s.split()

    def rw(idxs):
        return [s.lines[i] if s.fenced[i] else link_refs(s.lines[i], targets)
                for i in idxs]

    rest = rw(rest_idx)
    while rest and not rest[-1].strip():
        rest.pop()
    if not s.deps and s.head is None:
        return "\n".join(rest) + "\n"
    before, after = trim(rw(before_idx)), trim(rw(after_idx))
    parts = rest + ["", "## Dependencies", ""]
    if before:
        parts += before + [""]
    parts += ["<!-- flatten-skills START -->", ""]
    if units:
        parts += "\n\n".join(units).split("\n") + [""]
    parts += ["<!-- flatten-skills STOP -->"]
    if after:
        parts += [""] + after
    return "\n".join(parts) + "\n"


def check_links(text: str, path: Path, errors):
    lines = text.split("\n")
    slugs, counts = set(), {}
    for _, ln, fenced in iter_lines(lines):
        m = HEADING_RE.match(ln)
        if not fenced and m:
            base = slug(m.group(2))
            n = counts.get(base, 0)
            counts[base] = n + 1
            slugs.add(base if n == 0 else f"{base}-{n}")
    for i, ln, fenced in iter_lines(lines):
        if fenced:
            continue
        for m in ANCHOR_RE.finditer(blank_spans(ln)):
            if m.group(1) not in slugs:
                errors.append(f"{path}: line {i + 1}: anchor #{m.group(1)}"
                              " resolves to no heading")


def main(argv):
    check = "--check" in argv
    args = [a for a in argv if a != "--check"]
    root = None
    if "--skills-root" in args:
        i = args.index("--skills-root")
        root = Path(args[i + 1]).expanduser().resolve()
        del args[i:i + 2]
    errors = []
    files, suite_scoped = [], False
    for a in args:
        p = Path(a)
        if p.is_dir():
            own = p / "SKILL.md"
            files.extend((f, root) for f in
                         ([own] if own.exists() else sorted(p.glob("*/SKILL.md"))))
            suite_scoped |= not own.exists() and p.resolve() == OWN_ROOT
        else:
            files.append((p, root))
    if suite_scoped:
        named = {f.resolve() for f, _ in files}
        files.extend((h, root or OWN_ROOT) for h in declared_hosts(errors)
                     if h.resolve() not in named)
    if not files:
        print("no SKILL.md files found", file=sys.stderr)
        return 2

    cache = {}

    def load(path: Path, r=None) -> Skill:
        s = Skill(path, r)
        errors.extend(f"{s.path}: {e}" for e in s.errors)
        return s

    targets = []
    for f, r in files:
        s = load(f, r)
        cache.setdefault(s.name, s)
        targets.append(s)
    queue = [d for s in targets for d in s.deps]
    while queue:
        n = queue.pop(0)
        if n in cache:
            continue
        s = load(targets[0].root / n / "SKILL.md", targets[0].root)
        cache[n] = s
        queue.extend(s.deps)
    if errors:
        for e in errors:
            print(f"ERROR {e}", file=sys.stderr)
        return 1

    cyc = find_cycle([s.name for s in targets], lambda n: cache[n].deps)
    if cyc:
        print(f"ERROR dependency cycle: {' -> '.join(cyc)}", file=sys.stderr)
        return 1

    # Compute every file before writing anything.
    results = []
    for s in targets:
        order = closure_of(s, cache)
        closure = set(order) | {s.name}
        units = [build_unit(cache[n], closure, errors, s) for n in order]
        new_text = assemble(s, units, closure)
        check_links(new_text, s.path, errors)
        results.append((s, new_text))
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
            print(f"{s.path}: STALE")
        else:
            s.path.write_text(new_text, encoding="utf-8")
            print(f"{s.path}: refreshed")
    n = len(results)
    if check:
        print(f"{n} file(s): {changed} stale")
        return 1 if changed else 0
    print(f"{n} file(s): {changed} refreshed, {n - changed} fresh")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
