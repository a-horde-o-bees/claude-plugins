"""Compare a sample's heading tree against a template's, surface outliers and order violations.

Three operations:

1. `compare_to_template` — diff one sample against one template; return
   a `ComplianceReport` listing outlier headings (in sample, not in
   template), missing headings (in template, not in sample), and
   out-of-order top-level sections.
2. `compliance_summary` — aggregate per-sample reports across a samples
   directory; surface which outlier chain keys recur (canonicalization
   candidates) and which template chain keys are universally absent
   (template-revision candidates).
3. `is_placeholder` — recognize the `<placeholder>` heading convention
   that marks open-enumeration sections in templates. A heading whose
   text is wrapped in literal angle brackets (`<host name>`) declares
   that any sub-heading name is accepted at that position, so the
   compliance walker does not flag samples' content-driven headings as
   outliers.

The heading tree is the single source of truth — no frontmatter shape
declarations are read or required. Templates declare canonical
sub-purposes via the `###` headings under each `##` section, and
declare open-enumeration via the `<placeholder>` convention. Compliance
emerges from heading-tree diff.

Pure-Python, dependency-free; safe to unit-test against synthetic
fixtures.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from ._sample_tools import (
    CHAIN_SEPARATOR,
    Section,
    heading_text,
    parse_headings,
)


PLACEHOLDER_PATTERN = re.compile(r"^<[^>]+>$")


@dataclass
class HeadingMismatch:
    """One sample heading that has no corresponding template heading.

    - `chain_key` — the full chain (e.g. `Sample > Identification > popularity`).
    - `lineno` — 1-indexed line number of the offending heading in the sample.
    - `content_snippet` — first ~200 characters of the heading's direct
      content; helps the reviewer see what content the sample placed
      under this non-canonical heading without re-opening the file.
    """

    chain_key: str
    lineno: int
    content_snippet: str


@dataclass
class OrderViolation:
    """A section that appears out of order relative to the template.

    - `heading` — the section's heading text (e.g. `Distribution`).
    - `expected_after` — the heading that the template places this
      section after (e.g. `Transport`); `""` when this should be first.
    - `appears_after` — the heading that immediately precedes it in the
      sample (the offending neighbor).
    """

    heading: str
    expected_after: str
    appears_after: str


@dataclass
class ComplianceReport:
    """Per-sample compliance against a template."""

    sample_path: Path
    template_path: Path
    outliers: list[HeadingMismatch]
    missing: list[str]
    out_of_order: list[OrderViolation]

    @property
    def is_clean(self) -> bool:
        """No outliers, no order violations. `missing` is informational only."""
        return not self.outliers and not self.out_of_order


def is_placeholder(text: str) -> bool:
    """Whether a heading text declares an open-enumeration slot.

    Convention: heading text wrapped in literal angle brackets
    (`<host name>`, `<endpoint>`) marks the slot as open-enumeration.
    The placeholder itself is not a canonical heading; its parent is
    flagged as accepting any child heading name in samples.

    The angle-bracket convention does not collide with markdown
    rendering — markdown's special-character rule already requires
    angle brackets in prose to be inside backticks; using them in a
    heading is an explicit signal, not accidental.
    """
    return bool(PLACEHOLDER_PATTERN.match(text.strip()))


def _build_template_index(template_root: Section) -> tuple[set[str], set[str], list[str]]:
    """Walk the template tree; return (canonical_chains, open_parents, top_order).

    - `canonical_chains` — every chain key formed by joining non-placeholder
      heading texts from root to a child. Chains containing a placeholder
      anywhere in their path are excluded.
    - `open_parents` — chain keys (parent paths) whose children include
      at least one placeholder heading. Children of these parents in
      samples are accepted regardless of name.
    - `top_order` — the ordered list of level-2 section names under the
      `# Sample` wrapper, used for top-level order checking.
    """
    canonical: set[str] = set()
    open_parents: set[str] = set()
    top_order: list[str] = []

    def walk(section: Section, chain: list[str]) -> None:
        chain_str = CHAIN_SEPARATOR.join(chain) if chain else ""
        # Detect placeholder children of this node.
        for child in section.children:
            if is_placeholder(heading_text(child.heading_line)):
                open_parents.add(chain_str)
                break
        for child in section.children:
            text = heading_text(child.heading_line)
            if is_placeholder(text):
                continue
            new_chain = chain + [text]
            chain_key = CHAIN_SEPARATOR.join(new_chain)
            canonical.add(chain_key)
            # Capture top-level section order (children of `# Sample`).
            if len(chain) == 1 and chain[0] == "Sample":
                top_order.append(text)
            walk(child, new_chain)

    walk(template_root, [])
    return canonical, open_parents, top_order


def _walk_sample(sample_root: Section) -> tuple[list[tuple[str, int, str]], list[str]]:
    """Walk the sample tree; return (every_heading, top_section_order).

    - `every_heading` — list of `(chain_key, lineno, content_snippet)`
      for every heading reachable from the sample root.
    - `top_section_order` — ordered level-2 section names under the
      `# Sample` wrapper.
    """
    every_heading: list[tuple[str, int, str]] = []
    top_order: list[str] = []

    def walk(section: Section, chain: list[str]) -> None:
        for child in section.children:
            text = heading_text(child.heading_line)
            new_chain = chain + [text]
            chain_key = CHAIN_SEPARATOR.join(new_chain)
            snippet = (child.direct_content or "").strip().split("\n", 1)[0][:200]
            every_heading.append((chain_key, child.lineno, snippet))
            if len(chain) == 1 and chain[0] == "Sample":
                top_order.append(text)
            walk(child, new_chain)

    walk(sample_root, [])
    return every_heading, top_order


def _check_order(sample_seq: list[str], template_seq: list[str]) -> list[OrderViolation]:
    """Return order violations: a sample heading appears before a template-earlier sibling.

    The check ignores headings not present in `template_seq` (they're
    handled as outliers separately). Among the template-known headings
    in the sample, their relative order should match the template.
    """
    template_pos = {h: i for i, h in enumerate(template_seq)}
    violations: list[OrderViolation] = []
    last_pos = -1
    last_heading = ""
    for heading in sample_seq:
        if heading not in template_pos:
            continue
        pos = template_pos[heading]
        if pos < last_pos:
            expected_after = template_seq[pos - 1] if pos > 0 else ""
            violations.append(
                OrderViolation(
                    heading=heading,
                    expected_after=expected_after,
                    appears_after=last_heading,
                )
            )
        last_pos = max(last_pos, pos)
        last_heading = heading
    return violations


def compare_to_template(sample_path: Path, template_path: Path) -> ComplianceReport:
    """Diff one sample against one template; return a ComplianceReport.

    Outliers — sample headings whose chain key is not in the template's
    canonical-chain set AND whose parent chain is not open-enumeration.

    Missing — template chain keys not present in the sample. Sections
    are optional, so missing entries are informational; the report
    consumer decides which (if any) constitute violations.

    Order violations — top-level sections (`## ...` under `# Sample`)
    that appear in a different order than the template. Sub-purpose
    order within sections is not checked at this level — if needed,
    extend the function.
    """
    template_root = parse_headings(template_path)
    sample_root = parse_headings(sample_path)
    canonical, open_parents, template_top = _build_template_index(template_root)
    sample_headings, sample_top = _walk_sample(sample_root)

    outliers: list[HeadingMismatch] = []
    sample_chains: set[str] = set()
    for chain_key, lineno, snippet in sample_headings:
        sample_chains.add(chain_key)
        if chain_key in canonical:
            continue
        # Walk up the chain checking if any ancestor is an open-enumeration parent.
        parts = chain_key.split(CHAIN_SEPARATOR)
        if any(
            CHAIN_SEPARATOR.join(parts[:i]) in open_parents
            for i in range(1, len(parts))
        ):
            continue
        outliers.append(
            HeadingMismatch(chain_key=chain_key, lineno=lineno, content_snippet=snippet)
        )

    missing = sorted(canonical - sample_chains)
    out_of_order = _check_order(sample_top, template_top)

    return ComplianceReport(
        sample_path=sample_path,
        template_path=template_path,
        outliers=outliers,
        missing=missing,
        out_of_order=out_of_order,
    )


@dataclass
class CorpusCompliance:
    """Aggregate compliance across a samples directory.

    - `reports` — per-sample reports, one per non-meta `.md` file.
    - `outlier_counts` — `{chain_key: [files_where_it_appears]}` so
      reviewers can see which outlier names recur (canonicalization
      candidates).
    - `missing_counts` — `{chain_key: count}` for template chain keys
      absent across the corpus; high counts indicate template revisions
      worth considering.
    """

    reports: list[ComplianceReport]
    outlier_counts: dict[str, list[Path]]
    missing_counts: dict[str, int]


def compliance_summary(samples_dir: Path, template_path: Path) -> CorpusCompliance:
    """Run `compare_to_template` for every non-meta `.md` file under `samples_dir`."""
    sample_files = sorted(
        p for p in samples_dir.glob("*.md")
        if p.is_file() and not p.name.startswith("_")
    )
    reports: list[ComplianceReport] = []
    outlier_counts: dict[str, list[Path]] = {}
    missing_counts: dict[str, int] = {}
    for sample_path in sample_files:
        report = compare_to_template(sample_path, template_path)
        reports.append(report)
        for outlier in report.outliers:
            outlier_counts.setdefault(outlier.chain_key, []).append(sample_path)
        for missing in report.missing:
            missing_counts[missing] = missing_counts.get(missing, 0) + 1
    return CorpusCompliance(
        reports=reports,
        outlier_counts=outlier_counts,
        missing_counts=missing_counts,
    )
