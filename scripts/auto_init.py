"""Auto-init orchestrator — rectify deployed state to current templates.

Scans every plugin under plugins/, runs each system's init(force=True),
and rebuilds the `.claude/` tree to match current template shape. Data
preservation is handled outside the init contract: all `.claude/**/*.db`
files are mirrored to `.claude/pre-sync/<rel>` before any init runs, and
schemas are compared afterward — matching schemas restore backup data
(no data loss from wipe-and-recreate), diverging schemas keep the backup
and surface a migration flag so the user handles the change intelligently.

Called by /checkpoint after push. Exits 0 on clean sync, non-zero when
any DB backup has a schema mismatch that needs human migration.
"""

import importlib
import os
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path


def _git_root() -> Path:
    """Anchor at the enclosing git root rather than walking `__file__` parents.

    Matches what `framework.get_project_dir()` does internally when
    `CLAUDE_PROJECT_DIR` is unset. Script has no access to the plugin
    framework at import time (it bootstraps the framework), so we call
    git directly instead of importing the helper.
    """
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
    )
    return Path(result.stdout.strip()).resolve()


PROJECT_ROOT = _git_root()
CLAUDE_DIR = PROJECT_ROOT / ".claude"
PRE_SYNC_DIR = CLAUDE_DIR / "pre-sync"


TEMPLATE_CATEGORIES = ("rules", "conventions", "patterns")


def main() -> int:
    if _pre_sync_has_unresolved():
        print(
            f"{PRE_SYNC_DIR.relative_to(PROJECT_ROOT)} contains unresolved "
            "backups from a prior run. Resolve or remove before re-syncing.",
            file=sys.stderr,
        )
        return 2

    backups = _backup_databases()

    claimed = _run_all_plugin_inits()
    _prune_orphans(claimed)
    exit_code = _reconcile_backups(backups)
    _scan_navigators()

    return exit_code


def _pre_sync_has_unresolved() -> bool:
    if not PRE_SYNC_DIR.is_dir():
        return False
    return any(PRE_SYNC_DIR.rglob("*.db"))


def _backup_databases() -> list[tuple[Path, Path]]:
    """Mirror every .claude/**/*.db to .claude/pre-sync/<rel-path>."""
    backups: list[tuple[Path, Path]] = []
    if not CLAUDE_DIR.is_dir():
        return backups
    for db in CLAUDE_DIR.rglob("*.db"):
        if PRE_SYNC_DIR in db.parents:
            continue
        rel = db.relative_to(CLAUDE_DIR)
        backup = PRE_SYNC_DIR / rel
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(db, backup)
        backups.append((db, backup))
    return backups


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
    template. Other trees (.claude/logs for user content, plugin data dirs,
    worktrees, pre-sync) are left alone.
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


def _reconcile_backups(backups: list[tuple[Path, Path]]) -> int:
    """Restore-on-schema-match, flag-on-mismatch."""
    mismatches: list[tuple[Path, Path]] = []
    for original, backup in backups:
        if not original.exists():
            mismatches.append((original, backup))
            continue
        if _schemas_match(original, backup):
            shutil.copy2(backup, original)
            backup.unlink()
        else:
            mismatches.append((original, backup))

    _cleanup_empty_pre_sync()

    if mismatches:
        print("\nSchema migration required:", file=sys.stderr)
        for original, backup in mismatches:
            print(f"  {original.relative_to(PROJECT_ROOT)}", file=sys.stderr)
            print(f"    backup: {backup.relative_to(PROJECT_ROOT)}", file=sys.stderr)
        return 1
    return 0


def _schemas_match(a: Path, b: Path) -> bool:
    return _schema_statements(a) == _schema_statements(b)


def _schema_statements(db_path: Path) -> list[str]:
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute(
            "SELECT sql FROM sqlite_master WHERE sql IS NOT NULL ORDER BY name"
        ).fetchall()
    finally:
        conn.close()
    return [row[0] for row in rows]


def _cleanup_empty_pre_sync() -> None:
    if not PRE_SYNC_DIR.is_dir():
        return
    for d in sorted(PRE_SYNC_DIR.rglob("*"), reverse=True):
        if d.is_dir() and not any(d.iterdir()):
            d.rmdir()
    if PRE_SYNC_DIR.is_dir() and not any(PRE_SYNC_DIR.iterdir()):
        PRE_SYNC_DIR.rmdir()


def _print_changed(result: dict) -> None:
    for entry in result.get("files", []):
        before = entry.get("before")
        after = entry.get("after")
        if before != after:
            print(f"{entry['path']}: {before} → {after}")


if __name__ == "__main__":
    sys.exit(main())
