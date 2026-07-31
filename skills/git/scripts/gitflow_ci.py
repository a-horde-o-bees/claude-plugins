"""CI status: pure run-set classification plus the ci / ci-watch commands
that recurse submodules deepest-first."""
import json
import subprocess
from pathlib import Path

from gitflow_core import die, repo_paths, run

IN_PROGRESS = {"in_progress", "queued"}


def classify_runs(matching_runs):
    """Pure classification of one repo's matching run set.

    Returns `ci_status` plus the template variables for that status: passed →
    workflow_list; failed → failing_workflow, failing_url; dispatched →
    watch_ids; incomplete → trouble_list; no-runs → nothing further.
    """
    if not matching_runs:
        return {"ci_status": "no-runs"}

    watch_ids = [str(r["databaseId"]) for r in matching_runs if r["status"] in IN_PROGRESS]
    if watch_ids:
        return {"ci_status": "dispatched", "watch_ids": watch_ids}

    if all(r["conclusion"] == "success" for r in matching_runs):
        return {"ci_status": "passed",
                "workflow_list": ", ".join(r["workflowName"] for r in matching_runs)}

    failing = next((r for r in matching_runs if r["conclusion"] == "failure"), None)
    if failing:
        return {"ci_status": "failed",
                "failing_workflow": failing["workflowName"],
                "failing_url": failing["url"]}

    non_success = [r for r in matching_runs if r["conclusion"] != "success"]
    return {"ci_status": "incomplete",
            "trouble_list": "\n".join(f"{r['workflowName']}: {r['conclusion']}" for r in non_success)}


def _list_runs(cwd, branch=None):
    """Parsed `gh run list` for the repo, or None when gh cannot answer
    (no remote, no auth) — the caller reports that, never guesses."""
    args = ["gh", "run", "list", "--limit", "10",
            "--json", "databaseId,headSha,conclusion,status,workflowName,url"]
    if branch:
        args += ["--branch", branch]
    rc, out, _ = run(args, cwd)
    if rc != 0:
        return None
    return json.loads(out)


def ci_repo(cwd):
    """CI classification for one repo: no-ci when it has no workflows, else the
    run set matching the branch tip on origin (CI runs the pushed commit)."""
    _, branch, _ = run(["git", "branch", "--show-current"], cwd)
    rc, sha, _ = run(["git", "rev-parse", f"origin/{branch}"], cwd) if branch else (1, "", "")
    if rc != 0:
        _, sha, _ = run(["git", "rev-parse", "HEAD"], cwd)
    entry = {"cwd": str(cwd), "branch": branch, "sha": sha, "sha_short": sha[:8]}
    if not (Path(cwd) / ".github" / "workflows").is_dir():
        entry["ci_status"] = "no-ci"
        return entry
    runs = _list_runs(cwd, branch or None)
    if runs is None:
        entry["ci_status"] = "unavailable"
        return entry
    entry.update(classify_runs([r for r in runs if r["headSha"] == sha]))
    return entry


def cmd_ci(a):
    repos = []
    for path in repo_paths(a.cwd):
        entry = ci_repo(path)
        if a.branch and Path(path) == Path(a.cwd) and entry["branch"] != a.branch:
            die(f"{path}: on branch {entry['branch']}, not {a.branch}")
        repos.append(entry)
    watches = [{"cwd": r["cwd"], "sha": r["sha"], "watch_ids": r["watch_ids"]}
               for r in repos if r["ci_status"] == "dispatched"]
    print(json.dumps({"repos": repos, "watches": watches}, indent=1))


def cmd_ci_watch(a):
    for run_id in a.run_ids:
        # Don't fail-fast on individual run failure — gather final state across
        # all watched runs so the classifier sees the full picture.
        subprocess.run(["gh", "run", "watch", run_id, "--exit-status"], cwd=a.cwd, check=False)
    runs = _list_runs(a.cwd)
    out = {"sha": a.sha, "sha_short": a.sha[:8]}
    if runs is None:
        out["ci_status"] = "unavailable"
    else:
        out.update(classify_runs([r for r in runs if r["headSha"] == a.sha]))
    print(json.dumps(out))
