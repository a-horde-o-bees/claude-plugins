"""Setup orchestration — meta verbs and system-level dispatch helpers.

Top-level entry points for the new setup CLI surface:

- run_purposes() — lettered list of every migrated system with its
  purpose statement (one-liner). Drives the discovery experience; the
  user picks which system to explore.
- run_statuses() — aggregated status across every migrated system. Calls
  each system's status() with no scope to report state at every scope
  the system supports.
- run_system_usage(system_name) — renders one system's usage by reading
  the first paragraph of each setup/*.md component file plus the system's
  purpose() function.

Per-system verb invocation (install/uninstall/status) is dispatched by
the CLI directly to the named system's setup module, not orchestrated
here. Each system's setup/__init__.py owns its own install/uninstall/
status logic.
"""

from __future__ import annotations

import importlib
from pathlib import Path

from tools.environment import get_git_root_for, get_plugin_root, get_project_dir
from ._formatting import format_columns, format_section
from ._metadata import get_plugin_name
from ._system_discovery import _discover_systems


def _require_git_project_dir() -> None:
    """Refuse deploy verbs unless the project directory is inside a git repo."""
    project_dir = get_project_dir()
    try:
        get_git_root_for(project_dir)
    except RuntimeError as exc:
        raise RuntimeError(
            f"{project_dir} is not inside a git repository — run `git init` "
            "before deploying ocd systems so artifacts are tracked and reversible.",
        ) from exc


def run_purposes() -> None:
    """Print a lettered list of every migrated system with its purpose statement."""
    plugin_root = get_plugin_root()
    plugin_name = get_plugin_name(plugin_root)
    systems = _discover_systems(plugin_root)
    if not systems:
        print(f"No migrated systems in {plugin_name}.")
        return

    print(f"{plugin_name} systems:")
    print()
    rows: list[tuple[str, ...]] = []
    for idx, system_name in enumerate(systems):
        letter = chr(ord("A") + idx)
        try:
            mod = importlib.import_module(f"systems.{system_name}")
            purpose = mod.purpose() if hasattr(mod, "purpose") else "(no purpose declared)"
        except Exception as exc:  # noqa: BLE001
            purpose = f"(error loading: {exc})"
        rows.append((f"{letter}. {system_name}", purpose))
    for line in format_columns(rows):
        print(f"  {line}")
    print()
    print("Pick a system: `ocd-run setup <system>` for that system's usage.")


def run_statuses() -> None:
    """Print aggregated status across every migrated system."""
    plugin_root = get_plugin_root()
    plugin_name = get_plugin_name(plugin_root)
    systems = _discover_systems(plugin_root)
    if not systems:
        print(f"No migrated systems in {plugin_name}.")
        return

    print(f"{plugin_name} status")
    print()
    for system_name in systems:
        try:
            mod = importlib.import_module(f"systems.{system_name}")
            if hasattr(mod, "status"):
                result = mod.status()
            else:
                result = {"files": [], "extra": [{"label": "(no status)", "value": "system does not expose status"}]}
        except Exception as exc:  # noqa: BLE001
            result = {"files": [], "extra": [{"label": "error", "value": str(exc)}]}

        for line in format_section(system_name.capitalize(), result.get("files", []), result.get("extra")):
            print(line)
        print()


def run_system_usage(system_name: str) -> None:
    """Render one migrated system's usage.

    A system that exposes `verbs() -> list[dict]` controls its own verb
    listing. Otherwise, the listing is computed from standard handlers
    (`status`, `list_items`) plus any `workflows/<verb>.md` files.
    """
    plugin_root = get_plugin_root()
    workflows_dir = plugin_root / "systems" / system_name / "workflows"

    try:
        mod = importlib.import_module(f"systems.{system_name}")
        purpose = mod.purpose() if hasattr(mod, "purpose") else None
    except Exception as exc:  # noqa: BLE001
        print(f"error loading {system_name}: {exc}")
        return

    print(f"{system_name}")
    if purpose:
        print()
        print(f"  {purpose}")
    print()
    print("Verbs:")

    if hasattr(mod, "verbs"):
        verb_rows = [(v["name"], v.get("description", "")) for v in mod.verbs()]
    else:
        verb_rows = []
        if hasattr(mod, "status"):
            verb_rows.append(("status", "read-only state report (CLI-direct)"))
        if hasattr(mod, "list_items"):
            verb_rows.append(("list", "catalog of available items with purposes (CLI-direct)"))
        if workflows_dir.is_dir():
            for verb_md in sorted(workflows_dir.glob("*.md")):
                verb_rows.append((verb_md.stem, _first_paragraph(verb_md)))

    for line in format_columns(verb_rows):
        print(f"  {line}")
    print()
    print(f"Run a verb: `ocd-run setup {system_name} <verb> [args]`")


def _first_paragraph(md_path: Path) -> str:
    """Read the first non-heading, non-empty paragraph from a markdown file."""
    text = md_path.read_text()
    paragraphs: list[str] = []
    current: list[str] = []
    for line in text.splitlines():
        if not line.strip():
            if current:
                paragraphs.append(" ".join(current))
                current = []
            continue
        if line.startswith("#"):
            if current:
                paragraphs.append(" ".join(current))
                current = []
            continue
        current.append(line.strip())
    if current:
        paragraphs.append(" ".join(current))
    return paragraphs[0] if paragraphs else "(no description)"
