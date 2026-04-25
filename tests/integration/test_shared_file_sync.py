"""Contract test: propagated copies stay byte-equal to their canonical source.

`.githooks/pre-commit` copies each entry in its `SHARED_FILES` map from
a canonical location into every eligible plugin's target subdirectory.
This test parses that map, hashes the canonical and every vendored
copy, and asserts equality — so drift introduced by bypassed hooks,
direct branch pushes, or a rebase that skips the hook surfaces here
instead of at runtime.

The failure message names the drifting file and points at
`.githooks/pre-commit` as the fix point.
"""

from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path


HOOK_PATH = ".githooks/pre-commit"
_ENTRY_RE = re.compile(r'^\s*"([^"]+):([^"]+)"\s*$')


def _project_root() -> Path:
    conftest_dir = Path(__file__).parent
    result = subprocess.run(
        ["git", "-C", str(conftest_dir), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
    )
    return Path(result.stdout.strip()).resolve()


def _parse_shared_files(hook_text: str) -> list[tuple[str, str]]:
    """Extract (canonical, target_subdir) entries from the SHARED_FILES array."""
    entries: list[tuple[str, str]] = []
    in_array = False
    for line in hook_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("SHARED_FILES=("):
            in_array = True
            continue
        if in_array and stripped == ")":
            break
        if not in_array:
            continue
        match = _ENTRY_RE.match(line)
        if match:
            entries.append((match.group(1), match.group(2)))
    return entries


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _source_plugin(canonical: str) -> str | None:
    """Return the plugin name that owns canonical when it lives under plugins/,
    else None (canonical sources at project root are owned by no plugin)."""
    if not canonical.startswith("plugins/"):
        return None
    return canonical[len("plugins/"):].split("/", 1)[0]


def _expected_copies(
    project_root: Path,
    canonical: str,
    target_subdir: str,
) -> list[Path]:
    """Every plugin eligible to receive this canonical — opt-in by
    presence of the target subdirectory. Mirrors the pre-commit loop.
    """
    source_plugin = _source_plugin(canonical)
    filename = Path(canonical).name
    plugins_dir = project_root / "plugins"
    copies: list[Path] = []
    for plugin_dir in sorted(plugins_dir.iterdir()):
        if not plugin_dir.is_dir():
            continue
        if source_plugin is not None and plugin_dir.name == source_plugin:
            continue
        dest_dir = plugin_dir / target_subdir
        if not dest_dir.is_dir():
            continue
        copies.append(dest_dir / filename)
    return copies


class TestSharedFileSync:
    def test_every_canonical_matches_every_vendored_copy(self) -> None:
        root = _project_root()
        hook_text = (root / HOOK_PATH).read_text()
        entries = _parse_shared_files(hook_text)
        assert entries, (
            f"no SHARED_FILES entries parsed from {HOOK_PATH} — "
            "parser or hook format regressed"
        )

        for canonical, target_subdir in entries:
            canonical_path = root / canonical
            assert canonical_path.is_file(), (
                f"canonical source missing: {canonical} — "
                f"update {HOOK_PATH} to reflect actual layout"
            )
            canonical_hash = _hash(canonical_path)
            for copy in _expected_copies(root, canonical, target_subdir):
                assert copy.is_file(), (
                    f"expected vendored copy missing: {copy.relative_to(root)} — "
                    f"canonical at {canonical} has no counterpart; "
                    f"re-run the commit to let {HOOK_PATH} propagate"
                )
                assert _hash(copy) == canonical_hash, (
                    f"drift between {canonical} and {copy.relative_to(root)} — "
                    f"edit the canonical source and stage it so {HOOK_PATH} "
                    f"resyncs the copy"
                )
