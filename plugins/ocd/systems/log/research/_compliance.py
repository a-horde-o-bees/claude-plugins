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
    """A heading that appears out of order relative to its template siblings.

    - `chain_key` — the parent chain under which the violation occurs
      (e.g. `Sample > Identification`); empty string when the violation
      is at the synthetic-root level.
    - `heading` — the offending heading's text (e.g. `stars`).
    - `expected_after` — the heading that the template places this
      heading after (e.g. `url`); `""` when this should be first among
      its siblings.
    - `appears_after` — the heading that immediately precedes it in the
      sample (the offending neighbor).
    """

    chain_key: str
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


def _build_template_index(template_root: Section) -> tuple[set[str], set[str]]:
    """Walk the template tree; return (canonical_chains, open_parents).

    - `canonical_chains` — every chain key formed by joining non-placeholder
      heading texts from root to a child. Chains containing a placeholder
      anywhere in their path are excluded.
    - `open_parents` — chain keys (parent paths) whose children include
      at least one placeholder heading. Children of these parents in
      samples are accepted regardless of name.
    """
    canonical: set[str] = set()
    open_parents: set[str] = set()

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
            walk(child, new_chain)

    walk(template_root, [])
    return canonical, open_parents


def _walk_sample(sample_root: Section) -> list[tuple[str, int, str]]:
    """Walk the sample tree; return list of `(chain_key, lineno, content_snippet)` for every heading."""
    every_heading: list[tuple[str, int, str]] = []

    def walk(section: Section, chain: list[str]) -> None:
        for child in section.children:
            text = heading_text(child.heading_line)
            new_chain = chain + [text]
            chain_key = CHAIN_SEPARATOR.join(new_chain)
            snippet = (child.direct_content or "").strip().split("\n", 1)[0][:200]
            every_heading.append((chain_key, child.lineno, snippet))
            walk(child, new_chain)

    walk(sample_root, [])
    return every_heading


def _walk_order(
    template_section: Section,
    sample_section: Section,
    chain: list[str],
) -> list[OrderViolation]:
    """Walk template + sample trees in parallel; report order violations at every depth.

    At each level, the sample's heading order should be a subsequence of
    the template's order. Headings in the sample that aren't in the
    template at this level are skipped (they're flagged separately as
    outliers). Recursion continues into children that exist in both
    trees, so a swap deep in the hierarchy (`### stars` before `### url`
    under `## Identification`) is flagged just like a swap at the top
    level.

    Sections whose template declares a `<placeholder>` child are
    open-enumeration — their children are content-driven (e.g. host
    names ordered by README). Order checks are skipped for those
    sections; their children may appear in any order.
    """
    violations: list[OrderViolation] = []

    has_placeholder = any(
        is_placeholder(heading_text(c.heading_line))
        for c in template_section.children
    )
    if not has_placeholder:
        template_seq = [
            heading_text(c.heading_line) for c in template_section.children
        ]
        sample_seq = [
            heading_text(c.heading_line) for c in sample_section.children
        ]
        chain_key = CHAIN_SEPARATOR.join(chain) if chain else ""
        violations.extend(_check_order_at_level(sample_seq, template_seq, chain_key))

    template_by_name = {
        heading_text(c.heading_line): c for c in template_section.children
    }
    for sample_child in sample_section.children:
        name = heading_text(sample_child.heading_line)
        template_child = template_by_name.get(name)
        if template_child is not None:
            violations.extend(
                _walk_order(template_child, sample_child, chain + [name])
            )

    return violations


def _check_order_at_level(
    sample_seq: list[str],
    template_seq: list[str],
    chain_key: str,
) -> list[OrderViolation]:
    """Order violations at one level of the heading tree.

    Headings not in `template_seq` are ignored (handled as outliers
    separately). Among the template-known headings in `sample_seq`,
    their relative order should match the template.
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
                    chain_key=chain_key,
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

    Order violations — at every depth in the heading tree, the sample's
    heading order must be a subsequence of the template's order under
    the corresponding parent. A swap of `### stars` and `### url` under
    `## Identification` is flagged with the same machinery as a swap of
    `## Identification` and `## Language and runtime` at the top level.
    Children of open-enumeration parents (e.g. `## Host integrations`)
    are skipped — their order is content-driven.
    """
    template_root = parse_headings(template_path)
    sample_root = parse_headings(sample_path)
    canonical, open_parents = _build_template_index(template_root)
    sample_headings = _walk_sample(sample_root)

    outliers: list[HeadingMismatch] = []
    sample_chains: set[str] = set()
    for chain_key, lineno, snippet in sample_headings:
        sample_chains.add(chain_key)
        if chain_key in canonical:
            continue
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
    out_of_order = _walk_order(template_root, sample_root, [])

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
    - `consolidated_report` — `_CONSOLIDATED.md`'s report when the file
      exists in `samples_dir`; `None` when absent. `_CONSOLIDATED.md`
      mirrors `_TEMPLATE.md` heading-for-heading (heading-by-heading
      accumulation of supporting samples + notes), so it carries the
      same compliance contract as samples but is a different artifact
      kind (synthesis vs evidence) — kept separate from sample-aggregate
      counts so reviewers see its status independently.
    - `outlier_counts` — `{chain_key: [files_where_it_appears]}` so
      reviewers can see which outlier names recur (canonicalization
      candidates). Aggregates samples only, not `_CONSOLIDATED.md`.
    - `missing_counts` — `{chain_key: count}` for template chain keys
      absent across the corpus; high counts indicate template revisions
      worth considering. Aggregates samples only.
    """

    reports: list[ComplianceReport]
    consolidated_report: ComplianceReport | None
    outlier_counts: dict[str, list[Path]]
    missing_counts: dict[str, int]


def compliance_summary(samples_dir: Path, template_path: Path) -> CorpusCompliance:
    """Run `compare_to_template` for every non-meta `.md` file under `samples_dir`.

    `_CONSOLIDATED.md`, when present, is checked against the template
    using the same machinery and surfaced as `consolidated_report`.
    Other `_*.md` files (the template itself, indices, archives) are
    skipped.
    """
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

    consolidated_path = samples_dir / "_CONSOLIDATED.md"
    consolidated_report = (
        compare_to_template(consolidated_path, template_path)
        if consolidated_path.is_file() else None
    )

    return CorpusCompliance(
        reports=reports,
        consolidated_report=consolidated_report,
        outlier_counts=outlier_counts,
        missing_counts=missing_counts,
    )
