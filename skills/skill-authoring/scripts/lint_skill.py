#!/usr/bin/env python3
"""Lint SKILL.md files against the mechanically checkable well-formedness rules.

This docstring is the source of truth for what the script enforces.

Errors (must fix):
  - frontmatter: a leading `---` block with single-line `name:` and `description:`
  - name matches the skill's directory name
  - description fits the 1536-char listing budget
  - H1 names the skill (case-insensitive)
  - the first body paragraph after the H1 is the description, verbatim
    (markdown-authoring: one owner for the summary)

Source-convention errors (skill-source-conventions spec; flatten regions
and fenced code blocks exempt throughout):
  - exactly one H1; every other heading at H2 — uniform demotion on
    flattening requires it
  - no absolute path into the skill's own folder: bundled files are
    referenced as ${CLAUDE_SKILL_DIR}/...
  - marker hygiene: a `<!-- flatten-skills ... -->`-shaped line only as a
    bare delimiter of the file's single well-formed region
  - cross-skill references compile: a reference-shaped token (`/name`
    outside fences and code spans) must name a sibling suite skill; a
    skill's own invocation surface is exempt

Warnings (judgment calls — resolve or knowingly leave):
  - deviation fields set (when_to_use, disable-model-invocation, user-invocable):
    the suite leaves these unset; deviate only as a deliberate, recorded exception
  - a resolved but unlinked reference (bare `/name`): stale — a flatten
    refresh links it to the in-file unit anchor
  - `e.g.` outside the `(e.g. ...)` form, in prose (code spans and fences exempt)

Usage: lint_skill.py <skill-dir|SKILL.md|skills-root> ...
Exits non-zero if any error.
"""
import re
import sys
from pathlib import Path

LISTING_BUDGET = 1536
DEVIATION_FIELDS = ("when_to_use", "disable-model-invocation", "user-invocable")
START_RE = re.compile(r"^<!-- flatten-skills START -->\s*$")
STOP_RE = re.compile(r"^<!-- flatten-skills STOP -->\s*$")
MARKER_RE = re.compile(r"^\s*<!--\s*flatten-skills\b")
FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
SPAN_RE = re.compile(r"`[^`\n]+`")
# linked form first so the bare alternative never fires inside a link;
# shape shared with flatten_skills.py so tool and lint agree
REF_RE = re.compile(
    r"\[/([\w][\w-]*)\]\(#([\w-]+)\)|(?<![\w./}-])/([\w][\w-]*)\b(?!/)")


def blank_code(md: str) -> str:
    """Blank out fenced blocks and code spans, preserving line structure."""
    md = re.sub(r"```.*?```", lambda m: re.sub(r"[^\n]", "", m.group(0)), md, flags=re.S)
    return re.sub(r"`[^`\n]*`", "", md)


def iter_lines(lines):
    """Yield (index, line, in_fence); fence delimiter lines count as fenced."""
    fence = None
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


def source_lines(text: str):
    """Yield (lineno, line) for unfenced source-layer lines: fenced blocks and
    the flatten region's generated content excluded, marker lines included."""
    lines = text.split("\n")
    starts, stops = [], []
    for i, ln, fenced in iter_lines(lines):
        if fenced:
            continue
        if START_RE.match(ln):
            starts.append(i)
        elif STOP_RE.match(ln):
            stops.append(i)
    region = range(starts[0] + 1, stops[0]) if len(starts) == 1 == len(stops) \
        and starts[0] < stops[0] else range(0)
    for i, ln, fenced in iter_lines(lines):
        if not fenced and i not in region:
            yield i + 1, ln


def lint_conventions(text: str, skill_dir: str, siblings, errors, warns, offset=0):
    starts = stops = h1s = 0
    for ln_no, line in source_lines(text):
        ln_no += offset
        if START_RE.match(line):
            starts += 1
            continue
        if STOP_RE.match(line):
            stops += 1
            continue
        if MARKER_RE.match(line):
            errors.append(f"line {ln_no}: stray flatten marker line")
            continue
        m = re.match(r"^(#{1,6}) ", line)
        if m:
            level = len(m.group(1))
            h1s += level == 1
            if level > 2:
                errors.append(f"line {ln_no}: H{level} heading — sections stay at H2")
        for hit in re.finditer(r"(?:/home/|~/)\S*/skills/" + re.escape(skill_dir) + r"/(\S*)", line):
            errors.append(
                f"line {ln_no}: bundled file by absolute path — use "
                f"${{CLAUDE_SKILL_DIR}}/{hit.group(1).rstrip('`)],.;:')}")
        for hit in REF_RE.finditer(SPAN_RE.sub(lambda m: " " * len(m.group()), line)):
            name = hit.group(1) or hit.group(3)
            if name == skill_dir:
                continue
            if name not in siblings:
                errors.append(f"line {ln_no}: unresolved reference /{name}")
            elif hit.group(3):
                warns.append(f"line {ln_no}: bare reference /{name} — "
                             "stale; a flatten refresh links it")
    if h1s != 1:
        errors.append(f"{h1s} H1 headings — exactly one (the skill title)")
    if starts > 1 or stops > 1 or starts != stops:
        errors.append("malformed flatten region markers")


def lint(path: Path):
    errors, warns = [], []
    text = path.read_text(encoding="utf-8")

    m = re.match(r"\A---\n(.*?)\n---\n(.*)\Z", text, re.S)
    if not m:
        return ["no frontmatter block"], warns
    fm, body = m.groups()
    fields = dict(re.findall(r"^([\w-]+):[ \t]*(.*)$", fm, re.M))
    for k, v in fields.items():
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"":
            fields[k] = v[1:-1]
    name = fields.get("name", "")
    desc = fields.get("description", "")

    skill_dir = path.resolve().parent.name
    if not name:
        errors.append("frontmatter: missing name")
    elif name != skill_dir:
        errors.append(f"frontmatter: name '{name}' != directory '{skill_dir}'")
    if not desc:
        errors.append("frontmatter: missing description")
    elif len(desc) > LISTING_BUDGET:
        errors.append(f"description exceeds listing budget ({len(desc)} > {LISTING_BUDGET})")
    for f in DEVIATION_FIELDS:
        if f in fields:
            warns.append(f"deviation field set: {f}")

    h1 = re.search(r"^# (.+)$", body, re.M)
    if not h1:
        errors.append("no H1")
    else:
        if name and h1.group(1).strip().lower() != name.lower():
            errors.append(f"H1 '{h1.group(1).strip()}' does not name the skill")
        para = re.search(r"^# .+?\n\n(.*?)(?:\n\n|\Z)", body, re.S | re.M)
        first = re.sub(r"\s*\n\s*", " ", para.group(1)).strip() if para else ""
        if desc and first != desc:
            errors.append("first paragraph is not the description verbatim")

    for ln, line in enumerate(blank_code(text).splitlines(), 1):
        for hit in re.finditer(r"e\.g\.", line):
            if not line[: hit.start()].endswith("("):
                warns.append(f"line {ln}: 'e.g.' outside '(e.g. ...)' form")

    siblings = {d.name for d in path.resolve().parent.parent.iterdir()
                if (d / "SKILL.md").exists()} if path.resolve().parent.parent.is_dir() else set()
    lint_conventions(body, skill_dir, siblings, errors, warns,
                     offset=text[: m.start(2)].count("\n"))

    return errors, warns


def main(args):
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
    tot_e = tot_w = 0
    for f in files:
        errors, warns = lint(f)
        for e in errors:
            print(f"{f}: ERROR {e}")
        for w in warns:
            print(f"{f}: warn  {w}")
        tot_e += len(errors)
        tot_w += len(warns)
    print(f"{len(files)} file(s): {tot_e} error(s), {tot_w} warning(s)")
    return 1 if tot_e else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
