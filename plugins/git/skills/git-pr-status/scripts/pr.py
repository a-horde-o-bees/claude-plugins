"""GitHub PR merge gate + context resolution.

Subcommands:
  gate [--branch X]   merge-readiness classification for the open PR on a
                      branch (defaults to current). Combines PR-level state
                      (gh pr view), commit-level CI annotations
                      (gh api .../check-runs), and base-branch protection
                      (gh api .../branches/{base}/protection → solo vs team).

Output (stdout) is JSON. Skill bodies (/git-pr-status, /git-pr-merge) consume
named fields verbatim — no re-derivation, no inventing.

Blocker model: each blocker carries a severity.
  hard — never bypassed on any path (merge conflicts, red/pending CI, behind base).
  soft — bypassable on the solo fast path with confirmation; blocks the team path
         (review not approved, unresolved-conversation BLOCKED state, CI annotations).

`merge_ready` is true when there are no hard blockers AND (the path is solo OR
there are no soft blockers either). The skill still presents every blocker.
"""

import argparse
import json
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


def classify_checks(rollup: list[dict]) -> str:
    """Reduce a statusCheckRollup to one of: success, failure, pending, none.

    Handles both CheckRun entries (status/conclusion) and legacy StatusContext
    entries (state). Pending dominates nothing — a failure is reported even when
    other checks are still running, so a known-red build never hides behind a
    pending sibling.
    """
    if not rollup:
        return "none"

    saw_pending = False
    for c in rollup:
        if "status" in c and c.get("status") is not None:  # CheckRun
            if c["status"] != "COMPLETED":
                saw_pending = True
                continue
            verdict = (c.get("conclusion") or "").upper()
        else:  # StatusContext
            verdict = (c.get("state") or "").upper()
            if verdict == "PENDING":
                saw_pending = True
                continue
        if verdict in FAIL_CONCLUSIONS:
            return "failure"
        if verdict not in PASS_CONCLUSIONS:
            # Unknown verdict — treat conservatively as failure rather than pass.
            return "failure"

    return "pending" if saw_pending else "success"


def classify_gate(pr: dict, annotation_count: int, protection_enforced: bool) -> dict:
    """Pure merge-readiness classification.

    `pr` is the parsed `gh pr view --json ...` object; `annotation_count` is the
    summed commit-level annotation count; `protection_enforced` is whether the
    base branch carries protection rules (the team-vs-solo discriminator).
    """
    blockers: list[dict] = []

    checks = classify_checks(pr.get("statusCheckRollup") or [])
    if checks == "failure":
        blockers.append({"dimension": "ci", "severity": HARD, "detail": "CI checks failing"})
    elif checks == "pending":
        blockers.append({"dimension": "ci", "severity": HARD, "detail": "CI checks still running"})

    mergeable = (pr.get("mergeable") or "").upper()
    if mergeable == "CONFLICTING":
        blockers.append({"dimension": "mergeable", "severity": HARD, "detail": "merge conflicts with base"})

    state_status = (pr.get("mergeStateStatus") or "").upper()
    if state_status == "BEHIND":
        blockers.append({"dimension": "base", "severity": HARD, "detail": "branch is behind base — rebase/update needed"})
    elif state_status == "DIRTY":
        blockers.append({"dimension": "mergeable", "severity": HARD, "detail": "merge conflicts (dirty merge state)"})
    elif state_status == "BLOCKED":
        # Required reviews unmet and/or unresolved conversations per protection.
        blockers.append({"dimension": "review", "severity": SOFT, "detail": "blocked by branch protection (reviews/conversations)"})
    elif state_status == "DRAFT":
        blockers.append({"dimension": "draft", "severity": SOFT, "detail": "PR is a draft — mark ready before merge"})

    review_decision = (pr.get("reviewDecision") or "").upper()
    if review_decision == "CHANGES_REQUESTED":
        blockers.append({"dimension": "review", "severity": SOFT, "detail": "changes requested by a reviewer"})
    elif review_decision == "REVIEW_REQUIRED" and protection_enforced:
        blockers.append({"dimension": "review", "severity": SOFT, "detail": "required review not yet approved"})

    if annotation_count > 0:
        blockers.append({
            "dimension": "annotations",
            "severity": SOFT,
            "detail": f"{annotation_count} CI annotation(s) — warnings invisible in the PR summary",
        })

    hard = [b for b in blockers if b["severity"] == HARD]
    soft = [b for b in blockers if b["severity"] == SOFT]
    path = "team-gated" if protection_enforced else "solo-immediate"
    merge_ready = not hard and (path == "solo-immediate" or not soft)

    return {
        "protection": "enforced" if protection_enforced else "none",
        "recommended_path": path,
        "merge_ready": merge_ready,
        "checks": checks,
        "annotation_count": annotation_count,
        "review_decision": pr.get("reviewDecision"),
        "merge_state_status": pr.get("mergeStateStatus"),
        "mergeable": pr.get("mergeable"),
        "blockers": blockers,
    }


def _gh_json(args: list[str]):
    out = subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout
    return json.loads(out)


def _protection_enforced(base: str) -> bool:
    """True when the base branch carries protection rules. A 404 (no protection)
    is the solo signal; gh exits non-zero, which we read as 'none'."""
    r = subprocess.run(
        ["gh", "api", f"repos/{{owner}}/{{repo}}/branches/{base}/protection"],
        capture_output=True, text=True,
    )
    return r.returncode == 0


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
    result.update(classify_gate(pr, _annotation_count(head_sha), _protection_enforced(base)))
    print(json.dumps(result))
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="GitHub PR merge gate")
    sub = parser.add_subparsers(dest="cmd", required=True)

    gate = sub.add_parser("gate", help="classify merge-readiness for a branch's PR")
    gate.add_argument("--branch", help="branch name (defaults to current)")
    gate.set_defaults(func=_gate_cmd)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
