"""GitHub Actions CI operations: classify and watch.

Subcommands:
  classify --branch X   read gh run list for branch HEAD, return CI status as JSON
  classify --sha X      same but for a specific commit SHA
  watch --sha X --run-ids X Y Z   block on watched runs, then re-classify

Output (stdout) is JSON with a `ci_status` discriminator and named
template variables that _ci.md and _ci_watch.md substitute into their
return templates. `ci_status` values: passed, failed, dispatched,
incomplete, no-runs (the `watch` subcommand never returns `dispatched`
or `no-runs` since it always runs against an existing in-flight set).
"""

import argparse
import json
import subprocess
import sys

IN_PROGRESS = {"in_progress", "queued"}


def classify_runs(matching_runs: list[dict]) -> dict:
    """Pure classification given the matching run set.

    Returns a dict with `ci_status` and the named template variables
    appropriate for that status — see `_ci.md` § Report for the per-status
    variable shape.
    """
    if not matching_runs:
        return {"ci_status": "no-runs"}

    watch_ids = [
        str(r["databaseId"]) for r in matching_runs if r["status"] in IN_PROGRESS
    ]
    if watch_ids:
        return {"ci_status": "dispatched", "watch_ids": watch_ids}

    if all(r["conclusion"] == "success" for r in matching_runs):
        return {
            "ci_status": "passed",
            "workflow_list": ", ".join(r["workflowName"] for r in matching_runs),
        }

    failing = next(
        (r for r in matching_runs if r["conclusion"] == "failure"), None
    )
    if failing:
        return {
            "ci_status": "failed",
            "failing_workflow": failing["workflowName"],
            "failing_url": failing["url"],
        }

    non_success = [r for r in matching_runs if r["conclusion"] != "success"]
    return {
        "ci_status": "incomplete",
        "trouble_list": "\n".join(
            f"{r['workflowName']}: {r['conclusion']}" for r in non_success
        ),
    }


def _list_runs(branch: str | None) -> list[dict]:
    args = [
        "gh", "run", "list", "--limit", "10",
        "--json", "databaseId,headSha,conclusion,status,workflowName,url",
    ]
    if branch:
        args += ["--branch", branch]
    out = subprocess.run(args, check=True, capture_output=True, text=True).stdout
    return json.loads(out)


def _classify_cmd(args: argparse.Namespace) -> int:
    if args.sha:
        sha = args.sha
    else:
        sha = subprocess.run(
            ["git", "rev-parse", f"origin/{args.branch}"],
            check=True, capture_output=True, text=True,
        ).stdout.strip()

    runs = _list_runs(args.branch)
    matching = [r for r in runs if r["headSha"] == sha]

    out = {
        "branch": args.branch or "",
        "sha": sha,
        "sha_short": sha[:8],
    }
    out.update(classify_runs(matching))
    print(json.dumps(out))
    return 0


def _watch_cmd(args: argparse.Namespace) -> int:
    for run_id in args.run_ids:
        # Don't fail-fast on individual run failure — gather final state across all
        # watched runs so the classifier sees the full picture.
        subprocess.run(
            ["gh", "run", "watch", run_id, "--exit-status"], check=False,
        )

    runs = _list_runs(branch=None)
    matching = [r for r in runs if r["headSha"] == args.sha]

    out = {
        "sha": args.sha,
        "sha_short": args.sha[:8],
    }
    out.update(classify_runs(matching))
    print(json.dumps(out))
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="GitHub Actions CI operations: classify and watch",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    classify = sub.add_parser("classify", help="classify CI runs for branch or SHA")
    grp = classify.add_mutually_exclusive_group(required=True)
    grp.add_argument("--branch", help="branch name (resolves SHA via origin/<branch>)")
    grp.add_argument("--sha", help="commit SHA to classify directly")
    classify.set_defaults(func=_classify_cmd)

    watch = sub.add_parser("watch", help="block on in-progress runs then classify final state")
    watch.add_argument("--sha", required=True, help="commit SHA being watched")
    watch.add_argument("--run-ids", nargs="+", required=True, help="run IDs to watch")
    watch.set_defaults(func=_watch_cmd)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
