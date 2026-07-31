"""PR lifecycle mechanics: pr-preflight, pr-create, pr-watch-checks, merge,
pr-cleanup. Judgment (title, body, strategy choice) arrives as arguments."""
import json
import os

from gitflow_core import _default_branch, die, run
from gitflow_gate import _allowed_strategies


def cmd_pr_preflight(a):
    """The mechanical head of pr-open: preconditions plus authoring seeds.
    Judgment stays with the caller: the title, body, and depth tier."""
    if a.cwd != ".":
        os.chdir(a.cwd)
    _, branch, _ = run(["git", "branch", "--show-current"])
    if not branch:
        die("detached HEAD — checkout a branch first")
    rc, out, _ = run(["gh", "pr", "view", branch, "--json", "number,url,state"])
    if rc == 0:
        pr = json.loads(out)
        if (pr.get("state") or "").upper() == "OPEN":
            print(json.dumps({"branch": branch, "pr_exists": True, **pr}))
            return
    rc, _, _ = run(["git", "rev-parse", "--abbrev-ref", "@{upstream}"])
    if rc != 0:
        die(f"{branch} is not on origin — run /git push --branch {branch} first, then re-open")
    _, ahead, _ = run(["git", "rev-list", "@{upstream}..HEAD", "--count"])
    if int(ahead or "0") > 0:
        die(f"{ahead} local commit(s) unpushed — run /git push --branch {branch} first")
    base = a.base or _default_branch()
    _, subjects, _ = run(["git", "log", "--no-merges", "--pretty=format:%s%n%b", f"{base}...HEAD"])
    _, stat, _ = run(["git", "diff", "--stat", f"{base}...HEAD"])
    print(json.dumps({
        "branch": branch, "pr_exists": False, "base": base,
        "subjects": subjects.splitlines(), "diffstat": stat,
    }, indent=1))
    print("\nNEEDS: title (≤ ~70 chars, no trailing period) + body file — depth scaled "
          "to the diffstat weight; then pr-create")


def cmd_pr_create(a):
    if a.cwd != ".":
        os.chdir(a.cwd)
    _, branch, _ = run(["git", "branch", "--show-current"], check=True)
    upstream = getattr(a, "repo", None)
    if upstream:
        # Cross-repo (fork → upstream). Fine-grained PATs are resource-owner-bound
        # and 403 here regardless of grants; emit the compare-URL fallback instead
        # of dying so the caller can hand it to the user.
        _, login, _ = run(["gh", "api", "user", "--jq", ".login"], check=True)
        head = getattr(a, "head", None) or f"{login.strip()}:{branch}"
        base = a.base or _upstream_default_branch(upstream)
        args = ["gh", "pr", "create", "--repo", upstream, "--base", base,
                "--head", head, "--title", a.title, "--body-file", a.body_file]
        if a.draft:
            args.append("--draft")
        rc, out, err = run(args)
        if rc != 0:
            repo_name = upstream.split("/")[1]
            compare = (f"https://github.com/{upstream}/compare/{base}..."
                       f"{login.strip()}:{repo_name}:{branch}")
            print(json.dumps({"branch": branch, "base": base, "url": None,
                              "error": (err or out).strip().splitlines()[-1] if (err or out) else "pr create failed",
                              "fallback_compare_url": compare, "body_file": a.body_file}))
            return
        print(json.dumps({"branch": branch, "base": base,
                          "url": out.splitlines()[-1] if out else None, "draft": a.draft}))
        return
    base = a.base or _default_branch()
    args = ["gh", "pr", "create", "--base", base, "--head", branch,
            "--title", a.title, "--body-file", a.body_file]
    if a.draft:
        args.append("--draft")
    _, out, _ = run(args, check=True)
    print(json.dumps({"branch": branch, "base": base, "url": out.splitlines()[-1] if out else None,
                      "draft": a.draft}))


def _upstream_default_branch(repo):
    _, out, _ = run(["gh", "api", f"repos/{repo}", "--jq", ".default_branch"], check=True)
    return out.strip() or "main"


def cmd_search_prior_art(a):
    """Duplicate check before contributing: PRs + issues, all states, JSON."""
    fields = "number,title,state,url,updatedAt"
    results = {}
    for kind in ("prs", "issues"):
        rc, out, err = run(["gh", "search", kind, "--repo", a.repo, "--limit",
                            str(a.limit), "--json", fields] + a.terms)
        results[kind] = json.loads(out) if rc == 0 and out.strip() else []
        if rc != 0:
            results[f"{kind}_error"] = (err or "").strip().splitlines()[-1] if err else "search failed"
    print(json.dumps({"repo": a.repo, "terms": a.terms, **results}))


def cmd_contribute_prep(a):
    """Fork upstream, clone the fork beside --workdir, wire the upstream remote.
    Fork-as-origin keeps the standard push/commit commands working unchanged."""
    _, login, _ = run(["gh", "api", "user", "--jq", ".login"], check=True)
    login = login.strip()
    repo_name = a.upstream.split("/")[1]
    run(["gh", "repo", "fork", a.upstream, "--clone=false"], check=True)
    clone_path = os.path.join(a.workdir, repo_name)
    if not os.path.isdir(os.path.join(clone_path, ".git")):
        clone_args = ["git", "clone", f"https://github.com/{login}/{repo_name}.git", clone_path]
        if a.shallow:
            clone_args[2:2] = ["--depth", "1"]
        run(clone_args, check=True)
    rc, _, _ = run(["git", "remote", "get-url", "upstream"], clone_path)
    if rc != 0:
        run(["git", "remote", "add", "upstream", f"https://github.com/{a.upstream}.git"],
            clone_path, check=True)
    default = _upstream_default_branch(a.upstream)
    print(json.dumps({"clone_path": clone_path, "fork": f"{login}/{repo_name}",
                      "upstream": a.upstream, "default_branch": default,
                      "origin": "fork", "note": "origin is the fork; push lands there"}))


def cmd_pr_watch_checks(a):
    """Block until every check on the PR settles (used by pr-merge --auto).
    Non-zero gh exit means a check failed — the caller re-gates either way."""
    rc, _, _ = run(["gh", "pr", "checks", str(a.pr), "--watch", "--interval", "20"], a.cwd)
    print(json.dumps({"pr": a.pr, "settled": True, "all_passed": rc == 0}))


def cmd_merge(a):
    if a.cwd != ".":
        os.chdir(a.cwd)
    allowed = _allowed_strategies()
    if allowed and a.strategy not in allowed:
        die(f"strategy {a.strategy!r} not allowed by repo settings; allowed: {', '.join(allowed)}")
    args = ["gh", "pr", "merge", str(a.pr), f"--{a.strategy}"]
    if a.admin:
        args.append("--admin")
    run(args, check=True)
    print(json.dumps({"pr": a.pr, "merged": True, "strategy": a.strategy, "admin": a.admin}))


def cmd_pr_cleanup(a):
    """Restore local base and tear down a merged head branch. The PR's MERGED
    state is the authority, not git ancestry — squash/rebase merges leave the
    head's commits absent from base, so `-d` wrongly reports "not merged".
    Without a merged PR, a head carrying commits absent from base is refused."""
    if a.cwd != ".":
        os.chdir(a.cwd)
    _, current, _ = run(["git", "branch", "--show-current"])
    head = a.head or current
    if not head:
        die("detached HEAD and no --head given")
    base = a.base or _default_branch()
    if head == base:
        die(f"{head} is the base branch — nothing to clean up")

    rc, out, _ = run(["gh", "pr", "view", head, "--json", "state", "--jq", ".state"])
    merged = rc == 0 and out == "MERGED"
    if not merged:
        run(["git", "fetch", "origin", base, "--quiet"], check=True)
        _, unmerged, _ = run(["git", "rev-list", f"origin/{base}..{head}", "--count"])
        if int(unmerged or "0") > 0:
            die(f"{head} has {unmerged} commit(s) not in {base} and no merged PR — "
                "refusing to delete; merge or discard explicitly first")

    if current == head:
        run(["git", "checkout", base], check=True)
        current = base
    base_synced = current == base
    if base_synced:
        run(["git", "pull", "--prune"], check=True)

    rc, _, _ = run(["git", "ls-remote", "--exit-code", "--heads", "origin", head])
    remote_deleted = False
    if rc == 0:
        run(["git", "push", "origin", "--delete", head], check=True)
        remote_deleted = True

    rc, _, _ = run(["git", "show-ref", "--verify", "--quiet", f"refs/heads/{head}"])
    local_deleted = False
    if rc == 0:
        run(["git", "branch", "-D" if merged else "-d", head], check=True)
        local_deleted = True

    print(json.dumps({
        "head": head, "base": base, "pr_merged": merged,
        "base_synced": base_synced,
        "remote_head": "deleted" if remote_deleted else "already gone",
        "local_head": "deleted" if local_deleted else "already gone",
    }))
