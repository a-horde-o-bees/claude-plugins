#!/usr/bin/env python3
"""Assemble the flattened instruction payload: the normalized operation file
plus the named skills, normalized to the deduplicated union closure.

A skill declares its dependencies as /skill-name references in its SKILL.md
source (see skill-authoring/scripts/flatten_skills.py); its materialized
flatten region carries the closure. Concatenating SKILL.mds verbatim would
duplicate any unit two named skills share — or a named skill already inside
another's closure — so assembly re-normalizes from source layers instead:
each skill's region and ## Dependencies section are stripped, its references
are read, and every unit in the union closure (named skills first, then
their references breadth-first) is emitted exactly once as a `## <name>`
section. A reference like [/x](#x) then resolves to that single copy; any
bare /x reference is linked the same way at assembly time. Fenced blocks
and inline code spans are literal text, never references.

Each unit's headings are demoted (fence-aware) so nothing collides with the
sibling section anchors, and ${CLAUDE_SKILL_DIR} is substituted with the
unit's own folder — the spawns reading the payload have no dispatcher to bind
it, and a payload where the variable survives anywhere is refused.

  flatten.py --skills skill-authoring,reauthor --operation-file op.md \
             --skills-root ~/.claude/skills --out instruction.md
"""
import argparse
import re
from pathlib import Path

# the dispatcher-resolved skill-dir variable; spawns reading the payload can't bind it
SKILL_DIR_VAR = "${CLAUDE_SKILL_DIR}"

START_RE = re.compile(r'^<!-- flatten-skills START -->\s*$')
STOP_RE = re.compile(r'^<!-- flatten-skills STOP -->\s*$')
FENCE_RE = re.compile(r'^ {0,3}(`{3,}|~{3,})(.*)$')
LEVEL = re.compile(r'^(#{1,6})(\s)')
DEPS_HEAD_RE = re.compile(r'^## Dependencies\s*$')
SPAN_RE = re.compile(r'`[^`\n]+`')
# linked form first so the bare alternative never fires inside a link;
# shape shared with flatten_skills.py so the tools agree
REF_RE = re.compile(
    r'\[/([\w][\w-]*)\]\(#([\w-]+)\)|(?<![\w./}-])/([\w][\w-]*)\b(?!/)')


def body_of(text: str) -> str:
    """Strip YAML frontmatter if present; return the markdown body."""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[text.find("\n", end + 1) + 1:].lstrip("\n")
    return text


def fence_flags(lines):
    """[bool per line]: inside (or delimiting) a fenced code block."""
    flags, fence = [], None
    for ln in lines:
        m = FENCE_RE.match(ln)
        if fence:
            flags.append(True)
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= fence[1] \
                    and not m.group(2).strip():
                fence = None
        elif m:
            fence = (m.group(1)[0], len(m.group(1)))
            flags.append(True)
        else:
            flags.append(False)
    return flags


def link_refs(line: str, targets) -> str:
    """Rewrite bare /name -> [/name](#name) for names in targets;
    code spans are blanked for matching only, so positions survive."""
    blanked = SPAN_RE.sub(lambda m: " " * len(m.group()), line)
    out, last = [], 0
    for m in REF_RE.finditer(blanked):
        name = m.group(3)
        if name and name in targets:
            out.append(line[last:m.start()])
            out.append(f"[/{name}](#{name})")
            last = m.end()
    out.append(line[last:])
    return "".join(out)


def parse(text: str, own: str, known):
    """(body, refs): the source body minus its ## Dependencies section, and
    the sibling skills its source layer references, in appearance order."""
    lines = text.split("\n")
    flags = fence_flags(lines)
    head = start = stop = None
    h2s = []
    for i, ln in enumerate(lines):
        if flags[i]:
            continue
        if START_RE.match(ln) and start is None:
            start = i
        elif STOP_RE.match(ln) and start is not None and stop is None:
            stop = i
        elif DEPS_HEAD_RE.match(ln) and head is None:
            head = i
        elif ln.startswith("## "):
            h2s.append(i)
    end = len(lines)
    if head is not None:
        after = [j for j in h2s if j > head]
        end = after[0] if after else len(lines)

    generated = range(start + 1, stop) if start is not None and stop is not None \
        else range(0)
    refs, seen = [], set()
    for i, ln in enumerate(lines):
        if flags[i] or i in generated:
            continue
        for m in REF_RE.finditer(SPAN_RE.sub(lambda s: " " * len(s.group()), ln)):
            name = m.group(1) or m.group(3)
            if name != own and name in known and name not in seen:
                seen.add(name)
                refs.append(name)

    section = range(head, end) if head is not None else generated
    body = [ln for i, ln in enumerate(lines)
            if i not in section and i not in generated
            and not (start is not None and i in (start, stop))]
    return "\n".join(body), refs


def section(anchor: str, body: str, targets) -> str:
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
    flags = fence_flags(content)

    levels = [len(m.group(1)) for line, f in zip(content, flags)
              if not f and (m := LEVEL.match(line))]
    shift = max(0, 3 - min(levels)) if levels else 0

    out = []
    for line, f in zip(content, flags):
        m = None if f else LEVEL.match(line)
        if m:
            new = min(6, len(m.group(1)) + shift)
            out.append("#" * new + line[len(m.group(1)):])
        elif f:
            out.append(line)
        else:
            out.append(link_refs(line, targets))
    return f"## {anchor}\n\n" + "\n".join(out).strip() + "\n"


def closure(names, root: Path):
    """Union closure over source layers: [(name, source_body)] — the named
    skills in given order, then their references breadth-first, each once."""
    known = {d.name for d in root.iterdir() if (d / "SKILL.md").exists()}
    order, seen, queue = [], set(), list(names)
    while queue:
        n = queue.pop(0)
        if n in seen:
            continue
        seen.add(n)
        path = root / n / "SKILL.md"
        if not path.is_file():
            raise SystemExit(f"no SKILL.md under {root} for: {n}")
        body, refs = parse(body_of(path.read_text()), n, known)
        order.append((n, body.strip()))
        queue.extend(refs)
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
    targets = {n for n, _ in units}

    parts = [op]
    if units:
        parts.append("\n\n---\n\n# Inlined skills (each a `## section` below)\n")
    for n, src in units:
        parts.append(section(n, src.replace(SKILL_DIR_VAR, str(root / n)), targets))

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
