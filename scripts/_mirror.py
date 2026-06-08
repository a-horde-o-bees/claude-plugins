"""Shared config + helpers for the mirror tools (sync_skills, reconcile_manifest, …).

Single source of truth for paths, the manifest, and — leaning on the repo's
`.gitignore` rather than hardcoded constants — what counts as non-source cruft to
keep out of the mirror. Add a pattern to `.gitignore` and every mirror tool honors
it. Future `sync_*` scripts (e.g. sync_hooks) share this substrate.
"""
from __future__ import annotations

import filecmp
import fnmatch
import json
import os
import shutil
from pathlib import Path


def claude_home() -> Path:
    env = os.environ.get("CLAUDE_HOME")
    return (Path(env) if env else Path.home() / ".claude").resolve()


REPO = Path(__file__).resolve().parent.parent
SRC_ROOT = claude_home() / "skills"
DST_ROOT = REPO / "skills"
MANIFEST = REPO / ".claude" / "skill-manifest.json"
GITIGNORE = REPO / ".gitignore"
_FALLBACK = ["__pycache__", "*.pyc"]


def _ignore_globs() -> list[str]:
    """Exclusion globs read from the repo .gitignore (negations/anchored paths are
    harmless no-ops against basenames). Falls back to the pycache essentials."""
    if not GITIGNORE.is_file():
        return list(_FALLBACK)
    globs = [
        line.strip().rstrip("/")
        for line in GITIGNORE.read_text().splitlines()
        if line.strip() and not line.startswith(("#", "!"))
    ]
    return globs or list(_FALLBACK)


IGNORE_GLOBS = _ignore_globs()
IGNORE = shutil.ignore_patterns(*IGNORE_GLOBS)
# dircmp matches names exactly (no globbing) — the plain-name patterns (no glob or
# path metacharacters) are the dir/file names to drop; excluding e.g. __pycache__
# transitively drops the *.pyc inside it.
PRUNE_NAMES = [g for g in IGNORE_GLOBS if not any(c in g for c in "*?[/")]


def is_cruft(path: Path) -> bool:
    """True when path is an ignored artifact (matches a .gitignore glob/name)."""
    if any(part in PRUNE_NAMES for part in path.parts):
        return True
    return any(fnmatch.fnmatch(path.name, g) for g in IGNORE_GLOBS)


def manifest_load() -> list[str]:
    return json.loads(MANIFEST.read_text())["skills"]


def manifest_save(names: list[str]) -> None:
    MANIFEST.write_text(json.dumps({"skills": names}, indent=2) + "\n")


def live_skills() -> set[str]:
    if not SRC_ROOT.is_dir():
        return set()
    return {p.name for p in SRC_ROOT.iterdir() if (p / "SKILL.md").is_file()}


def differ(a: Path, b: Path) -> bool:
    """True when trees a and b differ in content, ignoring cruft."""
    cmp = filecmp.dircmp(a, b, ignore=PRUNE_NAMES)
    if cmp.left_only or cmp.right_only or cmp.diff_files or cmp.funny_files:
        return True
    return any(differ(a / sub, b / sub) for sub in cmp.common_dirs)


def newest_mtime(p: Path) -> float:
    """Newest non-cruft file mtime under p. 0.0 when empty/absent."""
    return max(
        (f.stat().st_mtime for f in p.rglob("*") if f.is_file() and not is_cruft(f)),
        default=0.0,
    )


def project_newer(name: str) -> bool:
    """True when the mirror differs from live AND is more recent (the anomaly:
    the project may hold a version the source of truth lacks)."""
    src, dst = SRC_ROOT / name, DST_ROOT / name
    return dst.is_dir() and differ(src, dst) and newest_mtime(dst) > newest_mtime(src) + 1


_BANNER = "!" * 72


def warn_project_newer(names: list[str]) -> None:
    print(f"\n{_BANNER}")
    print("!!  PROJECT-NEWER — the repo mirror is MORE RECENT than the live source for:")
    print(f"!!      {', '.join(names)}")
    print("!!  The project may hold changes NOT in ~/.claude/skills/; a sync would")
    print("!!  overwrite them. Back-port to the live source first, or pass --force.")
    print(_BANNER)
