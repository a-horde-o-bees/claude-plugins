#!/usr/bin/env python3
"""apply-over-queue driver: cached, sequential `claude -p` fan-out over a work queue.

Runs one operation over many targets while paying for the operation's (large, shared)
instruction payload once: every spawn reads the IDENTICAL flattened instruction FIRST, so it
serves from prompt cache (~0.1×), then claims its varying target from the queue AFTER — keeping
the cached prefix identical no matter the queue size. An identical prefix cache-reuses across
separate `claude -p` processes; sequential, back-to-back calls keep the 5-min prompt-cache TTL
warm so each spawn lands on a hot cache.

The cached prefix is byte-identical only if EVERYTHING before the target is fixed across spawns —
including cwd and the --add-dir set. Two output models keep that invariant:

  staged  (default) file/dir targets, possibly from different repos, are COPIED into one run-local
          workspace; every spawn runs with cwd fixed to that workspace and one fixed --add-dir set,
          so location never varies the prefix. The origin<->stage map drives a formal end-of-run
          diff and copy-back-on-approval (see stage.py). Live origins are untouched until apply.
  none    side-effecting operations (DB writes, external state) whose token is not a file to stage;
          cwd is the operation's own fixed home (--cwd). No staging, no diff — the op side-effects
          directly, and its safe pattern is an idempotent write or a fresh output dir.

The per-target operation is NOT defined here — it lives in the (already target-normalized)
instruction payload. This driver is mechanism only: flatten -> stage -> seed queue -> spawn loop,
asserting the cache saving on every spawn after the first and aborting if the prefix ever diverges.
"""
import argparse
import json
import shutil
import subprocess
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Below this cached-prefix size the per-spawn saving is immaterial, so the assertion is skipped.
CACHE_ASSERT_MIN_PREFIX = 2000


def sh(*cmd):
    return subprocess.run(cmd, text=True, capture_output=True)


def claude_p(prompt, cwd, add_dirs, exclude_dynamic, model=None):
    cmd = ["claude", "-p", "--output-format", "json", "--no-session-persistence",
           "--allowedTools", "Bash", "Read", "Write", "Edit"]
    if model:
        cmd += ["--model", model]
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


def claimed_list(rundir):
    # Claim order == spawn order (sequential, one target per spawn), so the token a spawn handled
    # is the one it appended to claimed.txt — reply-independent.
    p = rundir / "claimed.txt"
    return [l for l in p.read_text().splitlines() if l.strip()] if p.exists() else []


def origin_of(rundir, token):
    p = rundir / "stage_map.json"
    if p.exists():
        for e in json.loads(p.read_text()):
            if e["stage"] == token:
                return e["origin"]
    return token


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skills", default="", help="comma-separated entry skills to flatten "
                    "(OPTIONAL — the instruction's own /skill references are auto-discovered; "
                    "use this only to supplement a skill the instruction does not name)")
    ap.add_argument("--operation-file", required=True,
                    help="target-normalized per-item instruction (see _normalize-operation.md)")
    ap.add_argument("--items", default="", help="comma-separated target tokens (static queue)")
    ap.add_argument("--feeder", default=None,
                    help="dynamic queue: a command printing the next target token or DONE[:reason]; "
                    "`--dir <rundir>` is appended on each call. Use instead of --items.")
    ap.add_argument("--max", type=int, default=20, help="feeder-mode safety backstop on iterations")
    ap.add_argument("--isolation", choices=["staged", "none"], default="staged",
                    help="output model: staged (default — file/dir targets copied into one workspace, "
                    "diff + copy-back on approval) or none (side-effecting ops like DB writes; no "
                    "staging, no diff)")
    ap.add_argument("--repo", default=str(Path.home() / ".claude"),
                    help="where the flattened skills live (skills-root = repo/<disciplines-subdir>)")
    ap.add_argument("--cwd", default=None,
                    help="isolation=none only: the operation's fixed home cwd (default: --repo). "
                    "Ignored under staged, where cwd is forced to the workspace.")
    ap.add_argument("--add-dir", dest="add_dirs", action="append", default=[],
                    help="extra dir every spawn may access (repeatable); the SAME set on each spawn")
    ap.add_argument("--disciplines-subdir", default="skills",
                    help="where the entry/flattened skills live under --repo (default: skills)")
    ap.add_argument("--model", default=None,
                    help="model for the claude -p spawns (default: the CLI's default)")
    ap.add_argument("--cache-floor", type=float, default=0.8,
                    help="minimum fraction of the spawn-1 cached prefix (cache_read + cache_creation) "
                    "that each later spawn must re-read from cache; below it the run ABORTS — the prefix "
                    "diverged and the shared payload is being re-billed instead of cache-served")
    ap.add_argument("--run-id", default=None)
    ap.add_argument("--no-exclude-dynamic", dest="exclude_dynamic", action="store_false", default=True)
    a = ap.parse_args()

    run_id = a.run_id or f"run-{int(time.time())}"
    rundir = Path("/tmp/aoq") / run_id
    rundir.mkdir(parents=True, exist_ok=True)
    repo = Path(a.repo).expanduser()
    items = [s for s in a.items.split(",") if s]
    if not items and not a.feeder:
        raise SystemExit("provide --items (static queue) or --feeder (dynamic queue)")

    # 1. Flatten the shared payload (skills + the normalized operation-file).
    instr = rundir / "instruction.md"
    r = sh("python3", str(HERE / "flatten.py"), "--skills", a.skills,
           "--operation-file", a.operation_file,
           "--skills-root", str(repo / a.disciplines_subdir), "--out", str(instr))
    print(r.stdout.strip() or r.stderr.strip(), flush=True)
    if r.returncode:
        raise SystemExit("flatten failed")

    # 2. Local copies of the queue + stage helpers, so post-run diff/apply/discard run from {rundir}.
    qp = rundir / "queue.py"; shutil.copy(HERE / "queue.py", qp)
    sp = rundir / "stage.py"; shutil.copy(HERE / "stage.py", sp)

    def stage_add(origin):
        r = sh("python3", str(sp), "--dir", str(rundir), "add", origin)
        if r.returncode:
            raise SystemExit(f"stage failed for {origin}: {r.stderr.strip()}")
        return r.stdout.strip().splitlines()[-1]

    # 3. Output model: staged copies file/dir targets into one fixed workspace; none side-effects live.
    if a.isolation == "staged":
        work = rundir / "work"; work.mkdir(parents=True, exist_ok=True)
        seed = [] if a.feeder else [stage_add(it) for it in items]
        work_cwd = work
    else:
        seed = items                          # opaque tokens; the operation side-effects directly
        work_cwd = Path(a.cwd).expanduser() if a.cwd else repo
    sh("python3", str(qp), "--dir", str(rundir), "seed", *seed)

    # 4. The spawn stub — operation-AGNOSTIC. Identical on every spawn (the cache prefix); the
    #    operation and its output target live entirely in {instr}, and the target enters via the queue.
    stub = (f"Read {instr} in full FIRST — it is your complete operating instruction. "
            f"It is identical on every spawn and must be read before anything varying, "
            f"so it serves from prompt cache.\n"
            f"Then claim one target: run `python3 {qp} --dir {rundir} next` with the Bash tool. "
            f"It prints a single TARGET token, or NONE.\n"
            f"If it prints NONE: reply EMPTY and stop.\n"
            f"Otherwise carry out the operation described in {instr} against that TARGET, exactly "
            f"as specified there — it defines what the target is and where output goes. "
            f"Then run `python3 {qp} --dir {rundir} done <target>` and reply with the target token.")

    # One fixed --add-dir set, identical on every spawn (deduped, order-preserving).
    raw = [rundir, work_cwd, *(Path(d).expanduser() for d in a.add_dirs)]
    seen, add_dirs = set(), []
    for d in raw:
        if str(d) not in seen:
            seen.add(str(d)); add_dirs.append(d)

    # 5. Cache assertion. Spawn 1 ESTABLISHES the cached prefix (system + stub + the instruction it
    #    reads, all byte-identical); every later spawn must RE-READ that same prefix. We compare each
    #    spawn's cache_read to the spawn-1 prefix baseline (cache_read + cache_creation) — never to the
    #    spawn's own total, since the varying target enters AFTER the prefix and would skew a ratio.
    baseline: dict[str, "int | None"] = {"prefix": None}
    records = []                                        # per-target cache breakdown for the closing report
    def one_spawn(label):
        before = len(claimed_list(rundir))
        ok, u = claude_p(stub, cwd=work_cwd, add_dirs=add_dirs,
                         exclude_dynamic=a.exclude_dynamic, model=a.model)
        after = claimed_list(rundir)
        target = after[before] if len(after) > before else None   # the token this spawn claimed
        st = status(qp, rundir)
        if u is None:
            if target is not None:
                records.append({"target": target, "input": None, "cc": None, "cr": None,
                                "reread": None, "baseline": False})
            print(f"  {label}: ok={ok} usage=UNAVAILABLE — cannot verify cache saving "
                  f"-> done={st['done']} pending={st['pending']}", flush=True)
            return ok
        cr = u.get("cache_read_input_tokens") or 0
        cc = u.get("cache_creation_input_tokens") or 0
        inp = u.get("input_tokens") or 0
        is_base = baseline["prefix"] is None            # first spawn with usage sets the baseline
        if is_base:
            baseline["prefix"] = cr + cc
        base = baseline["prefix"]
        frac = None if is_base else ((cr / base) if base else 1.0)
        if target is not None:
            records.append({"target": target, "input": inp, "cc": cc, "cr": cr,
                            "reread": frac, "baseline": is_base})
        if is_base:
            print(f"  {label}: ok={ok} input={inp} cache_create={cc} cache_read={cr} "
                  f"prefix-baseline={base} -> done={st['done']} pending={st['pending']}", flush=True)
            return ok
        print(f"  {label}: ok={ok} input={inp} cache_create={cc} cache_read={cr} "
              f"reread={frac:.0%} of prefix -> done={st['done']} pending={st['pending']}", flush=True)
        if base and base >= CACHE_ASSERT_MIN_PREFIX and frac is not None and frac < a.cache_floor:
            raise SystemExit(
                f"\ncache assertion FAILED at {label}: re-read {frac:.0%} of the spawn-1 cached prefix "
                f"(cache_read={cr} vs prefix baseline {base}), below floor {a.cache_floor:.0%}. The "
                f"prompt prefix diverged across spawns, so the shared payload is being re-billed instead "
                f"of cache-served. Make the operation target-agnostic and keep cwd / --add-dir identical "
                f"every spawn (staged mode fixes cwd to the workspace; check --add-dir and the operation "
                f"for target literals).")
        return ok

    # 6. Drive the queue — static (fixed list, +2 warmup/retry slack) or dynamic (feeder yields the
    #    next target until DONE, or the --max backstop trips). Pass 1 / spawn 1 is the cache warmup.
    if a.feeder:
        import shlex
        feeder = shlex.split(a.feeder) + ["--dir", str(rundir)]
        print(f"run {run_id}: dynamic feeder | isolation={a.isolation} | cwd {work_cwd}", flush=True)
        passes, reason = 0, "max"
        while passes < a.max:
            nxt = (sh(*feeder).stdout.strip().splitlines() or [""])[-1].strip()
            if not nxt or nxt.startswith("DONE"):
                reason = nxt.split(":", 1)[1] if ":" in nxt else "exhausted"
                break
            token = stage_add(nxt) if a.isolation == "staged" else nxt
            sh("python3", str(qp), "--dir", str(rundir), "push", token)
            passes += 1
            one_spawn(f"pass {passes}")
        print(f"\nfeeder stopped: {reason} after {passes} pass(es)", flush=True)
    else:
        n = len(items)
        print(f"run {run_id}: {n} targets | isolation={a.isolation} | cwd {work_cwd}", flush=True)
        spawned = 0
        while spawned < n + 2 and int(status(qp, rundir)["pending"]) > 0:
            spawned += 1
            one_spawn(f"spawn {spawned}")

    # 7. Report + review gate.
    st = status(qp, rundir)
    print(f"\ndone={st['done']} claimed={st['claimed']} pending={st['pending']}", flush=True)
    if records:
        bl = baseline["prefix"]
        print(f"\ncache breakdown per target (prefix baseline = {bl if bl is not None else 'n/a'} tokens):",
              flush=True)
        print(f"  {'input':>8}  {'cache_create':>12}  {'cache_read':>10}  {'reread':>8}  target", flush=True)
        for r in records:
            disp = origin_of(rundir, r["target"]) if a.isolation == "staged" else r["target"]
            if r["cr"] is None:
                cells = f"  {'?':>8}  {'?':>12}  {'?':>10}  {'n/a':>8}"
            else:
                rr = "baseline" if r["baseline"] else f"{r['reread']:.0%}"
                cells = f"  {r['input']:>8}  {r['cc']:>12}  {r['cr']:>10}  {rr:>8}"
            print(f"{cells}  {disp}", flush=True)
    if a.isolation == "staged":
        print("\nstaged review — diff of each target vs its origin:", flush=True)
        print(sh("python3", str(sp), "--dir", str(rundir), "diff").stdout, flush=True)
        print(f"patch:    {rundir}/diff.patch", flush=True)
        print(f"apply:    python3 {sp} --dir {rundir} apply", flush=True)
        print(f"discard:  python3 {sp} --dir {rundir} discard", flush=True)
    else:
        print("side effects are live (isolation=none) — review per the operation's output target.", flush=True)
    print(f"queue state: {rundir}", flush=True)


if __name__ == "__main__":
    main()
