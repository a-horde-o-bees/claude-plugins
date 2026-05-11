"""Integration tests for the Python parent-walking lint.

The rule flags any `.parent`, `.parents[N]`, or `os.path.dirname(...)`
traversal whose chain roots at `__file__`. Tests act as regression
guards for:

  - Detection: every __file__-rooted pattern fires, including single
    `.parent`, `.parents[0]`, and single `dirname(__file__)` calls.
  - Non-detection: chains whose leftmost expression is any other
    identifier, call, or literal do NOT fire — parent-walking is
    about file-anchoring, not arbitrary path manipulation.
  - Chain de-dup: a `.parent.parent.parent.parent` chain reports as
    one violation on the outermost attribute, not one per `.parent`.
  - Rule label: all detections carry `"Python - parent-walking"`.
  - Allowlist: (rule, path) pairs matching an `allowlist.csv` pattern
    are suppressed by `filter_allowed`, and the scanner itself
    remains pure (returns raw violations).

Tests locate assertions by source snippet, so edits to the fixture
(comment tweaks, reordering) do not break anchors.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from systems.check._allowlist import (
    AllowlistEntry,
    filter_allowed,
    is_allowed,
    load_allowlist,
)
from systems.check._python import PARENT_WALKING, scan_parent_walking


def _lines_for(path: Path, substring: str) -> list[int]:
    """Return line numbers whose source line contains `substring`."""
    text = path.read_text(encoding="utf-8").splitlines()
    return [i + 1 for i, line in enumerate(text) if substring in line]


def _violations_on_line(path: Path, line: int) -> list:
    return [v for v in scan_parent_walking(path) if v.line == line]


class TestFileRootedDetection:
    """Every chain rooted at `__file__` fires — including single-level."""

    @pytest.mark.parametrize(
        "identifier",
        [
            "HERE =",
            "IMMEDIATE =",
            "ONE_UP =",
            "TWO_UP =",
            "FOUR_UP =",
            "ONE_PARENTS =",
            "THREE_PARENTS =",
            "NESTED_DIRNAME =",
            "DEEP_DIRNAME =",
        ],
    )
    def test_file_rooted_chain_flagged(
        self, parent_walking_sample: Path, identifier: str
    ):
        line_candidates = _lines_for(parent_walking_sample, identifier)
        assert line_candidates, f"fixture missing {identifier!r}"
        target = line_candidates[0]
        hits = _violations_on_line(parent_walking_sample, target)
        assert hits, (
            f"expected {identifier!r} on line {target} to fire "
            f"Python - parent-walking"
        )

    def test_deep_parent_chain_reports_one_violation_not_four(
        self, parent_walking_sample: Path
    ):
        """The 4-deep chain reports as a single violation, not one per
        inner `.parent`."""
        target = _lines_for(parent_walking_sample, "FOUR_UP =")[0]
        hits = _violations_on_line(parent_walking_sample, target)
        assert len(hits) == 1, (
            f"expected exactly 1 violation for the depth-4 chain on "
            f"line {target}; got {len(hits)}: {hits}"
        )


class TestNonFileRootedDetection:
    """Chains NOT rooted at `__file__` do not fire — they are ordinary
    path manipulation, not file-anchored walking."""

    @pytest.mark.parametrize(
        "identifier",
        [
            "VAR_PARENT =",
            "VAR_DEEP =",
            "VAR_PARENTS =",
            "VAR_DIRNAME =",
            "LITERAL_DIRNAME =",
        ],
    )
    def test_non_file_rooted_chain_not_flagged(
        self, parent_walking_sample: Path, identifier: str
    ):
        line_candidates = _lines_for(parent_walking_sample, identifier)
        assert line_candidates, f"fixture missing {identifier!r}"
        target = line_candidates[0]
        hits = _violations_on_line(parent_walking_sample, target)
        assert not hits, (
            f"expected {identifier!r} on line {target} to NOT fire; got {hits}"
        )


class TestRuleLabel:
    def test_all_violations_use_descriptive_label(
        self, parent_walking_sample: Path
    ):
        """Every violation carries `"Python - parent-walking"`."""
        violations = scan_parent_walking(parent_walking_sample)
        assert violations, "fixture should produce at least one violation"
        rules = {v.rule for v in violations}
        assert rules == {PARENT_WALKING}, (
            f"expected every violation to use {PARENT_WALKING!r}; "
            f"got rule set {rules}"
        )


class TestRobustness:
    def test_syntax_error_returns_empty(self, tmp_path: Path):
        bad = tmp_path / "bad.py"
        bad.write_text("def broken(:\n    pass\n", encoding="utf-8")
        assert scan_parent_walking(bad) == []

    def test_empty_file_returns_empty(self, tmp_path: Path):
        empty = tmp_path / "empty.py"
        empty.write_text("", encoding="utf-8")
        assert scan_parent_walking(empty) == []

    def test_arbitrary_path_file_returns_empty(self, tmp_path: Path):
        """A file that uses path manipulation but never anchors to
        __file__ should produce zero violations."""
        clean = tmp_path / "clean.py"
        clean.write_text(
            "from pathlib import Path\n"
            "p = Path('/etc')\n"
            "grand = p.parent.parent\n"
            "many = p.parents[5]\n",
            encoding="utf-8",
        )
        assert scan_parent_walking(clean) == []


class TestAllowlistLoader:
    def test_missing_file_returns_empty(self, tmp_path: Path):
        assert load_allowlist(tmp_path / "nonexistent.csv") == []

    def test_loads_valid_rows(self, tmp_path: Path):
        csv_path = tmp_path / "allowlist.csv"
        csv_path.write_text(
            "rule,pattern,reason\n"
            "Python - parent-walking,**/conftest.py,pytest anchor\n"
            "Python - parent-walking,plugins/*/run.py,plugin entry\n",
            encoding="utf-8",
        )
        entries = load_allowlist(csv_path)
        assert len(entries) == 2
        assert entries[0].pattern == "**/conftest.py"
        assert entries[1].reason == "plugin entry"

    def test_skips_rows_missing_rule_or_pattern(self, tmp_path: Path):
        csv_path = tmp_path / "allowlist.csv"
        csv_path.write_text(
            "rule,pattern,reason\n"
            ",**/empty-rule.py,missing rule\n"
            "Python - parent-walking,,missing pattern\n"
            "Python - parent-walking,valid.py,valid row\n",
            encoding="utf-8",
        )
        entries = load_allowlist(csv_path)
        assert len(entries) == 1
        assert entries[0].pattern == "valid.py"


class TestAllowlistMatching:
    def test_is_allowed_matches_rule_and_pattern(self, tmp_path: Path):
        entries = [
            AllowlistEntry("Python - parent-walking", "*conftest.py", "x")
        ]
        path = tmp_path / "tests" / "conftest.py"
        path.parent.mkdir(parents=True)
        path.touch()
        assert is_allowed(entries, "Python - parent-walking", path)

    def test_is_allowed_rejects_when_rule_mismatches(self, tmp_path: Path):
        entries = [AllowlistEntry("Other - rule", "*conftest.py", "x")]
        path = tmp_path / "conftest.py"
        path.touch()
        assert not is_allowed(entries, "Python - parent-walking", path)

    def test_is_allowed_rejects_when_pattern_mismatches(self, tmp_path: Path):
        entries = [
            AllowlistEntry("Python - parent-walking", "plugins/*/run.py", "x")
        ]
        path = tmp_path / "systems" / "other.py"
        path.parent.mkdir(parents=True)
        path.touch()
        assert not is_allowed(entries, "Python - parent-walking", path)

    def test_is_allowed_uses_project_relative_path(self, tmp_path: Path):
        """When a project_root is passed, the path is rendered
        project-relative before fnmatch. The allowlist author
        writes patterns against the project-relative form."""
        entries = [
            AllowlistEntry("Python - parent-walking", "a/b/anchor.py", "x")
        ]
        project_root = tmp_path
        path = project_root / "a" / "b" / "anchor.py"
        path.parent.mkdir(parents=True)
        path.touch()
        assert is_allowed(
            entries,
            "Python - parent-walking",
            path,
            project_root=project_root,
        )

    def test_filter_allowed_partitions_violations(self, tmp_path: Path):
        entries = [
            AllowlistEntry("Python - parent-walking", "*/conftest.py", "x")
        ]
        # Write two files: one allowlisted, one not.
        conftest = tmp_path / "project" / "conftest.py"
        conftest.parent.mkdir(parents=True)
        conftest.write_text(
            "from pathlib import Path\nHERE = Path(__file__).parent\n",
            encoding="utf-8",
        )
        non_anchor = tmp_path / "project" / "lib.py"
        non_anchor.write_text(
            "from pathlib import Path\nHERE = Path(__file__).parent\n",
            encoding="utf-8",
        )
        raw = scan_parent_walking(conftest) + scan_parent_walking(non_anchor)
        assert len(raw) == 2
        kept, suppressed = filter_allowed(raw, entries)
        assert len(kept) == 1
        assert kept[0].path == non_anchor
        assert len(suppressed) == 1
        assert suppressed[0].path == conftest


class TestBundledAllowlist:
    """The allowlist shipped at `systems/check/allowlist.csv` must
    cover the known anchors in this project: conftest.py, plugin
    run.py / bin shims, per-system __main__.py dispatchers."""

    @pytest.fixture(scope="class")
    def bundled_entries(self, project_root: Path) -> list[AllowlistEntry]:
        csv_path = (
            project_root
            / "plugins"
            / "ocd"
            / "systems"
            / "check"
            / "allowlist.csv"
        )
        entries = load_allowlist(csv_path)
        assert entries, f"bundled allowlist at {csv_path} should not be empty"
        return entries

    def test_conftest_is_allowlisted(
        self, bundled_entries: list[AllowlistEntry], project_root: Path
    ):
        conftest = project_root / "tests" / "plugins" / "ocd" / "conftest.py"
        assert conftest.is_file(), "expected project conftest.py to exist"
        assert is_allowed(
            bundled_entries,
            PARENT_WALKING,
            conftest,
            project_root=project_root,
        )

    def test_per_system_main_is_allowlisted(
        self, bundled_entries: list[AllowlistEntry], project_root: Path
    ):
        check_main = (
            project_root
            / "plugins"
            / "ocd"
            / "systems"
            / "check"
            / "__main__.py"
        )
        assert check_main.is_file()
        assert is_allowed(
            bundled_entries,
            PARENT_WALKING,
            check_main,
            project_root=project_root,
        )

    def test_plugin_bin_shim_is_allowlisted(
        self, bundled_entries: list[AllowlistEntry], project_root: Path
    ):
        bin_dir = project_root / "plugins" / "ocd" / "bin"
        if not bin_dir.is_dir():
            pytest.skip("plugins/ocd/bin not present in this checkout")
        shims = [p for p in bin_dir.iterdir() if p.is_file()]
        assert shims, "expected at least one shim in plugins/ocd/bin"
        first = shims[0]
        assert is_allowed(
            bundled_entries,
            PARENT_WALKING,
            first,
            project_root=project_root,
        )
