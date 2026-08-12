#!/usr/bin/env python3
"""Assemble the flattened instruction payload: the normalized operation file
plus the named skills' bodies, concatenated.

Skills arrive pre-materialized: a SKILL.md's flatten region (see
skill-authoring/scripts/flatten_skills.py) already carries the deduplicated
transitive closure of its declared dependencies, so assembly is concatenation —
no reference discovery, no recursive expansion. Each named skill is emitted
once as a `## <name>` section, its headings demoted (fence-aware) so nothing
in a body collides with the sibling section anchors, and `${CLAUDE_SKILL_DIR}`
substituted with that skill's own folder — the spawns reading the payload have
no dispatcher to bind it, and a payload where the variable survives anywhere
is refused. The operation references an inlined skill by bare name or by its
`## <name>` anchor.

  flatten.py --skills skill-authoring,reauthor --operation-file op.md \
             --skills-root ~/.claude/skills --out instruction.md
"""
import argparse
import re
from pathlib import Path

# the dispatcher-resolved skill-dir variable; spawns reading the payload can't bind it
SKILL_DIR_VAR = "${CLAUDE_SKILL_DIR}"

LEVEL = re.compile(r'^(#{1,6})(\s)')


def body_of(text: str) -> str:
    """Strip YAML frontmatter if present; return the markdown body."""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[text.find("\n", end + 1) + 1:].lstrip("\n")
    return text


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skills", default="",
                    help="comma-separated skills to inline after the operation, each a "
                         "folder under --skills-root whose SKILL.md is emitted verbatim "
                         "(pre-materialized; no reference discovery)")
    ap.add_argument("--operation-file", required=True)
    ap.add_argument("--skills-root", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    root = Path(a.skills_root).expanduser().resolve()
    op = Path(a.operation_file).expanduser().read_text().rstrip()
    names = list(dict.fromkeys(s for s in a.skills.split(",") if s))
    missing = [n for n in names if not (root / n / "SKILL.md").is_file()]
    if missing:
        raise SystemExit(f"no SKILL.md under {root} for: {', '.join(missing)}")

    parts = [op]
    if names:
        parts.append("\n\n---\n\n# Inlined skills (each a `## section` below)\n")
    for n in names:
        body = body_of((root / n / "SKILL.md").read_text()).rstrip()
        parts.append(section(n, body.replace(SKILL_DIR_VAR, str(root / n))))

    payload = "\n".join(parts) + "\n"
    if SKILL_DIR_VAR in payload:
        lines = [i for i, ln in enumerate(payload.splitlines(), 1) if SKILL_DIR_VAR in ln]
        raise SystemExit(
            f"refusing to emit: unresolved {SKILL_DIR_VAR} in payload (line(s) {lines}) — "
            "spawns have no dispatcher to bind it; resolve the operation file at normalize time")
    Path(a.out).expanduser().write_text(payload)
    print(f"flattened {len(names)} skill(s) -> {a.out}" +
          ("\n  " + "\n  ".join(names) if names else ""))


if __name__ == "__main__":
    main()
