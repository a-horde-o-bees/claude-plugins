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
    """Resolve plugin root from CLAUDE_PLUGIN_ROOT with __file__ fallback.

    Falls back to a deterministic walk from this module's own file
    position: plugin/__init__.py always lives at plugins/<name>/plugin/
    relative to the plugin root, so the walk is correct across dev,
    install cache, and any other install location.
    """
    env = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if env:
        return Path(env).resolve()
    return Path(__file__).resolve().parent.parent


def get_project_dir() -> Path:
    """Resolve project directory from CLAUDE_PROJECT_DIR.

    Raises when unset — project identity is not inferable from working
    directory. Claude Code sets this at runtime; scripts/run-plugin.sh
    exports it; tests set it explicitly in subprocess env or via
    monkeypatch.
    """
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if not env:
        raise RuntimeError(
            "CLAUDE_PROJECT_DIR is not set. Run under Claude Code, via "
            "scripts/run-plugin.sh, or set the variable explicitly."
        )
    return Path(env).resolve()


def get_plugin_data_dir() -> Path:
    """Resolve plugin data directory from CLAUDE_PLUGIN_DATA.

    Raises when unset — this is Claude Code-managed per-plugin persistent
    storage (venv, cached state) that survives plugin version upgrades
    and is not inferable from the install directory, the project, or
    the working directory.
    """
    env = os.environ.get("CLAUDE_PLUGIN_DATA")
    if not env:
        raise RuntimeError(
            "CLAUDE_PLUGIN_DATA is not set. Required for plugin venv and "
            "persistent state — must run under Claude Code plugin context."
        )
    return Path(env).resolve()


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
    src_dir: Path,
    dst_dir: Path,
    pattern: str = "*.md",
    force: bool = False,
    exclude: set[str] | None = None,
) -> list[dict]:
    """Deploy template files from src_dir to dst_dir.

    Returns list of {name, before, after} dicts. Files whose names are in
    exclude are skipped entirely — used for source-only documentation that
    should not deploy.
    """
    dst_dir.mkdir(parents=True, exist_ok=True)
    results = []

    if not src_dir.is_dir():
        return results

    skip_names = exclude or set()
    for src in sorted(src_dir.glob(pattern)):
        if src.name in skip_names:
            continue
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
    """Render a skill header with no infrastructure.

    Claude Code namespaces plugin slash commands automatically
    (`/<plugin>:<command>` on collision, `/<command>` when unique),
    so the skill name is used verbatim without a plugin prefix.
    """
    del plugin_name  # retained for signature compatibility with init-skill branch
    return f"/{skill_name}"


# --- Rules ---


RULES_SOURCE_ONLY = {"README.md", "architecture.md"}


def deploy_rules(plugin_root: Path, project_dir: Path, force: bool = False) -> list[dict]:
    """Deploy rule files. Returns [{path, before, after}] with relative deployed paths.

    Rules deploy to .claude/rules/{plugin_name}/ per-plugin subfolder for
    cross-plugin collision avoidance. Framework documentation (README.md,
    architecture.md) is plugin-source-only and excluded from deployment.
    """
    plugin_name = plugin_root.name
    deployed_rel = f".claude/rules/{plugin_name}"
    results = deploy_files(
        src_dir=plugin_root / "rules",
        dst_dir=project_dir / ".claude" / "rules" / plugin_name,
        pattern="*.md",
        force=force,
        exclude=RULES_SOURCE_ONLY,
    )
    for r in results:
        r["path"] = f"{deployed_rel}/{r.pop('name')}"
    return results


def get_rules_states(plugin_root: Path, project_dir: Path) -> list[dict]:
    """Get state of each rule file. Returns [{path, before, after}]."""
    src_dir = plugin_root / "rules"
    if not src_dir.is_dir():
        return []

    plugin_name = plugin_root.name
    deployed_rel = f".claude/rules/{plugin_name}"
    results = []
    for src in sorted(src_dir.glob("*.md")):
        if src.name in RULES_SOURCE_ONLY:
            continue
        if not src.is_file():
            continue
        dst = project_dir / ".claude" / "rules" / plugin_name / src.name
        state = compare_deployed(src, dst)
        results.append({
            "path": f"{deployed_rel}/{src.name}",
            "before": state,
            "after": state,
        })
    return results


# --- Patterns ---


PATTERNS_SOURCE_ONLY = {"README.md", "architecture.md"}


def deploy_patterns(plugin_root: Path, project_dir: Path, force: bool = False) -> list[dict]:
    """Deploy pattern files. Returns [{path, before, after}] with relative deployed paths.

    Patterns deploy to .claude/patterns/{plugin_name}/ per-plugin subfolder.
    Framework documentation is plugin-source-only and excluded from deployment.
    """
    plugin_name = plugin_root.name
    deployed_rel = f".claude/patterns/{plugin_name}"
    results = deploy_files(
        src_dir=plugin_root / "patterns",
        dst_dir=project_dir / ".claude" / "patterns" / plugin_name,
        pattern="*.md",
        force=force,
        exclude=PATTERNS_SOURCE_ONLY,
    )
    for r in results:
        r["path"] = f"{deployed_rel}/{r.pop('name')}"
    return results


def get_patterns_states(plugin_root: Path, project_dir: Path) -> list[dict]:
    """Get state of each pattern file. Returns [{path, before, after}]."""
    src_dir = plugin_root / "patterns"
    if not src_dir.is_dir():
        return []

    plugin_name = plugin_root.name
    deployed_rel = f".claude/patterns/{plugin_name}"
    results = []
    for src in sorted(src_dir.glob("*.md")):
        if src.name in PATTERNS_SOURCE_ONLY:
            continue
        if not src.is_file():
            continue
        dst = project_dir / ".claude" / "patterns" / plugin_name / src.name
        state = compare_deployed(src, dst)
        results.append({
            "path": f"{deployed_rel}/{src.name}",
            "before": state,
            "after": state,
        })
    return results


# --- System and skill discovery ---


def _discover_systems(plugin_root: Path) -> list[str]:
    """Discover server subsystems with init infrastructure.

    Returns sorted list of server package names whose package contains
    an _init.py module (conforming to the init/status contract).
    Server subsystems own state — database files, deployed conventions,
    configuration — and their init routines bootstrap or refresh that state.
    """
    servers_dir = plugin_root / "servers"
    if not servers_dir.is_dir():
        return []

    return sorted(
        init_path.parent.name
        for init_path in servers_dir.glob("*/_init.py")
    )


def _discover_workflow_skills(plugin_root: Path) -> list[str]:
    """Discover workflow skills. Returns sorted list of skill names.

    Workflow skills are pure slash command workflows without persistent state —
    each has a SKILL.md in plugins/<plugin>/skills/<name>/ and is invoked as
    `/<name>`. They are listed in init/status output so the user sees what
    commands the plugin ships, but the plugin does not deploy or track them.
    """
    skills_dir = plugin_root / "skills"
    if not skills_dir.is_dir():
        return []

    return sorted(
        skill_md.parent.name
        for skill_md in skills_dir.glob("*/SKILL.md")
    )


# --- Orchestration ---


_META_SKILLS = {"init", "status"}



def _show_permissions_status(plugin_root: Path) -> None:
    """Print permissions coverage for status display."""
    recommended = _get_recommended_patterns(plugin_root)
    if not recommended:
        return

    both = _get_both_settings()
    print("Permissions")

    for scope in ("project", "user"):
        present = recommended & both[scope]["allow"]
        print(f"  {scope}: {len(present)}/{len(recommended)} recommended patterns")

    # Check for redundancy or gaps
    proj_rec = recommended & both["project"]["allow"]
    user_rec = recommended & both["user"]["allow"]
    redundant = proj_rec & user_rec

    if redundant:
        print(f"  redundancy: {len(redundant)} patterns present in both scopes")
        print(f"  action needed: /init --permissions — consolidate to one scope")
    elif not proj_rec and not user_rec:
        print(f"  action needed: /init --permissions — setup recommended patterns")
    elif len(proj_rec) < len(recommended) and len(user_rec) < len(recommended):
        print(f"  action needed: /init --permissions — incomplete at both scopes")


def _merge_permissions(plugin_root: Path, scope: str) -> None:
    """Merge recommended auto-approve patterns into settings.json.

    Additive only — adds patterns not already present, never removes.
    scope: 'project' or 'user'
    """
    ref_path = plugin_root / "templates" / "settings.json"
    if not ref_path.exists():
        print("  recommended-permissions.json not found")
        return

    ref = read_json(ref_path)
    categories = ref.get("categories", {})

    if scope == "project":
        settings_path = get_project_dir() / ".claude" / "settings.json"
    else:
        settings_path = get_claude_home() / "settings.json"

    settings = read_json(settings_path)
    existing = set(settings.get("permissions", {}).get("allow", []))

    added = []
    for cat_name, cat in categories.items():
        desc = cat.get("description", cat_name)
        cat_added = []
        for pattern in cat.get("patterns", []):
            if pattern not in existing:
                cat_added.append(pattern)
        if cat_added:
            added.append((desc, cat_added))

    if not added:
        print(f"  {scope} settings — all recommended patterns already present")
        return

    # Merge
    if "permissions" not in settings:
        settings["permissions"] = {}
    if "allow" not in settings["permissions"]:
        settings["permissions"]["allow"] = []

    total = 0
    for desc, patterns in added:
        settings["permissions"]["allow"].extend(patterns)
        total += len(patterns)

    settings_path.parent.mkdir(parents=True, exist_ok=True)
    with open(settings_path, "w") as f:
        json.dump(settings, f, indent=2)
        f.write("\n")

    print(f"  {scope} settings — added {total} patterns:")
    for desc, patterns in added:
        print(f"    {desc}: {len(patterns)} patterns")


# --- Permissions analysis ---


def _settings_path(scope: str) -> Path:
    """Resolve settings.json path for a scope."""
    if scope == "project":
        return get_project_dir() / ".claude" / "settings.json"
    return get_claude_home() / "settings.json"


def _get_both_settings() -> dict:
    """Read settings at both scopes.

    Returns {scope: {path, allow, deny}} for project and user.
    """
    result = {}
    for scope in ("project", "user"):
        path = _settings_path(scope)
        settings = read_json(path)
        perms = settings.get("permissions", {})
        result[scope] = {
            "path": str(path),
            "allow": set(perms.get("allow", [])),
            "deny": set(perms.get("deny", [])),
        }
    return result


def _get_recommended_patterns(plugin_root: Path) -> set[str]:
    """Flat set of all template patterns across categories."""
    ref = read_json(plugin_root / "templates" / "settings.json")
    patterns = set()
    for cat in ref.get("categories", {}).values():
        patterns.update(cat.get("patterns", []))
    return patterns


def _get_recommended_by_category(plugin_root: Path) -> dict:
    """Template patterns grouped by category with descriptions."""
    ref = read_json(plugin_root / "templates" / "settings.json")
    return ref.get("categories", {})


def run_permissions_report() -> None:
    """Structured report of both scopes' permission state."""
    plugin_root = get_plugin_root()
    categories = _get_recommended_by_category(plugin_root)
    recommended = _get_recommended_patterns(plugin_root)
    both = _get_both_settings()

    print("Permissions Report")
    print()

    for scope in ("project", "user"):
        s = both[scope]
        present = recommended & s["allow"]
        non_rec = s["allow"] - recommended

        print(f"{scope} ({s['path']}):")
        print(f"  status: {len(present)}/{len(recommended)} recommended patterns")

        if len(present) < len(recommended):
            for cat_name, cat in categories.items():
                cat_patterns = set(cat.get("patterns", []))
                cat_present = cat_patterns & s["allow"]
                if len(cat_present) < len(cat_patterns):
                    missing = sorted(cat_patterns - s["allow"])
                    print(f"  {cat.get('description', cat_name)}: "
                          f"{len(cat_present)}/{len(cat_patterns)}"
                          f" — missing: {', '.join(missing)}")

        if non_rec:
            print(f"  non-recommended: {len(non_rec)} patterns")
        print()

    # Cross-scope analysis
    proj_rec = recommended & both["project"]["allow"]
    user_rec = recommended & both["user"]["allow"]
    redundant = proj_rec & user_rec
    if redundant:
        print(f"cross-scope: {len(redundant)} recommended patterns present in both scopes")
    else:
        print("cross-scope: no redundancy")


def run_permissions_deploy(scope: str) -> None:
    """Deploy recommended patterns to exactly one scope."""
    plugin_root = get_plugin_root()

    print("Permissions Deploy")
    print()
    print(f"scope: {scope}")
    _merge_permissions(plugin_root, scope)


def run_permissions_analyze() -> None:
    """Cross-scope health analysis."""
    plugin_root = get_plugin_root()
    recommended = _get_recommended_patterns(plugin_root)
    both = _get_both_settings()

    print("Permissions Analysis")
    print()

    needs_attention = False

    # Redundancy
    proj_rec = recommended & both["project"]["allow"]
    user_rec = recommended & both["user"]["allow"]
    redundant = sorted(proj_rec & user_rec)
    print(f"redundancy:")
    print(f"  count: {len(redundant)}")
    if redundant:
        needs_attention = True
        for p in redundant:
            print(f"    - {p}")
    print()

    # Broad patterns (non-recommended with wide wildcards)
    broad = []
    for scope in ("project", "user"):
        non_rec = both[scope]["allow"] - recommended
        for p in sorted(non_rec):
            if p in ("*", "Bash(*)") or p.endswith(":*)") and p.count(":") == 1 and len(p.split("(")[0]) <= 4:
                pass  # These are fine — short tool prefixes
            if p in ("*", "Bash(*)"):
                broad.append((p, scope))
    print(f"broad-patterns:")
    print(f"  count: {len(broad)}")
    if broad:
        needs_attention = True
        for p, s in broad:
            print(f"    - {p} (scope: {s})")
    print()

    # Contradictions
    contradictions = []
    for scope_a, scope_b in [("project", "user"), ("user", "project")]:
        conflicts = both[scope_a]["allow"] & both[scope_b]["deny"]
        for p in sorted(conflicts):
            contradictions.append((p, f"allow in {scope_a}", f"deny in {scope_b}"))
    print(f"contradictions:")
    print(f"  count: {len(contradictions)}")
    if contradictions:
        needs_attention = True
        for p, a, d in contradictions:
            print(f"    - {p}: {a}, {d}")
    print()

    print(f"health: {'needs-attention' if needs_attention else 'clean'}")


def run_permissions_clean(scope: str) -> None:
    """Remove recommended patterns from scope that are redundant with the other scope.

    Only removes patterns that exist in both the template AND the other
    scope's allow list. Never touches non-recommended or deny patterns.
    """
    plugin_root = get_plugin_root()
    recommended = _get_recommended_patterns(plugin_root)
    both = _get_both_settings()
    other_scope = "user" if scope == "project" else "project"

    # Find recommended patterns in target scope that also exist at other scope
    target_rec = recommended & both[scope]["allow"]
    other_rec = recommended & both[other_scope]["allow"]
    to_remove = sorted(target_rec & other_rec)

    print("Permissions Clean")
    print()
    print(f"scope: {scope}")

    if not to_remove:
        print(f"  nothing to clean — no redundant recommended patterns")
        return

    # Read and modify settings
    path = _settings_path(scope)
    settings = read_json(path)
    allow = settings.get("permissions", {}).get("allow", [])

    remove_set = set(to_remove)
    new_allow = [p for p in allow if p not in remove_set]
    settings["permissions"]["allow"] = new_allow

    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(settings, f, indent=2)
        f.write("\n")

    retained_rec = target_rec - remove_set
    non_rec = both[scope]["allow"] - recommended
    print(f"  removed: {len(to_remove)} patterns (redundant with {other_scope})")
    if retained_rec:
        print(f"  retained: {len(retained_rec)} recommended patterns (not in {other_scope})")
    if non_rec:
        print(f"  non-recommended retained: {len(non_rec)} patterns (not managed by plugin)")


def run_init(force: bool = False, system: str | None = None) -> None:
    """Generic init: deploy rules, call server subsystem init hooks, list skills.

    system: when provided, scopes init to one server subsystem — rules and
    workflow skill listing are skipped, and only the named subsystem's init
    runs. Unknown system names print an error listing available subsystems.

    force: passed through to each subsystem's init(), which defines its own
    destructive semantics (typically rebuilds the database from empty state).
    """
    plugin_root = get_plugin_root()
    project_dir = get_project_dir()
    plugin_name = get_plugin_name(plugin_root)

    systems = _discover_systems(plugin_root)
    if system is not None and system not in systems:
        print(f"Unknown system: {system}")
        print(f"Available: {', '.join(systems)}" if systems else "No systems discovered.")
        return

    print(f"{plugin_name} init" + (f" --system {system}" if system else ""))
    print()

    rules: list[dict] = []

    # Rules and patterns (plugin-wide; skipped when scoped to a single subsystem)
    if system is None:
        rules = deploy_rules(plugin_root, project_dir, force=force)
        for line in format_section("Rules", rules):
            print(line)
        print()

        patterns = deploy_patterns(plugin_root, project_dir, force=force)
        if patterns:
            for line in format_section("Patterns", patterns):
                print(line)
            print()

    # Server subsystems
    target_systems = [system] if system is not None else systems
    for system_name in target_systems:
        mod = importlib.import_module(f"servers.{system_name}._init")
        result = mod.init(force=force)
        for line in format_section(system_name, result["files"], result.get("extra")):
            print(line)
        print()

    # Workflow skills (only when not scoped)
    if system is None:
        skills = _discover_workflow_skills(plugin_root)
        shown = [s for s in skills if s not in _META_SKILLS]
        if shown:
            print("Skills")
            for skill_name in shown:
                print(f"  {format_bare_skill(plugin_name, skill_name)}")
            print()

    # Footer
    rules_changed = any(r["before"] != r["after"] for r in rules)
    if rules_changed:
        print("Done. Restart Claude session to load new rules.")
    else:
        print("Done.")


def run_status(system: str | None = None) -> None:
    """Generic status: report rules, server subsystems, and workflow skills.

    system: when provided, scopes output to one server subsystem —
    header, rules, and skill listing are skipped. Unknown system names
    print an error listing available subsystems.
    """
    plugin_root = get_plugin_root()
    project_dir = get_project_dir()
    claude_home = get_claude_home()
    plugin_name = get_plugin_name(plugin_root)

    systems = _discover_systems(plugin_root)
    if system is not None and system not in systems:
        print(f"Unknown system: {system}")
        print(f"Available: {', '.join(systems)}" if systems else "No systems discovered.")
        return

    # Header, rules, patterns (plugin-wide; skipped when scoped to a single subsystem)
    if system is None:
        installed_version = get_installed_version(plugin_root)
        source_version, marketplace_name = find_marketplace_source(
            plugin_name, plugin_root, claude_home,
        )
        print(format_header(plugin_name, installed_version, source_version, marketplace_name))
        print()

        rules = get_rules_states(plugin_root, project_dir)
        for line in format_section("Rules", rules):
            print(line)
        print()

        patterns = get_patterns_states(plugin_root, project_dir)
        if patterns:
            for line in format_section("Patterns", patterns):
                print(line)
            print()

    # Server subsystems
    target_systems = [system] if system is not None else systems
    for system_name in target_systems:
        mod = importlib.import_module(f"servers.{system_name}._init")
        result = mod.status()
        for line in format_section(system_name, result["files"], result.get("extra")):
            print(line)
        print()

    # Workflow skills and permissions (only when not scoped)
    if system is None:
        skills = _discover_workflow_skills(plugin_root)
        shown = [s for s in skills if s not in _META_SKILLS]
        if shown:
            print("Skills")
            for skill_name in shown:
                print(f"  {format_bare_skill(plugin_name, skill_name)}")
            print()

        _show_permissions_status(plugin_root)






