"""Doctor domains: the detection wrapper (detect.sh/git-roots.sh → JSON) and the
deterministic repairs — tier-1 gitlink repair, submodule init/declare/drop,
native-key writes, origin/HEAD set, and the multi-remote default-branch rename.
Approval gates stay with the verb docs; every repair here refuses the cases the
docs mark as deliberate decisions (tier-2 pollution, diverged state)."""
import json
import re
import subprocess
from pathlib import Path

from gitflow_core import die, run, submodule_entries
from gitflow_gate import _origin_slug

SCRIPTS_DIR = Path(__file__).resolve().parent

ROW_RE = re.compile(r"^\s*(\S+)\s+(\S+)\s+staged=(\d+)\s+history=(\d+)\s*$")
NATIVE_KEYS = {"branch", "update", "x-integration", "x-contribute"}
X_INTEGRATION_VALUES = {"read-only", "direct", "pr"}


def _disposition(state, history):
    """Fixed-rule repair disposition per state row; judgment (approvals, intent
    questions) stays with the caller."""
    if state == "broken-link":
        return "tier1-repair" if history == 0 else "tier2-surface-only"
    return {"orphan-gitlink": "declare-or-drop",
            "not-checked-out": "init",
            "declared-only": "init",
            "undeclared": "ambiguous-intent",
            "nested-independent": "skip-benign"}.get(state, "surface-anomaly")


def _detect(cwd):
    p = subprocess.run(["sh", str(SCRIPTS_DIR / "detect.sh")], cwd=cwd,
                       capture_output=True, text=True)
    status, problems = None, []
    for line in p.stdout.splitlines():
        if line.startswith("STATUS: "):
            status = line[len("STATUS: "):].strip()
        elif line.strip():
            dom, _, rest = line.partition(" ")
            sev, _, detail = rest.partition(" ")
            problems.append({"domain": dom, "severity": sev, "detail": detail})
    superproject, table = None, []
    for line in p.stderr.splitlines():
        m = ROW_RE.match(line)
        if m:
            table.append({"state": m[1], "path": m[2],
                          "staged": int(m[3]), "history": int(m[4]),
                          "disposition": _disposition(m[1], int(m[4]))})
        elif "superproject:" in line:
            superproject = line.split("superproject:", 1)[1].strip()
    return {"status": status, "exit": p.returncode, "problems": problems,
            "superproject": superproject, "submodules": table}


def cmd_doctor_detect(a):
    print(json.dumps(_detect(a.cwd), indent=1))


def _path_history(cwd, path):
    _, out, _ = run(["git", "log", "--all", "--oneline", "--", path], cwd)
    return len(out.splitlines())


def cmd_sub_repair(a):
    """Tier-1 gitlink repair: re-border each path as a gitlink, one commit for
    the batch. Refuses any path with superproject history (tier 2 — fixing that
    rewrites history and is never automatic)."""
    cwd = a.cwd
    for p in a.path:
        if _path_history(cwd, p) > 0:
            die(f"{p}: interior files are in superproject history (tier 2) — "
                "repair requires a history rewrite; a deliberate, separate decision, never automatic")
    for p in a.path:
        run(["git", "rm", "-r", "--cached", "--quiet", "--", p], cwd, check=True)
        # re-add creates the gitlink; git's "adding embedded git repository"
        # warning is the expected outcome, not a failure
        run(["git", "add", "--", p], cwd, check=True)
    run(["git", "commit", "-m", "Repair submodule gitlinks: " + ", ".join(a.path)], cwd, check=True)
    _, sha, _ = run(["git", "rev-parse", "--short", "HEAD"], cwd)
    print(json.dumps({"repaired": a.path, "commit": sha}))


def cmd_sub_init(a):
    run(["git", "submodule", "update", "--init", "--", a.path], a.cwd, check=True)
    print(json.dumps({"path": a.path, "initialized": True}))


def cmd_gitlink_drop(a):
    """Drop an orphan gitlink (staged 160000 entry with no .gitmodules
    declaration) from the index. The working tree is untouched."""
    cwd = a.cwd
    _, out, _ = run(["git", "ls-files", "--stage", "--", a.path], cwd)
    if not any(line.split()[0] == "160000" for line in out.splitlines()):
        die(f"{a.path}: no gitlink staged at this path — nothing to drop")
    run(["git", "rm", "--cached", "--", a.path], cwd, check=True)
    print(json.dumps({"path": a.path, "gitlink_dropped": True}))


def cmd_sub_declare(a):
    """Declare an on-disk repo as a submodule: .gitmodules path+url entry plus
    the gitlink. The repo must have a commit (a gitlink pins a sha)."""
    cwd = a.cwd
    sub = str(Path(cwd) / a.path)
    rc, _, _ = run(["git", "rev-parse", "HEAD"], sub)
    if rc != 0:
        die(f"{a.path}: not a git repo with a commit — a gitlink needs a sha to pin")
    url = a.url or _origin_slug_url(sub)
    if not url:
        die(f"{a.path}: no origin remote and no --url given — a declaration needs a url")
    name = a.name or a.path
    run(["git", "config", "-f", ".gitmodules", f"submodule.{name}.path", a.path], cwd, check=True)
    run(["git", "config", "-f", ".gitmodules", f"submodule.{name}.url", url], cwd, check=True)
    run(["git", "add", "--", ".gitmodules", a.path], cwd, check=True)
    print(json.dumps({"path": a.path, "name": name, "url": url, "declared": True,
                      "note": "staged, not committed — commit via /git commit"}))


def _origin_slug_url(sub_cwd):
    rc, out, _ = run(["git", "remote", "get-url", "origin"], sub_cwd)
    return out if rc == 0 and out else None


def cmd_write_native_key(a):
    """Write one parent-owned routing key into .gitmodules for a declared
    submodule. The four-key vocabulary is closed; values are validated."""
    if a.key not in NATIVE_KEYS:
        die(f"unknown native key {a.key!r} — the vocabulary is {', '.join(sorted(NATIVE_KEYS))}")
    if a.key == "x-integration" and a.value not in X_INTEGRATION_VALUES:
        die(f"x-integration must be one of {', '.join(sorted(X_INTEGRATION_VALUES))}")
    ent = next((e for e in submodule_entries(a.cwd) if e["path"] == a.path), None)
    if not ent:
        die(f"{a.path}: not a declared submodule — declare it first (sub-declare)")
    run(["git", "config", "-f", ".gitmodules", f"submodule.{ent['name']}.{a.key}", a.value],
        a.cwd, check=True)
    print(json.dumps({"path": a.path, "name": ent["name"], "key": a.key, "value": a.value}))


def cmd_origin_head_set(a):
    """Point refs/remotes/origin/HEAD at the repo's true default so branch
    resolution works locally. Resolves via the forge when the pointer is unset."""
    cwd = a.cwd
    _, cur, _ = run(["git", "symbolic-ref", "--short", "refs/remotes/origin/HEAD"], cwd)
    if cur:
        print(json.dumps({"origin_head": cur.removeprefix("origin/"), "action": "already-set"}))
        return
    rc, out, _ = run(["gh", "api", "repos/{owner}/{repo}", "--jq", ".default_branch"], cwd)
    default, source = (out, "forge") if rc == 0 and out else ("main", "fallback")
    run(["git", "remote", "set-head", "origin", default], cwd, check=True)
    print(json.dumps({"origin_head": default, "action": "set", "source": source}))


def _remote_host(cwd, remote):
    rc, url, _ = run(["git", "remote", "get-url", remote], cwd)
    if rc != 0:
        return None
    if "github.com" in url:
        return "github"
    if "gitlab.com" in url:
        return "gitlab"
    return "other"


def _flip_forge_default(cwd, remote, to):
    """Best-effort forge default-branch flip for one remote; returns a report
    string. Non-forge remotes (local paths, unknown hosts) are skipped."""
    host = _remote_host(cwd, remote)
    slug = _origin_slug(remote=remote, cwd=cwd)
    if host == "github" and slug:
        rc, _, err = run(["gh", "repo", "edit", slug, "--default-branch", to], cwd)
        return f"{remote}: forge default → {to}" if rc == 0 else f"{remote}: forge flip FAILED — {err.splitlines()[-1] if err else 'gh error'}"
    if host == "gitlab" and slug:
        enc = slug.replace("/", "%2F")
        rc, _, err = run(["glab", "api", "-X", "PUT", f"projects/{enc}", "-f", f"default_branch={to}"], cwd)
        return f"{remote}: forge default → {to}" if rc == 0 else f"{remote}: forge flip FAILED — {err.splitlines()[-1] if err else 'glab error'}"
    # a local-path remote has no forge; its HEAD is the "default" — flip it
    # directly, else deleting the old branch there is refused
    rc, url, _ = run(["git", "remote", "get-url", remote], cwd)
    if rc == 0:
        target = Path(url) if Path(url).is_absolute() else Path(cwd) / url
        if target.is_dir():
            rc2, _, _ = run(["git", "symbolic-ref", "HEAD", f"refs/heads/{to}"], str(target))
            if rc2 == 0:
                return f"{remote}: local remote HEAD → {to}"
    return f"{remote}: no forge to flip (host: {host or 'unreadable'})"


def cmd_default_branch_rename(a):
    """Rename the default branch across every remote, canonical order: local
    rename, publish, flip each forge default, delete the old branch, repoint
    HEAD. A forge that refuses the delete (protected old default) halts with
    what completed — protection carry-over is a manual, deliberate step."""
    cwd, to = a.cwd, a.to
    _, cur, _ = run(["git", "symbolic-ref", "--short", "refs/remotes/origin/HEAD"], cwd)
    old = a.old or (cur.removeprefix("origin/") if cur else "")
    if not old:
        die("cannot determine the current default branch — pass --old")
    if old == to:
        die(f"default branch is already {to} — nothing to rename")
    _, remotes_out, _ = run(["git", "remote"], cwd, check=True)
    remotes = remotes_out.splitlines()
    run(["git", "branch", "-m", old, to], cwd, check=True)
    print(f"local: {old} → {to}")
    for r in remotes:
        run(["git", "push", r, to], cwd, check=True)
        print(f"{r}: pushed {to}")
    for r in remotes:
        print(_flip_forge_default(cwd, r, to))
    for r in remotes:
        rc, _, err = run(["git", "push", r, "--delete", old], cwd)
        if rc != 0:
            die(f"{r}: could not delete {old} ({err.splitlines()[-1] if err else 'refused'}) — "
                f"either {old} is protected there (unprotect, delete, re-apply equivalent "
                f"protection to {to}) or the remote's default still points at {old}. "
                f"Completed so far: local rename, {to} pushed everywhere, forge flips attempted")
        print(f"{r}: deleted {old}")
    for r in remotes:
        run(["git", "remote", "set-head", r, to], cwd, check=True)
        run(["git", "fetch", "--prune", r], cwd, check=True)
        print(f"{r}: HEAD → {to}, pruned")
    print(json.dumps({"renamed": {"from": old, "to": to}, "remotes": remotes}))
