"""Markdown heading-tree analysis for research-corpus samples.

Three operations:

1. Parse a markdown file into a nested `Section` tree keyed by heading
   text, round-trip faithful with `serialize`.
2. Check structural invariants: sibling headings under a shared parent
   may not share text (raises `DuplicateHeadingError` with the two
   offending line numbers so humans can merge intent into one section).
3. Analyze a directory of samples: `count_sections` produces a coverage
   map (`chain_key -> [files]`); `consolidate_section` pulls one
   section's content across every sample that has it, so a reviewer
   can compare semantics without re-reading each file in full.

Chain keys use ` > ` as the separator: `Tests > CI` means the `CI`
heading nested directly under `Tests`. This matches how a reviewer
would say it aloud and round-trips cleanly in CSV `notes` fields.

Heading-text normalization strips leading `#` markers, trailing
closing-`#` markers (ATX-closed form), and trailing attr_list
(`{#id}`, `{.class}`) — so `## Config {#id1}` and `## Config` collide
under a single chain key `Config`, surfacing as duplicates for a
reviewer to reconcile.

Intended consumers:
- Per-corpus analysis during template deconfliction (human + agent).
- Future retrofit script that migrates samples to a master template.
- Agent observation emission during sample restructuring.

Pure-Python, dependency-free; safe to unit-test in isolation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


CHAIN_SEPARATOR = " > "


@dataclass
class Section:
    """One heading section with its direct content and child sections.

    - `heading_line` — the raw source line (e.g., `"## Transport"`); empty string for the synthetic root section that holds pre-first-heading preamble.
    - `level` — 0 for the root; 1–6 for `#` through `######`.
    - `direct_content` — every source line between this heading and the next heading of any level (preserving blank lines and trailing newlines). For the root, this is any preamble content before the first heading.
    - `children` — immediate child sections in source order.
    - `lineno` — 1-indexed line number of this heading in the source file; 0 for the synthetic root.
    """

    heading_line: str
    level: int
    direct_content: str = ""
    children: list["Section"] = field(default_factory=list)
    lineno: int = 0


class DuplicateHeadingError(Exception):
    """Raised when two sibling headings under a shared parent share text.

    `chain_key` is the full chain (`Tests > Unit`) so the reviewer knows
    which scope the collision is in. `first_lineno` / `second_lineno`
    point at the two offending heading lines for easy navigation.
    """

    def __init__(
        self,
        path: Path,
        chain_key: str,
        first_lineno: int,
        second_lineno: int,
    ) -> None:
        self.path = path
        self.chain_key = chain_key
        self.first_lineno = first_lineno
        self.second_lineno = second_lineno
        super().__init__(
            f"{path}: duplicate sibling heading {chain_key!r} at "
            f"lines {first_lineno} and {second_lineno}; merge into one "
            f"section or reword one to disambiguate"
        )


def _is_heading(line: str) -> tuple[bool, int]:
    """Return (is_heading, level). Level is 0 when not a heading.

    Follows CommonMark ATX heading rules conservatively: up to 3 leading
    spaces, 1–6 `#`, followed by space, end-of-line, or end-of-string.
    Indented by 4+ spaces is a code block, not a heading.
    """
    stripped = line.lstrip(" ")
    if len(line) - len(stripped) >= 4:
        return False, 0
    if not stripped.startswith("#"):
        return False, 0
    i = 0
    while i < len(stripped) and i < 6 and stripped[i] == "#":
        i += 1
    if i < 1 or i > 6:
        return False, 0
    rest = stripped[i:]
    if rest == "" or rest == "\n" or rest.startswith(" ") or rest.startswith("\t"):
        return True, i
    return False, 0


def heading_text(heading_line: str) -> str:
    """Canonical text for a heading line — used as a chain-key component.

    Strips leading `#` markers, trailing closing-`#` markers (ATX-closed
    headings), trailing attr_list (`{#id}` / `{.class}`), and surrounding
    whitespace. Other inline markdown (bold, italic, links) is kept as
    literal text — treating it as source characters rather than parsing
    semantics.
    """
    text = heading_line.lstrip(" \t").lstrip("#").lstrip(" \t").rstrip()

    # Strip trailing closing-# markers if preceded by whitespace.
    j = len(text)
    while j > 0 and text[j - 1] == "#":
        j -= 1
    if 0 < j < len(text) and text[j - 1] in (" ", "\t"):
        text = text[:j].rstrip()

    # Strip trailing attr_list — `{ ... }` preceded by whitespace.
    if text.endswith("}"):
        depth = 0
        for idx in range(len(text) - 1, -1, -1):
            c = text[idx]
            if c == "}":
                depth += 1
            elif c == "{":
                depth -= 1
                if depth == 0:
                    if idx == 0 or text[idx - 1] in (" ", "\t"):
                        text = text[:idx].rstrip()
                    break

    return text


def parse_headings(path: Path) -> Section:
    """Parse a markdown file into a nested `Section` tree.

    The synthetic root holds pre-first-heading content in its
    `direct_content`; each ATX heading becomes a child Section under
    the most recent ancestor of strictly-lower level.
    """
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)

    root = Section(
        heading_line="",
        level=0,
        direct_content="",
        children=[],
        lineno=0,
    )
    stack: list[Section] = [root]

    for idx, line in enumerate(lines, start=1):
        is_h, level = _is_heading(line)
        if is_h:
            heading_source = line.rstrip("\n").rstrip("\r")
            while stack[-1].level >= level:
                stack.pop()
            new_section = Section(
                heading_line=heading_source,
                level=level,
                direct_content="",
                children=[],
                lineno=idx,
            )
            stack[-1].children.append(new_section)
            stack.append(new_section)
        else:
            stack[-1].direct_content += line

    return root


def serialize(section: Section) -> str:
    """Round-trip a Section tree back to markdown source.

    Preserves heading lines verbatim (including attr_list, closing `#`s),
    direct content verbatim (including blank lines), and child order.
    For a tree produced by `parse_headings`, `serialize(parse_headings(p))`
    equals `p.read_text(encoding="utf-8")` — assuming the source used LF
    line endings.
    """
    parts: list[str] = []
    if section.heading_line:
        parts.append(section.heading_line + "\n")
    parts.append(section.direct_content)
    for child in section.children:
        parts.append(serialize(child))
    return "".join(parts)


def check_no_duplicate_headings(path: Path) -> None:
    """Raise `DuplicateHeadingError` if any two siblings share a chain key.

    Two headings with identical text under DIFFERENT parents are fine —
    the chain-key path (`Tests > Unit` vs `Coverage > Unit`) disambiguates.
    The rule fires only when siblings under the same parent produce the
    same chain key (same text after normalization).
    """
    root = parse_headings(path)

    def walk(section: Section, chain: list[str]) -> None:
        seen: dict[str, int] = {}  # text -> first lineno
        for child in section.children:
            text = heading_text(child.heading_line)
            if text in seen:
                chain_key = CHAIN_SEPARATOR.join(chain + [text])
                raise DuplicateHeadingError(
                    path=path,
                    chain_key=chain_key,
                    first_lineno=seen[text],
                    second_lineno=child.lineno,
                )
            seen[text] = child.lineno
            walk(child, chain + [text])

    walk(root, [])


def _iter_sample_files(sample_dir: Path) -> list[Path]:
    """Non-underscore-prefixed `.md` files directly under `sample_dir`.

    Skips meta files (`_TEMPLATE.md`, `_INDEX.md`, `_missing--*.md`,
    etc.) — the underscore convention already separates infrastructure
    from samples.
    """
    return sorted(
        p for p in sample_dir.glob("*.md")
        if p.is_file() and not p.name.startswith("_")
    )


def count_sections(sample_dir: Path) -> dict[str, list[Path]]:
    """Return `{chain_key: [files_with_that_heading]}` across a sample directory.

    Walks every non-underscore `.md` file under `sample_dir`, parses it,
    and records each heading's chain key (`Parent > Heading` form). A
    chain key appears as a dict key once; its value is the ordered list
    of files where that heading occurs. Counting is `len(files)`.

    Used for coverage analysis: which headings are near-universal vs.
    rare; which samples diverge from consensus structure.
    """
    result: dict[str, list[Path]] = {}

    for md_file in _iter_sample_files(sample_dir):
        root = parse_headings(md_file)

        def walk(section: Section, chain: list[str]) -> None:
            for child in section.children:
                text = heading_text(child.heading_line)
                new_chain = chain + [text]
                chain_key = CHAIN_SEPARATOR.join(new_chain)
                result.setdefault(chain_key, []).append(md_file)
                walk(child, new_chain)

        walk(root, [])

    return result


def consolidate_section(
    chain_key: str, sample_dir: Path
) -> list[tuple[Path, str]]:
    """Return `(file, section_source)` for every sample containing the chain.

    `chain_key` is parsed on the `CHAIN_SEPARATOR` separator (`" > "`)
    and matched against each sample's heading tree. The returned
    `section_source` is the full serialized subtree rooted at that
    heading — including its direct content and all nested children.

    Lets a reviewer compare how the same nominal section is populated
    across samples without reading each file in its entirety.
    """
    target_chain = [part.strip() for part in chain_key.split(CHAIN_SEPARATOR)]
    results: list[tuple[Path, str]] = []

    for md_file in _iter_sample_files(sample_dir):
        root = parse_headings(md_file)
        match = _find_section(root, target_chain)
        if match is not None:
            results.append((md_file, serialize(match)))

    return results


def _find_section(
    section: Section, remaining_chain: list[str]
) -> Section | None:
    """Descend `section`'s children matching `remaining_chain`; return the terminal node or None."""
    if not remaining_chain:
        return section
    head_target, *rest = remaining_chain
    for child in section.children:
        if heading_text(child.heading_line) == head_target:
            return _find_section(child, rest)
    return None
