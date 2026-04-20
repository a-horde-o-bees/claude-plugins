"""Shared pytest fixtures for the ocd plugin test suite."""

import shutil

import pytest
from pathlib import Path


def pytest_addoption(parser):
    parser.addoption(
        "--run-agent", action="store_true", default=False,
        help="Run agent tests (spawns claude CLI, makes real API calls)",
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "agent: marks tests that spawn real agents (deselect with '-m not agent')")


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--run-agent"):
        skip = pytest.mark.skip(reason="needs --run-agent flag (makes real API calls)")
        for item in items:
            if "agent" in item.keywords:
                item.add_marker(skip)


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Walk up from this conftest until a .git directory is found."""
    here = Path(__file__).resolve()
    for candidate in [here, *here.parents]:
        if (candidate / ".git").is_dir():
            return candidate
    raise RuntimeError("project root not found — no .git directory in ancestors")


@pytest.fixture(scope="session")
def claude_cli() -> str:
    """Return path to claude CLI, or skip if not available."""
    path = shutil.which("claude")
    if not path:
        pytest.skip("claude CLI not found on PATH")
    return path
