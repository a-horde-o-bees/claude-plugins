# PFN tests

Reproducible checks that an agent interprets each PFN construct the way `../SKILL.md` describes — run with **no PFN spec in context**, because the design goal is a notation the model reads correctly unaided. PFN documents only what the model would otherwise get wrong; these tests are the evidence for that, and the sole verification record for the skill.

## Run

```
uv run run.py               # every case, no spec loaded
uv run run.py --spec        # load the PFN spec first, for contrast
uv run run.py -n 3          # repeat each case 3× (behaviour is sampled, not deterministic)
uv run run.py --only while,async   # run named cases (cheap iteration)
```

Needs the `claude` CLI on PATH. Each case materializes a temp skill under `<repo>/.claude/skills/_pfn-*/`, runs `claude -p` from the repo root so it registers, scores a marker log at `/tmp/pfn-test.log`, then removes the fixture. If a run is interrupted, clean up with `rm -rf <repo>/.claude/skills/_pfn-*`.

## Coverage

One case per construct that has distinct runtime behavior, by spec section:

- **Steps / scope** — `scope` (indentation opens/closes blocks)
- **Annotations** — `annotation` (an imperative buried in an annotation → the one case the spec changes)
- **Variables** — `var` (inline), `varbash` (bash stdout), `condassign` (`a if c else b`), `accumulator` (built across a loop)
- **Conditionals** — `ifelse` (exclusive), `indepif` (independent)
- **Loops** — `loop` (`For each` + `Continue`), `while`, `breakloop`, `goto`
- **Invocations / Call** — `callfile`, `callsection`, `callargs` (passed argument), `readnoexec` (`Read:` loads, doesn't execute), `exitreturn` (`Return to caller`)
- **Spawn** — `async` (concurrent spawns join at the outdented step)
- **Exit** — `exitprocess` (full unwind)
- **Error Handling** — `errorhandling` (failure routes to handler, rest skipped)

Every case passes in both modes. Most constructs read identically with or without the spec, so their assertion is the same either way. **`annotation`** is the exception, and the reason PFN carries a rule at all: it asserts **opposite outcomes per mode**. With no spec the model *executes* an imperative buried in an annotation (the marker alone doesn't stop it), so the no-spec assertion expects that execution; `--spec` flips the assertion, because the spec's one sentence ("annotations describe, never instruct") reliably suppresses it. Measured 3/3 each way — the differential is the evidence that this lone rule earns its place in the prose.

Not behavior-tested (pure-format or standard-tool conventions, no distinct runtime effect): bullets, grouping headings, the blockquote annotation marker (same result as the em-dash `annotation` case), `Grep:`/`Glob:`, and the `Arguments` declaration (a skill's signature for its invoker, not control flow).
