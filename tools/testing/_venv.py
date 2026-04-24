"""Per-suite venv resolution.

The project venv at `<project>/.venv/bin/python3` backs project-level
tests. Each plugin's tests run under that plugin's own venv at
`~/.claude/plugins/data/<plugin>-<namespace>/venv/bin/python3`, where
install_deps.sh installs the plugin's requirements on SessionStart.

When both marketplace and inline dev venvs exist for the same plugin,
marketplace wins — tests should exercise the version users have
installed, not the development checkout's private venv.
"""

from pathlib import Path

from . import _environment


def resolve_project_venv() -> Path:
    """Return path to the project venv's python3.

    Raises RuntimeError when the venv is absent — the project venv is a
    bootstrap prerequisite and tests cannot proceed without it.
    """
    project_root = _environment.get_project_dir()
    path = project_root / ".venv" / "bin" / "python3"
    if not path.is_file():
        raise RuntimeError(
            f"project venv not found at {path} — bootstrap with `uv venv` "
            "before running project-run tests",
        )
    return path


def resolve_plugin_venv(plugin_name: str) -> Path:
    """Return path to the named plugin's venv python3.

    Searches `~/.claude/plugins/data/` for matching plugin data directories.
    Prefers marketplace install (`<plugin>-<namespace>`) over inline dev
    (`<plugin>-inline`). Raises RuntimeError when no matching venv is
    found — plugins with missing venvs should surface loudly rather than
    fall back to the project venv, which silently masks dependency drift.
    """
    data_dir = _environment.get_claude_home() / "plugins" / "data"
    if not data_dir.is_dir():
        raise RuntimeError(
            f"Claude plugin data directory not found at {data_dir}",
        )

    marketplace: list[Path] = []
    inline: list[Path] = []
    for entry in data_dir.iterdir():
        if not entry.is_dir():
            continue
        if entry.name == f"{plugin_name}-inline":
            inline.append(entry)
        elif entry.name.startswith(f"{plugin_name}-"):
            marketplace.append(entry)

    for candidate in marketplace + inline:
        venv_python = candidate / "venv" / "bin" / "python3"
        if venv_python.is_file():
            return venv_python

    raise RuntimeError(
        f"no venv found for plugin `{plugin_name}` under {data_dir} — "
        "ensure the plugin is installed and its SessionStart hook has run",
    )
