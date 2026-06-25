# Construct-interpretation tests

Reproducible checks that a construct written in the process-authoring notation **evokes** its intended behavior in an agent reading it cold. The notation is a construction guide for authors; an agent executes a finished flow by **reading it, with no guide in context** — so a construct works only insofar as its wording reliably produces the behavior on its own (`../SKILL.md` § the opening: process-authoring sets expectations, not meanings). These tests run each construct exactly that way (`claude -p`, no guide loaded): a passing case is evidence the wording evokes its behavior; a low hit-rate is evidence the wording is too weak and is the defect to strengthen. Most cases run under a prompt that asks the agent to follow the steps as written; the **wording A/B** (below) runs under a deliberately *neutral* prompt, so the construct's own verb — not the prompt — has to carry the agent into the action.

## Run

```
uv run run.py                          # every case
uv run run.py -n 3                     # repeat each case 3× (behavior is sampled, not deterministic)
uv run run.py --only apply,callskill   # run named cases (cheap iteration)
uv run run.py -n 8 --only fidelity_call,fidelity_execute   # the wording A/B — compare hit-rates
```

Needs the `claude` CLI on PATH. Each case materializes temp skills under `<repo>/.claude/skills/_pfn-*/`, runs `claude -p` from the repo root so they register, scores a marker log at `/tmp/pfn-test.log`, then removes the fixtures. If a run is interrupted, clean up with `rm -rf <repo>/.claude/skills/_pfn-*`.

## Coverage

One case per construct with distinct runtime behavior, by spec section:

- **Steps / scope** — `scope` (indentation opens and closes blocks)
- **Annotations** — `annotation` (the hazard, below)
- **Variables** — `varbash` (bash stdout), `condassign` (`a if c else b`, binding `{n}` inline), `callbind` (a call's return), `accumulator` (built across a loop)
- **Conditionals** — `ifelse` (exclusive chain), `indepif` (independent)
- **Loops** — `loop` (`For each` + `Continue next`), `while`, `breakloop`, `goto`
- **Invocations** — `callvars` (a `Call:` sees the caller's variables — same context, through a `[label](file.md)` component), `callskill` (`Call: /skill` dispatches via the Skill tool), `readnoexec` (`Read:` loads without executing), `apply` (`Apply … to:` runs a block through a skill as a lens), plus the wording A/B `fidelity_call` / `fidelity_execute` and its `fidelity_control` negative control (below); the `[label](#anchor)` target form is exercised by `callbind` and the exit/return cases
- **Spawn** — `async` (concurrent spawns join at the next outdented step)
- **Exit / return** — `exitreturn` (`Return to caller` resumes the caller), `exitprocess` (full unwind)
- **Error handling** — `iferror` (a sibling failure routes to the handler, the rest is skipped)

## The annotation hazard

Every case but one asserts a clean behavior. `annotation` asserts a **hazard**: an imperative buried in an annotation still executes (the marker `EXTRA` appears). The notation cannot prevent it — an agent runs an action it reads, wherever it sits. That measured execution is the evidence behind the guide's authoring advice to keep actions out of annotations: the rule is best-practice for the *author*, not something the guide enforces on the *executor*. So this case verifies the hazard is real, not that any rule suppresses it.

## The wording A/B and its negative control

`fidelity_call` / `fidelity_execute` are identical flows — a file-invocation buried among decoy steps, under the **neutral** prompt — differing only in the verb (`Call:` vs `Execute:`). The call's label looks self-sufficient ("append the line PASS"), so a weak verb could let the agent self-serve and never open the file; but `_record.md` overrides with a different action (`echo REC-Q8Z4`). The marker appears only if the verb pulled the agent into the file, so the hit-rate gap is the measurable evidence — a wording change is judged by whether it moves the rate, not by argument.

**Finding:** at n=6 and n=8, `Call:` and `Execute:` scored identically at 100% — no measurable difference, so the proposed `Execute:` rename was reverted. The arms saturate because a cold, single-task agent with no real prior and no context load just opens the file; this harness cannot reproduce the trained prior + orchestration load that drove the original miss.

**The negative control is what makes that finding trustworthy.** A green-everywhere arm table is ambiguous: it could mean "both verbs work" or "the fixture can't register failure at all." So every discrimination group ships a `control=True` arm that *should* fail to produce the marker — here `fidelity_control` invokes the file with `Read:` (loads without executing), so `REC-Q8Z4` must stay absent. `main` enforces it: a group whose control's marker *appears* — or that ships no control — is flagged **non-discriminating / unvalidated**, and the arm table must not be read as "no effect." A passing control is what licenses the comparison: it proves a difference *could* have shown.

```
uv run run.py -n 8 --only fidelity_call,fidelity_execute,fidelity_control
```

## Not behavior-tested

Pure-format or standard-tool conventions with no distinct runtime effect: bullets, grouping subheadings, the blockquote annotation marker (same hazard as the em-dash `annotation` case), `Grep:` / `Glob:` / `Tool:` (standard tool calls), `Spawn background agent to:` (no synchronous effect to observe), `Exit process:` content emission (the unwind is the `exitprocess` case), and the `Arguments` declaration (a skill's signature for its invoker, not control flow).
