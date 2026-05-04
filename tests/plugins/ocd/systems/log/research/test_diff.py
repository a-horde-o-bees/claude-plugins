"""Tests for systems.log.research._diff.

Set-based chain-key comparison between samples and the running
`_CONSOLIDATED*.md`. Uses tmp_path with synthetic markdown fixtures —
no dependency on the live research corpora.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

from systems.log.research._diff import (
    CorpusDiff,
    SampleDiff,
    collect_chain_keys,
    compare_to_consolidated,
    diff_summary,
)
from systems.log.research._sample_tools import CHAIN_SEPARATOR, parse_headings


def _write_md(directory: Path, name: str, content: str) -> Path:
    """Dedent + write a markdown fixture; return the path."""
    path = directory / name
    path.write_text(textwrap.dedent(content).lstrip("\n"), encoding="utf-8")
    return path


# ─── collect_chain_keys ──────────────────────────────────────────────────


class TestCollectChainKeys:
    def test_collects_chains_at_all_depths(self, tmp_path: Path):
        path = _write_md(tmp_path, "doc.md", """
            # Root

            ## A

            ### A1

            ### A2

            ## B

            ### B1
        """)
        root = parse_headings(path)
        chains = collect_chain_keys(root)
        assert "Root" in chains
        assert "Root" + CHAIN_SEPARATOR + "A" in chains
        assert "Root" + CHAIN_SEPARATOR + "A" + CHAIN_SEPARATOR + "A1" in chains
        assert "Root" + CHAIN_SEPARATOR + "A" + CHAIN_SEPARATOR + "A2" in chains
        assert "Root" + CHAIN_SEPARATOR + "B" in chains
        assert "Root" + CHAIN_SEPARATOR + "B" + CHAIN_SEPARATOR + "B1" in chains

    def test_includes_level_1_heading(self, tmp_path: Path):
        """Chain keys start at the synthetic-root's children — the level-1 heading appears."""
        path = _write_md(tmp_path, "doc.md", "# Sample\n\n## A\n")
        root = parse_headings(path)
        chains = collect_chain_keys(root)
        assert "Sample" in chains
        assert "Sample" + CHAIN_SEPARATOR + "A" in chains

    def test_empty_doc_returns_set_with_only_level_1(self, tmp_path: Path):
        path = _write_md(tmp_path, "empty.md", "# Root\n\nbody only, no sub-headings.\n")
        root = parse_headings(path)
        assert collect_chain_keys(root) == {"Root"}


# ─── compare_to_consolidated ─────────────────────────────────────────────


class TestCompareToConsolidated:
    def test_identifies_unique_and_common(self, tmp_path: Path):
        consolidated = _write_md(tmp_path, "_CONSOLIDATED.md", """
            # Sample

            ## A
            ## B
        """)
        sample = _write_md(tmp_path, "s.md", """
            # Sample

            ## A
            ## C
        """)
        result = compare_to_consolidated(sample, consolidated)
        assert "Sample" + CHAIN_SEPARATOR + "A" in result.common
        assert "Sample" + CHAIN_SEPARATOR + "C" in result.unique_to_sample
        # B is consolidated-unique, not sample-unique
        assert "Sample" + CHAIN_SEPARATOR + "B" not in result.unique_to_sample
        assert result.sample_chains == {"Sample", "Sample" + CHAIN_SEPARATOR + "A", "Sample" + CHAIN_SEPARATOR + "C"}

    def test_empty_consolidated_means_sample_chains_unique(self, tmp_path: Path):
        """Consolidated with only level-1 means samples' level-2+ chains are all unique."""
        consolidated = _write_md(tmp_path, "_CONSOLIDATED.md", "# Sample\n\n")
        sample = _write_md(tmp_path, "s.md", "# Sample\n\n## A\n## B\n")
        result = compare_to_consolidated(sample, consolidated)
        # Level-1 "Sample" is common; level-2 chains are unique to sample
        assert result.common == {"Sample"}
        assert result.unique_to_sample == {
            "Sample" + CHAIN_SEPARATOR + "A",
            "Sample" + CHAIN_SEPARATOR + "B",
        }

    def test_identical_trees_have_no_unique(self, tmp_path: Path):
        consolidated = _write_md(tmp_path, "_CONSOLIDATED.md", "# Sample\n\n## A\n## B\n")
        sample = _write_md(tmp_path, "s.md", "# Sample\n\n## A\n## B\n")
        result = compare_to_consolidated(sample, consolidated)
        assert result.unique_to_sample == set()
        assert "Sample" + CHAIN_SEPARATOR + "A" in result.common
        assert "Sample" + CHAIN_SEPARATOR + "B" in result.common


# ─── diff_summary — corpus-level aggregation ─────────────────────────────


class TestDiffSummary:
    def test_aggregates_chain_to_files_across_samples(self, tmp_path: Path):
        _write_md(tmp_path, "_CONSOLIDATED.md", "# Sample\n\n## A\n")
        _write_md(tmp_path, "s1.md", "# Sample\n\n## A\n## B\n")
        _write_md(tmp_path, "s2.md", "# Sample\n\n## A\n## C\n")
        summary = diff_summary(tmp_path, tmp_path / "_CONSOLIDATED.md")
        sa = "Sample" + CHAIN_SEPARATOR + "A"
        sb = "Sample" + CHAIN_SEPARATOR + "B"
        sc = "Sample" + CHAIN_SEPARATOR + "C"
        assert summary.sample_count == 2
        assert sa in summary.consolidated_chains
        assert {p.name for p in summary.chain_to_files[sa]} == {"s1.md", "s2.md"}
        assert {p.name for p in summary.chain_to_files[sb]} == {"s1.md"}
        assert {p.name for p in summary.chain_to_files[sc]} == {"s2.md"}

    def test_growth_candidates(self, tmp_path: Path):
        """Chains in samples but not in consolidated."""
        _write_md(tmp_path, "_CONSOLIDATED.md", "# Sample\n\n## A\n")
        _write_md(tmp_path, "s1.md", "# Sample\n\n## A\n## B\n")
        _write_md(tmp_path, "s2.md", "# Sample\n\n## C\n")
        summary = diff_summary(tmp_path, tmp_path / "_CONSOLIDATED.md")
        growth = summary.growth_candidates
        assert "Sample" + CHAIN_SEPARATOR + "B" in growth
        assert "Sample" + CHAIN_SEPARATOR + "C" in growth
        assert "Sample" + CHAIN_SEPARATOR + "A" not in growth

    def test_pruning_candidates(self, tmp_path: Path):
        """Chains in consolidated but no sample carries them."""
        _write_md(tmp_path, "_CONSOLIDATED.md", "# Sample\n\n## A\n## OrphanedBranch\n")
        _write_md(tmp_path, "s1.md", "# Sample\n\n## A\n")
        summary = diff_summary(tmp_path, tmp_path / "_CONSOLIDATED.md")
        assert "Sample" + CHAIN_SEPARATOR + "OrphanedBranch" in summary.pruning_candidates
        assert "Sample" + CHAIN_SEPARATOR + "A" not in summary.pruning_candidates

    def test_well_supported(self, tmp_path: Path):
        """Chains in both consolidated and samples."""
        _write_md(tmp_path, "_CONSOLIDATED.md", "# Sample\n\n## A\n## B\n## OrphanedBranch\n")
        _write_md(tmp_path, "s1.md", "# Sample\n\n## A\n## B\n## SampleOnly\n")
        summary = diff_summary(tmp_path, tmp_path / "_CONSOLIDATED.md")
        sa = "Sample" + CHAIN_SEPARATOR + "A"
        sb = "Sample" + CHAIN_SEPARATOR + "B"
        orphan = "Sample" + CHAIN_SEPARATOR + "OrphanedBranch"
        sample_only = "Sample" + CHAIN_SEPARATOR + "SampleOnly"
        assert sa in summary.well_supported
        assert sb in summary.well_supported
        assert orphan not in summary.well_supported  # consolidated-only
        assert sample_only not in summary.well_supported  # sample-only

    def test_skips_underscore_prefixed_files(self, tmp_path: Path):
        """`_CONSOLIDATED.md`, `_INDEX.md`, `_missing--*.md` are not samples."""
        _write_md(tmp_path, "_CONSOLIDATED.md", "# Sample\n\n## A\n")
        _write_md(tmp_path, "_INDEX.md", "# Index\n\n## SomeIndexOnlyChain\n")
        _write_md(tmp_path, "_missing--foo.md", "# Missing\n\n## SomeMissingChain\n")
        _write_md(tmp_path, "real.md", "# Sample\n\n## A\n")
        summary = diff_summary(tmp_path, tmp_path / "_CONSOLIDATED.md")
        assert summary.sample_count == 1  # only real.md
        # Chain keys carry their own root, so the index/missing chains aren't even in scope
        assert "Index" + CHAIN_SEPARATOR + "SomeIndexOnlyChain" not in summary.chain_to_files
        assert "Missing" + CHAIN_SEPARATOR + "SomeMissingChain" not in summary.chain_to_files

    def test_empty_samples_directory(self, tmp_path: Path):
        _write_md(tmp_path, "_CONSOLIDATED.md", "# Sample\n\n## A\n## B\n")
        summary = diff_summary(tmp_path, tmp_path / "_CONSOLIDATED.md")
        assert summary.sample_count == 0
        assert summary.chain_to_files == {}
        sa = "Sample" + CHAIN_SEPARATOR + "A"
        sb = "Sample" + CHAIN_SEPARATOR + "B"
        assert sa in summary.consolidated_chains
        assert sb in summary.consolidated_chains
        # All consolidated chains are pruning candidates when no samples exist
        assert sa in summary.pruning_candidates
        assert sb in summary.pruning_candidates


# ─── CorpusDiff API ──────────────────────────────────────────────────────


class TestCorpusDiff:
    def test_growth_pruning_well_supported_partition_chains(self, tmp_path: Path):
        """Every chain belongs to exactly one classification."""
        _write_md(tmp_path, "_CONSOLIDATED.md", "# Sample\n\n## A\n## OrphanInConsolidated\n")
        _write_md(tmp_path, "s.md", "# Sample\n\n## A\n## SampleOnly\n")
        summary = diff_summary(tmp_path, tmp_path / "_CONSOLIDATED.md")
        sa = "Sample" + CHAIN_SEPARATOR + "A"
        orphan = "Sample" + CHAIN_SEPARATOR + "OrphanInConsolidated"
        sample_only = "Sample" + CHAIN_SEPARATOR + "SampleOnly"
        assert sa in summary.well_supported
        assert sample_only in summary.growth_candidates
        assert orphan in summary.pruning_candidates
        # No overlap between the three classifications
        assert set(summary.growth_candidates.keys()).isdisjoint(summary.well_supported.keys())
        assert set(summary.growth_candidates.keys()).isdisjoint(summary.pruning_candidates)
        assert set(summary.well_supported.keys()).isdisjoint(summary.pruning_candidates)
