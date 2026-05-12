"""Contract test: propagated copies stay byte-equal to their canonical source.

`.githooks/pre-commit` propagates each file matching its `canonicals=(...)`
glob array — files at project-root `shared/<subfolder>/<file>` — into every
`<plugin>/skills/<name>/<subfolder>/<file>` that already exists
(file-existence opt-in). This test parses the canonicals globs, expands
them against the filesystem, walk-scans every skill-level vendored copy
of each canonical, and hashes each copy against its canonical — so drift
introduced by bypassed hooks, direct branch pushes, or a rebase that
skips the hook surfaces here instead of at runtime.

The failure message names the drifting file and points at
`.githooks/pre-commit` as the fix point.
"""

from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path


HOOK_PATH = ".githooks/pre-commit"
_ARRAY_RE = re.compile(r"^\s*canonicals=\(\s*(.+?)\s*\)\s*$")


def _project_root() -> Path:
    conftest_dir = Path(__file__).parent
    result = subprocess.run(
        ["git", "-C", str(conftest_dir), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
    )
    return Path(result.stdout.strip()).resolve()


def _parse_canonicals(hook_text: str, root: Path) -> list[str]:
    """Resolve the `canonicals=(...)` globs against the filesystem."""
    patterns: list[str] = []
    for line in hook_text.splitlines():
        match = _ARRAY_RE.match(line)
        if match:
            patterns = match.group(1).split()
            break
    resolved: list[str] = []
    for pattern in patterns:
        for path in sorted(root.glob(pattern)):
            if path.is_file() and path.name != "__init__.py":
                resolved.append(str(path.relative_to(root)))
    return resolved


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _skill_level_copies(root: Path, relpath: str) -> list[Path]:
    """Every skill-level vendored copy at the given relpath under each skill.

    Walks `plugins/*/skills/*/<relpath>` for files matching the path
    relative to the skill root — these are the file-existence-opt-in
    copies the pre-commit hook keeps byte-equal to canonical.
    """
    copies: list[Path] = []
    plugins_dir = root / "plugins"
    if not plugins_dir.is_dir():
        return copies
    for plugin_dir in sorted(plugins_dir.iterdir()):
        skills_dir = plugin_dir / "skills"
        if not skills_dir.is_dir():
            continue
        for skill_dir in sorted(skills_dir.iterdir()):
            target = skill_dir / relpath
            if target.is_file():
                copies.append(target)
    return copies


class TestSharedFileSync:
    def test_every_canonical_matches_every_skill_copy(self) -> None:
        root = _project_root()
        hook_text = (root / HOOK_PATH).read_text()
        canonicals = _parse_canonicals(hook_text, root)
        assert canonicals, (
            f"no canonicals globs resolved from {HOOK_PATH} — "
            "parser or hook format regressed"
        )

        for canonical in canonicals:
            assert canonical.startswith("shared/"), (
                f"canonical {canonical} does not start with shared/ — "
                f"hook propagation logic assumes the shared/ umbrella prefix"
            )
            canonical_path = root / canonical
            assert canonical_path.is_file(), (
                f"canonical source missing: {canonical} — "
                f"update {HOOK_PATH} to reflect actual layout"
            )
            canonical_hash = _hash(canonical_path)
            relpath = canonical[len("shared/"):]
            for copy in _skill_level_copies(root, relpath):
                assert _hash(copy) == canonical_hash, (
                    f"drift between {canonical} and {copy.relative_to(root)} — "
                    f"edit the canonical source and stage it so {HOOK_PATH} "
                    f"resyncs the copy"
                )
