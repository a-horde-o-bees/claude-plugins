"""PR gate + routing: merge-readiness classification (required checks,
blocker model) and per-repo integration routing with gap detection."""
import json
import os
from pathlib import Path

from gitflow_core import _default_branch, run, submodule_entries

HARD = "hard"
SOFT = "soft"

# statusCheckRollup conclusion/state values that mean a failed gate.
FAIL_CONCLUSIONS = {
    "FAILURE", "TIMED_OUT", "CANCELLED", "ACTION_REQUIRED", "STARTUP_FAILURE", "ERROR",
}
# Treated as non-blocking successes.
PASS_CONCLUSIONS = {"SUCCESS", "NEUTRAL", "SKIPPED", "STALE", "EXPECTED"}


def _check_verdict(c):
    """(check name, verdict) for one statusCheckRollup entry.

    verdict is one of: pass, fail, pending. Handles both CheckRun entries
    (status/conclusion + `name`) and legacy StatusContext entries (state +
    `context`). Unknown conclusions are treated conservatively as fail.
    """
    name = c.get("name") or c.get("context") or "?"
    if c.get("status") is not None:  # CheckRun
        if c["status"] != "COMPLETED":
            return name, "pending"
        verdict = (c.get("conclusion") or "").upper()
    else:  # StatusContext
        verdict = (c.get("state") or "").upper()
        if verdict == "PENDING":
            return name, "pending"
    if verdict in PASS_CONCLUSIONS:
        return name, "pass"
    return name, "fail"


def classify_required(rollup, required_contexts):
    """Classify the rollup against the REQUIRED-check set.

    Returns (status, advisories). `status` is one of success/failure/pending/none
    over the *required* checks only — a non-required check never affects it.
    `advisories` lists non-required checks that are failing or pending (surfaced,
    never gating). A required context with no run yet counts as pending (the gate
    waits for it rather than declaring success).
    """
    required = set(required_contexts or [])
    seen = set()
    req_fail = req_pending = False
    advisories = []

    for c in rollup or []:
        name, verdict = _check_verdict(c)
        if name in required:
            seen.add(name)
            if verdict == "pending":
                req_pending = True
            elif verdict == "fail":
                req_fail = True
        elif verdict in ("fail", "pending"):
            advisories.append({"name": name, "state": "failing" if verdict == "fail" else "pending"})

    if not required:
        status = "none"
    elif req_fail:
        status = "failure"
    elif req_pending or (required - seen):
        status = "pending"
    else:
        status = "success"
    return status, advisories


def classify_gate(pr, annotation_count, protection_enforced, required_contexts):
    """Pure merge-readiness classification.

    `pr` is the parsed `gh pr view --json ...` object; `annotation_count` is the
    summed commit-level annotation count; `protection_enforced` is whether the
    base branch carries protection rules (team-vs-solo); `required_contexts` is
    the protection's required-status-check names (required-vs-advisory).

    Blocker model: hard — never bypassed on any path (conflicts, behind base,
    a REQUIRED check failing or pending); soft — bypassable on the solo path
    with confirmation (review unmet, protection-BLOCKED, draft). Non-required
    check failures and annotation counts are advisories, never gating — GitHub
    itself reports such a PR mergeable (UNSTABLE) and never blocks on
    annotation count.
    """
    blockers = []
    advisories = []

    checks, ci_advisories = classify_required(pr.get("statusCheckRollup") or [], required_contexts)
    if checks == "failure":
        blockers.append({"dimension": "ci", "severity": HARD, "detail": "required CI check failing"})
    elif checks == "pending":
        blockers.append({"dimension": "ci", "severity": HARD, "detail": "required CI check still running or not started"})
    for adv in ci_advisories:
        advisories.append({"dimension": "ci", "detail": f"non-required check '{adv['name']}' {adv['state']} — does not block merge"})

    mergeable = (pr.get("mergeable") or "").upper()
    if mergeable == "CONFLICTING":
        blockers.append({"dimension": "mergeable", "severity": HARD, "detail": "merge conflicts with base"})

    state_status = (pr.get("mergeStateStatus") or "").upper()
    if state_status == "BEHIND":
        blockers.append({"dimension": "base", "severity": HARD, "detail": "branch is behind base — rebase/update needed"})
    elif state_status == "DIRTY":
        blockers.append({"dimension": "mergeable", "severity": HARD, "detail": "merge conflicts (dirty merge state)"})
    elif state_status == "DRAFT":
        blockers.append({"dimension": "draft", "severity": SOFT, "detail": "PR is a draft — mark ready before merge"})
    elif state_status == "BLOCKED" and protection_enforced and checks != "failure":
        # Protection blocks for a reason not already named by the required-check
        # or review classification below (e.g. unresolved conversations).
        blockers.append({"dimension": "protection", "severity": SOFT, "detail": "branch protection: requirements unmet (reviews/conversations)"})

    review_decision = (pr.get("reviewDecision") or "").upper()
    if review_decision == "CHANGES_REQUESTED":
        blockers.append({"dimension": "review", "severity": SOFT, "detail": "changes requested by a reviewer"})
    elif review_decision == "REVIEW_REQUIRED" and protection_enforced:
        blockers.append({"dimension": "review", "severity": SOFT, "detail": "required review not yet approved"})

    if annotation_count > 0:
        advisories.append({
            "dimension": "annotations",
            "detail": f"{annotation_count} CI annotation(s) across checks — warnings invisible in the PR summary; inspect, but they do not gate (GitHub never blocks on annotation count)",
        })

    hard = [b for b in blockers if b["severity"] == HARD]
    soft = [b for b in blockers if b["severity"] == SOFT]
    path = "team-gated" if protection_enforced else "solo-immediate"
    merge_ready = not hard and (path == "solo-immediate" or not soft)

    return {
        "protection": "enforced" if protection_enforced else "none",
        "required_contexts": sorted(required_contexts or []),
        "recommended_path": path,
        "merge_ready": merge_ready,
        "checks": checks,
        "annotation_count": annotation_count,
        "review_decision": pr.get("reviewDecision"),
        "merge_state_status": pr.get("mergeStateStatus"),
        "mergeable": pr.get("mergeable"),
        "blockers": blockers,
        "advisories": advisories,
    }


def _protection(base, cwd=".", repo=None):
    """(enforced, required_contexts) for the base branch.

    A 404 (no protection) is the solo signal. `repo` pins an explicit
    `owner/repo` slug — required when the repo has more than one remote
    (gh's `{owner}/{repo}` placeholder resolves ambiguously then)."""
    slug = repo or "{owner}/{repo}"
    rc, out, _ = run(["gh", "api", f"repos/{slug}/branches/{base}/protection"], cwd)
    if rc != 0:
        return False, []
    try:
        data = json.loads(out)
        contexts = (data.get("required_status_checks") or {}).get("contexts") or []
        return True, list(contexts)
    except (json.JSONDecodeError, AttributeError):
        return True, []


def classify_repo(perm, is_fork, protected, update_mode, has_origin_edits, x_integration=None):
    """Pure per-repo routing decision — root or submodule, same logic.

    - perm: viewerPermission on origin (ADMIN/WRITE/READ/NONE).
    - is_fork: origin is a fork (has an upstream parent).
    - protected: the branch work lands on carries branch protection.
    - update_mode: `submodule.<n>.update` (rebase/merge ⇒ track, else pin).
    - has_origin_edits: there is local work to land.
    - x_integration: explicit native override read-only|direct|pr, else None.

    Returns {integration, sync, upstream, gaps}. `gaps` lists routing-blocking
    ambiguities the parent must resolve before a deterministic checkpoint.
    """
    perm_u = (perm or "").upper()
    writable = perm_u in ("ADMIN", "WRITE")

    if x_integration in ("read-only", "direct", "pr"):
        integration = x_integration
    elif not writable:
        integration = "read-only"
    elif protected:
        integration = "pr"
    else:
        integration = "direct"

    sync = "track" if (update_mode or "").lower() in ("rebase", "merge") else "pin"
    upstream = "fork" if is_fork else "none"

    gaps = []
    if perm_u not in ("ADMIN", "WRITE", "READ", "NONE"):
        gaps.append("permission-undeterminable")
    if has_origin_edits and integration == "read-only":
        gaps.append("edits-to-readonly")

    return {"integration": integration, "sync": sync, "upstream": upstream, "gaps": gaps}


def branch_gap(integration, is_submodule, branch_declared):
    """Whether an undeclared `branch =` is a routing gap for this repo.

    A will-push submodule (direct/pr integration) with no declared branch is a
    gap — checkpoint halts rather than guess which branch edits push to."""
    return is_submodule and not branch_declared and integration in ("direct", "pr")


def _annotation_count(sha, cwd="."):
    """Sum commit-level check-run annotation counts — warnings (reviewdog,
    actionlint, CodeQL) that pass the rollup but are invisible in the PR view."""
    rc, out, _ = run(["gh", "api", f"repos/{{owner}}/{{repo}}/commits/{sha}/check-runs",
                      "--jq", "[.check_runs[].output.annotations_count] | add // 0"], cwd)
    if rc != 0:
        return 0
    try:
        return int((out or "0").strip() or "0")
    except ValueError:
        return 0


def _allowed_strategies(cwd="."):
    """Merge strategies the repo permits, in squash/merge/rebase order."""
    rc, out, _ = run(["gh", "api", "repos/{owner}/{repo}",
                      "--jq", "{squash: .allow_squash_merge, merge: .allow_merge_commit, rebase: .allow_rebase_merge}"], cwd)
    if rc != 0:
        return []
    repo = json.loads(out)
    return [k for k in ("squash", "merge", "rebase") if repo.get(k)]


def _has_admin(cwd="."):
    """Whether the viewer has admin rights — gates the offer to override protection
    on the team path (the solo-author-on-a-protected-repo case)."""
    rc, out, _ = run(["gh", "api", "repos/{owner}/{repo}", "--jq", ".permissions.admin // false"], cwd)
    return rc == 0 and out == "true"


def _origin_slug(remote="origin", cwd="."):
    """`owner/repo` parsed from a remote URL (https or scp-like ssh), or None.

    Parsing the slug ourselves and pinning it on every gh call is the fix for
    gh's ambiguous repo resolution when a repo has both origin and upstream."""
    rc, out, _ = run(["git", "remote", "get-url", remote], cwd)
    if rc != 0 or not out:
        return None
    url = out.removesuffix(".git").replace(":", "/")
    parts = [p for p in url.split("/") if p]
    return "/".join(parts[-2:]) if len(parts) >= 2 else None


def _repo_meta(slug, cwd="."):
    """viewerPermission + fork metadata for an explicit repo slug ({} on failure)."""
    rc, out, _ = run(["gh", "repo", "view", slug, "--json",
                      "viewerPermission,isFork,parent,defaultBranchRef"], cwd)
    if rc != 0:
        return {}
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return {}


def _gitmodules(name, key, cwd="."):
    _, out, _ = run(["git", "config", "-f", ".gitmodules", f"submodule.{name}.{key}"], cwd)
    return out


def _resolve_route(path, name=None, cwd="."):
    """Mechanical routing verdict for one repo. `path` is "." for the parent or
    a submodule path; `name` is the submodule's .gitmodules section name (None
    for the parent). Runs all gh/git probes in-process — no caller reasoning."""
    is_sub = path != "."
    rcwd = cwd if path == "." else str(Path(cwd) / path)
    slug = _origin_slug(cwd=rcwd)
    _, branch, _ = run(["git", "branch", "--show-current"], rcwd)
    meta = _repo_meta(slug, cwd) if slug else {}
    perm = meta.get("viewerPermission")
    is_fork = bool(meta.get("isFork"))

    update_mode = _gitmodules(name, "update", cwd) if is_sub and name else ""
    x_int = (_gitmodules(name, "x-integration", cwd) if is_sub and name else "") or None
    declared_branch = _gitmodules(name, "branch", cwd) if is_sub and name else ""
    branch_declared = bool(declared_branch) if is_sub else True

    # Integration is a repo property: route on the protection of the branch work
    # lands on — the repo's default branch (a submodule's declared `branch=` if
    # set), never whatever branch happens to be checked out now. A checkpoint run
    # from a feature branch must still read the repo as pr-integrated.
    default_branch = (meta.get("defaultBranchRef") or {}).get("name") or ""
    if not default_branch and not is_sub:
        default_branch = _default_branch(rcwd)
    policy_branch = (declared_branch or default_branch) if is_sub else default_branch
    protected = _protection(policy_branch, cwd=rcwd, repo=slug)[0] if policy_branch and slug else False

    if is_sub:
        _, outer, _ = run(["git", "status", "--short", "--", path], cwd)
        _, inner, _ = run(["git", "status", "--short"], rcwd)
        has_edits = bool(outer or inner)
    else:
        _, out, _ = run(["git", "status", "--short"], rcwd)
        has_edits = bool(out)

    route = classify_repo(perm, is_fork, protected, update_mode, has_edits, x_int)
    if branch_gap(route["integration"], is_sub, branch_declared):
        route["gaps"].append("undeclared-branch")

    parent = meta.get("parent") or {}
    route.update({
        "path": path,
        "name": name,
        "branch": branch,
        "declared_branch": declared_branch or None,
        "perm": perm,
        "is_fork": is_fork,
        "protected": protected,
        "parent": f"{parent['owner']['login']}/{parent['name']}" if parent else None,
        "has_edits": has_edits,
    })
    return route


def _gap_fix(gap, route):
    name = route.get("name") or route["path"]
    if gap == "undeclared-branch":
        return f"git config -f .gitmodules submodule.{name}.branch {route.get('branch') or '<branch>'}  (or run /git doctor)"
    if gap == "permission-undeterminable":
        return f"check gh auth / access to {route.get('path')} (gh repo view) — cannot read viewerPermission"
    if gap == "edits-to-readonly":
        return f"{route['path']} has local edits but you only have READ — land them in a writable fork, or set submodule.{name}.x-integration"
    return "resolve the routing ambiguity (see /git doctor)"


def _routes(cwd, paths=None):
    """Route the parent + every declared submodule; collect all gaps."""
    repos = [_resolve_route(".", cwd=cwd)]
    for ent in submodule_entries(cwd):
        path = ent["path"].strip()
        if paths and not any(path == p or path.startswith(p.rstrip("/") + "/") for p in paths):
            continue
        repos.append(_resolve_route(path, ent["name"], cwd=cwd))
    gaps = [{"repo": r["path"], "gap": g, "fix": _gap_fix(g, r)} for r in repos for g in r["gaps"]]
    return {"ok": not gaps, "gaps": gaps, "repos": repos}


def cmd_routes(a):
    print(json.dumps(_routes(a.cwd, a.paths or None)))


def cmd_protection(a):
    branch = a.branch or _default_branch(a.cwd)
    enforced, contexts = _protection(branch, cwd=a.cwd, repo=a.repo or _origin_slug(cwd=a.cwd))
    print(json.dumps({"branch": branch, "enforced": enforced, "required_contexts": sorted(contexts)}))


def cmd_gate(a):
    if a.cwd != ".":
        os.chdir(a.cwd)
    branch = a.branch
    if not branch:
        _, branch, _ = run(["git", "branch", "--show-current"], check=True)

    rc, out, _ = run(["gh", "pr", "view", branch,
                      "--json", "number,state,baseRefName,headRefName,url,isDraft,headRefOid,"
                                "reviewDecision,mergeStateStatus,mergeable,statusCheckRollup"])
    if rc != 0:
        # No PR for this branch — gh exits non-zero with "no pull requests found".
        print(json.dumps({"branch": branch, "pr_exists": False}))
        return

    pr = json.loads(out)
    base = pr.get("baseRefName") or "main"
    head_sha = pr.get("headRefOid") or ""
    enforced, required_contexts = _protection(base)

    result = {
        "branch": branch,
        "pr_exists": True,
        "pr_number": pr.get("number"),
        "state": pr.get("state"),
        "base": base,
        "head": pr.get("headRefName"),
        "url": pr.get("url"),
        "is_draft": pr.get("isDraft"),
        "head_sha": head_sha,
        "head_sha_short": head_sha[:8],
        "allowed_strategies": _allowed_strategies(),
        "has_admin": _has_admin(),
    }
    result.update(classify_gate(pr, _annotation_count(head_sha), enforced, required_contexts))
    print(json.dumps(result))
