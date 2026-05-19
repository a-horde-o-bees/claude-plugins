"""Fetch composition.md sources into <skill-dir>/sources/<slug>/ on demand.

The skill reads upstream content (scripts, agent prompts, schemas, eval-viewer
assets) from sources/<slug>/ at runtime. Those checkouts are gitignored and
re-fetched as needed — composition.md is the canonical record of url +
pinned commit; the on-disk checkout is a cache.

Idempotent:
- Missing checkout → clone fresh and checkout the pinned commit
- Present checkout at the pinned commit → reuse, no network
- Present checkout at the wrong commit → remove and re-fetch

Always writes a defensive `sources/.gitignore` containing `*` so the checkout
stays out of git history even if the skill is extracted to a repo without
a project-level rule.

Invocation from a workflow file:

    cd <THIS-FILE-DIR> && uv run python -m scripts._sources

Or programmatically:

    from scripts._sources import ensure_all
    ensure_all(Path('<skill-dir>'))
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


def _parse_sources_block(frontmatter_text: str) -> list[dict[str, str]]:
    """Extract the `sources:` block from composition.md frontmatter.

    Same bounded YAML subset that skill-composer's _spec.py emits — block list
    with two-space indentation, scalar values, optional double-quote wrapping.
    """
    lines = frontmatter_text.split("\n")
    sources: list[dict[str, str]] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip() == "sources:":
            i += 1
            current: dict[str, str] = {}
            while i < len(lines):
                inner = lines[i]
                if not inner.startswith(("- ", "  ")):
                    break
                if inner.startswith("- "):
                    if current:
                        sources.append(current)
                    current = {}
                    key, _, value = inner[2:].partition(":")
                else:
                    key, _, value = inner[2:].partition(":")
                current[key.strip()] = value.strip().strip('"')
                i += 1
            if current:
                sources.append(current)
            return sources
        i += 1
    return sources


def _read_composition_sources(composition_path: Path) -> list[dict[str, str]]:
    """Return the list of source entries declared in composition.md frontmatter."""
    text = composition_path.read_text()
    if not text.startswith("---"):
        return []
    end = text.find("\n---", 3)
    if end < 0:
        return []
    frontmatter = text[3:end].lstrip("\n")
    return _parse_sources_block(frontmatter)


def _derive_slug(url: str, skill_name: str) -> str:
    """Reproduce the existing slug pattern: <owner>-<repo>--<skill>."""
    cleaned = url.removesuffix(".git").rstrip("/")
    parts = cleaned.split("/")
    owner_repo = f"{parts[-2]}-{parts[-1]}"
    return f"{owner_repo}--{skill_name}" if skill_name else owner_repo


def ensure_source(skill_dir: Path, source: dict[str, str]) -> Path:
    """Ensure one source is present at its pinned commit. Returns its path.

    When `skill_name` is set in the source entry, only the upstream's
    `skills/<skill_name>/` subfolder is extracted to the target (matching
    the original vendoring layout so body path references at
    `sources/<slug>/<file>` resolve correctly). When unset, the repo
    root is used.

    A `.pin` file inside the target records the commit SHA for idempotency
    checks — the `.git` directory does not survive the subtree extraction.
    """
    url = source["url"]
    commit = source["commit"]
    skill_name = source.get("skill", "")
    slug = _derive_slug(url, skill_name)

    sources_dir = skill_dir / "sources"
    sources_dir.mkdir(exist_ok=True)
    gitignore = sources_dir / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("*\n")

    target = sources_dir / slug
    pin_file = target / ".pin"
    if pin_file.exists() and pin_file.read_text().strip() == commit:
        return target

    if target.exists():
        shutil.rmtree(target)

    tmp_clone = sources_dir / f".{slug}.fetching"
    if tmp_clone.exists():
        shutil.rmtree(tmp_clone)

    subprocess.run(
        ["git", "clone", "--quiet", url, str(tmp_clone)],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(tmp_clone), "checkout", "--quiet", commit],
        check=True,
    )

    if skill_name:
        subtree = tmp_clone / "skills" / skill_name
        if not subtree.is_dir():
            shutil.rmtree(tmp_clone)
            raise FileNotFoundError(
                f"path 'skills/{skill_name}' not found in {url}@{commit}"
            )
        shutil.move(str(subtree), str(target))
    else:
        target.mkdir()
        for item in tmp_clone.iterdir():
            if item.name == ".git":
                continue
            shutil.move(str(item), str(target / item.name))

    shutil.rmtree(tmp_clone)
    pin_file.write_text(commit + "\n")
    return target


def ensure_all(skill_dir: Path) -> list[Path]:
    """Ensure every source in <skill-dir>/composition.md is present at its pin."""
    composition = skill_dir / "composition.md"
    if not composition.exists():
        return []
    return [ensure_source(skill_dir, s) for s in _read_composition_sources(composition)]


def main() -> int:
    skill_dir = Path(sys.argv[1] if len(sys.argv) > 1 else __file__).resolve()
    if skill_dir.is_file():
        skill_dir = skill_dir.parent.parent
    paths = ensure_all(skill_dir)
    for p in paths:
        print(p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
