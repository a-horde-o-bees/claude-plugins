"""Permissions operations.

Auto-approve pattern analysis and deployment across project and user
scopes. Helpers and CLI entry points for listing coverage, installing
recommended patterns, analyzing cross-scope health, and cleaning
redundant entries.
"""

import json
from pathlib import Path

import framework


def _settings_path(scope: str) -> Path:
    """Resolve settings.json path for a scope."""
    if scope == "project":
        return framework.get_project_dir() / ".claude" / "settings.json"
    return framework.get_claude_home() / "settings.json"


def _get_both_settings() -> dict:
    """Read settings at both scopes.

    Returns {scope: {path, allow, deny}} for project and user.
    """
    result = {}
    for scope in ("project", "user"):
        path = _settings_path(scope)
        settings = framework.read_json(path)
        perms = settings.get("permissions", {})
        result[scope] = {
            "path": str(path),
            "allow": set(perms.get("allow", [])),
            "deny": set(perms.get("deny", [])),
        }
    return result


def _recommended_settings_path() -> Path:
    """Path to the permissions subsystem's recommended-patterns config."""
    return framework.get_plugin_root() / "systems" / "permissions" / "settings.json"


def _get_recommended_patterns() -> set[str]:
    """Flat set of all recommended patterns across categories."""
    ref = framework.read_json(_recommended_settings_path())
    patterns = set()
    for cat in ref.get("categories", {}).values():
        patterns.update(cat.get("patterns", []))
    return patterns


def _get_recommended_by_category() -> dict:
    """Recommended patterns grouped by category with descriptions."""
    ref = framework.read_json(_recommended_settings_path())
    return ref.get("categories", {})


def status_extra() -> list[dict]:
    """Build the subsystem status extra lines for permissions coverage.

    Returns an empty list when no recommendations are declared. Emits
    per-scope coverage counts and a redundancy count when patterns
    overlap across scopes. Next-step guidance is driven by the
    /ocd:setup guided skill reading this status; this subsystem only
    describes, it does not prescribe.
    """
    recommended = _get_recommended_patterns()
    if not recommended:
        return []

    both = _get_both_settings()
    extra: list[dict] = []

    for scope in ("project", "user"):
        present = recommended & both[scope]["allow"]
        extra.append({
            "label": f"{scope}",
            "value": f"{len(present)}/{len(recommended)} recommended patterns",
        })

    proj_rec = recommended & both["project"]["allow"]
    user_rec = recommended & both["user"]["allow"]
    redundant = proj_rec & user_rec

    if redundant:
        extra.append({
            "label": "redundancy",
            "value": f"{len(redundant)} patterns present in both scopes",
        })

    return extra


def _merge_permissions(scope: str) -> None:
    """Merge recommended auto-approve patterns into settings.json.

    Additive only — adds patterns not already present, never removes.
    scope: 'project' or 'user'
    """
    ref_path = _recommended_settings_path()
    if not ref_path.exists():
        print("  recommended-permissions.json not found")
        return

    ref = framework.read_json(ref_path)
    categories = ref.get("categories", {})

    settings_path = _settings_path(scope)
    settings = framework.read_json(settings_path)
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


def run_permissions_status() -> None:
    """Structured report of both scopes' permission state."""
    categories = _get_recommended_by_category()
    recommended = _get_recommended_patterns()
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

    proj_rec = recommended & both["project"]["allow"]
    user_rec = recommended & both["user"]["allow"]
    redundant = proj_rec & user_rec
    if redundant:
        print(f"cross-scope: {len(redundant)} recommended patterns present in both scopes")
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
    both = _get_both_settings()

    print("Permissions Analysis")
    print()

    needs_attention = False

    proj_rec = recommended & both["project"]["allow"]
    user_rec = recommended & both["user"]["allow"]
    redundant = sorted(proj_rec & user_rec)
    print("redundancy:")
    print(f"  count: {len(redundant)}")
    if redundant:
        needs_attention = True
        for p in redundant:
            print(f"    - {p}")
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
    """Remove recommended patterns from scope that are redundant with the other scope.

    Only removes patterns that exist in both the template AND the other
    scope's allow list. Never touches non-recommended or deny patterns.
    """
    recommended = _get_recommended_patterns()
    both = _get_both_settings()
    other_scope = "user" if scope == "project" else "project"

    target_rec = recommended & both[scope]["allow"]
    other_rec = recommended & both[other_scope]["allow"]
    to_remove = sorted(target_rec & other_rec)

    print("Permissions Clean")
    print()
    print(f"scope: {scope}")

    if not to_remove:
        print("  nothing to clean — no redundant recommended patterns")
        return

    path = _settings_path(scope)
    settings = framework.read_json(path)
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
