"""Conventions operations.

Reads manifest.yaml for convention patterns and dependencies.
Matches file paths against patterns. Produces topological ordering
for self-evaluation.
"""

import fnmatch
from pathlib import Path


def load_manifest(manifest_path: Path) -> dict[str, dict]:
    """Load manifest.yaml. Returns {relative_path: {pattern, dependencies}} map.

    Simple parser for the specific manifest structure — no PyYAML dependency.
    Raises FileNotFoundError if manifest does not exist.
    """
    content = manifest_path.read_text()
    result: dict[str, dict] = {}

    current_path = None
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped or stripped == "conventions:":
            continue

        # Entry key: "  .claude/rules/ocd-auth.md:"
        indent = len(line) - len(line.lstrip())
        if indent == 2 and stripped.endswith(":"):
            current_path = stripped[:-1]
            result[current_path] = {"pattern": "", "dependencies": []}
            continue

        if current_path is None:
            continue

        # Pattern: '    pattern: "*.py"'
        if stripped.startswith("pattern:"):
            value = stripped[len("pattern:"):].strip()
            result[current_path]["pattern"] = value.strip('"').strip("'")

        # Dependencies: '    dependencies: [.claude/rules/ocd-auth.md, .claude/ocd/conventions/cli.md]'
        elif stripped.startswith("dependencies:"):
            value = stripped[len("dependencies:"):].strip()
            value = value.strip("[]")
            if value:
                result[current_path]["dependencies"] = [
                    item.strip().strip('"').strip("'") for item in value.split(",")
                ]

    return result


def list_patterns(manifest_path: Path) -> list[tuple[str, str]]:
    """Return all conventions with their patterns. Returns [(path, pattern)] sorted by path."""
    manifest = load_manifest(manifest_path)
    return sorted((path, entry["pattern"]) for path, entry in manifest.items())


def list_matching(manifest_path: Path, file_paths: list[str]) -> dict[str, list[str]]:
    """Match target files against convention patterns.

    Returns {target_file: [matching_convention_paths]} map. Only files
    with at least one match are included.
    """
    manifest = load_manifest(manifest_path)
    result: dict[str, list[str]] = {}

    for file_path in file_paths:
        basename = Path(file_path).name
        matches = []
        for conv_path, entry in manifest.items():
            pattern = entry["pattern"]
            if fnmatch.fnmatch(basename, pattern) or fnmatch.fnmatch(file_path, pattern):
                matches.append(conv_path)
        if matches:
            result[file_path] = sorted(matches)

    return result


def topological_order(manifest_path: Path) -> list[list[str]]:
    """Topologically sort conventions by dependency order.

    Returns list of levels. Each level is a list of convention paths.
    Level 0 contains roots (no dependencies). Level N depends only on
    levels 0..N-1. Paths within same level are sorted alphabetically.

    Raises ValueError on missing dependencies or cycles.
    """
    manifest = load_manifest(manifest_path)

    if not manifest:
        return []

    # Validate dependencies exist
    all_paths = set(manifest)
    for path, entry in manifest.items():
        for dep in entry["dependencies"]:
            if dep not in all_paths:
                raise ValueError(f"{path} depends on {dep}, which was not found in manifest")

    # Kahn's algorithm with level tracking
    in_degree = {path: len(entry["dependencies"]) for path, entry in manifest.items()}

    levels: list[list[str]] = []
    current = sorted(p for p in in_degree if in_degree[p] == 0)

    while current:
        levels.append(current)
        next_level = []
        for node in current:
            for path, entry in manifest.items():
                if node in entry["dependencies"]:
                    in_degree[path] -= 1
                    if in_degree[path] == 0:
                        next_level.append(path)
        current = sorted(set(next_level))

    remaining = [p for p in in_degree if in_degree[p] > 0]
    if remaining:
        raise ValueError(f"Dependency cycle detected among: {', '.join(sorted(remaining))}")

    return levels


def validate_manifest(manifest_path: Path) -> dict:
    """Validate manifest against disk. Returns {missing: [...], untracked: [...]}.

    missing: paths in manifest but not on disk
    untracked: .md files in conventions dir not in manifest
    """
    # manifest is at .claude/ocd/conventions/manifest.yaml — 4 levels to project root
    project_dir = manifest_path.parent.parent.parent.parent
    manifest = load_manifest(manifest_path)
    conventions_dir = manifest_path.parent

    missing = []
    for path in manifest:
        full_path = project_dir / path
        if not full_path.exists():
            missing.append(path)

    untracked = []
    if conventions_dir.is_dir():
        manifest_basenames = {Path(p).name for p in manifest}
        for f in sorted(conventions_dir.glob("*.md")):
            if f.name not in manifest_basenames:
                untracked.append(str(f.relative_to(project_dir)))

    return {"missing": missing, "untracked": untracked}
