"""Shared pytest fixtures for the ocd plugin test suite."""

import shutil
import sys

import pytest
from pathlib import Path


@pytest.fixture(autouse=True)
def _bind_plugin_data_env(monkeypatch):
    """Point CLAUDE_PLUGIN_DATA at the venv hosting sys.executable.

    `plugins/ocd/bin/ocd-run` resolves its Python interpreter by walking a
    discovery chain; `$CLAUDE_PLUGIN_DATA/venv/bin/python3` is the first
    link. When pytest subprocess-invokes ocd-run from plugin tests, we want
    the subprocess to use the same venv pytest itself is running under —
    otherwise ocd-run falls back to system Python and imports of plugin
    dependencies (libcst, mcp, weasyprint) fail inside the subprocess.

    sys.executable layout: `<data-dir>/<name>/venv/bin/python3`. Walk three
    parents up to reach the data-dir Claude Code hands to the plugin.
    """
    exe = Path(sys.executable)
    candidate = exe.parent.parent.parent
    if (candidate / "venv" / "bin" / "python3").is_file():
        monkeypatch.setenv("CLAUDE_PLUGIN_DATA", str(candidate))


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
    """Resolve the git repository root containing this conftest.

    Delegates to the canonical environment helper so linked worktrees
    (where `.git` is a file pointer rather than a directory) resolve
    correctly.
    """
    from tools.environment import get_git_root_for

    return get_git_root_for(Path(__file__))


@pytest.fixture(scope="session")
def claude_cli() -> str:
    """Return path to claude CLI, or skip if not available."""
    path = shutil.which("claude")
    if not path:
        pytest.skip("claude CLI not found on PATH")
    return path


@pytest.fixture(scope="session")
def ocd_run(project_root: Path) -> Path:
    """Absolute path to plugins/ocd/bin/ocd-run, resolved from project root.

    CLI integration tests subprocess this bin directly so they exercise
    the full venv-resolution + run.py module promotion + argparse dispatch
    chain — the same path agents hit when invoking `ocd-run ...`.
    """
    return project_root / "plugins" / "ocd" / "bin" / "ocd-run"


@pytest.fixture(scope="session")
def preset_compact_css(project_root: Path) -> Path:
    """Absolute path to the bundled compact.css preset in the ocd plugin.

    Rendering integration tests reference the real preset stylesheet (not
    a synthetic one) so relative @font-face URLs, list-style choices, and
    font-weight declarations are exercised end-to-end.
    """
    return project_root / "plugins" / "ocd" / "systems" / "pdf" / "templates" / "compact" / "compact.css"


@pytest.fixture
def sandbox_worktree(request):
    """Disposable sandbox worktree for integration tests that modify project files.

    Wraps `systems.sandbox.worktree_setup` / `worktree_teardown` — the
    canonical ephemeral-worktree primitives. Yields the path to a
    detached worktree at `<parent>/<project>--tmp-pytest-<node>/`.
    Orphaned worktrees from crashed tests are swept by
    `ocd-run sandbox cleanup`. See testing.md Git Worktree Isolation.
    """
    from systems.sandbox import worktree_setup, worktree_teardown

    topic = f"pytest-{request.node.name.replace(':', '-').replace('[', '-').replace(']', '')}"
    path = worktree_setup(topic)
    try:
        yield path
    finally:
        worktree_teardown(topic)
