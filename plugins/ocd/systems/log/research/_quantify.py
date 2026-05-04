"""Adoption-table quantification for consolidated research trees.

Walks a consolidated markdown's section tree, finds branching points
(any heading with two or more direct heading children), and computes
adoption counts for each child branch by querying samples that exhibit
each branch's chain key.

Counts come from samples, not from the consolidated. The consolidated
provides the categorization shape; samples provide the evidence. The
denominator for coverage is "samples exhibiting the parent chain" —
applicability-aware, so a 20-sample role doesn't get diluted by 84
samples that don't have the role at all.

Idempotent — re-running with updated sample counts replaces existing
tables between sentinel comments rather than duplicating.

The methodology defers quantification to a final pass (run after the
qualitative tree converges), so this module produces output, not
opinions; it does not modify the tree shape.
"""

from dataclasses import dataclass
from pathlib import Path

from ._sample_tools import (
    CHAIN_SEPARATOR,
    Section,
    count_sections,
    heading_text,
    parse_headings,
    serialize,
)


ADOPTION_START = "<!-- adoption-table -->"
ADOPTION_END = "<!-- /adoption-table -->"
SAMPLE_ROOT = "Sample"


@dataclass
class BranchAdoption:
    """One child branch's adoption count under its parent.

    - `name` — the branch's heading text
    - `chain` — full chain key from `Sample` root to this branch
    - `count` — samples exhibiting this exact chain
    - `parent_total` — samples exhibiting the parent chain (denominator)
    """

    name: str
    chain: str
    count: int
    parent_total: int

    @property
    def coverage(self) -> float:
        return (self.count / self.parent_total * 100) if self.parent_total else 0.0


@dataclass
class BranchPoint:
    """One branching point in the consolidated — a section with 2+ heading children of the same level."""

    parent_chain: str
    parent_total: int
    parent_level: int
    branches: list[BranchAdoption]


def find_branch_points(
    consolidated_path: Path, samples_dir: Path
) -> list[BranchPoint]:
    """Walk the consolidated and identify every branching point with sample counts.

    A branching point is any section with two or more direct heading
    children at the same level. Single-child sections get no adoption
    table — there's nothing to compare.

    The walk descends below `# Sample` (level-1 root). Counts come from
    `count_sections(samples_dir)`, which builds chain keys with the same
    `CHAIN_SEPARATOR` convention.
    """
    consolidated = parse_headings(consolidated_path)
    sample_counts = count_sections(samples_dir)

    samples_root = next(
        (
            c
            for c in consolidated.children
            if c.level == 1 and heading_text(c.heading_line) == SAMPLE_ROOT
        ),
        None,
    )
    if samples_root is None:
        return []

    results: list[BranchPoint] = []

    def walk(section: Section, chain: list[str]) -> None:
        if len(section.children) >= 2:
            parent_chain = CHAIN_SEPARATOR.join(chain) if chain else SAMPLE_ROOT
            parent_total = (
                len(sample_counts.get(parent_chain, []))
                if chain
                else _total_samples(samples_dir)
            )
            branches: list[BranchAdoption] = []
            for child in section.children:
                child_text = heading_text(child.heading_line)
                child_chain = CHAIN_SEPARATOR.join([*chain, child_text]) if chain else f"{SAMPLE_ROOT}{CHAIN_SEPARATOR}{child_text}"
                count = len(sample_counts.get(child_chain, []))
                branches.append(
                    BranchAdoption(
                        name=child_text,
                        chain=child_chain,
                        count=count,
                        parent_total=parent_total,
                    )
                )
            branches.sort(key=lambda b: (-b.count, b.name))
            results.append(
                BranchPoint(
                    parent_chain=parent_chain,
                    parent_total=parent_total,
                    parent_level=section.level,
                    branches=branches,
                )
            )

        for child in section.children:
            child_text = heading_text(child.heading_line)
            walk(child, [*chain, child_text] if chain else [SAMPLE_ROOT, child_text])

    # Seed the walk inside the `# Sample` root — chain stays empty until we descend.
    for top in samples_root.children:
        walk(top, [SAMPLE_ROOT, heading_text(top.heading_line)])

    return results


def _total_samples(samples_dir: Path) -> int:
    """Total non-underscore `.md` files in the samples dir — corpus denominator."""
    return len([p for p in samples_dir.glob("*.md") if not p.name.startswith("_")])


def render_table(branch_point: BranchPoint) -> str:
    """Render one branching point's adoption as a fenced markdown block.

    Wrapped in `<!-- adoption-table -->` ... `<!-- /adoption-table -->`
    sentinels so re-running the quantifier can replace the block without
    parsing markdown.
    """
    name_width = max(len("Path"), max(len(b.name) for b in branch_point.branches))
    header = f"| {'Path'.ljust(name_width)} | Count | Coverage |"
    divider = f"| {'-' * name_width} | ----: | -------: |"
    rows = [
        f"| {b.name.ljust(name_width)} | {b.count:5d} | {b.coverage:6.0f}% |"
        for b in branch_point.branches
    ]
    body = "\n".join([header, divider, *rows])
    return (
        f"{ADOPTION_START}\n"
        f"\n"
        f"Adoption — {branch_point.parent_total} samples exhibit `{branch_point.parent_chain}`.\n"
        f"\n"
        f"{body}\n"
        f"\n"
        f"{ADOPTION_END}\n"
    )


def write_tables(consolidated_path: Path, samples_dir: Path) -> int:
    """Insert or replace adoption tables in the consolidated, in place.

    For each branching point, the rendered table is appended to the
    parent section's `direct_content` — the body between the parent
    heading and its first child. Re-running detects existing sentinel
    blocks and replaces them.

    Returns the number of tables written.
    """
    branch_points = find_branch_points(consolidated_path, samples_dir)
    if not branch_points:
        return 0

    consolidated = parse_headings(consolidated_path)

    samples_root = next(
        (
            c
            for c in consolidated.children
            if c.level == 1 and heading_text(c.heading_line) == SAMPLE_ROOT
        ),
        None,
    )
    if samples_root is None:
        return 0

    chain_to_branch_point = {bp.parent_chain: bp for bp in branch_points}
    written = 0

    def visit(section: Section, chain: list[str]) -> None:
        nonlocal written
        if chain:
            chain_key = CHAIN_SEPARATOR.join(chain)
            bp = chain_to_branch_point.get(chain_key)
            if bp is not None:
                section.direct_content = _replace_or_append(
                    section.direct_content, render_table(bp)
                )
                written += 1
        for child in section.children:
            child_text = heading_text(child.heading_line)
            visit(child, [*chain, child_text] if chain else [SAMPLE_ROOT, child_text])

    for top in samples_root.children:
        visit(top, [SAMPLE_ROOT, heading_text(top.heading_line)])

    consolidated_path.write_text(serialize(consolidated), encoding="utf-8")
    return written


def _replace_or_append(content: str, table: str) -> str:
    """Replace any existing adoption table block, or append before next section.

    Sentinels: `<!-- adoption-table -->` ... `<!-- /adoption-table -->`.
    The table is placed inside `direct_content` — the area between a
    parent heading and its first child heading.
    """
    start = content.find(ADOPTION_START)
    end = content.find(ADOPTION_END)
    if start != -1 and end != -1 and end > start:
        end_full = end + len(ADOPTION_END)
        # Strip the trailing newline of the existing block so we don't
        # accumulate blank lines on every re-run.
        if end_full < len(content) and content[end_full] == "\n":
            end_full += 1
        return content[:start] + table + content[end_full:]

    # Append at the end of direct_content. Ensure a blank line separator.
    if content and not content.endswith("\n\n"):
        if content.endswith("\n"):
            content += "\n"
        else:
            content += "\n\n"
    return content + table
