"""Fixtures scoped to check-system integration tests.

Per the fixture_*.{md,py} naming convention, scanner sample inputs
co-locate with the tests that consume them. Tests receive paths
through pytest fixtures defined here so test bodies never anchor to
`__file__` directly.
"""

import sys
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def messy_markdown() -> Path:
    """Path to the co-located messy-fixture markdown file.

    Packs every known pathological case (placeholders in multiple
    contexts, ordered list broken by blockquote, blank-line discipline
    violations, literal characters) into one file so tests can make
    many assertions against a single lint scan. Do not modify in
    place — copy to tmp_path for autofix tests.
    """
    return Path(__file__).parent / "fixture_messy.md"


@pytest.fixture(scope="session")
def parent_walking_sample() -> Path:
    """Path to the co-located parent-walking fixture Python file.

    Mirrors `messy_markdown`: one file packing every parent-walking
    pattern (chained `.parent`, `.parents[N>=1]`, nested dirname calls)
    alongside legitimate cases (single `.parent`, `.parents[0]`) so
    the scanner can be asserted in one scan. Not a real module — only
    its AST is parsed. pytest skips `fixture_*.py` from collection by
    default (doesn't match the `test_*.py` discovery glob).
    """
    return Path(__file__).parent / "fixture_parent_walking.py"


@pytest.fixture(scope="session")
def dormancy_fixtures_dir() -> Path:
    """Directory holding synthetic dormancy fixture *packages*.

    Each child subdirectory is a Python package (`compliant_runtime`,
    `deploy_only`, `broken_ready_always_true`, …) that the dormancy
    checker imports by name. Unlike the `fixture_*.py` single-file
    scanner inputs, these are full packages with `_init.py` — they
    must be importable, which is what the autouse fixture below
    arranges by putting this directory on `sys.path`.
    """
    return Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session", autouse=True)
def _dormancy_fixtures_on_syspath(dormancy_fixtures_dir: Path):
    """Ensure dormancy fixture packages are importable for the session.

    Module-level `sys.path.insert` in test files is what drove the
    parent-walking in the old test — moving both the path lookup and
    the sys.path mutation here keeps test bodies free of `__file__`
    anchoring. Autouse + session scope ensures the setup runs before
    any check-system test executes.
    """
    path_str = str(dormancy_fixtures_dir)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)
    yield
