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
    """Resolve the active project directory: env var, then git root."""
    env = os.environ.get(CLAUDE_PROJECT_DIR_ENV)
    if env:
        path = Path(env).resolve()
        if path.is_dir():
            return path
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        path = Path(result.stdout.strip()).resolve()
        if path.is_dir():
            return path
    raise RuntimeError(
        f"project directory not discoverable — set {CLAUDE_PROJECT_DIR_ENV} "
        "or invoke from within a git checkout"
    )


def scope_skills_dir(scope: str, project_dir: Path | None = None) -> Path:
    """Where deployed skills (composed or installed) live for a scope."""
    if scope == "user":
        return get_claude_home() / "skills"
    if scope == "project":
        if project_dir is None:
            project_dir = get_project_dir()
        return project_dir / ".claude" / "skills"
    raise ValueError(f"unknown scope: {scope!r} — expected 'user' or 'project'")


def skill_folder(name: str, scope: str, project_dir: Path | None = None) -> Path:
    """Resolve a deployed skill's folder."""
    return scope_skills_dir(scope, project_dir) / name


def composition_path(
    name: str,
    scope: str,
    project_dir: Path | None = None,
) -> Path:
    """Resolve a deployed skill's composition.md."""
    return skill_folder(name, scope, project_dir) / "composition.md"


def skill_md_path(
    name: str,
    scope: str,
    project_dir: Path | None = None,
) -> Path:
    """Resolve a deployed skill's SKILL.md."""
    return skill_folder(name, scope, project_dir) / "SKILL.md"


def sources_subdir(
    name: str,
    scope: str,
    project_dir: Path | None = None,
) -> Path:
    """The `sources/` subfolder where embedded exemplar skills live."""
    return skill_folder(name, scope, project_dir) / "sources"


def source_embed_path(
    skill_name: str,
    source_slug: str,
    scope: str,
    project_dir: Path | None = None,
) -> Path:
    """Where one embedded exemplar source is sparse-checked into."""
    return sources_subdir(skill_name, scope, project_dir) / source_slug


_SLUG_PATTERN = re.compile(r"[^a-z0-9]+")


def compositions_in_scope(scope: str, project_dir: Path | None = None) -> list[Path]:
    """Return spec paths for every deployed skill at the given scope.

    Walks `<scope>/.claude/skills/*/composition.md`. Returns absolute
    paths sorted by skill folder name.
    """
    skills_dir = scope_skills_dir(scope, project_dir)
    if not skills_dir.is_dir():
        return []
    results: list[Path] = []
    for entry in sorted(skills_dir.iterdir()):
        if not entry.is_dir():
            continue
        spec = entry / "composition.md"
        if spec.is_file():
            results.append(spec)
    return results


def derive_source_slug(url: str) -> str:
    """Stable slug derived from a repo URL — used for embed folder names.

    Uses the last two path segments to stay readable across URL shapes:
        https://github.com/anthropics/skills.git → anthropics-skills
        git@github.com:foo/bar.git → foo-bar
        file:///tmp/.../fixture-source → <parent>-fixture-source

    Single-segment paths produce just that segment. Empty or unusable
    paths fall back to a SHA-1 prefix of the URL for collision safety.
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

    slug = _SLUG_PATTERN.sub("-", slug_source.lower()).strip("-")
    if not slug:
        slug = hashlib.sha1(url.encode("utf-8")).hexdigest()[:12]
    return slug
