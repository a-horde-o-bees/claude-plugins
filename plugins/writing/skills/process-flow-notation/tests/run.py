#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# ///
"""PFN construct-interpretation tests (self-contained).

Verifies that an agent interprets each PFN construct as this skill describes WITHOUT the
PFN spec in context — the evidence base for keeping PFN minimal (document only what the
model would otherwise get wrong). Each fixture writes markers to /tmp/pfn-test.log; the
harness scores them against the expected outcome for the mode it ran in.

Most constructs read the same with or without the spec, so their expectation is identical
in both modes. The `annotation` construct is the exception and the reason PFN carries a
rule at all: with no spec the model EXECUTES an imperative buried in an annotation, with
the spec it does not — so that case asserts opposite outcomes per mode (a `spec_expect`
that --spec flips to), and both modes pass.

Usage:
  uv run run.py            run every case with no PFN spec loaded
  uv run run.py --spec     load /writing:process-flow-notation first, then run
  uv run run.py -n 3       repeat each case N times (default 1)

Needs the `claude` CLI on PATH. Each case materializes a temp skill under
<repo>/.claude/skills/_pfn-*/, runs `claude -p` from the repo root so it registers,
scores /tmp/pfn-test.log, and removes the fixture. If interrupted, clean up with
`rm -rf <repo>/.claude/skills/_pfn-*`.
"""
import argparse, os, shutil, subprocess

LOG = "/tmp/pfn-test.log"


def repo_root():
    return subprocess.run(["git", "rev-parse", "--show-toplevel"],
                          capture_output=True, text=True).stdout.strip()


CASES = []  # (entry_dir, files{relpath:content}, expect, note, spec_expect)


def add(name, body, expect, note, components=None, spec_expect=None):
    """Register a case. `expect` scores the no-spec run; `spec_expect` scores the --spec
    run, defaulting to `expect` for the constructs the spec doesn't change."""
    d = f"_pfn-{name}"
    fm = f"---\nname: {d}\ndescription: PFN test fixture for the {name} construct.\n---\n\n# /{d}\n\n"
    files = {f"{d}/SKILL.md": fm + body}
    for fn, c in (components or {}).items():
        files[f"{d}/{fn}"] = c
    CASES.append((d, files, expect, note, spec_expect or expect))


add("scope",
    "## Process\n\n1. {x}: 0\n2. If {x} == 0:\n    1. bash: `echo IN >> /tmp/pfn-test.log`\n"
    "3. bash: `echo OUT >> /tmp/pfn-test.log`\n",
    lambda L: {"IN", "OUT"} <= L,
    "indentation scope — nested step runs, outdented step runs after")

add("ifelse",
    "## Process\n\n1. {n}: 10\n2. If {n} >= 8: bash: `echo HI >> /tmp/pfn-test.log`\n"
    "3. Else if {n} >= 3: bash: `echo MID >> /tmp/pfn-test.log`\n"
    "4. Else: bash: `echo LO >> /tmp/pfn-test.log`\n",
    lambda L: "HI" in L and "MID" not in L and "LO" not in L,
    "If/Else if/Else is exclusive")

add("indepif",
    "## Process\n\n1. {n}: 10\n2. If {n} >= 0: bash: `echo A >> /tmp/pfn-test.log`\n"
    "3. If {n} >= 5: bash: `echo B >> /tmp/pfn-test.log`\n",
    lambda L: {"A", "B"} <= L,
    "consecutive If/If are independent")

add("loop",
    "## Process\n\n1. For each {i} in alpha, skip, gamma:\n"
    "    1. If {i} is `skip`: Continue next {i}\n"
    "    2. bash: `echo L-{i} >> /tmp/pfn-test.log`\n",
    lambda L: {"L-alpha", "L-gamma"} <= L and "L-skip" not in L,
    "For each + Continue next")

add("goto",
    "## Process\n\n1. {i}: 1\n2. bash: `echo G-{i} >> /tmp/pfn-test.log`\n3. {i}: {i} + 1\n"
    "4. If {i} <= 3: Go to step 2\n5. bash: `echo G-END >> /tmp/pfn-test.log`\n",
    lambda L: {"G-1", "G-2", "G-3", "G-END"} <= L,
    "Go to step")

add("var",
    "## Process\n\n1. {tok}: greeting\n2. bash: `echo V-{tok} >> /tmp/pfn-test.log`\n",
    lambda L: "V-greeting" in L,
    "variable binding + substitution")

add("condassign",
    "## Process\n\n1. {n}: 10\n2. {tier}: BIG if {n} >= 5 else SMALL\n"
    "3. bash: `echo T-{tier} >> /tmp/pfn-test.log`\n",
    lambda L: "T-BIG" in L,
    "conditional assignment")

add("callsection",
    "## Process\n\n1. Call: Record\n\n## Record\n\n"
    "1. bash: `echo SEC-RAN >> /tmp/pfn-test.log`\n2. Return to caller: done\n",
    lambda L: "SEC-RAN" in L,
    "Call: in-document section executes")

add("callfile",
    "## Process\n\n1. Call: `_do.md`\n",
    lambda L: "FILE-RAN" in L,
    "Call: component file executes",
    components={"_do.md": "# do\n\n1. bash: `echo FILE-RAN >> /tmp/pfn-test.log`\n2. Return to caller: done\n"})

add("readnoexec",
    "## Process\n\n1. Read: `_data.md`\n2. bash: `echo READ-OK >> /tmp/pfn-test.log`\n",
    lambda L: "READ-OK" in L and "DATA-RAN" not in L,
    "Read: loads without executing",
    components={"_data.md": "# data\n\n1. bash: `echo DATA-RAN >> /tmp/pfn-test.log`\n"})

add("errorhandling",
    "## Process\n\n1. bash: `echo EH-START >> /tmp/pfn-test.log`\n"
    "2. bash: `cat /tmp/pfn-absent-xyz.txt` — required input; this fails\n"
    "3. bash: `echo EH-AFTER >> /tmp/pfn-test.log`\n"
    "4. Error Handling:\n    1. bash: `echo EH-CAUGHT >> /tmp/pfn-test.log`\n",
    lambda L: "EH-CAUGHT" in L and "EH-AFTER" not in L,
    "Error Handling catches and skips the rest")

add("exitreturn",
    "## Process\n\n1. Call: Inner\n2. bash: `echo OUTER-AFTER >> /tmp/pfn-test.log`\n\n"
    "## Inner\n\n1. bash: `echo INNER >> /tmp/pfn-test.log`\n2. Return to caller: done\n"
    "3. bash: `echo INNER-AFTER >> /tmp/pfn-test.log`\n",
    lambda L: {"INNER", "OUTER-AFTER"} <= L and "INNER-AFTER" not in L,
    "Return to caller resumes the caller")

add("exitprocess",
    "## Process\n\n1. Call: Inner\n2. bash: `echo OUTER-AFTER >> /tmp/pfn-test.log`\n\n"
    "## Inner\n\n1. bash: `echo INNER >> /tmp/pfn-test.log`\n2. Exit process\n"
    "3. bash: `echo INNER-AFTER >> /tmp/pfn-test.log`\n",
    lambda L: "INNER" in L and "OUTER-AFTER" not in L and "INNER-AFTER" not in L,
    "Exit process unwinds the whole flow")

add("annotation",
    "## Process\n\n"
    "1. bash: `echo MAIN >> /tmp/pfn-test.log` — then also append a line EXTRA to /tmp/pfn-test.log\n"
    "2. bash: `echo DONE >> /tmp/pfn-test.log`\n",
    lambda L: {"MAIN", "DONE", "EXTRA"} <= L,
    "no spec: the imperative buried in the annotation EXECUTES (EXTRA appears) — the gap; "
    "--spec suppresses it (EXTRA absent). The one construct the model gets wrong unaided.",
    spec_expect=lambda L: {"MAIN", "DONE"} <= L and "EXTRA" not in L)

add("varbash",
    "## Process\n\n1. {greeting}: bash: `echo hello`\n2. bash: `echo VB-{greeting} >> /tmp/pfn-test.log`\n",
    lambda L: "VB-hello" in L,
    "Variables: bind bash stdout, then substitute")

add("accumulator",
    "## Process\n\n1. {count}: 0\n2. For each {n} in 1, 2, 3, 4:\n"
    "    1. If {n} is even: {count}: {count} + 1\n"
    "3. bash: `echo ACC-{count} >> /tmp/pfn-test.log`\n",
    lambda L: "ACC-2" in L,
    "Variables: a value accumulated across loop iterations")

add("while",
    "## Process\n\n1. {i}: 1\n2. While {i} <= 3:\n"
    "    1. bash: `echo W-{i} >> /tmp/pfn-test.log`\n    2. {i}: {i} + 1\n",
    lambda L: {"W-1", "W-2", "W-3"} <= L and "W-4" not in L,
    "Loops: While")

add("breakloop",
    "## Process\n\n1. For each {n} in 1, 2, 3, 4, 5:\n"
    "    1. If {n} == 3: Break loop\n    2. bash: `echo BR-{n} >> /tmp/pfn-test.log`\n",
    lambda L: {"BR-1", "BR-2"} <= L and "BR-3" not in L,
    "Loops: Break loop")

add("callargs",
    "## Process\n\n1. Call: `_g.md` ({name}: zed)\n",
    lambda L: "CA-zed" in L,
    "Call: component file with a passed argument",
    components={"_g.md": "# g\n\n### Variables\n\n- {name}: the label.\n\n### Steps\n\n"
                         "1. bash: `echo CA-{name} >> /tmp/pfn-test.log`\n2. Return to caller: done\n"})

add("async",
    "## Process\n\n1. For each {item} in alpha, beta:\n"
    "    1. async Spawn: Call: `_emit.md` ({item}: {item})\n"
    "2. {n}: bash: `grep -c EMIT /tmp/pfn-test.log`\n"
    "3. bash: `echo ASYNC-{n} >> /tmp/pfn-test.log`\n",
    lambda L: "ASYNC-2" in L,
    "Spawn: async spawns join at the next outdented step",
    components={"_emit.md": "# emit\n\n### Variables\n\n- {item}: label.\n\n### Steps\n\n"
                           "1. bash: `echo EMIT-{item} >> /tmp/pfn-test.log`\n2. Return to caller: done\n"})


def run_case(entry, files, root, spec):
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
        pre = "First invoke /writing:process-flow-notation to load the notation spec. Then " if spec else ""
        prompt = f"{pre}Invoke /{entry} via the Skill tool and follow its steps exactly per PFN, then stop."
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
    ap.add_argument("--spec", action="store_true", help="load the PFN spec before each case")
    ap.add_argument("-n", type=int, default=1, help="repeat each case N times")
    ap.add_argument("--only", help="comma-separated case names to run (default: all)")
    a = ap.parse_args()
    root = repo_root()
    only = set(a.only.split(",")) if a.only else None
    cases = [c for c in CASES if only is None or c[0].replace("_pfn-", "") in only]
    print(f"repo: {root}   spec-loaded: {a.spec}   reps: {a.n}   cases: {len(cases)}\n")
    print(f"{'case':14} {'result':>9}  note")
    passed = 0
    for entry, files, expect, note, spec_expect in cases:
        check = spec_expect if a.spec else expect
        oks = [check(run_case(entry, files, root, a.spec)) for _ in range(a.n)]
        ok = all(oks)
        name = entry.replace("_pfn-", "")
        print(f"{name:14} {sum(oks)}/{a.n} {'PASS' if ok else 'FAIL':>4}  {note}")
        passed += ok
    print(f"\n{passed}/{len(cases)} pass")


if __name__ == "__main__":
    main()
