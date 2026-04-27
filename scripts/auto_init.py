"""Auto-init orchestrator — rectify deployed state to current templates.

Scans every plugin under plugins/, runs each system's init(force=True)
to bring deployed state into alignment with current templates, and
prunes orphans in template categories whose source systems have been
removed.

Per the new Init/Status Contract in python.md *Force semantics*, each
system's init(force=True) is surgical — destructive only where state
has actually drifted. DB-backed systems compose `tools.db.rectify`,
which compares schema up front and no-ops when the live DB matches
expected; data preservation across forced rebuilds is the system's
responsibility (timestamped backups beside the live DB on schema
divergence). Auto-init no longer maintains a project-level pre-sync
backup-and-restore mechanism.

Called by /checkpoint after push. Exits 0 on success.
"""

import importlib
import os
import subprocess
import sys
from pathlib import Path


def _git_root() -> Path:
    """Anchor at the enclosing git root rather than walking `__file__` parents."""
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
    )
    return Path(result.stdout.strip()).resolve()


PROJECT_ROOT = _git_root()
CLAUDE_DIR = PROJECT_ROOT / ".claude"


TEMPLATE_CATEGORIES = ("rules", "conventions", "patterns")


def main() -> int:
    claimed = _run_all_plugin_inits()
    _prune_orphans(claimed)
    backups = _collect_db_backups()
    _scan_navigators()
    if backups:
        _report_backups(backups)
    return 0


def _run_all_plugin_inits() -> set[Path]:
    """Run every plugin's system inits. Returns absolute paths of every file claimed."""
    claimed: set[Path] = set()
    plugins_dir = PROJECT_ROOT / "plugins"
    if not plugins_dir.is_dir():
        return claimed
    for plugin_dir in sorted(plugins_dir.iterdir()):
        if not plugin_dir.is_dir():
            continue
        claimed.update(_run_plugin_inits(plugin_dir))
    return claimed


def _run_plugin_inits(plugin_dir: Path) -> set[Path]:
    """Run one plugin's system inits. Returns absolute paths of every file claimed."""
    claimed: set[Path] = set()
    _clear_plugin_modules()
    systems_dir = plugin_dir / "systems"
    if not systems_dir.is_dir():
        return claimed
    added = [str(systems_dir), str(plugin_dir)]
    for entry in added:
        sys.path.insert(0, entry)
    os.environ["CLAUDE_PLUGIN_ROOT"] = str(plugin_dir)
    os.environ["CLAUDE_PROJECT_DIR"] = str(PROJECT_ROOT)
    try:
        for init_file in sorted(systems_dir.glob("*/_init.py")):
            system_name = init_file.parent.name
            try:
                mod = importlib.import_module(f"systems.{system_name}._init")
            except ModuleNotFoundError:
                continue
            if not hasattr(mod, "init"):
                continue
            result = mod.init(force=True)
            _print_changed(result)
            for entry in result.get("files", []):
                claimed.add((PROJECT_ROOT / entry["path"]).resolve())
    finally:
        for entry in added:
            sys.path.remove(entry)
        _clear_plugin_modules()
    return claimed


def _prune_orphans(claimed: set[Path]) -> None:
    """Remove files under .claude/{category}/<plugin>/ that no system claimed.

    Scoped to TEMPLATE_CATEGORIES where every file should trace back to a
    template. Catches files left behind when a system is removed entirely
    — its init no longer runs, so the per-system deploy_files orphan
    pruning never fires for those files.
    """
    for category in TEMPLATE_CATEGORIES:
        category_dir = CLAUDE_DIR / category
        if not category_dir.is_dir():
            continue
        for path in sorted(category_dir.rglob("*"), reverse=True):
            if path.is_file() and path.resolve() not in claimed:
                path.unlink()
                print(f"{path.relative_to(PROJECT_ROOT)}: orphan removed")
            elif path.is_dir() and not any(path.iterdir()):
                path.rmdir()


def _clear_plugin_modules() -> None:
    prefixes = ("framework", "plugin", "systems")
    for key in list(sys.modules):
        root = key.split(".", 1)[0]
        if root in prefixes:
            del sys.modules[key]


def _scan_navigators() -> None:
    """Run navigator scan for each plugin that ships a navigator system."""
    plugins_dir = PROJECT_ROOT / "plugins"
    if not plugins_dir.is_dir():
        return
    for plugin_dir in sorted(plugins_dir.iterdir()):
        if not (plugin_dir / "systems" / "navigator").is_dir():
            continue
        subprocess.run(
            [f"{plugin_dir.name}-run", "navigator", "scan", "."],
            cwd=PROJECT_ROOT,
            check=False,
            capture_output=True,
        )


def _collect_db_backups() -> list[Path]:
    """Find any timestamped DB backups left beside live DBs.

    Each system writes its own backup on schema divergence per the
    Init/Status Contract. After all inits run, scan for them so the
    end-of-run summary can flag them for the user.
    """
    backups: list[Path] = []
    if not CLAUDE_DIR.is_dir():
        return backups
    for path in sorted(CLAUDE_DIR.rglob("*.db.backup-*")):
        if path.is_file():
            backups.append(path)
    return backups


def _report_backups(backups: list[Path]) -> None:
    """Surface backup paths so the user knows manual review is pending."""
    print("\nDB backups left behind by schema migrations:", file=sys.stderr)
    for backup in backups:
        print(f"  {backup.relative_to(PROJECT_ROOT)}", file=sys.stderr)
    print(
        "\nReview each backup and either fold the data into the new schema "
        "or remove the file once you're confident.",
        file=sys.stderr,
    )


def _print_changed(result: dict) -> None:
    for entry in result.get("files", []):
        before = entry.get("before")
        after = entry.get("after")
        if before != after:
            print(f"{entry['path']}: {before} → {after}")


if __name__ == "__main__":
    sys.exit(main())
