"""Path resolution for skill folders, source embeds, and the plugin data dir.

Under the redesigned model, every deployed skill (composed or installed)
is a self-contained folder at `<scope>/.claude/skills/<name>/` holding
SKILL.md, composition.md, and (for compositions during development) a
`sources/<source-slug>/` subfolder per embedded exemplar.

No shared cache directory. No separate compositions/ working area. No
sources.json or install registry — each skill's composition.md is its
own provenance record; walking `<scope>/.claude/skills/*/composition.md`
enumerates every deployed skill the plugin owns.

Cross-cutting primitives (`get_project_dir`, `get_plugin_root`,
`get_claude_home`) come from this skill's own vendored copy of
`environment.py` — the canonical lives at project-root `dependencies/`
and propagates here via `.githooks/pre-commit`. Each skill bundles its
own copy so it runs independently of any plugin or project import path.
"""

import hashlib
import os
import re
from pathlib import Path
from urllib.parse import urlparse

from scripts._environment import (
    get_claude_home,
    get_plugin_root,
    get_project_dir,
)


CLAUDE_PLUGIN_DATA_ENV = "CLAUDE_PLUGIN_DATA"


def get_data_dir() -> Path:
    """Resolve the plugin data directory (transient state only).

    Holds nothing user-facing under the redesigned model — reserved for
    future transient state if any verb needs disk space the user shouldn't
    git-track. Currently unused at the script level; kept for parity with
    Claude Code's plugin data dir convention.
    """
    env = os.environ.get(CLAUDE_PLUGIN_DATA_ENV)
    if env:
        path = Path(env).resolve()
        path.mkdir(parents=True, exist_ok=True)
        return path

    plugin_root = get_plugin_root()
    parts = plugin_root.parts

    if "cache" in parts:
        idx = parts.index("cache")
        if idx + 3 < len(parts) and parts[idx - 1].endswith("plugins"):
            plugins_dir = Path(*parts[: idx])
            author = parts[idx + 1]
            plugin_name = parts[idx + 2]
            path = plugins_dir / "data" / f"{plugin_name}-{author}"
            path.mkdir(parents=True, exist_ok=True)
            return path

    plugin_basename = plugin_root.name
    path = (
        get_claude_home()
        / "plugins"
        / "data"
        / f"{plugin_basename}-inline"
    )
    path.mkdir(parents=True, exist_ok=True)
    return path


def destination_dir(destination: str, project_dir: Path | None = None) -> Path:
    """Resolve a destination string to the parent directory for composed skills.

    A composed skill is portable — `--destination` describes where the
    skill folder is stood up. Three forms:

    - `user` — the user-scope Claude Code skills location (`~/.claude/skills/`)
    - `project` — the project-scope Claude Code skills location
      (`<project-root>/.claude/skills/`)
    - any other value — treated as a path. Absolute paths used as-is;
      relative paths resolve against the project directory. This is how
      composed skills get placed adjacent to a plugin shell in a monorepo
      (e.g., `plugins/composed-skills/skills/`).
    """
    if destination == "user":
        return get_claude_home() / "skills"
    if destination == "project":
        if project_dir is None:
            project_dir = get_project_dir()
        return project_dir / ".claude" / "skills"
    path = Path(destination)
    if not path.is_absolute():
        if project_dir is None:
            project_dir = get_project_dir()
        path = project_dir / path
    return path.resolve()


def skill_folder(name: str, destination: str, project_dir: Path | None = None) -> Path:
    """Resolve a composed skill's folder."""
    return destination_dir(destination, project_dir) / name


def composition_path(
    name: str,
    destination: str,
    project_dir: Path | None = None,
) -> Path:
    """Resolve a composed skill's composition.md."""
    return skill_folder(name, destination, project_dir) / "composition.md"


def skill_md_path(
    name: str,
    destination: str,
    project_dir: Path | None = None,
) -> Path:
    """Resolve a composed skill's SKILL.md."""
    return skill_folder(name, destination, project_dir) / "SKILL.md"


def sources_subdir(
    name: str,
    destination: str,
    project_dir: Path | None = None,
) -> Path:
    """The `sources/` subfolder where embedded exemplar skills live."""
    return skill_folder(name, destination, project_dir) / "sources"


def source_embed_path(
    skill_name: str,
    source_slug: str,
    destination: str,
    project_dir: Path | None = None,
) -> Path:
    """Where one embedded exemplar source is sparse-checked into."""
    return sources_subdir(skill_name, destination, project_dir) / source_slug


_SLUG_PATTERN = re.compile(r"[^a-z0-9]+")


def compositions_in_destination(
    destination: str,
    project_dir: Path | None = None,
) -> list[Path]:
    """Return composition.md paths for every composed skill at the destination.

    Walks `<destination-dir>/*/composition.md`. Returns absolute paths
    sorted by skill folder name.
    """
    parent = destination_dir(destination, project_dir)
    if not parent.is_dir():
        return []
    results: list[Path] = []
    for entry in sorted(parent.iterdir()):
        if not entry.is_dir():
            continue
        spec = entry / "composition.md"
        if spec.is_file():
            results.append(spec)
    return results


def derive_source_slug(url: str, skill: str) -> str:
    """Stable slug derived from a repo URL plus skill name.

    Used for embed folder names — `sources/<slug>/SKILL.md`. Includes
    the skill segment so multiple skills from the same repo don't
    collide on the filesystem. Shape: `<repo-segments>--<skill>` with
    double-dash separator.

    Examples:
        https://github.com/anthropics/skills.git + pdf
            → anthropics-skills--pdf
        git@github.com:foo/bar.git + my-skill
            → foo-bar--my-skill
        file:///tmp/.../fixture-source + fixture-skill
            → <parent>-fixture-source--fixture-skill

    Empty or unusable URL paths fall back to a SHA-1 prefix of the URL
    for collision safety; the skill suffix is appended either way.
    """
    parsed = urlparse(url) if "://" in url else None
    if parsed and parsed.path:
        path = parsed.path.lstrip("/")
    else:
        # ssh-style git@host:owner/repo.git
        if ":" in url:
            path = url.split(":", 1)[1]
        else:
            path = url
    if path.endswith(".git"):
        path = path[: -len(".git")]

    segments = [s for s in path.split("/") if s]
    if len(segments) >= 2:
        slug_source = "-".join(segments[-2:])
    elif segments:
        slug_source = segments[0]
    else:
        slug_source = path

    repo_slug = _SLUG_PATTERN.sub("-", slug_source.lower()).strip("-")
    if not repo_slug:
        repo_slug = hashlib.sha1(url.encode("utf-8")).hexdigest()[:12]

    skill_slug = _SLUG_PATTERN.sub("-", skill.lower()).strip("-")
    return f"{repo_slug}--{skill_slug}"
