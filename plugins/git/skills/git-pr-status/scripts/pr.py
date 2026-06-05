"""GitHub PR merge gate + context resolution.

Subcommands:
  gate [--branch X]   merge-readiness classification for the open PR on a
                      branch (defaults to current). Combines PR-level state
                      (gh pr view), commit-level CI annotations
                      (gh api .../check-runs), and base-branch protection
                      (gh api .../branches/{base}/protection → solo vs team,
                      plus the required-status-check contexts).

Output (stdout) is JSON. Skill bodies (/git-pr-status, /git-pr-merge) consume
named fields verbatim — no re-derivation, no inventing.

Blocker model: each entry carries a severity.
  hard — never bypassed on any path: merge conflicts, behind base, and a
         REQUIRED status check failing or still pending.
  soft — bypassable on the solo fast path with confirmation; blocks the team
         path: review unmet, branch-protection BLOCKED, draft.

Non-required check failures and CI annotation counts are *advisories*, not
blockers — surfaced for visibility, never gating. This mirrors GitHub itself,
which reports such a PR `mergeStateStatus: UNSTABLE` (mergeable) and never
blocks merge on annotation count. The gate reads branch protection's
`required_status_checks.contexts` to tell required from advisory; gating on
"any red check" (or any annotation) would block every PR behind a repo's
report-only checks and benign CI warnings.

`merge_ready` is true when there are no hard blockers AND (the path is solo OR
there are no soft blockers either). The skill still presents every blocker and
advisory.
"""

import argparse
import json
import os
import subprocess
import sys

HARD = "hard"
SOFT = "soft"

# statusCheckRollup conclusion/state values that mean a failed gate.
FAIL_CONCLUSIONS = {
    "FAILURE", "TIMED_OUT", "CANCELLED", "ACTION_REQUIRED", "STARTUP_FAILURE", "ERROR",
}
# Treated as non-blocking successes.
PASS_CONCLUSIONS = {"SUCCESS", "NEUTRAL", "SKIPPED", "STALE", "EXPECTED"}


def _check_verdict(c: dict) -> tuple[str, str]:
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


def classify_required(rollup: list[dict], required_contexts: list[str]) -> tuple[str, list[dict]]:
    """Classify the rollup against the REQUIRED-check set.

    Returns (status, advisories). `status` is one of success/failure/pending/none
    over the *required* checks only — a non-required check never affects it.
    `advisories` lists non-required checks that are failing or pending (surfaced,
    never gating). A required context with no run yet counts as pending (the gate
    waits for it rather than declaring success).
    """
    required = set(required_contexts or [])
    seen: set[str] = set()
    req_fail = req_pending = False
    advisories: list[dict] = []

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


def classify_gate(
    pr: dict, annotation_count: int, protection_enforced: bool, required_contexts: list[str]
) -> dict:
    """Pure merge-readiness classification.

    `pr` is the parsed `gh pr view --json ...` object; `annotation_count` is the
    summed commit-level annotation count; `protection_enforced` is whether the
    base branch carries protection rules (team-vs-solo); `required_contexts` is
    the protection's required-status-check names (required-vs-advisory).
    """
    blockers: list[dict] = []
    advisories: list[dict] = []

    checks, ci_advisories = classify_required(pr.get("statusCheckRollup") or [], required_contexts)
    if checks == "failure":
        blockers.append({"dimension": "ci", "severity": HARD, "detail": "required CI check failing"})
    elif checks == "pending":
        blockers.append({"dimension": "ci", "severity": HARD, "detail": "required CI check still running or not started"})
    for a in ci_advisories:
        advisories.append({"dimension": "ci", "detail": f"non-required check '{a['name']}' {a['state']} — does not block merge"})

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


def _gh_json(args: list[str]):
    out = subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout
    return json.loads(out)


def _protection(base: str, repo: str | None = None) -> tuple[bool, list[str]]:
    """(enforced, required_contexts) for the base branch.

    A 404 (no protection) is the solo signal — gh exits non-zero, read as
    (False, []). When protection exists, return its required-status-check
    contexts (empty list if protection has no required checks).

    `repo` pins an explicit `owner/repo` slug — required when the repo has
    more than one remote (gh's `{owner}/{repo}` placeholder resolves
    ambiguously then). When None, gh resolves from the current repo."""
    slug = repo or "{owner}/{repo}"
    r = subprocess.run(
        ["gh", "api", f"repos/{slug}/branches/{base}/protection"],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        return False, []
    try:
        data = json.loads(r.stdout)
        contexts = (data.get("required_status_checks") or {}).get("contexts") or []
        return True, list(contexts)
    except (json.JSONDecodeError, AttributeError):
        return True, []


def classify_repo(
    perm: str | None,
    is_fork: bool,
    protected: bool,
    update_mode: str | None,
    has_origin_edits: bool,
    x_integration: str | None = None,
) -> dict:
    """Pure per-repo routing decision — root or submodule, same logic.

    Inputs are the detected signals plus parent-owned native `.gitmodules`
    overrides; no `gh`/`git` calls here so it is fully unit-testable.

    - perm: viewerPermission on origin (ADMIN/WRITE/READ/NONE).
    - is_fork: origin is a fork (has an upstream parent).
    - protected: the working branch on origin carries branch protection.
    - update_mode: `submodule.<n>.update` (none/checkout/rebase/merge/'') → pin vs track.
    - has_origin_edits: there is local work to land (gitlink will move / dirty tree).
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

    gaps: list[str] = []
    if perm_u not in ("ADMIN", "WRITE", "READ", "NONE"):
        gaps.append("permission-undeterminable")
    if has_origin_edits and integration == "read-only":
        gaps.append("edits-to-readonly")

    return {"integration": integration, "sync": sync, "upstream": upstream, "gaps": gaps}


def reconcile_merge(merge_commit_sha: str | None, local_head: str | None) -> str:
    """Verdict that a submodule's HEAD matches its PR's recorded merge commit.

    Guards the parent pin advance against trusting `git pull`'s side effect:
    after a squash/rebase merge the merged sha is new, and the pin must capture
    *that* sha, not the discarded feature-branch tip. Prefix-tolerant (short vs
    full). 'unknown' when either sha is missing."""
    a = (merge_commit_sha or "").strip()
    b = (local_head or "").strip()
    if not a or not b:
        return "unknown"
    return "ok" if a == b or a.startswith(b) or b.startswith(a) else "mismatch"


def _annotation_count(sha: str) -> int:
    """Sum commit-level check-run annotation counts — warnings (reviewdog,
    actionlint, CodeQL) that pass the rollup but are invisible in the PR view."""
    r = subprocess.run(
        ["gh", "api", f"repos/{{owner}}/{{repo}}/commits/{sha}/check-runs",
         "--jq", "[.check_runs[].output.annotations_count] | add // 0"],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        return 0
    try:
        return int((r.stdout or "0").strip() or "0")
    except ValueError:
        return 0


def _allowed_strategies() -> list[str]:
    """Merge strategies the repo permits, in squash/merge/rebase order."""
    try:
        repo = _gh_json(["api", "repos/{owner}/{repo}",
                         "--jq", "{squash: .allow_squash_merge, merge: .allow_merge_commit, rebase: .allow_rebase_merge}"])
    except subprocess.CalledProcessError:
        return []
    return [k for k in ("squash", "merge", "rebase") if repo.get(k)]


def _has_admin() -> bool:
    """Whether the viewer has admin rights — gates the offer to override protection
    on the team path (the solo-author-on-a-protected-repo case)."""
    r = subprocess.run(
        ["gh", "api", "repos/{owner}/{repo}", "--jq", ".permissions.admin // false"],
        capture_output=True, text=True,
    )
    return r.returncode == 0 and (r.stdout or "").strip() == "true"


def _origin_slug(remote: str = "origin") -> str | None:
    """`owner/repo` parsed from a remote URL (https or scp-like ssh), or None.

    Parsing the slug ourselves and pinning it on every gh call is the fix for
    gh's ambiguous repo resolution when a repo has both origin and upstream."""
    r = subprocess.run(["git", "remote", "get-url", remote], capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        return None
    url = r.stdout.strip().removesuffix(".git").replace(":", "/")
    parts = [p for p in url.split("/") if p]
    return "/".join(parts[-2:]) if len(parts) >= 2 else None


def _repo_meta(slug: str) -> dict:
    """viewerPermission + fork metadata for an explicit repo slug ({} on failure)."""
    r = subprocess.run(
        ["gh", "repo", "view", slug, "--json", "viewerPermission,isFork,parent"],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        return {}
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return {}


def _default_branch() -> str:
    r = subprocess.run(
        ["git", "symbolic-ref", "--short", "refs/remotes/origin/HEAD"],
        capture_output=True, text=True,
    )
    return r.stdout.strip().removeprefix("origin/") or "main"


def _protection_cmd(args: argparse.Namespace) -> int:
    if args.cwd:
        os.chdir(args.cwd)
    branch = args.branch or _default_branch()
    enforced, contexts = _protection(branch, repo=args.repo or _origin_slug())
    print(json.dumps({"branch": branch, "enforced": enforced, "required_contexts": sorted(contexts)}))
    return 0


def _route_cmd(args: argparse.Namespace) -> int:
    """Resolve a repo's routing (--cwd points at the repo). Combines detected
    gh signals with parent-supplied native overrides (--update-mode/--x-integration)."""
    if args.cwd:
        os.chdir(args.cwd)
    slug = args.repo or _origin_slug()
    branch = args.branch or subprocess.run(
        ["git", "branch", "--show-current"], capture_output=True, text=True,
    ).stdout.strip()
    meta = _repo_meta(slug) if slug else {}
    perm = meta.get("viewerPermission")
    is_fork = bool(meta.get("isFork"))
    enforced = _protection(branch, repo=slug)[0] if branch and slug else False
    parent = meta.get("parent") or {}
    parent_slug = f"{parent['owner']['login']}/{parent['name']}" if parent else None

    result = classify_repo(perm, is_fork, enforced, args.update_mode, args.has_edits, args.x_integration)
    result.update({
        "repo": slug,
        "branch": branch,
        "perm": perm,
        "is_fork": is_fork,
        "protected": enforced,
        "parent": parent_slug,
    })
    print(json.dumps(result))
    return 0


def _gate_cmd(args: argparse.Namespace) -> int:
    branch = args.branch or subprocess.run(
        ["git", "branch", "--show-current"], check=True, capture_output=True, text=True,
    ).stdout.strip()

    view = subprocess.run(
        ["gh", "pr", "view", branch,
         "--json", "number,state,baseRefName,headRefName,url,isDraft,headRefOid,"
                   "reviewDecision,mergeStateStatus,mergeable,statusCheckRollup"],
        capture_output=True, text=True,
    )
    if view.returncode != 0:
        # No PR for this branch — gh exits non-zero with "no pull requests found".
        print(json.dumps({"branch": branch, "pr_exists": False}))
        return 0

    pr = json.loads(view.stdout)
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
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="GitHub PR merge gate")
    sub = parser.add_subparsers(dest="cmd", required=True)

    gate = sub.add_parser("gate", help="classify merge-readiness for a branch's PR")
    gate.add_argument("--branch", help="branch name (defaults to current)")
    gate.set_defaults(func=_gate_cmd)

    prot = sub.add_parser("protection", help="is a branch PR-governed (branch-protected)")
    prot.add_argument("--branch", help="branch (defaults to the repo's default branch)")
    prot.add_argument("--repo", help="owner/repo slug (defaults to origin's)")
    prot.add_argument("--cwd", help="run against the repo at this path")
    prot.set_defaults(func=_protection_cmd)

    route = sub.add_parser("repo-route", help="resolve a repo's routing")
    route.add_argument("--branch", help="working branch (defaults to current)")
    route.add_argument("--repo", help="owner/repo slug (defaults to origin's)")
    route.add_argument("--cwd", help="run against the repo at this path")
    route.add_argument("--update-mode", help="submodule.<n>.update value (pin vs track)")
    route.add_argument("--x-integration", choices=["read-only", "direct", "pr"], help="native integration override")
    route.add_argument("--has-edits", action="store_true", help="local work is pending to land")
    route.set_defaults(func=_route_cmd)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
