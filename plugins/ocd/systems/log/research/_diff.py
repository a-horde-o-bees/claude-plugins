"""Diff between sample heading trees and the running `_CONSOLIDATED*.md`.

Under the breadth-then-depth methodology, the consolidated document is
the evolving single-source-of-truth that grows from corpus evidence —
not a fixed template against which samples are checked. This module
expresses that comparison:

- Chain keys present in samples but missing from the consolidated are
  **growth candidates** — observations the corpus carries that the tree
  has not yet absorbed
- Chain keys in the consolidated with zero sample support are
  **pruning candidates** — branches the tree has but no sample exemplifies
- Chain keys present in both are **well-supported** — the corpus
  validates the consolidated's structure at that path

Inputs are paths. Outputs are dataclasses suitable for CLI formatting
or programmatic consumption.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ._sample_tools import (
    CHAIN_SEPARATOR,
    Section,
    heading_text,
    parse_headings,
)


@dataclass
class SampleDiff:
    """Per-sample chain-key diff against the consolidated.

    - `sample_path` — sample file analyzed
    - `sample_chains` — every chain key reachable from the sample's root
    - `unique_to_sample` — chains the sample has, the consolidated lacks
    - `common` — chains in both
    """

    sample_path: Path
    sample_chains: set[str]
    unique_to_sample: set[str]
    common: set[str]


@dataclass
class CorpusDiff:
    """Aggregate diff across the samples directory vs the consolidated.

    - `consolidated_path` — consolidated file the diff is against
    - `sample_count` — number of `<entity>.md` files compared
    - `consolidated_chains` — chain keys reachable in the consolidated
    - `chain_to_files` — `{chain_key: sorted_files_with_that_chain}` across samples

    Derived properties classify each chain by where it appears.
    """

    consolidated_path: Path
    sample_count: int
    consolidated_chains: set[str]
    chain_to_files: dict[str, list[Path]]

    @property
    def growth_candidates(self) -> dict[str, list[Path]]:
        """Chain keys in samples not in consolidated — corpus says it; tree should grow."""
        return {
            c: f for c, f in self.chain_to_files.items()
            if c not in self.consolidated_chains
        }

    @property
    def pruning_candidates(self) -> list[str]:
        """Chain keys in consolidated with zero sample support — branches without exemplars."""
        return sorted(self.consolidated_chains - set(self.chain_to_files.keys()))

    @property
    def well_supported(self) -> dict[str, list[Path]]:
        """Chain keys in both consolidated and at least one sample."""
        return {
            c: f for c, f in self.chain_to_files.items()
            if c in self.consolidated_chains
        }


def collect_chain_keys(root: Section) -> set[str]:
    """Return every chain key reachable from `root`'s tree.

    Chain keys join heading text from the synthetic root's children
    down to each descendant. By convention samples use `# Sample` as
    their level-1, so chain keys begin with `Sample > ...`; the
    consolidated document follows the same convention so chains align
    for comparison. Same shape as `count_sections` and
    `consolidate_section` — these functions interoperate through
    matching chain-key conventions.
    """
    result: set[str] = set()

    def walk(section: Section, chain: list[str]) -> None:
        for child in section.children:
            text = heading_text(child.heading_line)
            new_chain = chain + [text]
            result.add(CHAIN_SEPARATOR.join(new_chain))
            walk(child, new_chain)

    walk(root, [])
    return result


def compare_to_consolidated(sample_path: Path, consolidated_path: Path) -> SampleDiff:
    """One sample's chain keys vs the consolidated's; set-based diff."""
    sample_root = parse_headings(sample_path)
    consolidated_root = parse_headings(consolidated_path)
    sample_chains = collect_chain_keys(sample_root)
    consolidated_chains = collect_chain_keys(consolidated_root)

    return SampleDiff(
        sample_path=sample_path,
        sample_chains=sample_chains,
        unique_to_sample=sample_chains - consolidated_chains,
        common=sample_chains & consolidated_chains,
    )


def diff_summary(samples_dir: Path, consolidated_path: Path) -> CorpusDiff:
    """Aggregate diff across the samples directory.

    Skips meta files (`_*.md` — including `_CONSOLIDATED*.md`,
    `_INDEX.md`, `_missing--*.md`). Operates only on per-entity
    `<entity>.md` files.
    """
    consolidated_root = parse_headings(consolidated_path)
    consolidated_chains = collect_chain_keys(consolidated_root)

    sample_files = sorted(
        p for p in samples_dir.glob("*.md")
        if p.is_file() and not p.name.startswith("_")
    )

    chain_to_files: dict[str, list[Path]] = {}
    for sf in sample_files:
        root = parse_headings(sf)
        for chain in collect_chain_keys(root):
            chain_to_files.setdefault(chain, []).append(sf)

    return CorpusDiff(
        consolidated_path=consolidated_path,
        sample_count=len(sample_files),
        consolidated_chains=consolidated_chains,
        chain_to_files=chain_to_files,
    )
