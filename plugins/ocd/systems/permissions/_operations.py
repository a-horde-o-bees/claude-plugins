"""Permissions operations.

Auto-approve pattern analysis and deployment across project and user
scopes. Helpers and CLI entry points for listing coverage, installing
recommended patterns, analyzing cross-scope health, and cleaning
redundant entries.
"""

import json
from pathlib import Path

from systems import setup
from tools import environment


def _settings_path(scope: str) -> Path:
    """Resolve settings.json path for a scope."""
    if scope == "project":
        return environment.get_project_dir() / ".claude" / "settings.json"
    return environment.get_claude_home() / "settings.json"


def _get_both_settings() -> dict:
    """Read settings at both scopes.

    Returns {scope: {path, allow, deny, additional_directories}} for
    project and user.
    """
    result = {}
    for scope in ("project", "user"):
        path = _settings_path(scope)
        settings = setup.read_json(path)
        perms = settings.get("permissions", {})
        result[scope] = {
            "path": str(path),
            "allow": set(perms.get("allow", [])),
            "deny": set(perms.get("deny", [])),
            "additional_directories": list(perms.get("additionalDirectories", [])),
        }
    return result


def _recommended_settings_path() -> Path:
    """Path to the permissions subsystem's recommended-patterns config."""
    return environment.get_plugin_root() / "systems" / "permissions" / "settings.json"


def _get_recommended_patterns() -> set[str]:
    """Flat set of all recommended patterns across categories."""
    ref = setup.read_json(_recommended_settings_path())
    patterns = set()
    for cat in ref.get("categories", {}).values():
        patterns.update(cat.get("patterns", []))
    return patterns


def _get_recommended_by_category() -> dict:
    """Recommended patterns grouped by category with descriptions."""
    ref = setup.read_json(_recommended_settings_path())
    return ref.get("categories", {})


def _get_recommended_additional_directories() -> dict:
    """Recommended additionalDirectories block with description and paths."""
    ref = setup.read_json(_recommended_settings_path())
    block = ref.get("additionalDirectories", {})
    return {
        "description": block.get("description", ""),
        "paths": list(block.get("paths", [])),
    }


def status_extra() -> list[dict]:
    """Build the subsystem status extra lines for permissions coverage.

    Returns an empty list when no recommendations are declared. Emits
    per-scope coverage counts and a redundancy count when patterns
    overlap across scopes. Next-step guidance is driven by the
    /ocd:setup guided skill reading this status; this subsystem only
    describes, it does not prescribe.
    """
    recommended = _get_recommended_patterns()
    rec_dirs = set(_get_recommended_additional_directories()["paths"])
    if not recommended and not rec_dirs:
        return []

    both = _get_both_settings()
    extra: list[dict] = []

    for scope in ("project", "user"):
        present = recommended & both[scope]["allow"]
        present_dirs = rec_dirs & set(both[scope]["additional_directories"])
        bits = []
        if recommended:
            bits.append(f"{len(present)}/{len(recommended)} recommended patterns")
        if rec_dirs:
            bits.append(f"{len(present_dirs)}/{len(rec_dirs)} additional directories")
        extra.append({
            "label": f"{scope}",
            "value": ", ".join(bits),
        })

    proj_rec = recommended & both["project"]["allow"]
    user_rec = recommended & both["user"]["allow"]
    redundant = proj_rec & user_rec

    proj_dirs = rec_dirs & set(both["project"]["additional_directories"])
    user_dirs = rec_dirs & set(both["user"]["additional_directories"])
    redundant_dirs = proj_dirs & user_dirs

    if redundant or redundant_dirs:
        parts = []
        if redundant:
            parts.append(f"{len(redundant)} patterns")
        if redundant_dirs:
            parts.append(f"{len(redundant_dirs)} directories")
        extra.append({
            "label": "redundancy",
            "value": f"{' + '.join(parts)} present in both scopes",
        })

    return extra


def _merge_permissions(scope: str) -> None:
    """Merge recommended auto-approve patterns and sibling directories.

    Additive only — adds entries not already present, never removes.
    scope: 'project' or 'user'
    """
    ref_path = _recommended_settings_path()
    if not ref_path.exists():
        print("  recommended-permissions.json not found")
        return

    ref = setup.read_json(ref_path)
    categories = ref.get("categories", {})
    rec_dirs_block = _get_recommended_additional_directories()

    settings_path = _settings_path(scope)
    settings = setup.read_json(settings_path)
    existing_patterns = set(settings.get("permissions", {}).get("allow", []))
    existing_dirs = list(settings.get("permissions", {}).get("additionalDirectories", []))

    added = []
    for cat_name, cat in categories.items():
        desc = cat.get("description", cat_name)
        cat_added = [p for p in cat.get("patterns", []) if p not in existing_patterns]
        if cat_added:
            added.append((desc, cat_added))

    dirs_to_add = [d for d in rec_dirs_block["paths"] if d not in existing_dirs]

    if not added and not dirs_to_add:
        print(f"  {scope} settings — all recommended entries already present")
        return

    if "permissions" not in settings:
        settings["permissions"] = {}
    if "allow" not in settings["permissions"]:
        settings["permissions"]["allow"] = []
    if dirs_to_add and "additionalDirectories" not in settings["permissions"]:
        settings["permissions"]["additionalDirectories"] = []

    total_patterns = 0
    for desc, patterns in added:
        settings["permissions"]["allow"].extend(patterns)
        total_patterns += len(patterns)

    if dirs_to_add:
        settings["permissions"]["additionalDirectories"].extend(dirs_to_add)

    settings_path.parent.mkdir(parents=True, exist_ok=True)
    with open(settings_path, "w") as f:
        json.dump(settings, f, indent=2)
        f.write("\n")

    if total_patterns:
        print(f"  {scope} settings — added {total_patterns} patterns:")
        for desc, patterns in added:
            print(f"    {desc}: {len(patterns)} patterns")
    if dirs_to_add:
        print(f"  {scope} settings — added {len(dirs_to_add)} additional directories:")
        print(f"    {rec_dirs_block['description']}")
        for d in dirs_to_add:
            print(f"    - {d}")


def run_permissions_status() -> None:
    """Structured report of both scopes' permission state."""
    categories = _get_recommended_by_category()
    recommended = _get_recommended_patterns()
    rec_dirs_block = _get_recommended_additional_directories()
    rec_dirs = set(rec_dirs_block["paths"])
    both = _get_both_settings()

    print("Permissions Report")
    print()

    for scope in ("project", "user"):
        s = both[scope]
        present = recommended & s["allow"]
        non_rec = s["allow"] - recommended
        dirs_present = rec_dirs & set(s["additional_directories"])
        dirs_missing = sorted(rec_dirs - set(s["additional_directories"]))

        print(f"{scope} ({s['path']}):")
        print(f"  status: {len(present)}/{len(recommended)} recommended patterns")
        if rec_dirs:
            print(
                f"  additional directories: "
                f"{len(dirs_present)}/{len(rec_dirs)} recommended",
            )
            if dirs_missing:
                print(f"    missing: {', '.join(dirs_missing)}")

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

    proj_rec = recommended & both["project"]["allow"]
    user_rec = recommended & both["user"]["allow"]
    redundant = proj_rec & user_rec
    proj_dirs = rec_dirs & set(both["project"]["additional_directories"])
    user_dirs = rec_dirs & set(both["user"]["additional_directories"])
    redundant_dirs = proj_dirs & user_dirs

    if redundant or redundant_dirs:
        parts = []
        if redundant:
            parts.append(f"{len(redundant)} patterns")
        if redundant_dirs:
            parts.append(f"{len(redundant_dirs)} directories")
        print(f"cross-scope: {' + '.join(parts)} present in both scopes")
    else:
        print("cross-scope: no redundancy")


def run_permissions_deploy(scope: str) -> None:
    """Deploy recommended patterns to exactly one scope."""
    print("Permissions Deploy")
    print()
    print(f"scope: {scope}")
    _merge_permissions(scope)


def run_permissions_analyze() -> None:
    """Cross-scope health analysis."""
    recommended = _get_recommended_patterns()
    rec_dirs = set(_get_recommended_additional_directories()["paths"])
    both = _get_both_settings()

    print("Permissions Analysis")
    print()

    needs_attention = False

    proj_rec = recommended & both["project"]["allow"]
    user_rec = recommended & both["user"]["allow"]
    redundant = sorted(proj_rec & user_rec)
    proj_dirs = rec_dirs & set(both["project"]["additional_directories"])
    user_dirs = rec_dirs & set(both["user"]["additional_directories"])
    redundant_dirs = sorted(proj_dirs & user_dirs)
    print("redundancy:")
    print(f"  patterns: {len(redundant)}")
    if redundant:
        needs_attention = True
        for p in redundant:
            print(f"    - {p}")
    print(f"  additional directories: {len(redundant_dirs)}")
    if redundant_dirs:
        needs_attention = True
        for d in redundant_dirs:
            print(f"    - {d}")
    print()

    broad = []
    for scope in ("project", "user"):
        non_rec = both[scope]["allow"] - recommended
        for p in sorted(non_rec):
            if p in ("*", "Bash(*)"):
                broad.append((p, scope))
    print("broad-patterns:")
    print(f"  count: {len(broad)}")
    if broad:
        needs_attention = True
        for p, s in broad:
            print(f"    - {p} (scope: {s})")
    print()

    contradictions = []
    for scope_a, scope_b in [("project", "user"), ("user", "project")]:
        conflicts = both[scope_a]["allow"] & both[scope_b]["deny"]
        for p in sorted(conflicts):
            contradictions.append((p, f"allow in {scope_a}", f"deny in {scope_b}"))
    print("contradictions:")
    print(f"  count: {len(contradictions)}")
    if contradictions:
        needs_attention = True
        for p, a, d in contradictions:
            print(f"    - {p}: {a}, {d}")
    print()

    print(f"health: {'needs-attention' if needs_attention else 'clean'}")


def run_permissions_clean(scope: str) -> None:
    """Remove recommended entries from scope that are redundant with the other scope.

    Only removes entries that exist in both the template AND the other
    scope's allow list or additionalDirectories. Never touches
    non-recommended or deny entries.
    """
    recommended = _get_recommended_patterns()
    rec_dirs = set(_get_recommended_additional_directories()["paths"])
    both = _get_both_settings()
    other_scope = "user" if scope == "project" else "project"

    target_rec = recommended & both[scope]["allow"]
    other_rec = recommended & both[other_scope]["allow"]
    patterns_to_remove = sorted(target_rec & other_rec)

    target_dirs = rec_dirs & set(both[scope]["additional_directories"])
    other_dirs = rec_dirs & set(both[other_scope]["additional_directories"])
    dirs_to_remove = sorted(target_dirs & other_dirs)

    print("Permissions Clean")
    print()
    print(f"scope: {scope}")

    if not patterns_to_remove and not dirs_to_remove:
        print("  nothing to clean — no redundant recommended entries")
        return

    path = _settings_path(scope)
    settings = setup.read_json(path)
    perms = settings.setdefault("permissions", {})

    if patterns_to_remove:
        allow = perms.get("allow", [])
        pattern_removals = set(patterns_to_remove)
        perms["allow"] = [p for p in allow if p not in pattern_removals]

    if dirs_to_remove:
        add_dirs = perms.get("additionalDirectories", [])
        dir_removals = set(dirs_to_remove)
        perms["additionalDirectories"] = [d for d in add_dirs if d not in dir_removals]

    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(settings, f, indent=2)
        f.write("\n")

    if patterns_to_remove:
        print(f"  removed: {len(patterns_to_remove)} patterns (redundant with {other_scope})")
    if dirs_to_remove:
        print(
            f"  removed: {len(dirs_to_remove)} additional directories "
            f"(redundant with {other_scope})",
        )
    retained_rec = target_rec - set(patterns_to_remove)
    non_rec = both[scope]["allow"] - recommended
    if retained_rec:
        print(f"  retained: {len(retained_rec)} recommended patterns (not in {other_scope})")
    if non_rec:
        print(f"  non-recommended retained: {len(non_rec)} patterns (not managed by plugin)")
