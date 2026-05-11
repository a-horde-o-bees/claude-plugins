"""Path resolution for skill folders, source embeds, and the plugin data dir.

Under the redesigned model, every deployed skill (composed or installed)
is a self-contained folder at `<scope>/.claude/skills/<name>/` holding
SKILL.md, composition.md, and (for compositions during development) a
`sources/<source-slug>/` subfolder per embedded exemplar.

No shared cache directory. No separate compositions/ working area. No
sources.json or install registry — each skill's composition.md is its
own provenance record; walking `<scope>/.claude/skills/*/composition.md`
enumerates every deployed skill the plugin owns.
"""

import hashlib
import os
import re
import subprocess
from pathlib import Path
from urllib.parse import urlparse


CLAUDE_PLUGIN_DATA_ENV = "CLAUDE_PLUGIN_DATA"
CLAUDE_PLUGIN_ROOT_ENV = "CLAUDE_PLUGIN_ROOT"
CLAUDE_PROJECT_DIR_ENV = "CLAUDE_PROJECT_DIR"
CLAUDE_HOME_ENV = "CLAUDE_HOME"


def get_plugin_root() -> Path:
    """Walk up from this file until `.claude-plugin/plugin.json` is found."""
    env = os.environ.get(CLAUDE_PLUGIN_ROOT_ENV)
    if env:
        return Path(env).resolve()
    here = Path(__file__).resolve()
    for ancestor in here.parents:
        if (ancestor / ".claude-plugin" / "plugin.json").exists():
            return ancestor
    raise RuntimeError(
        f"plugin root not found walking up from {here} — no ancestor "
        f"contains .claude-plugin/plugin.json. Set {CLAUDE_PLUGIN_ROOT_ENV} "
        "explicitly when running outside a plugin tree."
    )


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


def get_claude_home() -> Path:
    env = os.environ.get(CLAUDE_HOME_ENV)
    if env:
        return Path(env).resolve()
    return (Path.home() / ".claude").resolve()


def get_project_dir() -> Path:
    """Resolve the active project directory: env var, then git root.

    Defensive guard — refuses any resolution that lands inside Claude
    home. Caches at `~/.claude/plugins/.../skills/<name>/` are themselves
    git checkouts; without the guard, `git rev-parse --show-toplevel`
    fired from a cache subdirectory returns `~/.claude` and the script
    then writes to `~/.claude/.claude/skills/`. The corrective error
    names the env var the caller should set.
    """
    claude_home = get_claude_home()

    def _reject_if_inside_home(path: Path) -> None:
        try:
            path.relative_to(claude_home)
        except ValueError:
            return
        raise RuntimeError(
            f"resolved project directory {path} is inside Claude home "
            f"({claude_home}) — set {CLAUDE_PROJECT_DIR_ENV} to your "
            "project root explicitly. Common cause: invoking from a "
            "plugin cache subdirectory."
        )

    env = os.environ.get(CLAUDE_PROJECT_DIR_ENV)
    if env:
        path = Path(env).resolve()
        if path.is_dir():
            _reject_if_inside_home(path)
            return path
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        path = Path(result.stdout.strip()).resolve()
        if path.is_dir():
            _reject_if_inside_home(path)
            return path
    raise RuntimeError(
        f"project directory not discoverable — set {CLAUDE_PROJECT_DIR_ENV} "
        "or invoke from within a git checkout"
    )


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
