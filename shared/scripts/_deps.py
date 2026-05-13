"""Resolve and ensure a markdown file's declared dependencies, transitively.

Reads YAML frontmatter from a markdown file for a `dependencies`
block-list, applies the resolution order from the `markdown-dependency-resolution`
rule, deploys the skill's bundled fallback if nothing is found, and
recursively resolves each resolved rule's own declared deps. Cycle-safe
via a visited set; output is the full transitive closure.

Invocation:

    uv run _deps.py                 # reads <skill-root>/SKILL.md
    uv run _deps.py <path>          # reads <path> (absolute or relative
                                    # to the enclosing skill root)

Component markdown files (`_<verb>.md`) declare their own deps in
frontmatter and are read via the path form, so verb-specific deps load
only when the verb fires. Rules can also declare frontmatter deps;
those cascade. The body-level `[[name]]` cross-reference convention
(see the `markdown` rule) aligns body references with frontmatter
declarations.

Output (stdout) — data only; the consuming workflow owns the load
directive (see the `markdown-dependency-resolution` rule):

    Dependencies for this skill:
    - <absolute path>
    - <absolute path>

Exit code 0 on success (resolved, possibly with silent deploys).
Exit code 1 when a declared dependency has no bundled fallback and is
not present at any deployed location, or when the path argument does
not point at a readable markdown file.
"""

import shutil
import sys
from pathlib import Path

# Sibling import — _deps.py and _environment.py travel together in
# every skill's scripts/ folder.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _environment import get_claude_home, get_project_dir  # noqa: E402


def _skill_root() -> Path:
    """Walk up from this script to the enclosing skill folder.

    Layout assumption: <skill>/scripts/_deps.py — script's parent is
    scripts/, script's parent's parent is the skill folder.
    """
    return Path(__file__).resolve().parent.parent


def _scope_claude_dir() -> Path:
    """Detect the .claude/ directory of the scope where this skill is installed.

    Walks up from the skill folder. When the skill lives at
    `<scope>/.claude/skills/<name>/`, the scope's .claude/ is two
    levels above the skill folder. Falls back to the active project's
    .claude/ when the layout isn't recognized (e.g., the skill runs
    from a plugin cache or from this project's own source tree during
    development).
    """
    skill_root = _skill_root()
    candidate = skill_root.parent.parent
    home = get_claude_home()
    if candidate == home:
        return home
    if candidate.name == ".claude":
        return candidate
    return get_project_dir() / ".claude"


def _parse_frontmatter_dependencies(skill_md: Path) -> list[str]:
    """Return the `dependencies` block-list from SKILL.md's YAML frontmatter.

    Block-list form is the only supported syntax:

        ---
        dependencies:
          - name-one
          - name-two
        ---

    Stdlib-only — no PyYAML dependency. Empty list when no SKILL.md,
    no frontmatter, or no `dependencies` key.
    """
    if not skill_md.is_file():
        return []
    lines = skill_md.read_text().splitlines()
    if not lines or lines[0].strip() != "---":
        return []
    deps: list[str] = []
    in_block = False
    for line in lines[1:]:
        stripped = line.strip()
        if stripped == "---":
            break
        if not in_block:
            if line.startswith("dependencies:"):
                rest = line.split(":", 1)[1].strip()
                if rest:
                    raise ValueError(
                        f"`dependencies` must use block-list form (one '- name' "
                        f"per line); got inline value: {rest}"
                    )
                in_block = True
            continue
        if stripped.startswith("- "):
            deps.append(stripped[2:].strip().strip('"').strip("'"))
        elif line and not line.startswith((" ", "\t")):
            in_block = False
    return deps


def _resolve(name: str, skill_root: Path, scope_claude: Path) -> tuple[str, Path]:
    """Find the resolved path for one dependency, deploying fallback if needed.

    Resolution order is asymmetric by install scope. User-scope skills
    only check user scope (so they stay portable across projects);
    project-scope skills check project first, falling back to user-scope
    promotions as defaults.

    Returns (location, path) where location is `rules` (deployed under
    `rules/dependencies/`) or `dependencies` (deployed under
    `dependencies/`). Raises RuntimeError when the dep is absent
    everywhere and the skill has no bundled copy to deploy.
    """
    user_claude = get_claude_home()
    is_user_scope = scope_claude == user_claude

    candidates: list[tuple[str, Path]] = []
    if not is_user_scope:
        candidates.append(("rules", scope_claude / "rules" / "dependencies" / f"{name}.md"))
    candidates.append(("rules", user_claude / "rules" / "dependencies" / f"{name}.md"))
    if not is_user_scope:
        candidates.append(("dependencies", scope_claude / "dependencies" / f"{name}.md"))
    candidates.append(("dependencies", user_claude / "dependencies" / f"{name}.md"))

    for location, candidate in candidates:
        if candidate.is_file():
            return (location, candidate)

    bundled = skill_root / "_dependencies" / f"{name}.md"
    if not bundled.is_file():
        raise RuntimeError(
            f"dependency '{name}' is not present at any deployed location and "
            f"the skill has no bundled copy at {bundled} — declare the dep in "
            f"SKILL.md frontmatter only when the skill bundles its seed at "
            f"<skill>/_dependencies/{name}.md"
        )
    target = scope_claude / "dependencies" / f"{name}.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(bundled, target)
    return ("dependencies", target)


def _resolve_md_path(argv: list[str], skill_root: Path) -> Path:
    """Resolve the markdown file whose frontmatter to read.

    No arg → SKILL.md at the skill root. One positional arg → that path,
    absolute or skill-root-relative. Component verb files invoke with
    their own path so verb-specific deps load only when the verb fires.
    """
    if not argv:
        return skill_root / "SKILL.md"
    arg = Path(argv[0])
    md_path = arg if arg.is_absolute() else (skill_root / arg)
    md_path = md_path.resolve()
    if not md_path.is_file():
        raise RuntimeError(
            f"markdown file not found: {md_path} — pass an absolute path "
            f"or a path relative to the skill root ({skill_root})"
        )
    return md_path


def main(argv: list[str]) -> int:
    skill_root = _skill_root()
    scope_claude = _scope_claude_dir()
    md_path = _resolve_md_path(argv, skill_root)

    # BFS over the dep graph. Each resolved rule's own frontmatter may
    # declare further deps; the visited set prevents cycles.
    resolved_paths: list[Path] = []
    visited: set[str] = set()
    queue: list[str] = list(_parse_frontmatter_dependencies(md_path))
    while queue:
        name = queue.pop(0)
        if name in visited:
            continue
        visited.add(name)
        _, path = _resolve(name, skill_root, scope_claude)
        resolved_paths.append(path)
        for child in _parse_frontmatter_dependencies(path):
            if child not in visited:
                queue.append(child)

    if not resolved_paths:
        return 0

    print("Dependencies for this skill:")
    for path in resolved_paths:
        print(f"- {path}")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except (RuntimeError, ValueError) as e:
        print(f"deps: {e}", file=sys.stderr)
        sys.exit(1)
