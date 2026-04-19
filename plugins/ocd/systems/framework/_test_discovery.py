"""Test suite discovery.

Scans a worktree checkout and enumerates the suites that pytest should
run. Each suite names its path, config, and the venv whose python3 runs
its pytest invocation.
"""

from dataclasses import dataclass
from pathlib import Path

from . import _venv


@dataclass
class Suite:
    name: str
    """Human identifier used in the report (e.g. 'project', 'ocd', 'blueprint')."""

    rel_path: Path
    """Path relative to the worktree that pytest collects from."""

    pytest_ini: Path | None
    """Path to `-c` config argument, or None when pytest finds config automatically."""

    venv: Path
    """Python interpreter to run pytest under for this suite."""


def discover_suites(
    worktree: Path,
    plugin_filter: str | None = None,
    project_only: bool = False,
) -> list[Suite]:
    """Return the list of suites to run in this invocation.

    When `plugin_filter` is set, returns only that plugin's suite (and no
    project suite). When `project_only` is set, returns only the project
    suite. Default returns all present suites — project first, then each
    plugin in directory-name order.
    """
    suites: list[Suite] = []

    project_tests = worktree / "tests"
    if plugin_filter is None and project_tests.is_dir():
        suites.append(
            Suite(
                name="project",
                rel_path=Path("tests"),
                pytest_ini=None,
                venv=_venv.resolve_project_venv(),
            ),
        )

    if project_only:
        return suites

    plugins_dir = worktree / "plugins"
    if not plugins_dir.is_dir():
        return suites

    for plugin_dir in sorted(plugins_dir.iterdir()):
        if not plugin_dir.is_dir():
            continue
        pytest_ini = plugin_dir / "pytest.ini"
        if not pytest_ini.is_file():
            continue
        plugin_name = plugin_dir.name
        if plugin_filter is not None and plugin_name != plugin_filter:
            continue
        suites.append(
            Suite(
                name=plugin_name,
                rel_path=Path("plugins") / plugin_name,
                pytest_ini=Path("plugins") / plugin_name / "pytest.ini",
                venv=_venv.resolve_plugin_venv(plugin_name),
            ),
        )

    return suites
