---
name: apply-over-queue
description: Use to run one expensive, uniform operation across many targets while paying for the operation's large instruction once — a sequential `claude -p` fan-out where every spawn serves that instruction from prompt cache (~0.1×) regardless of queue size. Targets may live anywhere: file/dir targets are edited in a staged workspace and reviewed as one formal diff before anything lands (default), or the operation side-effects directly for tokens that are not files (e.g. DB writes). Use when the per-item instruction is large and shared and the queue is long enough to amortize a brief cache warmup — e.g. authoring descriptions over many sessions, or reauthoring many skills under one discipline set.
---

# apply-over-queue

Run a uniform operation over a queue of targets as a sequence of `claude -p` spawns that share one large, identical instruction payload — so the payload is paid for once and served from prompt cache on every later spawn, no matter how long the queue.

The queue is **static** (`--items`, a fixed list, each target yielded once) or **dynamic** (`--feeder`, a command yielding the next target until it returns `DONE`). The static list is the degenerate feeder; a feeder that re-yields one target until a pass leaves it unchanged converges it. Either way the operation is invariant and only the target varies — the exact property the cache relies on.

## The cache contract

The saving holds only if **everything in the prompt before the target is byte-identical across spawns**. Three mechanisms guarantee that:

- **Recursive flatten** (`flatten.py`) compiles the referenced skills' bodies — and the components they reference, depth-first and deduplicated — into one self-contained instruction with every `/skill` call inlined as a `## section`. No runtime skill dispatch to vary or re-pay for. **The instruction self-declares its skills:** every `/skill` reference *in the instruction body* is discovered and flattened (latest version), so a well-formed instruction needs no `--skills`. Each inlined body has `${CLAUDE_SKILL_DIR}` substituted with that skill's own directory, so dispatcher-convention commands stay runnable in the cold spawns. Corollary: only `/`-prefix a skill you want flattened — mention any other skill *without* the leading slash (e.g. "apply-over-queue", not "/apply-over-queue"), or its whole tree gets inlined. (File paths are safe — a `/name` inside a path like `…/skills/engaged-time/x.py` is not discovered.)
- **Cache-safe ordering.** Every spawn reads that identical payload **before** claiming its varying target from the queue. The target enters as tool output, after the cached prefix — so the prefix stays byte-identical and cache-reuses across separate `claude -p` processes. A target read ahead of the payload would diverge the prefix and bust the cache.
- **Fixed location.** cwd and the `--add-dir` set are part of the prefix, so they too must not vary per target. Under `staged` (default) the driver **copies every file/dir target into one run-local workspace** and runs every spawn with cwd fixed to that workspace — targets from different repos no longer diverge the prefix. Under `none` the cwd is the operation's own fixed home, not the target's.

The payload's per-item instruction must therefore be **target-agnostic**. Normalization enforces that: it reshapes the raw instruction so the target is abstracted to a queue-supplied role — or exits naming why it can't — and resolves its variables to literals.

The saving is then **asserted, not trusted**. A warmup spawn establishes the cached prefix, the first real spawn sets the baseline, and `run.py` requires every later spawn to re-read most of it, aborting if the prefix ever diverges (`--cache-floor`). The measurement is taken at the **prefix boundary** — the one model call right after the spawn reads the shared instruction and *before* the target's body enters context — so the ratio reflects shared-prefix reuse alone, never the per-target payload (which would otherwise inflate the baseline and the per-spawn total alike, and scale with each spawn's tool-call count). The whole-turn cumulative usage is reported as cost but never asserted on.

### Keeping the prefix hot

The prompt cache has a ~5-minute TTL, so a single per-item spawn slower than that would let the shared prefix age out before the next spawn reads it. Two empty-target spawns prevent this — both run the **identical stub** with `AOQ_EMPTY=1`, so `queue.py next` returns `NONE` and they re-read the exact cached prefix without claiming work:

- **warmup** — one upfront, establishing the cache so the first real spawn is already warm (no cold-start race, no special-casing of spawn 1). A failed warmup is fatal — there is no shared cache to build on.
- **keepalive** — fired every `--warm-interval` seconds (default 240, twice per TTL so a single missed ping is survived) *while a work-spawn runs*, refreshing the cache for the next spawn. Work-spawns stay sequential; the only concurrency is one heavy spawn plus a lightweight ping. A failed keepalive retries once if transient (server hiccup) and is skipped if decisive (auth/permission); either way it is non-fatal — the next spawn's reading catches any real divergence.

## Normalization

Turn the raw instruction into a **target-normalized, fully-literal** operation file the queue can drive — or exit naming why it can't. Runs once, before flattening; the output is the per-item instruction baked into the cache-warm payload, so a target left un-abstracted here busts the prefix on every spawn, and a variable left unresolved reaches spawns with no dispatcher to bind it.

### The operation contract

A normalized operation operates on **exactly one TARGET per spawn**, supplied at runtime by `queue.py next`. The file must open with the contract, then state the procedure against the abstract target:

```
# Operation

You will be given exactly one TARGET — {target-kind} — emitted by the queue.
Operate only on that TARGET; do not reference, read, or depend on any other item.

{the procedure, phrased against TARGET}

Output: {where output lands, expressed purely as a function of TARGET}
```

### Reshapeability gate

The instruction qualifies only if all four hold. Judge each against the raw instruction and the queue's target tokens; if one fails irreducibly (can't be rewritten to satisfy it), **Exit process** naming the failed criterion and what to change.

1. **Single target axis** — exactly one thing varies per item; the procedure and disciplines are invariant. (Fails: two independent things vary per run and can't collapse to one token.)
2. **Opaque-token-expressible** — the target is one token a queue can yield (path, id, string). (Fails: the "target" is a structured bundle of unrelated inputs.)
3. **Independence** — processing one target needs nothing from another target's output or ordering. (Fails: item N consumes item N−1's result — sequential spawns are independent by design.)
4. **Self-contained output** — where output lands is a function of the target alone. (Fails: output location depends on aggregate/cross-item state.)

The gate protects the cache contract, not correctness of the operation itself — a normalized file can still describe a bad operation. Normalization only guarantees the operation is *shaped* for independent, per-target, cache-warm fan-out.

### Variable resolution

The raw instruction may carry `${CLAUDE_SKILL_DIR}` — the skill-dir binding a normal skill invocation provides and a cold spawn lacks. Normalization is the last point where that binding exists, because the orchestrator knows where it read the instruction from:

- Replace every `${CLAUDE_SKILL_DIR}` with the directory the raw instruction was read from.
- Any other `${VAR}` with no binding in the invocation context: **Exit process** naming it.

`flatten.py` backstops this mechanically: it substitutes the variable in every skill body it inlines (it resolves each skill's folder itself) and refuses to emit a payload where `${CLAUDE_SKILL_DIR}` survives — a missed resolution aborts loudly instead of letting a spawn guess a path.

## Output models

- **`staged`** (default) — for file/dir targets. The driver stages each origin into the workspace (`stage.py add`), the spawns edit the copies, and review is a formal `git diff --no-index` of every copy vs its origin, applied back to the live origins only on approval. Origins are untouched until apply, the diff is reliable even after repeated modification (a convergence feeder), and a target may be a single file or a whole directory — staging copies whatever the operation reads at runtime.
- **`none`** — for side-effecting operations whose token is not a file to stage (DB writes, external state). No staging, no diff; the operation side-effects directly under its fixed `--cwd`. Its safe pattern is an *idempotent* write or one into a *fresh output dir* reviewed before adopting.

## Arguments

- `--instruction <path>` — the raw per-item instruction (what to do to a target); normalized before flattening.
- `--items <x,y,...>` — **static queue:** the target tokens, each yielded once. Under `staged` these are file/dir paths; under `none`, any token the operation understands.
- `--feeder <cmd>` — **dynamic queue** (instead of `--items`): a command printing the next target token or `DONE[:reason]`; `--dir <rundir>` is appended on each call. The queue feeds until the feeder stops.
- `[--max <n>]` — feeder-mode iteration backstop (default 20); the feeder decides real termination.
- `[--skills <a,b,...>]` — **optional** supplement: extra skills to flatten that the instruction does not itself `/`-reference. The instruction's own `/skill` references are always discovered and flattened, so a well-formed instruction needs no `--skills`.
- `[--isolation <staged|none>]` — output model (default `staged`).
- `[--repo <path>]` — where the flattened skills live (skills-root = `repo/<disciplines-subdir>`; default `~/.claude`). Independent of where the targets live.
- `[--cwd <path>]` — `none` only: the operation's fixed home cwd (default `--repo`). Ignored under `staged` (cwd is forced to the workspace).
- `[--add-dir <path>]` — extra dir every spawn may access (repeatable); the same set on each spawn.
- `[--cache-floor <frac>]` — minimum fraction of the instruction prefix (measured at the boundary call, before the per-target payload loads) each later spawn must re-read (default `0.95`); below it the run aborts.
- `[--warm-interval <secs>]` — seconds between cache-keepalive pings while a work-spawn runs (default `240`; fires twice per ~300s TTL, so one missed ping is survived). Tighten toward `TTL/(misses_to_survive + 2)` for more headroom; keepalives are cheap (~one prefix read each).
- `[--max-spawn-minutes <n>]` — wall-clock ceiling per work-spawn (default `20`); one that outlives it is killed as hung/malformed and counted as a failure.
- `[--continue-on-failure]` — on a work-spawn failure (hung or errored), skip it and continue. Default (off) **halts the chain** so a malformed operation can't spawn N more doomed calls; completed targets are still reported and the pending queue is resumable.
- `[--model <name>]` — model for the `claude -p` spawns (default: the CLI's default).
- `[--no-exclude-dynamic]` — keep per-machine sections (cwd, git status) in the system prompt; default moves them out for better cross-call cache reuse.

## Process

1. If `--instruction` is missing, or neither `--items` nor `--feeder` is given: Exit process: usage.
2. **Normalize the instruction** (`{raw}` = the `--instruction` file):
    1. Read `{raw}` and inspect the queue's target tokens to identify the **varying target** and its kind.
    2. Run the reshapeability gate:
        - For each criterion, decide pass / reshapeable / irreducible-fail.
        - If any criterion is an irreducible fail: **Exit process** — `cannot normalize: {criterion} — {what about {raw} violates it} — {how to adjust}`.
    3. Rewrite `{raw}` into the operation contract:
        1. Abstract every concrete target reference to the TARGET role.
        2. Preserve the procedure and any disciplines/criteria verbatim in intent.
        3. State the output as a function of TARGET (a path derived from it, DB rows keyed by it, a file in a named output dir).
        4. Apply /procedure-authoring to the procedure and /concise-prose to the whole — no target literals, no cross-item language ("for each", "all of them", "the rest") survive.
    4. Apply Variable resolution: `${CLAUDE_SKILL_DIR}` → the directory `{raw}` was read from; any other unbound `${VAR}`: **Exit process** naming it.
    5. `{normalized}`: write the result to a scratch file.
3. **Run the driver** — bash: `python3 scripts/run.py --operation-file {normalized} <--items {items} | --feeder "{feeder}" [--max {max}]> [--skills {skills}] [--isolation {isolation}] [--repo {repo}] [--cwd {cwd}]`:
    - It flattens the payload, stages the targets (under `staged`), **warms the cache** with one empty-target spawn, then drives the queue sequential — a static list to exhaustion, or a feeder until it returns `DONE` — spawning one `claude -p` per target with a concurrent keepalive holding the cache hot.
    - It prints each spawn's prefix re-read fraction and **aborts if a spawn falls below `--cache-floor`** — the prefix diverged; make the operation target-agnostic and the cwd/`--add-dir` set identical.
    - A work-spawn that hangs past `--max-spawn-minutes` or errors **halts the chain** unless `--continue-on-failure` is set.
    - On completion it prints a **per-target cache breakdown** (each target's input / cache_create / cache_read / prefix-reread, by origin path under `staged`) so the realized saving is auditable at a glance.
4. **Review gate** (apply /confirm-shared-intent — never finalize without explicit approval):
    - `staged`: the driver prints the per-target diff summary and writes the full patch to `{rundir}/diff.patch`. Present it with the done/claimed/pending counts. On approval run the driver's printed `apply` command (`stage.py … apply` — copies each changed copy back to its origin); on rejection run its `discard` command. Republish if the targets are published skills.
    - `none`: side effects are already live. Present the done/pending counts and point the user at the operation's output (the fresh dir it wrote, or the records it changed) for review.

## Notes

- **Sequential work, not parallel work.** Work-spawns run one at a time — parallel *work*-spawns would race the cold cache and each cold-write the payload. The keepalive is the only thing that runs alongside a work-spawn, and it's a cheap empty-target read, not work. Parallelize work-spawns only on explicit request.
- **The cache assertion is the safety net.** A silently-diverged prefix re-bills the full payload every spawn; the per-spawn prefix-reuse gate turns that into a loud abort. A spawn whose `usage` can't be read warns (can't verify) but does not abort.
- **Read an abort by pattern, not by the single reading — ~100% is the healthy norm.** The measurement excludes the per-target payload, so a working chain reads 99–100% every spawn; the 0.95 floor is headroom, not a target. Readings jitter a few points around 100%, including slightly **over** (the measurement call's `cache_read` includes the assistant's own generated turn, which varies a few hundred tokens spawn to spawn) — 99–101% are all the same healthy signal, and a genuine divergence reads as a multi-thousand-token drop, not a jitter.
    - **A one-off sub-floor spawn** is almost always transient — a cache-TTL break on the prefix tail, or the instruction-read turn generating differently and re-keying the blocks after it. **Resume the pending queue at the same floor** (the queue is resumable; a well-formed operation is idempotent) and judge the next spawns: back at ~100% ⇒ transient, move on.
    - **Consistently** low reads mean the prefix genuinely varies per spawn — fix the operation, the cwd, or the `--add-dir` set.
    - Never lower `--cache-floor` to make the abort pass; it converts the loud abort back into the silent re-billing the gate exists to catch.
- **Amortize the warmup** — the warmup spawn pays near-full price to fill the cache; worth it only when the shared payload is large and the queue long enough that the warmup + per-spawn reads beat just paying cold each time.
- **Pool by home repo only as a fallback** — for an operation that genuinely needs in-repo execution context (e.g. running tests against the live tree) and so can't be staged: group the targets by repo and run one queue per repo, paying a cold cache per pool. The staged workspace is the default and is location-independent.
