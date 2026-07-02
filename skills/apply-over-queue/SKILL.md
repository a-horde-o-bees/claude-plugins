---
name: apply-over-queue
description: Use to run one expensive, uniform operation across many targets while paying for the operation's large instruction once — a cached, sequential `claude -p` fan-out where every spawn reads the same flattened payload from prompt cache (~0.1×) regardless of queue size. Recursively flattens the referenced skills into a self-contained instruction, normalizes it so the per-item target is abstracted out (or exits naming why it can't), and applies it over the queue. Targets may live anywhere: file/dir targets are staged into one workspace and reviewed as a formal diff (default), or `none` for side-effecting ops like DB writes. Asserts the cache saving on every spawn and aborts if the prefix diverges. Use when the per-item instruction is large and shared and the queue is long enough to amortize a brief cache warmup — e.g. authoring descriptions over many sessions, or reauthoring many skills under one discipline set.
---

# apply-over-queue

Run a uniform operation over a queue of targets as a sequence of `claude -p` spawns that share one large, identical instruction payload — so the payload is paid for once and served from prompt cache on every later spawn, no matter how long the queue.

The saving holds only if **everything in the prompt before the target is byte-identical across spawns**. Three mechanisms guarantee that:

- **Recursive flatten** (`flatten.py`) compiles the referenced skills' bodies — and the components they reference, depth-first and deduplicated — into one self-contained instruction with every `/skill` call inlined as a `## section`. No runtime skill dispatch to vary or re-pay for. **The instruction self-declares its skills:** every `/skill` reference *in the instruction body* is discovered and flattened (latest version), so a well-formed instruction needs no `--skills`. Corollary: only `/`-prefix a skill you want flattened — mention any other skill *without* the leading slash (e.g. "apply-over-queue", not "/apply-over-queue"), or its whole tree gets inlined. (File paths are safe — a `/name` inside a path like `…/skills/transcripts/x.py` is not discovered.)
- **Cache-safe ordering.** Every spawn reads that identical payload **before** claiming its varying target from the queue. The target enters as tool output, after the cached prefix — so the prefix stays byte-identical and cache-reuses across separate `claude -p` processes. A target read ahead of the payload would diverge the prefix and bust the cache.
- **Fixed location.** cwd and the `--add-dir` set are part of the prefix, so they too must not vary per target. Under `staged` (default) the driver **copies every file/dir target into one run-local workspace** and runs every spawn with cwd fixed to that workspace — targets from different repos no longer diverge the prefix. Under `none` the cwd is the operation's own fixed home, not the target's.

The payload's per-item instruction must therefore be **target-agnostic**. This skill enforces that: it normalizes the raw instruction so the target is abstracted to a queue-supplied role, or exits naming why it can't (`_normalize-operation.md`). The cache saving is then **asserted, not trusted**: a warmup spawn establishes the cached prefix, the first real spawn sets the baseline, and `run.py` requires every later spawn to re-read most of it. The measurement is taken at the **prefix boundary** — the one model call right after the spawn reads the shared instruction and *before* the target's body enters context — so the ratio reflects shared-prefix reuse alone, never the per-target payload (which would otherwise inflate the baseline and the per-spawn total alike, and scale with each spawn's tool-call count). The run aborts if that prefix ever diverges (`--cache-floor`); the whole-turn cumulative usage is reported as cost but never asserted on.

**Keeping the prefix hot.** The prompt cache has a ~5-minute TTL, so a single per-item spawn slower than that would let the shared prefix age out before the next spawn reads it. Two empty-target spawns prevent this — both run the **identical stub** with `AOQ_EMPTY=1`, so `queue.py next` returns `NONE` and they re-read the exact cached prefix without claiming work:

- **warmup** — one upfront, establishing the cache so the first real spawn is already warm (no cold-start race, no special-casing of spawn 1). A failed warmup is fatal — there is no shared cache to build on.
- **keepalive** — fired every `--warm-interval` seconds (default 240, twice per TTL so a single missed ping is survived) *while a work-spawn runs*, refreshing the cache for the next spawn. Work-spawns stay sequential; the only concurrency is one heavy spawn plus a lightweight ping. A failed keepalive retries once if transient (server hiccup) and is skipped if decisive (auth/permission); either way it is non-fatal — the next spawn's reading catches any real divergence.

The queue is **static** (`--items`, a fixed list, each target yielded once) or **dynamic** (`--feeder`, a command yielding the next target until it returns `DONE`). The static list is the degenerate feeder; a feeder that re-yields one target until a pass leaves it unchanged converges it. Either way the operation is invariant and only the target varies — the exact property the cache relies on.

## Output models

- **`staged`** (default) — for file/dir targets. The driver stages each origin into the workspace (`stage.py add`), the spawns edit the copies, and review is a formal `git diff --no-index` of every copy vs its origin, applied back to the live origins only on approval. Origins are untouched until apply, the diff is reliable even after repeated modification (a convergence feeder), and a target may be a single file or a whole directory — staging copies whatever the operation reads at runtime.
- **`none`** — for side-effecting operations whose token is not a file to stage (DB writes, external state). No staging, no diff; the operation side-effects directly under its fixed `--cwd`. Its safe pattern is an *idempotent* write or one into a *fresh output dir* reviewed before adopting.

## Arguments

- `[--skills <a,b,...>]` — **optional** supplement: extra skills to flatten that the instruction does not itself `/`-reference. The instruction's own `/skill` references are always discovered and flattened, so a well-formed instruction needs no `--skills`.
- `--instruction <path>` — the raw per-item instruction (what to do to a target); normalized before flattening.
- `--items <x,y,...>` — **static queue:** the target tokens, each yielded once. Under `staged` these are file/dir paths; under `none`, any token the operation understands.
- `--feeder <cmd>` — **dynamic queue** (instead of `--items`): a command printing the next target token or `DONE[:reason]`; `--dir <rundir>` is appended on each call. The queue feeds until the feeder stops.
- `[--max <n>]` — feeder-mode iteration backstop (default 20); the feeder decides real termination.
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

1. If `--instruction` is missing, or neither `--items` nor `--feeder` is given: Exit process: usage. (`--skills` is optional — the instruction self-declares its skills.)
2. **Normalize the instruction.** Call: `_normalize-operation.md` ({raw} = `--instruction`, {items} = `--items`, {out} = {normalized}).
    - If it exits (the instruction can't be reshaped into a per-target operation): propagate that reason and stop — the user adjusts the instruction and re-runs.
3. **Run the driver:**

   bash: `python3 scripts/run.py --skills {skills} --operation-file {normalized} <--items {items} | --feeder "{feeder}" [--max {max}]> [--isolation {isolation}] [--repo {repo}] [--cwd {cwd}]`

   It flattens the payload, stages the targets (under `staged`), **warms the cache** (one empty-target spawn), then drives the queue sequential — a static list to exhaustion, or a feeder until it returns `DONE` — spawning one `claude -p` per target with a concurrent keepalive holding the cache hot, printing each spawn's prefix re-read fraction, and **aborting if a spawn falls below `--cache-floor`** (the prefix diverged — make the operation target-agnostic and the cwd/`--add-dir` set identical). A work-spawn that hangs past `--max-spawn-minutes` or errors **halts the chain** unless `--continue-on-failure` is set. On completion it prints a **per-target cache breakdown** (each target's input / cache_create / cache_read / prefix-reread, by origin path under `staged`) so the realized saving is auditable at a glance.
4. **Review gate** (apply /confirm-shared-intent — never finalize without explicit approval):
    - `staged`: the driver prints the per-target diff summary and writes the full patch to `{rundir}/diff.patch`. Present it with the done/claimed/pending counts. On approval run the driver's printed `apply` command (`stage.py … apply` — copies each changed copy back to its origin); on rejection run its `discard` command. Republish if the targets are published skills.
    - `none`: side effects are already live. Present the done/pending counts and point the user at the operation's output (the fresh dir it wrote, or the records it changed) for review.

## Notes

- **Sequential work, not parallel work.** Work-spawns run one at a time — parallel *work*-spawns would race the cold cache and each cold-write the payload. The keepalive is the only thing that runs alongside a work-spawn, and it's a cheap empty-target read, not work. Parallelize work-spawns only on explicit request.
- **The cache assertion is the safety net.** A silently-diverged prefix re-bills the full payload every spawn; the per-spawn prefix-reuse gate turns that into a loud abort. A spawn whose `usage` can't be read warns (can't verify) but does not abort.
- **Amortize the warmup** — the warmup spawn pays near-full price to fill the cache; worth it only when the shared payload is large and the queue long enough that the warmup + per-spawn reads beat just paying cold each time.
- **Pool by home repo only as a fallback** — for an operation that genuinely needs in-repo execution context (e.g. running tests against the live tree) and so can't be staged. The staged workspace is the default and is location-independent; pooling trades that for in-repo context, paying a cold cache per pool.
