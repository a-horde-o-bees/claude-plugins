#!/usr/bin/env python3
"""Assemble the flattened instruction payload: the normalized operation file
plus the named skills, normalized to the deduplicated union closure.

Skills arrive pre-materialized: a SKILL.md's flatten region (see
skill-authoring/scripts/flatten_skills.py) carries the closure of its declared
dependencies. Concatenating those files verbatim would duplicate any unit two
named skills share — or a named skill already inside another's closure — so
assembly re-normalizes from source layers instead: each named skill's region
is stripped, its `deps` declaration read, and every unit in the union closure
(named skills first, then their deps breadth-first) is emitted exactly once as
a `## <name>` section. An anchor reference like `[x](#x)` in an operation or a
host body resolves to that single copy.

Each unit's headings are demoted (fence-aware) so nothing collides with the
sibling section anchors, and `${CLAUDE_SKILL_DIR}` is substituted with the
unit's own folder — the spawns reading the payload have no dispatcher to bind
it, and a payload where the variable survives anywhere is refused.

  flatten.py --skills skill-authoring,reauthor --operation-file op.md \
             --skills-root ~/.claude/skills --out instruction.md
"""
import argparse
import json
import re
from pathlib import Path

# the dispatcher-resolved skill-dir variable; spawns reading the payload can't bind it
SKILL_DIR_VAR = "${CLAUDE_SKILL_DIR}"

START_RE = re.compile(r'^<!-- flatten-skills START (.*) -->\s*$')
STOP_RE = re.compile(r'^<!-- flatten-skills STOP -->\s*$')
FENCE_RE = re.compile(r'^ {0,3}(`{3,}|~{3,})(.*)$')
LEVEL = re.compile(r'^(#{1,6})(\s)')


def body_of(text: str) -> str:
    """Strip YAML frontmatter if present; return the markdown body."""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[text.find("\n", end + 1) + 1:].lstrip("\n")
    return text


def split_region(text: str):
    """(source_text, deps): the text minus its flatten region (marker lines
    included), and the region's declared deps ([] when no region). Marker
    lines inside fenced code blocks are literal text."""
    lines = text.split("\n")
    fence, start, stop, deps = None, None, None, []
    for i, ln in enumerate(lines):
        m = FENCE_RE.match(ln)
        if fence:
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= fence[1] \
                    and not m.group(2).strip():
                fence = None
            continue
        if m:
            fence = (m.group(1)[0], len(m.group(1)))
            continue
        sm = START_RE.match(ln)
        if sm and start is None:
            start = i
            decl = json.loads(sm.group(1))
            deps = [d for d in decl.get("deps", []) if isinstance(d, str)]
        elif STOP_RE.match(ln) and start is not None and stop is None:
            stop = i
    if start is not None and stop is not None:
        lines = lines[:start] + lines[stop + 1:]
    return "\n".join(lines), deps


def section(anchor: str, body: str) -> str:
    """Emit a body under a unique `## <anchor>`: drop its title H1, then shift ALL its
    headings (fence-aware) so the shallowest lands at `###`. This guarantees nothing in
    a body sits at `##`, so body headings — including stray H1s in example output —
    never collide with the sibling section anchors."""
    lines = body.splitlines()
    i = 0
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i < len(lines) and re.match(r'#\s', lines[i]):   # the unit's own title H1
        i += 1
    content = lines[i:]

    levels, in_fence = [], False
    for line in content:
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        elif not in_fence:
            m = LEVEL.match(line)
            if m:
                levels.append(len(m.group(1)))
    shift = max(0, 3 - min(levels)) if levels else 0

    out, in_fence = [], False
    for line in content:
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            out.append(line)
            continue
        m = None if in_fence else LEVEL.match(line)
        if m:
            new = min(6, len(m.group(1)) + shift)
            out.append("#" * new + line[len(m.group(1)):])
        else:
            out.append(line)
    return f"## {anchor}\n\n" + "\n".join(out).strip() + "\n"


def closure(names, root: Path):
    """Union closure over source layers: [(name, source_body)] — the named
    skills in given order, then their declared deps breadth-first, each once."""
    order, seen, queue = [], set(), list(names)
    while queue:
        n = queue.pop(0)
        if n in seen:
            continue
        seen.add(n)
        path = root / n / "SKILL.md"
        if not path.is_file():
            raise SystemExit(f"no SKILL.md under {root} for: {n}")
        src, deps = split_region(body_of(path.read_text()))
        order.append((n, src.rstrip()))
        queue.extend(deps)
    return order


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skills", default="",
                    help="comma-separated skills to inline after the operation; overlap is "
                         "fine — the payload is normalized to the deduplicated union "
                         "closure, so a skill already inside another's closure is emitted "
                         "once")
    ap.add_argument("--operation-file", required=True)
    ap.add_argument("--skills-root", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    root = Path(a.skills_root).expanduser().resolve()
    op = Path(a.operation_file).expanduser().read_text().rstrip()
    names = list(dict.fromkeys(s for s in a.skills.split(",") if s))
    units = closure(names, root)

    parts = [op]
    if units:
        parts.append("\n\n---\n\n# Inlined skills (each a `## section` below)\n")
    for n, src in units:
        parts.append(section(n, src.replace(SKILL_DIR_VAR, str(root / n))))

    payload = "\n".join(parts) + "\n"
    if SKILL_DIR_VAR in payload:
        lines = [i for i, ln in enumerate(payload.splitlines(), 1) if SKILL_DIR_VAR in ln]
        raise SystemExit(
            f"refusing to emit: unresolved {SKILL_DIR_VAR} in payload (line(s) {lines}) — "
            "spawns have no dispatcher to bind it; resolve the operation file at normalize time")
    Path(a.out).expanduser().write_text(payload)
    print(f"flattened {len(units)} unit(s) -> {a.out}" +
          ("\n  " + "\n  ".join(n for n, _ in units) if units else ""))


if __name__ == "__main__":
    main()
