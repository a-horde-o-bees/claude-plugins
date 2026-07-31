"""Checkpoint sequencing: preflight (branch + routing + per-submodule plan),
submodule prep/reconcile, and feature-branch creation."""
import json
from pathlib import Path

from gitflow_core import _default_branch, die, run, submodule_entries
from gitflow_gate import _routes


def cmd_checkpoint_preflight(a):
    """The mechanical head of a checkpoint: branch resolution, routing, and the
    per-submodule plan. Judgment stays with the caller: the feature-branch name
    (when needs_feature_branch) and every land/halt decision downstream."""
    cwd = a.cwd
    _, branch, _ = run(["git", "branch", "--show-current"], cwd)
    if not branch:
        die(f"{cwd}: detached HEAD — checkout a branch first")
    if a.branch and a.branch != branch:
        die(f"{cwd}: on branch {branch}, not {a.branch} — branch mismatch")
    _, root, _ = run(["git", "rev-parse", "--show-toplevel"], cwd, check=True)
    default_branch = _default_branch(cwd)

    routes = _routes(cwd, a.paths or None)
    if not routes["ok"]:
        print(json.dumps(routes, indent=1))
        die("routing is ambiguous — resolve every gap, then re-invoke:\n"
            + "\n".join(f"- {g['repo']}: {g['gap']} → {g['fix']}" for g in routes["gaps"]))

    parent = next(r for r in routes["repos"] if r["path"] == ".")
    path = a.path or parent["integration"]
    effective = "direct" if a.base_mode else path

    pin_only, ledger, land = [], [], []
    for r in routes["repos"]:
        if r["path"] == ".":
            continue
        if r["integration"] == "read-only":
            pin_only.append(r["path"])
            ledger.append(f"{r['path']}: pin-only (vendored)")
        elif r["integration"] == "direct":
            ledger.append(f"{r['path']}: direct (verbs push it)")
        elif not r["has_edits"]:
            pin_only.append(r["path"])
            ledger.append(f"{r['path']}: pin-only (already landed / no work)")
        else:  # pr-integrated with pending work — the caller lands it via recursion
            land.append({"path": r["path"], "name": r["name"], "integration": r["integration"],
                         "declared_branch": r["declared_branch"]})

    scope = ["--"] + a.paths if a.paths else []
    _, pending, _ = run(["git", "status", "--short"] + scope, cwd)
    on_default = branch == default_branch
    needs_feature_branch = (effective == "pr" and on_default and bool(pending))

    # Surface the root augmentations file mechanically — a prose-only
    # "remember to load it" step is exactly the kind that gets skipped
    # without a trace. The caller still reads the file for step bodies;
    # this key tells it the file and which steps exist.
    aug_file = Path(root) / ".claude" / "git" / "checkpoint.md"
    augmentations = {"present": aug_file.is_file(), "file": str(aug_file), "steps": []}
    if augmentations["present"]:
        text = aug_file.read_text(encoding="utf-8")
        if "## Augmentations" in text:
            section = text.split("## Augmentations", 1)[1]
            augmentations["steps"] = [
                line[4:].strip() for line in section.splitlines()
                if line.startswith("### ")
            ]

    print(json.dumps({
        "branch": branch,
        "default_branch": default_branch,
        "on_default": on_default,
        "root": root,
        "parent_integration": parent["integration"],
        "effective_path": effective,
        "pending": pending.splitlines(),
        "needs_feature_branch": needs_feature_branch,
        "pin_only": pin_only,
        "land": land,
        "ledger": ledger,
        "augmentations": augmentations,
        "routes": routes,
    }, indent=1))


def cmd_sub_prep(a):
    """Normalize a submodule off detached HEAD onto its declared branch — the
    safe attach/create cases only; divergence halts for a human decision."""
    cwd = a.cwd
    ent = next((e for e in submodule_entries(cwd) if e["path"] == a.path), None)
    if not ent:
        die(f"{a.path}: not a declared submodule of {cwd}")
    sub = str(Path(cwd) / a.path)
    _, cur, _ = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], sub, check=True)
    if cur != "HEAD":
        print(json.dumps({"path": a.path, "branch": cur, "action": "already-attached"}))
        return
    wb = ent["declared_branch"]
    if not wb:
        die(f"{a.path}: detached with no branch= in .gitmodules — declare one (or run /git doctor)")
    _, head, _ = run(["git", "rev-parse", "HEAD"], sub, check=True)
    rcd, decl, _ = run(["git", "rev-parse", "--verify", wb], sub)
    if rcd != 0:
        run(["git", "checkout", "-b", wb], sub, check=True)
        action = "created-branch"
    elif decl == head:
        run(["git", "checkout", wb], sub, check=True)
        action = "attached"
    else:
        die(f"{a.path}: declared branch {wb} ({decl[:8]}) diverges from detached HEAD ({head[:8]}) — resolve manually")
    print(json.dumps({"path": a.path, "branch": wb, "action": action}))


def cmd_sub_reconcile(a):
    """Pin a landed submodule to origin's merged tip. After a squash/rebase
    merge the merged sha is new — the pin must capture that sha, not the
    discarded feature-branch tip. Refuses on a dirty submodule tree."""
    cwd = a.cwd
    sub = str(Path(cwd) / a.path)
    _, dirty, _ = run(["git", "status", "--short"], sub)
    if dirty:
        die(f"{a.path}: dirty tree — will not reset over uncommitted work:\n{dirty}")
    default = _default_branch(sub)
    run(["git", "fetch", "origin", default], sub, check=True)
    _, merged, _ = run(["git", "rev-parse", f"origin/{default}"], sub, check=True)
    _, head, _ = run(["git", "rev-parse", "HEAD"], sub, check=True)
    if head != merged:
        run(["git", "checkout", default], sub, check=True)
        run(["git", "reset", "--hard", merged], sub, check=True)
    print(json.dumps({"path": a.path, "default_branch": default, "pinned": merged,
                      "moved": head != merged}))


def cmd_branch_create(a):
    run(["git", "checkout", "-b", a.name], a.cwd, check=True)
    print(json.dumps({"branch": a.name, "created": True}))
