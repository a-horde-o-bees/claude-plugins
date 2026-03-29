"""Generic plugin framework.

Universal deployment, formatting, skill discovery, and orchestration
for init and status operations. No plugin-specific logic — skill
infrastructure lives in skill-level _init.py files.

Propagated to every plugin via pre-commit hook.
"""

import importlib
import json
import os
import shutil
import sys
from pathlib import Path


# --- Environment ---


def get_plugin_root() -> Path:
    """Resolve plugin root from CLAUDE_PLUGIN_ROOT or script location."""
    env = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if env:
        return Path(env)
    return Path(__file__).parent.parent


def get_project_dir() -> Path:
    """Resolve project directory from environment or cwd."""
    return Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))


def get_claude_home() -> Path:
    return Path.home() / ".claude"


# --- Plugin metadata ---


def read_json(path: Path) -> dict:
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def get_installed_version(plugin_root: Path) -> str:
    data = read_json(plugin_root / ".claude-plugin" / "plugin.json")
    return data.get("version", "unknown")


def get_plugin_name(plugin_root: Path) -> str:
    data = read_json(plugin_root / ".claude-plugin" / "plugin.json")
    return data.get("name", "unknown")


def find_marketplace_source(
    plugin_name: str, plugin_root: Path, claude_home: Path,
) -> tuple[str | None, str | None]:
    """Find source version for local-directory marketplaces.

    Returns (source_version, marketplace_name) tuple.
    Both None if not a local marketplace or if any lookup fails.
    """
    installed = read_json(claude_home / "plugins" / "installed_plugins.json")
    plugins = installed.get("plugins", {})

    marketplace_name = None
    plugin_root_str = str(plugin_root)
    for key, entries in plugins.items():
        for entry in entries:
            if entry.get("installPath") == plugin_root_str:
                parts = key.split("@", 1)
                if len(parts) == 2:
                    marketplace_name = parts[1]
                break
        if marketplace_name:
            break

    if not marketplace_name:
        return None, None

    known = read_json(claude_home / "plugins" / "known_marketplaces.json")
    marketplace = known.get(marketplace_name, {})
    source = marketplace.get("source", {})

    if source.get("source") != "directory":
        return None, marketplace_name

    marketplace_path = Path(source.get("path", ""))
    if not marketplace_path.is_dir():
        return None, marketplace_name

    manifest = read_json(marketplace_path / ".claude-plugin" / "marketplace.json")
    for plugin_entry in manifest.get("plugins", []):
        if plugin_entry.get("name") == plugin_name:
            plugin_source = plugin_entry.get("source", "")
            source_dir = (marketplace_path / plugin_source).resolve()
            source_plugin = read_json(source_dir / ".claude-plugin" / "plugin.json")
            return source_plugin.get("version"), marketplace_name

    return None, marketplace_name


def format_header(
    plugin_name: str,
    installed_version: str,
    source_version: str | None,
    marketplace_name: str | None,
) -> str:
    parts = [f"{plugin_name} v{installed_version}"]
    if source_version and source_version != installed_version:
        parts.append(f"update available: v{source_version}")
    elif source_version:
        parts.append("up to date")
    return " | ".join(parts)


# --- Deployment primitives ---


def stamp_deployed(path: Path) -> None:
    """Replace type: template with type: deployed in frontmatter only."""
    content = path.read_text()
    if not content.startswith("---\n"):
        return
    end = content.index("\n---\n", 4)
    frontmatter = content[: end + 5]
    stamped = frontmatter.replace("type: template", "type: deployed")
    path.write_text(stamped + content[end + 5 :])


def compare_deployed(src: Path, dst: Path) -> str:
    """Compare single source template against deployed file.

    Returns:
    - "absent": dst does not exist
    - "current": dst matches src (with template->deployed stamp applied)
    - "divergent": dst exists but content differs from src
    """
    if not dst.exists():
        return "absent"
    src_deployed = src.read_bytes().replace(b"type: template", b"type: deployed", 1)
    if src_deployed == dst.read_bytes():
        return "current"
    return "divergent"


def deploy_files(
    src_dir: Path, dst_dir: Path, pattern: str = "*.md", force: bool = False,
) -> list[dict]:
    """Deploy template files from src_dir to dst_dir.

    Returns list of {name, before, after} dicts.
    """
    dst_dir.mkdir(parents=True, exist_ok=True)
    results = []

    if not src_dir.is_dir():
        return results

    for src in sorted(src_dir.glob(pattern)):
        if not src.is_file():
            continue
        dst = dst_dir / src.name
        before = compare_deployed(src, dst)

        if before == "absent":
            shutil.copy2(src, dst)
            stamp_deployed(dst)
            after = "current"
        elif before == "divergent" and force:
            shutil.copy2(src, dst)
            stamp_deployed(dst)
            after = "current"
        else:
            after = before

        results.append({"name": src.name, "before": before, "after": after})

    return results


# --- Formatting ---


def format_columns(rows: list[tuple[str, ...]], separator: str = "  ") -> list[str]:
    """Format rows into aligned columns."""
    if not rows:
        return []
    widths = [max(len(cell) for cell in col) for col in zip(*rows)]
    return [separator.join(cell.ljust(w) for cell, w in zip(row, widths)).rstrip() for row in rows]


def format_section(header: str, items: list[dict], extra: list[dict] | None = None) -> list[str]:
    """Render a section with header, file items, and optional extra lines.

    Items are dicts with {path, before, after}.
    Extra are dicts with {label, value}.
    """
    rows = []
    for item in items:
        if item["before"] == item["after"]:
            value = item["after"]
        else:
            value = f"{item['before']} \u2192 {item['after']}"
        rows.append((item["path"], value))

    if extra:
        for e in extra:
            rows.append((e["label"], e["value"]))

    lines = [header]
    for row in format_columns(rows):
        lines.append(f"  {row}")
    return lines


def format_bare_skill(plugin_name: str, skill_name: str) -> str:
    """Render a skill header with no infrastructure."""
    return f"/{plugin_name}-{skill_name}"




# --- Rules ---


def deploy_rules(plugin_root: Path, project_dir: Path, force: bool = False) -> list[dict]:
    """Deploy rule files. Returns [{path, before, after}] with relative deployed paths."""
    results = deploy_files(
        src_dir=plugin_root / "rules",
        dst_dir=project_dir / ".claude" / "rules",
        pattern="*.md",
        force=force,
    )
    for r in results:
        r["path"] = f".claude/rules/{r.pop('name')}"
    return results


def get_rules_states(plugin_root: Path, project_dir: Path) -> list[dict]:
    """Get state of each rule file. Returns [{path, before, after}]."""
    src_dir = plugin_root / "rules"
    if not src_dir.is_dir():
        return []

    results = []
    for src in sorted(src_dir.glob("*.md")):
        if not src.is_file():
            continue
        dst = project_dir / ".claude" / "rules" / src.name
        state = compare_deployed(src, dst)
        results.append({
            "path": f".claude/rules/{src.name}",
            "before": state,
            "after": state,
        })
    return results


# --- Skill discovery ---


def _discover_skills(plugin_root: Path) -> list[tuple[str, bool]]:
    """Discover all skills. Returns [(name, has_init)] sorted by name.

    has_init is True if the skill has scripts/_init.py (infrastructure skill).
    """
    skills_dir = plugin_root / "skills"
    if not skills_dir.is_dir():
        return []

    skills = []
    for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
        name = skill_md.parent.name
        init_path = skill_md.parent / "_init.py"
        skills.append((name, init_path.is_file()))
    return skills


# --- Orchestration ---


_META_SKILLS = {"init", "status"}


def run_init(force: bool = False) -> None:
    """Generic init: deploy rules, call skill init hooks. Prints unified output."""
    plugin_root = get_plugin_root()
    project_dir = get_project_dir()
    plugin_name = get_plugin_name(plugin_root)

    print(f"{plugin_name} init")
    print()

    # Rules
    rules = deploy_rules(plugin_root, project_dir, force=force)
    for line in format_section("Rules", rules):
        print(line)
    print()

    # Skills
    skills = _discover_skills(plugin_root)
    for skill_name, has_init in skills:
        if not has_init:
            continue
        mod = importlib.import_module(f"skills.{skill_name}._init")
        result = mod.init(plugin_root, project_dir, force=force)
        header = f"/{plugin_name}-{skill_name}"
        for line in format_section(header, result["files"], result.get("extra")):
            print(line)
        print()

    # Bare skills
    for skill_name, has_init in skills:
        if has_init or skill_name in _META_SKILLS:
            continue
        print(format_bare_skill(plugin_name, skill_name))

    # Footer
    rules_changed = any(r["before"] != r["after"] for r in rules)
    if rules_changed:
        print()
        print("Done. Restart Claude session to load new rules.")
    else:
        print()
        print("Done.")


def run_status() -> None:
    """Generic status: check rules, call skill status hooks. Prints unified output."""
    plugin_root = get_plugin_root()
    project_dir = get_project_dir()
    claude_home = get_claude_home()

    plugin_name = get_plugin_name(plugin_root)
    installed_version = get_installed_version(plugin_root)
    source_version, marketplace_name = find_marketplace_source(
        plugin_name, plugin_root, claude_home,
    )

    print(format_header(plugin_name, installed_version, source_version, marketplace_name))
    print()

    # Rules
    rules = get_rules_states(plugin_root, project_dir)
    for line in format_section("Rules", rules):
        print(line)
    print()

    # Skills
    skills = _discover_skills(plugin_root)
    for skill_name, has_init in skills:
        if not has_init:
            continue
        mod = importlib.import_module(f"skills.{skill_name}._init")
        result = mod.status(plugin_root, project_dir)
        header = f"/{plugin_name}-{skill_name}"
        for line in format_section(header, result["files"], result.get("extra")):
            print(line)
        print()

    # Bare skills
    for skill_name, has_init in skills:
        if has_init or skill_name in _META_SKILLS:
            continue
        print(format_bare_skill(plugin_name, skill_name))










