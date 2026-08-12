"""Shared core: process/exit primitives and the repo-tree probes
(submodule entries, per-repo state, depth-first walks, default branch)."""
import re
import subprocess
import sys
from pathlib import Path
from typing import NoReturn

SUSPICIOUS = re.compile(
    r"(^|/)(\.env[^/]*|.*\.(pem|key|p12|pfx)|id_rsa[^/]*|credentials[^/]*|.*secret.*|node_modules|dist|build|__pycache__)(/|$)",
    re.IGNORECASE)
BIG_FILE = 5 * 1024 * 1024


def run(args, cwd=".", check=False, raw=False):
    """raw=True returns stdout unstripped — for column-significant output
    like `git status --short`, whose first line's leading space is data."""
    p = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    if check and p.returncode != 0:
        die(f"command failed in {cwd}: {' '.join(args)}\n{p.stderr.strip()}")
    out = p.stdout if raw else p.stdout.strip()
    return p.returncode, out, p.stderr.strip()


def die(msg, code=1) -> NoReturn:
    print(f"BLOCKED: {msg}")
    sys.exit(code)


def submodule_entries(cwd):
    rc, out, _ = run(["git", "config", "-f", ".gitmodules", "--get-regexp", r"^submodule\..+\.path$"], cwd)
    entries = []
    if rc == 0:
        for line in out.splitlines():
            key, _, path = line.partition(" ")
            name = key[len("submodule."):-len(".path")]
            rcb, branch, _ = run(["git", "config", "-f", ".gitmodules", f"submodule.{name}.branch"], cwd)
            entries.append({"name": name, "path": path, "declared_branch": branch if rcb == 0 else None})
    return entries


def repo_state(cwd, paths=None):
    """Everything code can decide about one repo (no recursion)."""
    st = {"cwd": str(cwd), "blockers": [], "advisories": []}
    rc, branch, _ = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd)
    if rc != 0:
        st["blockers"].append("not a git repository")
        return st
    st["branch"] = branch
    st["detached"] = branch == "HEAD"

    scope = ["--"] + paths if paths else []
    _, status, _ = run(["git", "status", "--porcelain"] + scope, cwd)
    st["status"] = status.splitlines()
    _, diffstat, _ = run(["git", "diff", "--stat"] + scope, cwd)
    st["diffstat"] = diffstat

    # co-author trailer opt-in — surfaced here because a boxed repo's read passthrough
    # excludes `git config`, so inspect is the trailer condition's only sanctioned source
    rc_ca, coauthor, _ = run(["git", "config", "--type=bool", "--get", "user.claude-coauthor"], cwd)
    st["claude_coauthor"] = (coauthor.strip() == "true") if rc_ca == 0 else None

    # default branch + protection + publicness (all graceful without a remote / gh)
    _, head_ref, _ = run(["git", "symbolic-ref", "--short", "refs/remotes/origin/HEAD"], cwd)
    st["default_branch"] = head_ref.split("/", 1)[1] if "/" in head_ref else None
    st["protected_default"] = None
    st["public_bound"] = None
    rc, name_with_owner, _ = run(["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"], cwd)
    if rc == 0 and name_with_owner and st["default_branch"]:
        rc2, _, _ = run(["gh", "api", f"repos/{name_with_owner}/branches/{st['default_branch']}/protection"], cwd)
        st["protected_default"] = rc2 == 0
        rc3, pub, _ = run(["gh", "api", f"repos/{name_with_owner}",
                           "--jq", 'if .private==false or .fork then "yes" else "no" end'], cwd)
        st["public_bound"] = pub == "yes" if rc3 == 0 else None

    # suspicious untracked
    st["suspicious_untracked"] = []
    for line in st["status"]:
        if not line.startswith("??"):
            continue
        rel = line[3:]
        p = Path(cwd) / rel
        big = p.is_file() and p.stat().st_size > BIG_FILE
        if SUSPICIOUS.search(rel) or big:
            st["suspicious_untracked"].append(rel + (" (large)" if big else ""))

    # submodules: conformance + pin advances
    st["submodules"] = []
    for ent in submodule_entries(cwd):
        sub = dict(ent)
        sub_cwd = str(Path(cwd) / ent["path"])
        rc, sub_branch, _ = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], sub_cwd)
        if rc != 0:
            sub["blocker"] = "submodule not initialized"
            st["submodules"].append(sub)
            continue
        sub["detached"] = sub_branch == "HEAD"
        if sub["detached"]:
            if not ent["declared_branch"]:
                sub["blocker"] = "detached with no branch= in .gitmodules"
            else:
                _, head, _ = run(["git", "rev-parse", "HEAD"], sub_cwd)
                rcd, decl, _ = run(["git", "rev-parse", "--verify", ent["declared_branch"]], sub_cwd)
                sub["normalize"] = ("create-branch" if rcd != 0
                                    else "attach" if decl == head
                                    else None)
                if sub["normalize"] is None:
                    sub["blocker"] = (f"declared branch {ent['declared_branch']} ({decl[:8]}) "
                                      f"diverges from checked-out HEAD ({head[:8]})")
        rc, _, _ = run(["git", "diff", "--quiet", "--", ent["path"]], cwd)
        if rc != 0:
            _, pinned_line, _ = run(["git", "ls-tree", "HEAD", "--", ent["path"]], cwd)
            pinned = pinned_line.split()[2] if len(pinned_line.split()) > 2 else None
            _, head_sha, _ = run(["git", "rev-parse", "HEAD"], sub_cwd)
            log = ""
            if pinned:
                _, log, _ = run(["git", "log", "--oneline", f"{pinned}..{head_sha}"], sub_cwd)
            sub["pin_advance"] = {"pinned": pinned, "head": head_sha, "log": log.splitlines()}
        if sub.get("blocker"):
            st["blockers"].append(f"submodule {ent['path']}: {sub['blocker']}")
        st["submodules"].append(sub)
    return st


def walk(cwd, paths=None, depth=0):
    """Depth-first repo states, deepest first in the returned list."""
    st = repo_state(cwd, paths)
    out = []
    for sub in st.get("submodules", []):
        if not sub.get("blocker"):
            out.extend(walk(str(Path(cwd) / sub["path"]), None, depth + 1))
    st["depth"] = depth
    out.append(st)
    return out


def repo_paths(cwd):
    """Initialized repo paths, deepest first, parent last. Light — no gh calls."""
    out = []
    for ent in submodule_entries(cwd):
        sub = Path(cwd) / ent["path"]
        if (sub / ".git").exists():
            out.extend(repo_paths(str(sub)))
    out.append(str(cwd))
    return out


def _default_branch(cwd="."):
    _, out, _ = run(["git", "symbolic-ref", "--short", "refs/remotes/origin/HEAD"], cwd)
    return out.removeprefix("origin/") or "main"
