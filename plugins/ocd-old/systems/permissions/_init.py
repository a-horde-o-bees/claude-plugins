"""Permissions subsystem brief status.

Brief facade-level status() returning the wide-table per-scope shape
shared across migrated systems. The verbose CLI report (per-category
breakdown, missing pattern lists) lives in `_operations` and is
invoked through `dispatch("status", ...)`.
"""

from systems import setup

from . import _operations

SUPPORTED_SCOPES = ("user", "project")


def status(scope: str | None = None) -> dict:
    """Coverage table per scope: rows for recommended patterns and additional directories.

    scope=None reports both scopes; scope='user' or 'project' narrows
    to one. Uses `setup.status_table` so the brief status output
    matches the per-scope grid every other migrated system uses, with
    cross-scope redundancy surfaced in `extra`.
    """
    if scope and scope not in SUPPORTED_SCOPES:
        return {
            "rows": [],
            "columns": [],
            "extra": [{"label": "error", "value": f"unsupported scope: {scope}"}],
        }

    scopes = list((scope,) if scope else SUPPORTED_SCOPES)

    recommended = _operations._get_recommended_patterns()
    rec_dirs = set(_operations._get_recommended_additional_directories()["paths"])
    both = _operations._get_both_settings()

    items: list[str] = []
    if recommended:
        items.append("recommended patterns")
    if rec_dirs:
        items.append("additional directories")

    def state_of(item: str, scope_name: str) -> str:
        s = both[scope_name]
        if item == "recommended patterns":
            present = recommended & s["allow"]
            return f"{len(present)}/{len(recommended)}"
        if item == "additional directories":
            present = rec_dirs & set(s["additional_directories"])
            return f"{len(present)}/{len(rec_dirs)}"
        return ""

    extra: list[dict] = []
    if "user" in scopes and "project" in scopes:
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

    return setup.status_table(items, scopes, state_of, extra=extra)
