"""Per-suite venv resolution.

The project venv at `<project>/.venv/bin/python3` backs project-level
tests. Plugins with their own dependency manifest (`install_deps.sh` +
`pyproject.toml`) run their tests under the plugin venv at
`~/.claude/plugins/data/<plugin>-<namespace>/venv/bin/python3`, where
install_deps.sh installs the plugin's requirements on SessionStart.

Stdlib-only plugins authored under the community-skill pattern (no
`install_deps.sh`, no plugin-level pyproject.toml — e.g.
progressive-composer) have no plugin venv at all; their tests fall
back to the project venv. The fallback is structurally gated: only
plugins whose source tree lacks `hooks/install_deps.sh` qualify, so
plugins that DO declare their own deps still surface loudly when their
venv is missing rather than silently masking dependency drift.

When both marketplace and inline dev venvs exist for the same plugin,
marketplace wins — tests should exercise the version users have
installed, not the development checkout's private venv.
"""

from pathlib import Path

from tools import environment


def resolve_project_venv() -> Path:
    """Return path to the project venv's python3.

    Raises RuntimeError when the venv is absent — the project venv is a
    bootstrap prerequisite and tests cannot proceed without it.
    """
    project_root = environment.get_project_dir()
    path = project_root / ".venv" / "bin" / "python3"
    if not path.is_file():
        raise RuntimeError(
            f"project venv not found at {path} — bootstrap with `uv venv` "
            "before running project-run tests",
        )
    return path


def resolve_plugin_venv(plugin_name: str) -> Path:
    """Return path to the named plugin's venv python3.

    For plugins that ship `hooks/install_deps.sh` (the dependency-manifest
    pattern), searches `~/.claude/plugins/data/` for matching plugin
    data directories. Prefers marketplace install (`<plugin>-<namespace>`)
    over inline dev (`<plugin>-inline`). Raises RuntimeError when no
    matching venv is found — these plugins should surface loudly rather
    than fall back to the project venv, which would silently mask
    dependency drift.

    For stdlib-only plugins (no `install_deps.sh`), returns the project
    venv directly — they have no third-party deps so the project venv's
    pytest is sufficient to exercise their tests.
    """
    if not _plugin_declares_own_venv(plugin_name):
        return resolve_project_venv()

    data_dir = environment.get_claude_home() / "plugins" / "data"
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


def _plugin_declares_own_venv(plugin_name: str) -> bool:
    """A plugin owns a venv when its source tree ships `hooks/install_deps.sh`."""
    project_root = environment.get_project_dir()
    install_script = project_root / "plugins" / plugin_name / "hooks" / "install_deps.sh"
    return install_script.is_file()
