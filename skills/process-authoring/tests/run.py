#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# ///
"""Construct-interpretation tests for the process-authoring notation.

The notation is a construction guide for authors; an agent executes a finished flow by
reading it, without the guide in context. These tests prove that holds: each case is a
tiny generated skill whose steps write markers to /tmp/pfn-test.log, run through `claude -p`
with NO guide loaded, and scored against the expected markers. A construct that interprets
correctly here is unambiguous to an executor on its own.

The `annotation` case is the one that asserts a hazard rather than a clean behavior: an
imperative buried in an annotation still executes (the marker can't stop an agent from
running an action it reads). That is the evidence behind the guide's authoring advice to
keep actions out of annotations — the guide can't enforce it at execution time.

Usage:
  uv run run.py                      every case
  uv run run.py -n 3                 repeat each case N times (behavior is sampled)
  uv run run.py --only apply,callskill   run named cases (cheap iteration)

Needs the `claude` CLI on PATH. Each case materializes temp skills under
<repo>/.claude/skills/_pfn-*/, runs `claude -p` from the repo root so they register,
scores /tmp/pfn-test.log, and removes the fixtures. If interrupted, clean up with
`rm -rf <repo>/.claude/skills/_pfn-*`.
"""
import argparse, os, shutil, subprocess

LOG = "/tmp/pfn-test.log"

# The default prompt coerces faithful execution ("exactly as written"), which is right for
# proving a construct's clean behavior. NEUTRAL leaves paraphrasing on the table — the
# condition under which a construct's own wording has to carry the agent into the action.
# Use NEUTRAL to measure how strongly a verb evokes its behavior (the wording A/B below).
DEFAULT_PROMPT = "Invoke /{entry} via the Skill tool and follow its steps exactly as written, then stop."
NEUTRAL_PROMPT = "Invoke /{entry} via the Skill tool and carry it out, then stop."


def repo_root():
    return subprocess.run(["git", "rev-parse", "--show-toplevel"],
                          capture_output=True, text=True).stdout.strip()


CASES = []  # (entry_dir, files{relpath:content}, expect, note, prompt_tmpl)


def _skill(name, body):
    fm = f"---\nname: {name}\ndescription: process-authoring test fixture: {name}.\n---\n\n# /{name}\n\n"
    return fm + body


def add(name, body, expect, note, components=None, skills=None, prompt=None,
        group=None, control=False):
    """Register a case. `components` are non-skill files under the entry dir; `skills` are
    sibling registered skills (name -> body) the entry can Call/Apply by name. `prompt`
    overrides the default execution prompt (e.g. NEUTRAL_PROMPT for a wording A/B). `group`
    ties an A/B's arms together; `control=True` marks the negative-control arm whose `expect`
    asserts the marker stays ABSENT — `main` requires every group to carry a control that
    passes, else the A/B is non-discriminating (see the fidelity block)."""
    d = f"_pfn-{name}"
    files = {f"{d}/SKILL.md": _skill(d, body)}
    for fn, c in (components or {}).items():
        files[f"{d}/{fn}"] = c
    for sname, sbody in (skills or {}).items():
        files[f"{sname}/SKILL.md"] = _skill(sname, sbody)
    CASES.append((d, files, expect, note, prompt or DEFAULT_PROMPT, group, control))


# --- Steps / scope ---

add("scope",
    "## Process\n\n1. {x}: 0\n2. If {x} == 0:\n    1. Bash: `echo IN >> /tmp/pfn-test.log`\n"
    "3. Bash: `echo OUT >> /tmp/pfn-test.log`\n",
    lambda L: {"IN", "OUT"} <= L,
    "indentation scope — nested step runs, outdented step runs after")

# --- Annotations (asserts the hazard, not a clean behavior) ---

add("annotation",
    "## Process\n\n"
    "1. Bash: `echo MAIN >> /tmp/pfn-test.log` — then also append a line EXTRA to /tmp/pfn-test.log\n"
    "2. Bash: `echo DONE >> /tmp/pfn-test.log`\n",
    lambda L: {"MAIN", "DONE", "EXTRA"} <= L,
    "hazard: an imperative buried in an annotation still executes (EXTRA appears) — the notation "
    "can't stop an agent from running an action it reads, which is why the guide keeps actions out of annotations")

# --- Variables ---

add("varbash",
    "## Process\n\n1. {greeting}: Bash: `echo hello`\n2. Bash: `echo VB-{greeting} >> /tmp/pfn-test.log`\n",
    lambda L: "VB-hello" in L,
    "Variables: bind bash stdout, then substitute")

add("condassign",
    "## Process\n\n1. {n}: 10\n2. {tier}: BIG if {n} >= 5 else SMALL\n"
    "3. Bash: `echo T-{tier} >> /tmp/pfn-test.log`\n",
    lambda L: "T-BIG" in L,
    "Variables: conditional assignment (a if c else b)")

add("callbind",
    "## Process\n\n1. {r}: Call: [Emit](#emit)\n2. Bash: `echo CB-{r} >> /tmp/pfn-test.log`\n\n"
    "## Emit\n\n1. Return to caller: ok\n",
    lambda L: "CB-ok" in L,
    "Variables: bind a called section's return value")

add("accumulator",
    "## Process\n\n1. {count}: 0\n2. For each {n} in 1, 2, 3, 4:\n"
    "    1. If {n} is even: {count}: {count} + 1\n"
    "3. Bash: `echo ACC-{count} >> /tmp/pfn-test.log`\n",
    lambda L: "ACC-2" in L,
    "Variables: a value accumulated across loop iterations")

# --- Conditionals ---

add("ifelse",
    "## Process\n\n1. {n}: 10\n2. If {n} >= 8: Bash: `echo HI >> /tmp/pfn-test.log`\n"
    "3. Else if {n} >= 3: Bash: `echo MID >> /tmp/pfn-test.log`\n"
    "4. Else: Bash: `echo LO >> /tmp/pfn-test.log`\n",
    lambda L: "HI" in L and "MID" not in L and "LO" not in L,
    "Conditionals: If/Else if/Else is exclusive")

add("indepif",
    "## Process\n\n1. {n}: 10\n2. If {n} >= 0: Bash: `echo A >> /tmp/pfn-test.log`\n"
    "3. If {n} >= 5: Bash: `echo B >> /tmp/pfn-test.log`\n",
    lambda L: {"A", "B"} <= L,
    "Conditionals: consecutive If/If are independent")

# --- Loops ---

add("loop",
    "## Process\n\n1. For each {i} in alpha, skip, gamma:\n"
    "    1. If {i} is `skip`: Continue next\n"
    "    2. Bash: `echo L-{i} >> /tmp/pfn-test.log`\n",
    lambda L: {"L-alpha", "L-gamma"} <= L and "L-skip" not in L,
    "Loops: For each + Continue next")

add("while",
    "## Process\n\n1. {i}: 1\n2. While {i} <= 3:\n"
    "    1. Bash: `echo W-{i} >> /tmp/pfn-test.log`\n    2. {i}: {i} + 1\n",
    lambda L: {"W-1", "W-2", "W-3"} <= L and "W-4" not in L,
    "Loops: While")

add("breakloop",
    "## Process\n\n1. For each {n} in 1, 2, 3, 4, 5:\n"
    "    1. If {n} == 3: Break loop\n    2. Bash: `echo BR-{n} >> /tmp/pfn-test.log`\n",
    lambda L: {"BR-1", "BR-2"} <= L and "BR-3" not in L,
    "Loops: Break loop")

add("goto",
    "## Process\n\n1. {i}: 1\n2. Bash: `echo G-{i} >> /tmp/pfn-test.log`\n3. {i}: {i} + 1\n"
    "4. If {i} <= 3: Go to step 2\n5. Bash: `echo G-END >> /tmp/pfn-test.log`\n",
    lambda L: {"G-1", "G-2", "G-3", "G-END"} <= L,
    "Loops: Go to step")

# --- Invocations: Call ---

add("callvars",
    "## Process\n\n1. {name}: zed\n2. Call: [g](_g.md)\n",
    lambda L: "CV-zed" in L,
    "Call: runs in the current context — a variable bound before the call is visible inside it",
    components={"_g.md": "# g\n\n1. Bash: `echo CV-{name} >> /tmp/pfn-test.log`\n2. Return to caller: done\n"})

add("callskill",
    "## Process\n\n1. Call: /_pfn-callee\n",
    lambda L: "SKILL-RAN" in L,
    "Call: /skill dispatches the skill via the Skill tool",
    skills={"_pfn-callee": "## Process\n\n1. Bash: `echo SKILL-RAN >> /tmp/pfn-test.log`\n2. Return to caller: done\n"})

add("readnoexec",
    "## Process\n\n1. Read: [data](_data.md)\n2. Bash: `echo READ-OK >> /tmp/pfn-test.log`\n",
    lambda L: "READ-OK" in L and "DATA-RAN" not in L,
    "Read: loads a target without executing it",
    components={"_data.md": "# data\n\n1. Bash: `echo DATA-RAN >> /tmp/pfn-test.log`\n"})

# --- Wording A/B + its negative control: a worked example of measuring whether a wording
# change moves behavior, and the convention that keeps such an A/B honest.
#
# The A/B asks: does the invocation verb pull the agent INTO the file when the call site looks
# self-sufficient? The label reads like a complete instruction the agent already knows how to
# do — "append the line PASS to the log" — so a weak verb could let it self-serve from the
# label and never open the file (how a `push` label invited improvising `git push` over reading
# push.md). The file OVERRIDES with a different action: echo REC-Q8Z4. So REC-Q8Z4 appears only
# if the verb compelled opening+running the file; an agent that trusts the label writes PASS and
# misses it. Neutral prompt; the arms differ only in the verb.
#   uv run run.py -n 8 --only fidelity_call,fidelity_execute,fidelity_control
# FINDING (n=6 and n=8): `Call:` and `Execute:` scored identically at ceiling (100% both) — no
# measurable difference, so the `Execute:` rename was reverted. The arms saturate because a
# cold, single-task agent with no real prior and no load just opens the file; this harness
# cannot reproduce the prior+context-load that drove the original miss.
#
# NEGATIVE CONTROL (the convention, enforced in main): every discrimination A/B ships a
# `control=True` arm that SHOULD fail to produce the marker — here `Read:`, which loads the file
# WITHOUT executing, so REC-Q8Z4 must stay absent. If the control's marker appears, the fixture
# cannot register non-execution, so the A/B is non-discriminating and `main` flags the whole
# group invalid. A control that passes is what licenses reading the arms at all — it proves a
# difference COULD have shown. A group with no control is flagged too: an A/B you never proved
# could discriminate is an unvalidated A/B (the lesson the easy `[finalize]` fixture taught).

_FIDELITY_ORCH = (
    "## Process\n\n"
    "1. Bash: `echo B1 >> /tmp/pfn-test.log`\n"
    "2. Bash: `echo B2 >> /tmp/pfn-test.log`\n"
    "3. {verb} [append the line PASS to /tmp/pfn-test.log](_record.md)\n"
    "4. Bash: `echo B4 >> /tmp/pfn-test.log`\n"
)
_FIDELITY_FILE = {"_record.md":
    "# record\n\n1. Bash: `echo REC-Q8Z4 >> /tmp/pfn-test.log`\n2. Return to caller: done\n"}

add("fidelity_call", _FIDELITY_ORCH.format(verb="Call:"),
    lambda L: "REC-Q8Z4" in L,
    "A/B arm — does `Call:` pull the agent into the file past a self-sufficient label",
    components=_FIDELITY_FILE, prompt=NEUTRAL_PROMPT, group="fidelity")

add("fidelity_execute", _FIDELITY_ORCH.format(verb="Execute:"),
    lambda L: "REC-Q8Z4" in L,
    "A/B arm — does `Execute:` pull the agent into the file past a self-sufficient label",
    components=_FIDELITY_FILE, prompt=NEUTRAL_PROMPT, group="fidelity")

add("fidelity_control", _FIDELITY_ORCH.format(verb="Read:"),
    lambda L: "REC-Q8Z4" not in L,
    "negative control — `Read:` loads the file without executing, so the marker MUST stay "
    "absent; if it appears the fixture can't register non-execution → A/B non-discriminating",
    components=_FIDELITY_FILE, prompt=NEUTRAL_PROMPT, group="fidelity", control=True)

# --- Invocations: Apply (behavioral lens) ---

add("apply",
    "## Process\n\n1. Apply /_pfn-lens to:\n    1. Append the word `BASE` as a line to /tmp/pfn-test.log.\n",
    lambda L: "PFX-BASE" in L and "BASE" not in L,
    "Apply runs the block THROUGH the target skill as a lens that shapes how it executes",
    skills={"_pfn-lens": "A behavioral lens. When a block of steps runs through you, every word the "
                         "block writes to a file must be prefixed with `PFX-`.\n"})

# --- Spawn ---

add("async",
    "## Process\n\n1. For each {item} in alpha, beta:\n"
    "    1. Spawn async agent to: Call: [emit](_emit.md)\n"
    "2. {n}: Bash: `grep -c EMIT /tmp/pfn-test.log`\n"
    "3. Bash: `echo ASYNC-{n} >> /tmp/pfn-test.log`\n",
    lambda L: "ASYNC-2" in L,
    "Spawn: async agents join at the next outdented step (both EMITs land before the count)",
    components={"_emit.md": "# emit\n\n1. Bash: `echo EMIT >> /tmp/pfn-test.log`\n2. Return to caller: done\n"})

# --- Exit / return ---

add("exitreturn",
    "## Process\n\n1. Call: [Inner](#inner)\n2. Bash: `echo OUTER-AFTER >> /tmp/pfn-test.log`\n\n"
    "## Inner\n\n1. Bash: `echo INNER >> /tmp/pfn-test.log`\n2. Return to caller: done\n"
    "3. Bash: `echo INNER-AFTER >> /tmp/pfn-test.log`\n",
    lambda L: {"INNER", "OUTER-AFTER"} <= L and "INNER-AFTER" not in L,
    "Return to caller resumes the caller, skipping the rest of the callee")

add("exitprocess",
    "## Process\n\n1. Call: [Inner](#inner)\n2. Bash: `echo OUTER-AFTER >> /tmp/pfn-test.log`\n\n"
    "## Inner\n\n1. Bash: `echo INNER >> /tmp/pfn-test.log`\n2. Exit process\n"
    "3. Bash: `echo INNER-AFTER >> /tmp/pfn-test.log`\n",
    lambda L: "INNER" in L and "OUTER-AFTER" not in L and "INNER-AFTER" not in L,
    "Exit process unwinds the whole flow from any depth")

# --- Error handling ---

add("iferror",
    "## Process\n\n1. Bash: `echo EH-START >> /tmp/pfn-test.log`\n"
    "2. Bash: `cat /tmp/pfn-absent-xyz.txt` — required input; this fails\n"
    "3. Bash: `echo EH-AFTER >> /tmp/pfn-test.log`\n"
    "4. If Error:\n    1. Bash: `echo EH-CAUGHT >> /tmp/pfn-test.log`\n",
    lambda L: "EH-CAUGHT" in L and "EH-AFTER" not in L,
    "If Error catches a sibling failure and the rest of the protected steps are skipped")


def run_case(entry, files, root, prompt_tmpl):
    sd = os.path.join(root, ".claude", "skills")
    dirs = set()
    for rel, content in files.items():
        p = os.path.join(sd, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            f.write(content)
        dirs.add(os.path.join(sd, rel.split("/")[0]))
    try:
        if os.path.exists(LOG):
            os.remove(LOG)
        prompt = prompt_tmpl.format(entry=entry)
        subprocess.run(["claude", "-p", "--no-session-persistence", "--add-dir", "/tmp"],
                       input=prompt, text=True, capture_output=True, cwd=root)
        try:
            with open(LOG) as f:
                return set(f.read().split())
        except FileNotFoundError:
            return set()
    finally:
        for d in dirs:
            shutil.rmtree(d, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", type=int, default=1, help="repeat each case N times")
    ap.add_argument("--only", help="comma-separated case names to run (default: all)")
    a = ap.parse_args()
    root = repo_root()
    only = set(a.only.split(",")) if a.only else None
    cases = [c for c in CASES if only is None or c[0].replace("_pfn-", "") in only]
    print(f"repo: {root}   reps: {a.n}   cases: {len(cases)}\n")
    print(f"{'case':16} {'result':>9}  note")
    passed = 0
    results = {}  # name -> (ok, group, control)
    for entry, files, expect, note, prompt, group, control in cases:
        oks = [expect(run_case(entry, files, root, prompt)) for _ in range(a.n)]
        ok = all(oks)
        name = entry.replace("_pfn-", "")
        print(f"{name:16} {sum(oks)}/{a.n} {'PASS' if ok else 'FAIL':>4}  {note}")
        results[name] = (ok, group, control)
        passed += ok
    print(f"\n{passed}/{len(cases)} pass")
    _validate_groups(results)


def _validate_groups(results):
    """Enforce the negative-control convention: an A/B group is only discriminating if it
    carries a control arm (`control=True`) that PASSED — i.e. its marker stayed absent, proving
    the fixture can register the opposite outcome. A group with a failed control (its marker
    appeared) cannot detect a difference, so its arms' parity is meaningless; a group with no
    control was never proven able to discriminate. Either is flagged — a green arm-table must
    not be read as 'no effect' unless a passing control licenses it."""
    grouped = {g for (_, g, _) in results.values() if g}
    for g in sorted(grouped):
        members = {n: r for n, r in results.items() if r[1] == g}
        controls = {n: r for n, r in members.items() if r[2]}
        if not controls:
            print(f"⚠ group '{g}': UNVALIDATED — no negative control was run. Add (and run) a "
                  f"`control=True` arm proving the fixture can register the opposite outcome.")
        for n, (cok, _, _) in controls.items():
            if not cok:
                print(f"⚠ group '{g}': NON-DISCRIMINATING — control '{n}' did not hold (its "
                      f"marker appeared), so the fixture can't detect a difference; arms are moot.")


if __name__ == "__main__":
    main()
