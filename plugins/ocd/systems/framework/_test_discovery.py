"""Test suite discovery.

Scans a worktree checkout and enumerates the suites that pytest should
run. Each suite names its path, config, and the venv whose python3 runs
its pytest invocation.

Tests live at repo root under `tests/`. Project-level tests are in
`tests/` directly (excluding the `tests/plugins/` subtree); per-plugin
tests live under `tests/plugins/<name>/`. Keeping tests at the repo
root rather than inside `plugins/<name>/` means the plugin cache never
carries test artifacts (there is no `.claudeignore` mechanism — dev vs
prod separation is structural).
"""

from dataclasses import dataclass
from pathlib import Path

from . import _venv


@dataclass
class Suite:
    name: str
    """Human identifier used in the report (e.g. 'project', 'plugin:ocd')."""

    rel_paths: list[Path]
    """Paths relative to the worktree that pytest collects from. List so the
    project suite can enumerate top-level test subdirs other than `plugins/`."""

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
    plugin_tests_root = project_tests / "plugins"

    if plugin_filter is None and project_tests.is_dir():
        # Project-scope tests are anything under tests/ that is NOT under
        # tests/plugins/ — the latter is per-plugin territory with its own
        # venv. Enumerate project-level test siblings of `plugins/`.
        project_paths = [
            Path("tests") / entry.name
            for entry in sorted(project_tests.iterdir())
            if entry.is_dir() and entry.name != "plugins"
        ]
        if project_paths:
            suites.append(
                Suite(
                    name="project",
                    rel_paths=project_paths,
                    pytest_ini=None,
                    venv=_venv.resolve_project_venv(),
                ),
            )

    if project_only:
        return suites

    if not plugin_tests_root.is_dir():
        return suites

    for plugin_tests_dir in sorted(plugin_tests_root.iterdir()):
        if not plugin_tests_dir.is_dir():
            continue
        pytest_ini = plugin_tests_dir / "pytest.ini"
        if not pytest_ini.is_file():
            continue
        plugin_name = plugin_tests_dir.name
        if plugin_filter is not None and plugin_name != plugin_filter:
            continue
        rel = Path("tests") / "plugins" / plugin_name
        suites.append(
            Suite(
                name=f"plugin:{plugin_name}",
                rel_paths=[rel],
                pytest_ini=rel / "pytest.ini",
                venv=_venv.resolve_plugin_venv(plugin_name),
            ),
        )

    return suites
