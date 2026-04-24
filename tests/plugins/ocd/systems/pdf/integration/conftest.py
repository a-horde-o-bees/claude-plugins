"""Fixtures scoped to pdf-system integration tests.

Per the fixture_*.md naming convention, rendering sample inputs
co-locate with the tests that consume them. Tests receive paths
through this fixture so test bodies never anchor to `__file__`.
"""

from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def messy_markdown() -> Path:
    """Path to the co-located messy-fixture markdown file.

    Packs every pathological case (italic text, placeholders, ordered
    list broken by blockquote, blank-line issues, literal characters)
    into one file so generate_pdf runs once per module and rendering
    assertions fan out over the single output PDF. Do not modify in
    place.
    """
    return Path(__file__).parent / "fixture_messy.md"
