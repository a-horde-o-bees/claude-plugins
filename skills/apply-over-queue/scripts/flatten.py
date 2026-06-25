#!/usr/bin/env python3
"""Compile a flattened, deduplicated instruction payload from a set of skills.

Resolves the reference graph depth-first (visited-set → dedup + cycle-safety) over
two kinds of unit:
  - **skills** — `/skill-name` references, resolved against the skills root.
  - **components** — `.md` files a body references that ACTUALLY EXIST in the owning
    skill's folder (`Call: _verb.md`, `criteria.md`, `extraction-patterns.md`, …).
    Existence-gating is deliberate: it catches real components and silently skips
    syntax examples (e.g. PFN's illustrative `Call: _file.md`, which has no such file).

Each unit is emitted once as a `## <anchor>` section (skill → `name`; component →
`skill/relpath`), its own headings demoted one level (fence-aware) so they nest as
`###`, and every reference rewritten to `Call: ## <anchor>` so the document is
self-contained. Non-`.md` assets (scripts, templates) are left as runtime file refs.

  flatten.py --skills skill-authoring,reauthor --operation-file op.md \
             --skills-root ~/.claude/skills --out instruction.md
"""
import argparse
import re
from pathlib import Path

# /skill-name token, optional skill:/Call: prefix, optional backticks
SKILLREF = re.compile(r'(?:(?:skill|Call)\s*:\s*)?`?/([a-z][a-z0-9][a-z0-9-]*)`?')
# a relative .md path, optional skill:/Call: prefix, optional backticks
MDREF = re.compile(r'(?:(?:skill|Call)\s*:\s*)?`?([\w][\w./-]*\.md)`?')
HEADING = re.compile(r'^#{1,6}\s')
# strict /skill discovery for the operation file: the /name must NOT sit inside a path
# (negative lookbehind on a word char or slash), so a concrete file path like
# `.../skills/transcripts/x.py` never mis-discovers the `transcripts` skill. A leading
# backtick / space / `(` is fine; `skills/transcripts` is not.
DISCOVER = re.compile(r'(?<![\w/])/([a-z][a-z0-9][a-z0-9-]*)')
# the same path-guarded /name token, optionally backtick-wrapped, for REWRITING a ref to an
# anchor link — consumes the backticks (so the result is a live link, not inline code), leaves
# any preceding Call:/Apply: verb. The `in included_skills` check is the final guard.
REWRITE = re.compile(r'(?<![\w/])`?/([a-z][a-z0-9][a-z0-9-]*)`?')


def body_of(text: str) -> str:
    """Strip YAML frontmatter if present; return the markdown body."""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[text.find("\n", end + 1) + 1:].lstrip("\n")
    return text


def components_in(body: str, folder: Path):
    """Existing .md files (relative to folder) this body references — never SKILL.md."""
    out = []
    for ref in dict.fromkeys(MDREF.findall(body)):       # ordered, deduped
        if ref.endswith("SKILL.md"):
            continue
        if (folder / ref).is_file() and ref not in out:
            out.append(ref)
    return out


def collect(entries, root: Path, known: set):
    """Post-order list of units: (anchor, source_path, owner_skill, folder)."""
    units, seen = [], set()

    def visit_skill(name):
        if name in seen or name not in known:
            return
        seen.add(name)
        folder = root / name
        body = body_of((folder / "SKILL.md").read_text())
        for ref in SKILLREF.findall(body):
            if ref != name:
                visit_skill(ref)
        for comp in components_in(body, folder):
            visit_component(name, folder, comp)
        units.append((name, folder / "SKILL.md", name, folder))

    def visit_component(owner, folder, relpath):
        anchor = f"{owner}/{relpath[:-3]}"               # drop .md, keep subpath
        if anchor in seen:
            return
        seen.add(anchor)
        body = body_of((folder / relpath).read_text())
        for ref in SKILLREF.findall(body):
            visit_skill(ref)
        for comp in components_in(body, folder):
            visit_component(owner, folder, comp)
        units.append((anchor, folder / relpath, owner, folder))

    for e in entries:
        visit_skill(e)
    return units


def rewrite(body: str, owner: str, folder: Path, included_skills: set) -> str:
    # A /name skill ref (in the inlined set) → an anchor link to its `## name` section, leaving
    # any Call:/Apply: verb and surrounding prose untouched. So `Apply: /description-authoring`
    # becomes `Apply: [description-authoring](#description-authoring)`, resolving in the flat payload.
    body = REWRITE.sub(
        lambda m: f"[{m.group(1)}](#{m.group(1)})" if m.group(1) in included_skills else m.group(0), body)

    def comp_sub(m):
        ref = m.group(1)
        if not ref.endswith("SKILL.md") and (folder / ref).is_file():
            anchor = f"{owner}/{ref[:-3]}"
            return f"[{anchor}](#{anchor})"
        return m.group(0)

    return MDREF.sub(comp_sub, body)


LEVEL = re.compile(r'^(#{1,6})(\s)')


def section(anchor: str, body: str) -> str:
    """Emit a body under a unique `## <anchor>`: drop its title H1, then shift ALL its
    headings (fence-aware) so the shallowest lands at `###`. This guarantees nothing in
    a body sits at `##`, so body headings — including stray H1s in example output —
    never collide with the sibling skill/component anchors."""
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
                    help="comma-separated entry skills — OPTIONAL supplement; the operation "
                         "file's own /skill references are auto-discovered and flattened, so a "
                         "well-formed instruction needs no --skills. Use it to add a skill the "
                         "instruction does not name.")
    ap.add_argument("--operation-file", required=True)
    ap.add_argument("--skills-root", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    root = Path(a.skills_root).expanduser()
    known = {p.name for p in root.iterdir() if (p / "SKILL.md").exists()}
    op = Path(a.operation_file).expanduser().read_text().rstrip()
    # A well-formed instruction self-declares its disciplines via /skill references; discover
    # and flatten them so the instruction is self-sufficient. --skills only SUPPLEMENTS this.
    op_refs = [r for r in DISCOVER.findall(body_of(op)) if r in known]
    entries = list(dict.fromkeys([s for s in a.skills.split(",") if s] + op_refs))
    units = collect(entries, root, known)
    included_skills = {anchor for anchor, _, owner, _ in units if anchor == owner}

    parts = [rewrite(op, "", root, included_skills),
             "\n\n---\n\n# Flattened references (each call below points to a `## section`)\n"]
    for anchor, path, owner, folder in units:
        parts.append(section(anchor, rewrite(body_of(path.read_text()).rstrip(),
                                             owner, folder, included_skills)))

    Path(a.out).expanduser().write_text("\n".join(parts) + "\n")
    print(f"flattened {len(units)} units -> {a.out}\n  " + "\n  ".join(a for a, *_ in units))


if __name__ == "__main__":
    main()
