"""Shared pytest fixtures for the ocd plugin test suite."""

import pytest
from pathlib import Path


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Walk up from this conftest until a .git directory is found."""
    here = Path(__file__).resolve()
    for candidate in [here, *here.parents]:
        if (candidate / ".git").is_dir():
            return candidate
    raise RuntimeError("project root not found — no .git directory in ancestors")
