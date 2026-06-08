#!/usr/bin/env python3
"""apply-over-queue driver: cached, sequential `claude -p` fan-out over a work queue.

Runs one operation over many targets while paying for the operation's (large,
shared) instruction payload once: every spawn reads the IDENTICAL flattened
instruction FIRST, so it serves from prompt cache (~0.1×), then claims its
varying target from the queue AFTER — keeping the cached prefix identical no
matter the queue size. An identical instruction prefix cache-reuses across
separate `claude -p` processes; sequential, back-to-back calls keep the 5-min
prompt-cache TTL warm so each spawn lands on a hot cache.

The per-target operation is NOT defined here — it lives in the (already
target-normalized) instruction payload. This driver is mechanism only:
flatten → seed queue → spawn loop. Output handling is pluggable via --isolation:

  none      (default) the operation side-effects directly (DB writes, or writing
            into a fresh output dir it names); no git. Review is the operation's
            concern — its safe pattern is an idempotent write or a fresh dir.
  worktree  one git worktree branched from the repo's HEAD; each spawn's file
            changes are committed on the branch, reviewed as a diff, merged on
            approval. Live source is untouched until merge.

Targets are opaque tokens the operation understands (repo-relative paths, session
ids, anything). One run can mix trees.
"""
import argparse
import json
import shutil
import subprocess
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sh(*cmd):
    return subprocess.run(cmd, text=True, capture_output=True)


def claude_p(prompt, cwd, add_dirs, exclude_dynamic):
    cmd = ["claude", "-p", "--output-format", "json", "--no-session-persistence",
           "--allowedTools", "Bash", "Read", "Write", "Edit"]
    if exclude_dynamic:
        cmd.append("--exclude-dynamic-system-prompt-sections")
    for d in add_dirs:
        cmd += ["--add-dir", str(d)]
    p = subprocess.run(cmd, input=prompt, text=True, capture_output=True, cwd=str(cwd))
    usage = None
    for line in reversed(p.stdout.splitlines()):
        line = line.strip()
        if line.startswith("{"):
            try:
                usage = json.loads(line).get("usage"); break
            except json.JSONDecodeError:
                continue
    return p.returncode == 0, usage


def status(qp, rundir):
    out = sh("python3", str(qp), "--dir", str(rundir), "status").stdout.strip()
    return dict(kv.split("=") for kv in out.split())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skills", required=True, help="comma-separated entry skills to flatten")
    ap.add_argument("--operation-file", required=True,
                    help="target-normalized per-item instruction (see _normalize-operation.md)")
    ap.add_argument("--items", required=True, help="comma-separated target tokens")
    ap.add_argument("--isolation", choices=["none", "worktree"], default="none",
                    help="output handling: none (side-effecting, default) or worktree (git diff review)")
    ap.add_argument("--repo", default=str(Path.home() / ".claude"),
                    help="git repo to worktree (isolation=worktree only)")
    ap.add_argument("--cwd", default=None,
                    help="working dir for spawns under isolation=none (default: --repo)")
    ap.add_argument("--add-dir", dest="add_dirs", action="append", default=[],
                    help="extra dir the spawns may access (repeatable)")
    ap.add_argument("--disciplines-subdir", default="skills",
                    help="where the entry/flattened skills live (default: skills)")
    ap.add_argument("--run-id", default=None)
    ap.add_argument("--no-exclude-dynamic", dest="exclude_dynamic", action="store_false", default=True)
    a = ap.parse_args()

    run_id = a.run_id or f"run-{int(time.time())}"
    rundir = Path("/tmp/aoq") / run_id
    rundir.mkdir(parents=True, exist_ok=True)
    repo = Path(a.repo).expanduser()
    items = [s for s in a.items.split(",") if s]

    # 1. Flatten the shared payload (skills + the normalized operation-file).
    instr = rundir / "instruction.md"
    r = sh("python3", str(HERE / "flatten.py"), "--skills", a.skills,
           "--operation-file", a.operation_file,
           "--skills-root", str(repo / a.disciplines_subdir), "--out", str(instr))
    print(r.stdout.strip() or r.stderr.strip(), flush=True)
    if r.returncode:
        raise SystemExit("flatten failed")

    # 2. Seed the queue.
    qp = rundir / "queue.py"
    shutil.copy(HERE / "queue.py", qp)
    sh("python3", str(qp), "--dir", str(rundir), "seed", *items)

    # 3. Output isolation: worktree (git review) or none (side-effecting).
    branch = wt = None
    if a.isolation == "worktree":
        wt = rundir / "wt"
        branch = f"aoq/{run_id}"
        if wt.exists():
            shutil.rmtree(wt)
        r = sh("git", "-C", str(repo), "worktree", "add", "-b", branch, str(wt), "HEAD")
        if r.returncode:
            raise SystemExit(f"worktree add failed: {r.stderr}")
        work_cwd = wt
    else:
        work_cwd = Path(a.cwd).expanduser() if a.cwd else repo

    # 4. The spawn stub — operation-AGNOSTIC. Identical on every spawn (cache prefix);
    #    the operation and its output target live entirely in {instr}.
    stub = (f"Read {instr} in full FIRST — it is your complete operating instruction. "
            f"It is identical on every spawn and must be read before anything varying, "
            f"so it serves from prompt cache.\n"
            f"Then claim one target: run `python3 {qp} --dir {rundir} next` with the Bash tool. "
            f"It prints a single TARGET token, or NONE.\n"
            f"If it prints NONE: reply EMPTY and stop.\n"
            f"Otherwise carry out the operation described in {instr} against that TARGET, exactly "
            f"as specified there — it defines what the target is and where output goes. "
            f"Then run `python3 {qp} --dir {rundir} done <target>` and reply with the target token.")

    add_dirs = [rundir, *(Path(d).expanduser() for d in a.add_dirs)]
    if a.isolation == "none":
        add_dirs.append(work_cwd)

    # 5. Sequential cache-warm loop. +2 covers warmup/retry slack.
    n = len(items)
    print(f"run {run_id}: {n} targets | isolation={a.isolation} | cwd {work_cwd}"
          + (f" | branch {branch}" if branch else ""), flush=True)
    spawned = 0
    while spawned < n + 2 and int(status(qp, rundir)["pending"]) > 0:
        ok, u = claude_p(stub, cwd=work_cwd, add_dirs=add_dirs, exclude_dynamic=a.exclude_dynamic)
        spawned += 1
        g = (lambda k: u.get(k) if u else "?")
        note = ""
        if a.isolation == "worktree":
            sh("git", "-C", str(wt), "add", "-A")
            changed = subprocess.run(["git", "-C", str(wt), "diff", "--cached", "--quiet"]).returncode != 0
            if changed:
                sh("git", "-C", str(wt), "commit", "-q", "-m", f"apply-over-queue (spawn {spawned})")
            files = sh("git", "-C", str(wt), "show", "--stat", "--oneline", "-1").stdout.strip().splitlines()
            note = " -> " + (files[-2].split("|")[0].strip() if len(files) > 1 and changed else "(no change)")
        else:
            st = status(qp, rundir)
            note = f" -> done={st['done']} pending={st['pending']}"
        print(f"  spawn {spawned}: ok={ok} input={g('input_tokens')} "
              f"cache_create={g('cache_creation_input_tokens')} "
              f"cache_read={g('cache_read_input_tokens')}{note}", flush=True)

    # 6. Report.
    st = status(qp, rundir)
    print(f"\ndone={st['done']} claimed={st['claimed']} pending={st['pending']}", flush=True)
    if a.isolation == "worktree":
        stat = sh("git", "-C", str(repo), "diff", "--stat", f"HEAD..{branch}").stdout
        print(f"worktree: {wt}\nbranch:   {branch}", flush=True)
        print(f"review:   git -C {repo} diff HEAD..{branch}", flush=True)
        print(stat, flush=True)
        print(f"merge:    git -C {repo} merge {branch}", flush=True)
        print(f"discard:  git -C {repo} worktree remove --force {wt} && git -C {repo} branch -D {branch}", flush=True)
    else:
        print("side effects are live (isolation=none) — review per the operation's output target.", flush=True)
        print(f"queue state: {rundir}", flush=True)


if __name__ == "__main__":
    main()
