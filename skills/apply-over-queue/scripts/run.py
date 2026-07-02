#!/usr/bin/env python3
"""apply-over-queue driver: cached `claude -p` fan-out over a work queue.

Runs one operation over many targets while paying for the operation's (large, shared) instruction
payload once: every spawn reads the IDENTICAL flattened instruction FIRST, so it serves from prompt
cache (~0.1×), then claims its varying target from the queue AFTER — keeping the cached prefix
identical no matter the queue size. An identical prefix cache-reuses across separate `claude -p`
processes.

Keeping that prefix HOT across the 5-minute prompt-cache TTL is the job of two mechanisms:

  warmup   one empty-target spawn (AOQ_EMPTY=1 -> queue `next` returns NONE) reads the instruction
           and exits, establishing the cache before any real work — so the first real spawn is
           already warm and there is no cold-start special case.
  keepalive while a work-spawn runs, an empty-target ping fires every --warm-interval seconds, using
           the IDENTICAL stub to re-read and refresh the exact cached prefix without claiming work.
           A single per-item spawn slower than the TTL would otherwise age the cache before the next
           spawn reads it; the keepalive prevents that. Work-spawns stay sequential — the only
           concurrency is one heavy spawn plus a lightweight ping alongside it.

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
instruction payload. This driver is mechanism only: flatten -> stage -> seed -> warm -> spawn loop,
asserting the cache saving on every spawn after the first and aborting if the prefix ever diverges.
"""
import argparse
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Below this cached-prefix size the per-spawn saving is immaterial, so the assertion is skipped.
CACHE_ASSERT_MIN_PREFIX = 2000

# Best-effort classification of a failed spawn's error output. Decisive = retry won't help (and the
# run is probably doomed); transient = a momentary server/network hiccup worth one retry.
_DECISIVE = ("authentication_error", "permission_error", "invalid_request_error",
             "401", "403", "invalid api key", "invalid_api_key")
_TRANSIENT = ("rate_limit", "overloaded", "api_error", "429", "529", "500", "502", "503", "504",
              "timeout", "timed out", "connection", "econnreset", "temporarily")


def classify_error(text):
    t = (text or "").lower()
    if any(s in t for s in _DECISIVE):
        return "decisive"
    if any(s in t for s in _TRANSIENT):
        return "transient"
    return "unknown"


def sh(*cmd):
    return subprocess.run(cmd, text=True, capture_output=True)


def _build_cmd(add_dirs, exclude_dynamic, model):
    cmd = ["claude", "-p", "--output-format", "stream-json", "--verbose",
           "--no-session-persistence",
           "--allowedTools", "Bash", "Read", "Write", "Edit"]
    if model:
        cmd += ["--model", model]
    if exclude_dynamic:
        cmd.append("--exclude-dynamic-system-prompt-sections")
    for d in add_dirs:
        cmd += ["--add-dir", str(d)]
    return cmd


def _parse_stream(stdout_text, instr_path):
    """Two usage views from the JSONL event stream:
       result_usage  — the turn's CUMULATIVE total (summed over every internal call); the per-target
                       cost figure, but useless for a reuse ratio (it absorbs the target's body reads
                       and scales with the spawn's tool-call count).
       measure_usage — the SINGLE call right after the instruction is read, BEFORE the target's body
                       enters context; cache_read / (cache_read+cache_creation) there is shared-prefix
                       reuse alone — the cache-assertion signal.
    Streaming can split one API call across several assistant events that share one usage object, so
    collapse consecutive events with an identical usage signature into one call, recording whether
    that call issued the Read of the shared instruction."""
    calls, result_usage = [], None
    for line in (stdout_text or "").splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        t = ev.get("type")
        if t == "assistant":
            msg = ev.get("message") or {}
            u = msg.get("usage")
            if not u:
                continue
            sig = (u.get("input_tokens") or 0, u.get("cache_read_input_tokens") or 0,
                   u.get("cache_creation_input_tokens") or 0)
            read_instr = any(
                b.get("type") == "tool_use" and b.get("name") == "Read"
                and ((b.get("input") or {}).get("file_path", "") == instr_path
                     or (b.get("input") or {}).get("file_path", "").endswith("instruction.md"))
                for b in msg.get("content") or [])
            if calls and calls[-1]["sig"] == sig:
                calls[-1]["read_instr"] = calls[-1]["read_instr"] or read_instr
            else:
                calls.append({"sig": sig, "usage": u, "read_instr": read_instr})
        elif t == "result":
            result_usage = ev.get("usage")
    measure_usage = None
    for i, c in enumerate(calls):
        if c["read_instr"] and i + 1 < len(calls):
            measure_usage = calls[i + 1]["usage"]
            break
    return result_usage, measure_usage


def claude_p_blocking(prompt, cwd, add_dirs, exclude_dynamic, instr_path, model=None, extra_env=None):
    """Run a spawn to completion — used for the fast empty-target warmup / keepalive pings."""
    env = {**os.environ, **(extra_env or {})}
    p = subprocess.run(_build_cmd(add_dirs, exclude_dynamic, model), input=prompt, text=True,
                       capture_output=True, cwd=str(cwd), env=env)
    ru, mu = _parse_stream(p.stdout, instr_path)
    return p.returncode == 0, ru, mu, (p.stderr or "")


def run_work_spawn(prompt, cwd, add_dirs, exclude_dynamic, instr_path, model,
                   warm_interval, max_spawn_seconds, keepalive, out_path, err_path):
    """Run one real (target-claiming) spawn, firing `keepalive` every `warm_interval` seconds it stays
    alive so a long spawn can't age the shared cache before the next spawn reads it. Kills the spawn
    if it outlives `max_spawn_seconds` (hung / malformed). stdout/stderr go to files so polling can't
    deadlock on a full pipe buffer."""
    cmd = _build_cmd(add_dirs, exclude_dynamic, model)
    hung = False
    with open(out_path, "w") as outf, open(err_path, "w") as errf:
        # No AOQ_EMPTY -> this spawn claims a real target from the queue.
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=outf, stderr=errf,
                             text=True, cwd=str(cwd), env={**os.environ})
        if p.stdin is not None:
            try:
                p.stdin.write(prompt)
            finally:
                p.stdin.close()
        start = last_touch = time.time()
        while True:
            try:
                p.wait(timeout=5)
                break
            except subprocess.TimeoutExpired:
                pass
            now = time.time()
            if now - start > max_spawn_seconds:
                p.kill()
                try:
                    p.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    pass
                hung = True
                break
            if now - last_touch >= warm_interval:
                keepalive()                       # blocking; refreshes the shared cache
                last_touch = time.time()
    out_text = Path(out_path).read_text() if Path(out_path).exists() else ""
    err_text = Path(err_path).read_text() if Path(err_path).exists() else ""
    ru, mu = _parse_stream(out_text, instr_path)
    ok = (p.returncode == 0) and not hung
    return ok, ru, mu, hung, err_text


def status(qp, rundir):
    out = sh("python3", str(qp), "--dir", str(rundir), "status").stdout.strip()
    return dict(kv.split("=") for kv in out.split())


def claimed_list(rundir):
    # Claim order == spawn order (one target per work-spawn), so the token a spawn handled is the one
    # it appended to claimed.txt — reply-independent. Keepalives claim nothing, so they never appear.
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
    ap.add_argument("--cache-floor", type=float, default=0.95,
                    help="minimum fraction of the instruction prefix (system + stub + flattened "
                    "instruction, measured at the call right after the spawn reads the instruction and "
                    "BEFORE the per-target payload loads) that each later spawn must re-read from cache; "
                    "below it the run ABORTS — the prefix diverged and is being re-billed not cache-served")
    ap.add_argument("--warm-interval", type=float, default=240.0,
                    help="seconds between cache-keepalive pings while a work-spawn runs. A ping is an "
                    "empty-target spawn (AOQ_EMPTY) that re-reads the shared prefix so a slow spawn "
                    "can't let it age past the ~300s prompt-cache TTL. Default 240 fires twice per TTL, "
                    "so a single missed ping is survived (the next lands before expiry)")
    ap.add_argument("--max-spawn-minutes", type=float, default=20.0,
                    help="wall-clock ceiling per work-spawn; one that outlives it is killed as "
                    "hung/malformed (and treated as a failure)")
    ap.add_argument("--continue-on-failure", action="store_true", default=False,
                    help="on a work-spawn failure (hung or errored), skip it and continue. Default "
                    "(off): halt the chain so a malformed operation can't spawn N more doomed calls")
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
    #    A keepalive/warmup spawn runs this SAME stub with AOQ_EMPTY=1, so `queue.py next` returns NONE
    #    and it refreshes the exact cached prefix without claiming work.
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

    # 5. Keepalive / warmup. An empty-target spawn re-reads the shared prefix (identical stub +
    #    AOQ_EMPTY=1 -> NONE) to refresh its cache entry without claiming work. On failure: retry once
    #    if transient (or unclassifiable); skip if decisive (auth/permission — retry won't help). A
    #    failed keepalive is non-fatal (the cache may age, and the next work-spawn's reading catches
    #    any real divergence); a failed warmup IS fatal (no shared cache to build on).
    def fire_keepalive(label="keepalive"):
        ok, _, _, err = claude_p_blocking(stub, cwd=work_cwd, add_dirs=add_dirs,
                                          exclude_dynamic=a.exclude_dynamic, instr_path=str(instr),
                                          model=a.model, extra_env={"AOQ_EMPTY": "1"})
        if ok:
            return True
        cls = classify_error(err)
        if cls == "decisive":
            print(f"  {label} failed (decisive: likely auth/permission — run probably doomed); "
                  f"not retrying", flush=True)
            return False
        ok, _, _, _ = claude_p_blocking(stub, cwd=work_cwd, add_dirs=add_dirs,           # one retry
                                        exclude_dynamic=a.exclude_dynamic, instr_path=str(instr),
                                        model=a.model, extra_env={"AOQ_EMPTY": "1"})
        if not ok:
            print(f"  {label} failed twice ({cls}); cache may age — the next spawn's reading will "
                  f"catch any real divergence", flush=True)
        return ok

    # 6. Cache assertion. The warmup ESTABLISHES the cached prefix; the first real spawn reads it warm
    #    and SETS the baseline (system + stub + the instruction it reads, all byte-identical); every
    #    later spawn must RE-READ that same prefix. The signal is the measurement call (measure_usage):
    #    one call's usage right after the instruction is read and before the target's body enters
    #    context, so cache_read / (cache_read+cache_creation) reflects shared-prefix reuse alone. The
    #    whole-turn total (result_usage) is reported as cost but never asserted on.
    baseline: dict[str, "int | None"] = {"prefix": None}
    records = []                                          # per-target cache breakdown for the report
    work_out = rundir / "_work_stdout.jsonl"
    work_err = rundir / "_work_stderr.txt"

    def one_spawn(label):
        before = len(claimed_list(rundir))
        ok, ru, mu, hung, err = run_work_spawn(
            stub, cwd=work_cwd, add_dirs=add_dirs, exclude_dynamic=a.exclude_dynamic,
            instr_path=str(instr), model=a.model, warm_interval=a.warm_interval,
            max_spawn_seconds=a.max_spawn_minutes * 60, keepalive=lambda: fire_keepalive(),
            out_path=work_out, err_path=work_err)
        after = claimed_list(rundir)
        target = after[before] if len(after) > before else None
        st = status(qp, rundir)

        tot = ru or mu or {}                             # cost view (cumulative); for the report only
        cr_t = tot.get("cache_read_input_tokens") or 0
        cc_t = tot.get("cache_creation_input_tokens") or 0
        inp_t = tot.get("input_tokens") or 0

        fail = hung or not ok
        suffix = (f" HUNG>{a.max_spawn_minutes:g}min KILLED" if hung
                  else (f" ERRORED({classify_error(err)})" if not ok else ""))

        if mu is None:                                   # no usable measurement call -> can't assert
            if target is not None:
                records.append({"target": target, "input": inp_t or None, "cc": cc_t or None,
                                "cr": cr_t or None, "reread": None, "baseline": False})
            why = "usage unavailable" if ru is None else "instruction-read boundary not found"
            print(f"  {label}: ok={ok}{suffix} prefix measurement UNAVAILABLE ({why}) -> "
                  f"done={st['done']} pending={st['pending']}", flush=True)
            return "failed" if fail else "ok"

        m_cr = mu.get("cache_read_input_tokens") or 0
        m_cc = mu.get("cache_creation_input_tokens") or 0
        is_base = baseline["prefix"] is None             # first spawn with a measurement sets baseline
        if is_base:
            baseline["prefix"] = m_cr + m_cc
        base = baseline["prefix"]
        frac = None if is_base else ((m_cr / base) if base else 1.0)
        if target is not None:
            records.append({"target": target, "input": inp_t, "cc": cc_t, "cr": cr_t,
                            "reread": frac, "baseline": is_base})
        head = f"  {label}: ok={ok}{suffix} input={inp_t} cache_create={cc_t} cache_read={cr_t} "
        if is_base:
            print(head + f"instr-prefix-baseline={base} -> done={st['done']} pending={st['pending']}",
                  flush=True)
            return "failed" if fail else "ok"
        print(head + f"instr-prefix-reread={frac:.0%} -> done={st['done']} pending={st['pending']}",
              flush=True)
        if base and base >= CACHE_ASSERT_MIN_PREFIX and frac is not None and frac < a.cache_floor:
            raise SystemExit(
                f"\ncache assertion FAILED at {label}: re-read {frac:.0%} of the instruction prefix "
                f"(measurement-call cache_read={m_cr} vs prefix baseline {base}), below floor "
                f"{a.cache_floor:.0%}. The shared prefix (system + stub + flattened instruction) diverged "
                f"across spawns and is being re-billed instead of cache-served. Keep it byte-identical: "
                f"make the operation target-agnostic and keep cwd / --add-dir identical every spawn "
                f"(staged mode fixes cwd to the workspace; check --add-dir and the operation for target "
                f"literals).")
        return "failed" if fail else "ok"

    # 7. Warm the shared cache once (empty-target), then drive the queue. Warmup is fatal on failure.
    print("warmup: establishing the shared cache (empty-target spawn)…", flush=True)
    if not fire_keepalive(label="warmup"):
        raise SystemExit("warmup failed — could not establish the shared cache; aborting "
                         "(check auth / API reachability).")

    cfg = (f"warm-interval={a.warm_interval:g}s max-spawn={a.max_spawn_minutes:g}min "
           f"continue-on-failure={a.continue_on_failure}")
    halted = False
    if a.feeder:
        import shlex
        feeder = shlex.split(a.feeder) + ["--dir", str(rundir)]
        print(f"run {run_id}: dynamic feeder | isolation={a.isolation} | cwd {work_cwd} | {cfg}", flush=True)
        passes, reason = 0, "max"
        while passes < a.max:
            nxt = (sh(*feeder).stdout.strip().splitlines() or [""])[-1].strip()
            if not nxt or nxt.startswith("DONE"):
                reason = nxt.split(":", 1)[1] if ":" in nxt else "exhausted"
                break
            token = stage_add(nxt) if a.isolation == "staged" else nxt
            sh("python3", str(qp), "--dir", str(rundir), "push", token)
            passes += 1
            if one_spawn(f"pass {passes}") == "failed" and not a.continue_on_failure:
                halted, reason = True, "spawn failed (--continue-on-failure off)"
                break
        print(f"\nfeeder stopped: {reason} after {passes} pass(es)", flush=True)
    else:
        n = len(items)
        print(f"run {run_id}: {n} targets | isolation={a.isolation} | cwd {work_cwd} | {cfg}", flush=True)
        spawned = 0
        while spawned < n + 2 and int(status(qp, rundir)["pending"]) > 0:
            spawned += 1
            if one_spawn(f"spawn {spawned}") == "failed" and not a.continue_on_failure:
                halted = True
                break

    if halted:
        print("\nHALTED: a work-spawn failed and --continue-on-failure is off. Completed targets are "
              "below; fix the operation and re-run to resume the still-pending queue.", flush=True)

    # 8. Report + review gate.
    st = status(qp, rundir)
    print(f"\ndone={st['done']} claimed={st['claimed']} pending={st['pending']}", flush=True)
    if records:
        bl = baseline["prefix"]
        print(f"\ncache breakdown per target — input/create/read are whole-turn totals (cost); reread is "
              f"the instruction-prefix reuse (assertion signal), baseline = {bl if bl is not None else 'n/a'} tokens:",
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
