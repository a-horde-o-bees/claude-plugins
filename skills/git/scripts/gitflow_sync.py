"""Integration-inbound mechanics: fetch a remote, switch branches, and
integrate another ref into the current branch (merge / rebase / cherry-pick)
with a structured conflict workflow. Conflict *resolution* is judgment and
stays with the verb doc; everything here is deterministic state machinery."""
import json
import sys
from pathlib import Path

from gitflow_core import die, run

CONFLICT_MARKERS = ("<<<<<<< ", "=======", ">>>>>>> ")


def _git_dir(cwd):
    rc, out, err = run(["git", "rev-parse", "--git-dir"], cwd)
    if rc != 0:
        die(f"not a git repository: {cwd}\n{err}")
    return Path(cwd) / out if not Path(out).is_absolute() else Path(out)


def _in_progress(cwd):
    """The in-flight multi-step operation, if any: merge|rebase|cherry-pick|None."""
    g = _git_dir(cwd)
    if (g / "MERGE_HEAD").exists():
        return "merge"
    if (g / "rebase-merge").exists() or (g / "rebase-apply").exists():
        return "rebase"
    if (g / "CHERRY_PICK_HEAD").exists():
        return "cherry-pick"
    return None


def _dirty(cwd):
    _, status, _ = run(["git", "status", "--porcelain"], cwd)
    return bool(status)


def _unmerged(cwd):
    _, out, _ = run(["git", "diff", "--name-only", "--diff-filter=U"], cwd)
    return out.splitlines()


def _head(cwd):
    _, sha, _ = run(["git", "rev-parse", "--short", "HEAD"], cwd)
    return sha


def _conflict_exit(cwd, mode):
    print(json.dumps({
        "result": "conflicts", "mode": mode, "files": _unmerged(cwd),
        "next": ("resolve each file with judgment (both sides' intent), then "
                 "`integrate --continue`; or `integrate --abort` to back out"),
    }, indent=1))
    sys.exit(1)


def _done_exit(cwd, mode, source=None):
    out = {"result": "completed", "mode": mode, "head": _head(cwd)}
    if source:
        out["source"] = source
    print(json.dumps(out))
    sys.exit(0)


def cmd_fetch(a):
    rc, _, err = run(["git", "remote", "get-url", a.remote], a.cwd)
    if rc != 0:
        _, remotes, _ = run(["git", "remote"], a.cwd)
        die(f"no remote '{a.remote}' (have: {', '.join(remotes.splitlines()) or 'none'})")
    rc, _, err = run(["git", "fetch", "--prune", a.remote], a.cwd)
    if rc != 0:
        die(f"fetch failed: {err}")
    # fetch reports ref updates on stderr; pass them through as the summary
    print(json.dumps({"remote": a.remote, "fetched": True,
                      "updates": [l.strip() for l in err.splitlines() if "->" in l]}))


def cmd_switch(a):
    if _in_progress(a.cwd):
        die(f"a {_in_progress(a.cwd)} is in progress — finish (integrate --continue) or abort first")
    if _dirty(a.cwd):
        die("working tree not clean — commit (or discard deliberately) before switching branches")
    rc, _, _ = run(["git", "rev-parse", "--verify", f"refs/heads/{a.branch}"], a.cwd)
    if rc != 0:
        die(f"no local branch '{a.branch}' (branch-create makes new ones)")
    run(["git", "switch", a.branch], a.cwd, check=True)
    print(json.dumps({"branch": a.branch, "head": _head(a.cwd)}))


def _validate_source(cwd, source):
    parts = source.split("..") if ".." in source else [source]
    for p in parts:
        p = p.strip(".")
        if not p:
            continue
        rc, _, _ = run(["git", "rev-parse", "--verify", f"{p}^{{commit}}"], cwd)
        if rc != 0:
            die(f"source ref does not resolve to a commit: {p} (fetch first?)")


def cmd_integrate(a):
    if a.cont and a.abort:
        die("--continue and --abort are mutually exclusive")
    if a.cont:
        return _integrate_continue(a)
    if a.abort:
        return _integrate_abort(a)
    if not (a.source and a.mode):
        die("start needs --source and --mode (or use --continue / --abort)")

    op = _in_progress(a.cwd)
    if op:
        die(f"a {op} is already in progress — integrate --continue or --abort first")
    rc, branch, _ = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], a.cwd)
    if rc != 0 or branch == "HEAD":
        die("detached HEAD — switch to a branch before integrating")
    if _dirty(a.cwd):
        die("working tree not clean — commit first so the integration is revertible")
    _validate_source(a.cwd, a.source)

    cmdline = {
        "merge": ["git", "merge", "--no-edit", a.source],
        "rebase": ["git", "-c", "core.editor=true", "rebase", a.source],
        "cherry-pick": ["git", "-c", "core.editor=true", "cherry-pick", a.source],
    }[a.mode]
    rc, out, err = run(cmdline, a.cwd)
    if rc == 0:
        _done_exit(a.cwd, a.mode, a.source)
    if _in_progress(a.cwd) or _unmerged(a.cwd):
        _conflict_exit(a.cwd, a.mode)
    die(f"{a.mode} failed without conflicts: {err or out}")


def _files_with_markers(cwd, paths):
    flagged = []
    for rel in paths:
        p = Path(cwd) / rel
        if not p.is_file():
            continue
        try:
            text = p.read_text(errors="ignore")
        except OSError:
            continue
        if any(line.startswith(CONFLICT_MARKERS) for line in text.splitlines()):
            flagged.append(rel)
    return flagged


def _integrate_continue(a):
    op = _in_progress(a.cwd)
    if not op:
        die("nothing in progress to continue")
    unmerged = _unmerged(a.cwd)
    flagged = _files_with_markers(a.cwd, unmerged)
    if flagged:
        die("conflict markers remain in: " + ", ".join(flagged))
    if unmerged:
        run(["git", "add", "--"] + unmerged, a.cwd, check=True)

    cont = {
        "merge": ["git", "commit", "--no-edit"],
        "rebase": ["git", "-c", "core.editor=true", "rebase", "--continue"],
        "cherry-pick": ["git", "-c", "core.editor=true", "cherry-pick", "--continue"],
    }[op]
    rc, out, err = run(cont, a.cwd)
    if rc == 0 and not _in_progress(a.cwd):
        _done_exit(a.cwd, op)
    if _in_progress(a.cwd):
        # a later rebase/cherry-pick step conflicted; hand back the next batch
        _conflict_exit(a.cwd, op)
    die(f"{op} --continue failed: {err or out}")


def _integrate_abort(a):
    op = _in_progress(a.cwd)
    if not op:
        die("nothing in progress to abort")
    aborter = {"merge": ["git", "merge", "--abort"],
               "rebase": ["git", "rebase", "--abort"],
               "cherry-pick": ["git", "cherry-pick", "--abort"]}[op]
    run(aborter, a.cwd, check=True)
    print(json.dumps({"result": "aborted", "mode": op, "head": _head(a.cwd)}))
