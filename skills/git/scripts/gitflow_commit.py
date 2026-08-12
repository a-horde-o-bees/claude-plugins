"""Commit/push pipeline: inspect (state + NEEDS), apply (plan execution),
push (deepest-first landing), setup-deny (boxing the repo)."""
import json
import sys
import tempfile
from pathlib import Path

from gitflow_core import die, repo_state, run, walk


def cmd_inspect(a):
    repos = walk(a.cwd, a.paths or None)
    state = {"repos": repos}
    state_file = Path(a.cwd) / ".git" / "gitflow-state.json"
    if state_file.parent.is_dir():
        state_file.write_text(json.dumps(state, indent=1))
    print(json.dumps(state, indent=1))
    blockers = [b for r in repos for b in r["blockers"]]
    changed = [r for r in repos if r.get("status")]
    if blockers:
        print("\nBLOCKED:\n" + "\n".join(f"- {b}" for b in blockers))
        sys.exit(1)
    if not changed:
        print("\nCLEAN: no changes in scope")
        return
    print("\nNEEDS (supply as the plan file, one repos[] entry per changed repo, deepest first):")
    print("- groups: partition each repo's changed files by topic — files[] + message per group")
    print("- pins: consume|revert per advancing submodule")
    print("- untracked: include|exclude|ignore per suspicious untracked file")
    for r in changed:
        loc = r["cwd"]
        print(f"repo {loc}: {len(r['status'])} changed path(s)"
              + (f", {len(r['suspicious_untracked'])} suspicious untracked" if r["suspicious_untracked"] else "")
              + (", public-bound" if r.get("public_bound") else ""))


def cmd_apply(a):
    """Execute a plan file: gate → validate the whole plan → then commit.

    Nothing is committed until every repo, disposition, and group pathspec
    has validated — a bad group dies with the full problem list and zero
    commits made, never a partial apply. Each repo's index is reset (mixed)
    before its groups stage: a plan speaks in whole files, so pre-staged
    content belongs to whichever group claims its path — it never rides
    into the first group's commit. Groups stage with `git add -A --`, which
    records deletions of worktree-absent paths (plain `git add` is fatal on
    a staged deletion)."""
    plan = json.loads(Path(a.plan).read_text())
    repos = sorted(plan["repos"], key=lambda r: -len(Path(r["cwd"]).parts))

    # Phase 1 — gate every repo + validate every disposition value, before
    # any mutation beyond the advised submodule normalization.
    for r in repos:
        cwd = r["cwd"]
        st = repo_state(cwd)
        if st["blockers"]:
            die(f"{cwd}: " + "; ".join(st["blockers"]))
        if (st["branch"] == st.get("default_branch") and st.get("protected_default")
                and not (a.on_base or plan.get("on_base"))):
            die(f"{cwd}: refusing to commit onto protected default branch {st['branch']} "
                f"(pass --on-base for an intentional base commit)")
        # normalize safely-attachable detached submodules
        for sub in st.get("submodules", []):
            sub_cwd = str(Path(cwd) / sub["path"])
            if sub.get("normalize") == "attach":
                run(["git", "checkout", sub["declared_branch"]], sub_cwd, check=True)
            elif sub.get("normalize") == "create-branch":
                run(["git", "checkout", "-b", sub["declared_branch"]], sub_cwd, check=True)
        for sub_path, decision in (r.get("pins") or {}).items():
            if decision not in ("consume", "revert"):
                die(f"{cwd}: pin {sub_path}: unknown disposition {decision!r}")
        for rel, decision in (r.get("untracked") or {}).items():
            if decision not in ("include", "exclude", "ignore"):
                die(f"{cwd}: untracked {rel}: unknown disposition {decision!r}")

    # Phase 2 — reset each index to HEAD (whole-file plan semantics), then
    # dry-run every group so the entire plan proves executable before the
    # first commit. Problems are collected and reported together.
    problems = []
    for r in repos:
        cwd = r["cwd"]
        run(["git", "reset", "-q"], cwd)
        claimed: dict[str, int] = {}
        for i, g in enumerate(r.get("groups") or [], 1):
            if not g.get("files") or not g.get("message", "").strip():
                problems.append(f"{cwd}: group {i}: needs files[] and a non-empty message")
                continue
            for f in g["files"]:
                if f in claimed:
                    problems.append(
                        f"{cwd}: group {i}: {f!r} already claimed by group {claimed[f]}")
                claimed[f] = i
            rc, out, err = run(["git", "add", "-A", "--dry-run", "--"] + g["files"], cwd)
            if rc != 0:
                problems.append(f"{cwd}: group {i}: {err or out}")
            elif not out.strip() and not any(
                    p in (r.get("pins") or {}) for p in g["files"]):
                problems.append(
                    f"{cwd}: group {i}: no changes match its files[] — nothing to commit")
    if problems:
        die("plan validation failed — nothing committed:\n"
            + "\n".join(f"- {p}" for p in problems))

    # Phase 3 — execute: dispositions, then topic commits.
    made = []
    for r in repos:
        cwd = r["cwd"]
        for sub_path, decision in (r.get("pins") or {}).items():
            if decision == "revert":
                run(["git", "submodule", "update", "--", sub_path], cwd, check=True)
        for rel, decision in (r.get("untracked") or {}).items():
            if decision == "ignore":
                with open(Path(cwd) / ".gitignore", "a") as f:
                    f.write(rel.rstrip("/") + ("/" if rel.endswith("/") else "") + "\n")
        for g in r["groups"]:
            run(["git", "add", "-A", "--"] + g["files"], cwd, check=True)
            with tempfile.NamedTemporaryFile("w", suffix=".msg", delete=False) as f:
                f.write(g["message"])
                msg_file = f.name
            run(["git", "commit", "-F", msg_file], cwd, check=True)
            _, sha, _ = run(["git", "rev-parse", "--short", "HEAD"], cwd)
            made.append((cwd, sha, g["message"].splitlines()[0]))
    print("COMMITTED:")
    for cwd, sha, subject in made:
        print(f"- {cwd} {sha} {subject}")
    for r in repos:
        # raw: `--short` output is column-significant — a stripped first line
        # turns an unstaged ` M` into what reads as a staged `M `.
        _, status, _ = run(["git", "status", "--short"], r["cwd"], raw=True)
        status = status.rstrip("\n")
        print(f"{r['cwd']}: " + ("clean tree" if not status else f"remaining:\n{status}"))


def cmd_push(a):
    repos = walk(a.cwd)
    top = repos[-1]
    if a.branch and top["branch"] != a.branch:
        die(f"{top['cwd']}: on branch {top['branch']}, not {a.branch} — branch mismatch, nothing pushed")
    skips = set(a.skip or [])
    for r in repos:  # deepest first
        cwd = r["cwd"]
        if any(str(Path(cwd)).endswith(s.rstrip("/")) for s in skips):
            print(f"{cwd}: pin-only — skipped (its changes land via their own lifecycle)")
            continue
        if r.get("detached"):
            die(f"{cwd}: detached HEAD — attach a branch before pushing")
        rc, _, _ = run(["git", "remote", "get-url", "origin"], cwd)
        if rc != 0:
            print(f"{cwd}: no origin remote — skipped")
            continue
        rc, u, _ = run(["git", "rev-parse", "--abbrev-ref", "@{u}"], cwd)
        if rc != 0 or u != f"origin/{r['branch']}":
            # No tracking, or tracking a foreign remote/name (e.g. a contribution
            # branch cut from upstream/main): the verb's contract is origin, so
            # re-point rather than honoring the mismatched tracking ref.
            run(["git", "push", "-u", "origin", r["branch"]], cwd, check=True)
            print(f"{cwd}: pushed {r['branch']} (upstream set to origin/{r['branch']})")
            continue
        # fetch + rebase onto upstream so the push is fast-forward by construction
        run(["git", "fetch"], cwd, check=True)
        rc_ff, _, _ = run(["git", "merge-base", "--is-ancestor", "@{u}", "HEAD"], cwd)
        if rc_ff == 0:
            # already fast-forward; rebasing would pointlessly linearize any
            # merge commits the branch carries (flattening a fork's upstream
            # merge into per-commit replays that conflict with cherry-picks)
            _, _, err = run(["git", "push"], cwd, check=True)
            print(f"{cwd}: pushed {r['branch']}" + (f" — {err.splitlines()[-1]}" if err else ""))
            continue
        rc, _, err = run(["git", "rebase", "@{u}"], cwd)
        if rc != 0:
            run(["git", "rebase", "--abort"], cwd)
            die(f"{cwd}: rebase onto upstream conflicts — resolve manually, nothing pushed\n{err}")
        _, _, err = run(["git", "push"], cwd, check=True)
        print(f"{cwd}: pushed {r['branch']}" + (f" — {err.splitlines()[-1]}" if err else ""))


DENY = ["Bash(git *)", "Bash(git)", "Bash(gh *)", "Bash(gh)"]


def cmd_setup_deny(a):
    scope = getattr(a, "scope", "project")
    base = Path.home() if scope == "user" else Path(a.cwd)
    settings_path = base / ".claude" / "settings.json"
    settings = json.loads(settings_path.read_text()) if settings_path.is_file() else {}
    deny = settings.setdefault("permissions", {}).setdefault("deny", [])
    added = [d for d in DENY if d not in deny]
    deny.extend(added)
    # Redirect hook: PreToolUse fires before permission rules, so it denies the
    # raw git/gh call WITH a redirect to the /git skill; the deny rules above
    # remain the fail-closed backstop if hooks are disabled or the script breaks.
    hook_cmd = f"bash {Path(__file__).parent / 'redirect-denied-git.sh'}"
    denied = settings.setdefault("hooks", {}).setdefault("PreToolUse", [])
    have = any(h.get("command") == hook_cmd
               for entry in denied for h in entry.get("hooks", []))
    if not have:
        denied.append({"matcher": "Bash",
                       "hooks": [{"type": "command", "command": hook_cmd}]})
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(json.dumps(settings, indent=2) + "\n")
    print(f"{settings_path}: deny entries " + (f"added: {', '.join(added)}" if added else "already present")
          + ("; redirect hook installed" if not have else "; redirect hook already present"))
