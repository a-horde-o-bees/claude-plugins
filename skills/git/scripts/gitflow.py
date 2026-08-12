#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["pyyaml"]
# ///
"""gitflow: the deterministic driver behind the /git verbs.

Invoke via `uv run` (canonical — encapsulates the pyyaml dependency); plain
`python3` also works where pyyaml is installed, degrading workflow-YAML
structural checks to regex-only without it.

State machine with judgment stop-points: everything code can decide lives here;
the verb docs supply judgment (grouping, messages, dispositions, names) and the
driver refuses to act without it. Exit: 0 ok, 1 blocked/refused (reason on
stdout), 2 usage/environment.

Commit/push pipeline:
  inspect [--cwd DIR] [--paths P ...]     repo state + NEEDS block (judgment wanted)
  apply --plan PLAN.json [--cwd] [--on-base]   execute a plan file; refuse gaps
  push [--cwd] [--branch B] [--skip P ...]     land branches deepest-first
  setup-deny [--cwd] [--scope project|user]    box the repo (or the whole user) : deny direct git/gh

Upstream contribution (repos we don't own):
  search-prior-art --repo O/R TERM ...    duplicate check: PRs + issues, JSON
  contribute-prep --upstream O/R --workdir D [--shallow]   fork, clone fork, wire upstream remote
  pr-create ... [--repo O/R] [--head owner:branch]         cross-repo PR; 403 → compare-URL fallback JSON

CI (classification is pure; docs emit the matching template verbatim):
  ci [--cwd] [--branch B]                 recurse submodules deepest-first, classify
                                          each repo's runs: passed|failed|dispatched|
                                          incomplete|no-runs|no-ci
  ci-watch --sha X --run-ids I ... [--cwd]     block on in-flight runs, re-classify

CI doctor (config hardening; audit/reconcile are read-only):
  ci-audit [DIR] [--resolve]              scan workflows for hardening findings;
                                          --resolve pins each unpinned action's
                                          ref to its commit SHA via gh
  ci-reconcile [--branch B] [--dir DIR]   required-check contexts vs defined jobs

PR gate + routing:
  gate [--branch B]                       merge-readiness verdict for the branch's PR
  protection [--branch B] [--repo SLUG] [--cwd]   is a branch PR-governed
  routes [--cwd] [--paths P ...]          route parent + every submodule; gaps halt

PR lifecycle (open/merge/cleanup mechanics; judgment arrives as arguments):
  pr-preflight [--base B] [--cwd]         pr-open preconditions + authoring seeds
  pr-create --title T --body-file F [--base B] [--draft] [--cwd]
  pr-watch-checks --pr N [--cwd]          block until every check settles
  merge --pr N --strategy S [--admin] [--cwd]   validate strategy, merge the PR
  pr-cleanup [--head H] [--base B] [--cwd]      restore base, tear down merged head

Release (synthesis and review stay with the caller):
  release-preflight [--cwd]               preconditions + last tag + synthesis range
  release-validate --version V --current C [--tag T] [--cwd]
  release-cut --version V --current C --manifest M ... [--tag T] [--cwd]
                                          stage + commit + annotated tag + push together
  read [--cwd] -- <read-only git args>    inspection passthrough for boxed repos
                                          (diff/log/show/…; refuses write-capable forms)

Sync (integration-inbound: bring refs in; conflicts resolve with judgment):
  fetch --remote R [--cwd]                fetch + prune one remote; refs summary
  switch --branch B [--cwd]               switch to an existing local branch (clean tree only)
  integrate --source REF --mode merge|rebase|cherry-pick [--cwd]
                                          integrate REF into the current branch; on
                                          conflict: structured file list, exit 1
  integrate --continue|--abort [--cwd]    finish after resolving (marker-guarded) / back out

Checkpoint sequencing (the mechanical steps between verb calls):
  checkpoint-preflight [--cwd] [--branch B] [--paths P ...] [--base-mode] [--path I]
                                          branch + routes + per-submodule plan
  sub-prep --path P [--cwd]               normalize a submodule off detached HEAD
  sub-reconcile --path P [--cwd]          pin a landed submodule to its merged tip
  branch-create --name N [--cwd]          create + switch to a feature branch

Doctor (approval gates stay with the verb docs; repairs refuse the deliberate cases):
  doctor-detect [--cwd]                   detect.sh + git-roots state table → JSON
  sub-repair --path P ... [--cwd]         tier-1 gitlink repair batch + one commit
  sub-init --path P [--cwd]               init a declared-but-absent submodule
  gitlink-drop --path P [--cwd]           drop an orphan gitlink from the index
  sub-declare --path P [--name N] [--url U] [--cwd]   declare an on-disk repo
  write-native-key --path P --key K --value V [--cwd]  parent-owned routing key
  origin-head-set [--cwd]                 point origin/HEAD at the true default
  default-branch-rename [--to B] [--old B] [--cwd]    rename across every remote
  release-bootstrap-detect [--cwd]        manifests/CHANGELOG/tags/hooks for bootstrap
"""
import argparse

from gitflow_checkpoint import cmd_branch_create, cmd_checkpoint_preflight, cmd_sub_prep, cmd_sub_reconcile
from gitflow_ci import cmd_ci, cmd_ci_watch
from gitflow_ci_doctor import cmd_ci_audit, cmd_ci_reconcile
from gitflow_commit import cmd_apply, cmd_inspect, cmd_push, cmd_setup_deny
from gitflow_doctor import (cmd_default_branch_rename, cmd_doctor_detect, cmd_gitlink_drop,
                            cmd_origin_head_set, cmd_sub_declare, cmd_sub_init, cmd_sub_repair,
                            cmd_write_native_key)
from gitflow_gate import cmd_gate, cmd_protection, cmd_routes
from gitflow_pr import cmd_merge, cmd_pr_cleanup, cmd_pr_create, cmd_pr_preflight, cmd_pr_watch_checks, cmd_search_prior_art, cmd_contribute_prep
from gitflow_release import (cmd_read, cmd_release_bootstrap_detect, cmd_release_cut,
                             cmd_release_preflight, cmd_release_validate)
from gitflow_sync import cmd_fetch, cmd_integrate, cmd_switch


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("inspect")
    p.add_argument("--cwd", default=".")
    p.add_argument("--paths", nargs="*", default=None)
    p = sub.add_parser("apply")
    p.add_argument("--plan", required=True)
    p.add_argument("--cwd", default=".")
    p.add_argument("--on-base", action="store_true")
    p = sub.add_parser("push")
    p.add_argument("--cwd", default=".")
    p.add_argument("--branch", default=None,
                   help="required confirmation at the top level: must match the current branch")
    p.add_argument("--skip", action="append", default=None,
                   help="pin-only submodule path to skip (repeatable)")
    p = sub.add_parser("setup-deny")
    p.add_argument("--cwd", default=".")
    p.add_argument("--scope", choices=["project", "user"], default="project",
                   help="project: <cwd>/.claude/settings.json; user: ~/.claude/settings.json")

    p = sub.add_parser("ci")
    p.add_argument("--cwd", default=".")
    p.add_argument("--branch", default=None,
                   help="confirmation at the top level: must match the current branch")
    p = sub.add_parser("ci-watch")
    p.add_argument("--cwd", default=".")
    p.add_argument("--sha", required=True)
    p.add_argument("--run-ids", nargs="+", required=True)

    p = sub.add_parser("ci-audit")
    p.add_argument("dir", nargs="?", default=".github/workflows")
    p.add_argument("--cwd", default=".")
    p.add_argument("--resolve", action="store_true",
                   help="resolve each unpinned action's ref to its commit SHA via gh")
    p = sub.add_parser("ci-reconcile")
    p.add_argument("--branch", default=None)
    p.add_argument("--dir", default=".github/workflows")
    p.add_argument("--cwd", default=".")

    p = sub.add_parser("gate")
    p.add_argument("--branch", default=None)
    p.add_argument("--cwd", default=".")
    p = sub.add_parser("protection")
    p.add_argument("--branch", default=None)
    p.add_argument("--repo", default=None)
    p.add_argument("--cwd", default=".")
    p = sub.add_parser("routes")
    p.add_argument("--cwd", default=".")
    p.add_argument("--paths", nargs="*", default=None)

    p = sub.add_parser("pr-preflight")
    p.add_argument("--base", default=None)
    p.add_argument("--cwd", default=".")
    p = sub.add_parser("pr-create")
    p.add_argument("--title", required=True)
    p.add_argument("--body-file", required=True)
    p.add_argument("--base", default=None)
    p.add_argument("--draft", action="store_true")
    p.add_argument("--cwd", default=".")
    p.add_argument("--repo", default=None, help="upstream owner/repo for a cross-repo (fork) PR")
    p.add_argument("--head", default=None, help="owner:branch head override (default: <login>:<current>)")
    p = sub.add_parser("search-prior-art")
    p.add_argument("--repo", required=True)
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("terms", nargs="+")
    p = sub.add_parser("contribute-prep")
    p.add_argument("--upstream", required=True, help="owner/repo to contribute to")
    p.add_argument("--workdir", required=True, help="directory to clone the fork under")
    p.add_argument("--shallow", action="store_true")
    p = sub.add_parser("pr-watch-checks")
    p.add_argument("--pr", required=True)
    p.add_argument("--cwd", default=".")
    p = sub.add_parser("merge")
    p.add_argument("--pr", required=True)
    p.add_argument("--strategy", required=True, choices=["squash", "merge", "rebase"])
    p.add_argument("--admin", action="store_true")
    p.add_argument("--cwd", default=".")
    p = sub.add_parser("pr-cleanup")
    p.add_argument("--head", default=None)
    p.add_argument("--base", default=None)
    p.add_argument("--cwd", default=".")

    p = sub.add_parser("release-preflight")
    p.add_argument("--cwd", default=".")
    p = sub.add_parser("release-validate")
    p.add_argument("--version", required=True)
    p.add_argument("--current", required=True)
    p.add_argument("--tag", default=None)
    p.add_argument("--cwd", default=".")
    p = sub.add_parser("release-cut")
    p.add_argument("--version", required=True)
    p.add_argument("--current", required=True)
    p.add_argument("--manifest", action="append", required=True,
                   help="manifest path to stage (repeatable); CHANGELOG.md is always staged")
    p.add_argument("--tag", default=None)
    p.add_argument("--cwd", default=".")
    p = sub.add_parser("read")
    p.add_argument("--cwd", default=".")
    p.add_argument("git_args", nargs=argparse.REMAINDER,
                   help="read-only git command, e.g. read -- log v1.2.0..HEAD --stat")

    p = sub.add_parser("release-bootstrap-detect")
    p.add_argument("--cwd", default=".")

    p = sub.add_parser("doctor-detect")
    p.add_argument("--cwd", default=".")
    p = sub.add_parser("sub-repair")
    p.add_argument("--path", action="append", required=True,
                   help="tier-1 path to re-border as a gitlink (repeatable); one commit for the batch")
    p.add_argument("--cwd", default=".")
    p = sub.add_parser("sub-init")
    p.add_argument("--path", required=True)
    p.add_argument("--cwd", default=".")
    p = sub.add_parser("gitlink-drop")
    p.add_argument("--path", required=True)
    p.add_argument("--cwd", default=".")
    p = sub.add_parser("sub-declare")
    p.add_argument("--path", required=True)
    p.add_argument("--name", default=None)
    p.add_argument("--url", default=None, help="defaults to the submodule's origin remote")
    p.add_argument("--cwd", default=".")
    p = sub.add_parser("write-native-key")
    p.add_argument("--path", required=True)
    p.add_argument("--key", required=True, choices=["branch", "update", "x-integration", "x-contribute"])
    p.add_argument("--value", required=True)
    p.add_argument("--cwd", default=".")
    p = sub.add_parser("origin-head-set")
    p.add_argument("--cwd", default=".")
    p = sub.add_parser("default-branch-rename")
    p.add_argument("--to", default="main")
    p.add_argument("--old", default=None, help="defaults to origin/HEAD's current target")
    p.add_argument("--cwd", default=".")

    p = sub.add_parser("fetch")
    p.add_argument("--remote", required=True)
    p.add_argument("--cwd", default=".")
    p = sub.add_parser("switch")
    p.add_argument("--branch", required=True)
    p.add_argument("--cwd", default=".")
    p = sub.add_parser("integrate")
    p.add_argument("--source", default=None, help="ref (or A..B range for cherry-pick) to integrate")
    p.add_argument("--mode", choices=["merge", "rebase", "cherry-pick"], default=None)
    p.add_argument("--continue", dest="cont", action="store_true",
                   help="finish after conflicts are resolved (refuses leftover markers)")
    p.add_argument("--abort", action="store_true")
    p.add_argument("--cwd", default=".")

    p = sub.add_parser("checkpoint-preflight")
    p.add_argument("--cwd", default=".")
    p.add_argument("--branch", default=None)
    p.add_argument("--paths", nargs="*", default=None)
    p.add_argument("--base-mode", action="store_true")
    p.add_argument("--path", choices=["pr", "direct"], default=None,
                   help="internal: a parent passes its decided integration into a recursive submodule run")
    p = sub.add_parser("sub-prep")
    p.add_argument("--path", required=True)
    p.add_argument("--cwd", default=".")
    p = sub.add_parser("sub-reconcile")
    p.add_argument("--path", required=True)
    p.add_argument("--cwd", default=".")
    p = sub.add_parser("branch-create")
    p.add_argument("--name", required=True)
    p.add_argument("--cwd", default=".")

    a = ap.parse_args()
    {
        "inspect": cmd_inspect, "apply": cmd_apply, "push": cmd_push, "setup-deny": cmd_setup_deny,
        "ci": cmd_ci, "ci-watch": cmd_ci_watch,
        "ci-audit": cmd_ci_audit, "ci-reconcile": cmd_ci_reconcile,
        "gate": cmd_gate, "protection": cmd_protection, "routes": cmd_routes,
        "pr-preflight": cmd_pr_preflight, "pr-create": cmd_pr_create, "search-prior-art": cmd_search_prior_art, "contribute-prep": cmd_contribute_prep,
        "pr-watch-checks": cmd_pr_watch_checks, "merge": cmd_merge, "pr-cleanup": cmd_pr_cleanup,
        "release-preflight": cmd_release_preflight, "release-validate": cmd_release_validate,
        "release-cut": cmd_release_cut, "read": cmd_read,
        "release-bootstrap-detect": cmd_release_bootstrap_detect,
        "doctor-detect": cmd_doctor_detect, "sub-repair": cmd_sub_repair, "sub-init": cmd_sub_init,
        "gitlink-drop": cmd_gitlink_drop, "sub-declare": cmd_sub_declare,
        "write-native-key": cmd_write_native_key, "origin-head-set": cmd_origin_head_set,
        "default-branch-rename": cmd_default_branch_rename,
        "fetch": cmd_fetch, "switch": cmd_switch, "integrate": cmd_integrate,
        "checkpoint-preflight": cmd_checkpoint_preflight, "sub-prep": cmd_sub_prep,
        "sub-reconcile": cmd_sub_reconcile, "branch-create": cmd_branch_create,
    }[a.cmd](a)


if __name__ == "__main__":
    main()
