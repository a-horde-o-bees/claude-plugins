"""Path resolution and allowed-directory checking."""

from __future__ import annotations

from pathlib import Path


def resolve_path(file_path: str, project_dir: Path) -> Path:
    p = Path(file_path)
    if not p.is_absolute():
        return (project_dir / p).resolve()
    return p.resolve()


def is_within_directory(abs_path: Path, directory: Path) -> bool:
    resolved = directory.resolve()
    return abs_path == resolved or resolved in abs_path.parents


def get_allowed_directories(project_dir: Path, settings: dict) -> set[Path]:
    """Build set of allowed directories from merged settings."""
    dirs = {project_dir}
    for d in settings.get("permissions", {}).get("additionalDirectories", []):
        expanded = Path(d).expanduser()
        if not expanded.is_absolute():
            expanded = (project_dir / expanded).resolve()
        else:
            expanded = expanded.resolve()
        dirs.add(expanded)
    return dirs


def is_within_allowed_dirs(abs_path: Path, project_dir: Path, settings: dict) -> bool:
    for directory in get_allowed_directories(project_dir, settings):
        if is_within_directory(abs_path, directory):
            return True
    return False
