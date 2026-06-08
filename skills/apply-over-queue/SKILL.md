---
name: apply-over-queue
description: Use to run one expensive, uniform operation across many targets while paying for the operation's large instruction once — a cached, sequential `claude -p` fan-out where every spawn reads the same flattened payload from prompt cache (~0.1×) regardless of queue size. Recursively flattens the referenced skills into a self-contained instruction, normalizes it so the per-item target is abstracted out (or exits naming why it can't), and applies it over the queue. Output is pluggable: side-effecting by default, git-worktree diff-review by flag. Use when the per-item instruction is large and shared and the queue is long enough to amortize a 2-3 call cache warmup — e.g. authoring descriptions over many sessions, or reauthoring many skills under one discipline set.
---

# apply-over-queue

Run a uniform operation over a queue of targets as a sequence of `claude -p` spawns that share one large, identical instruction payload — so the payload is paid for once and served from prompt cache on every later spawn, no matter how long the queue.

Two mechanisms make that hold:

- **Recursive flatten** (`flatten.py`) compiles the entry skills' bodies — and the components they reference, depth-first and deduplicated — into one self-contained instruction with every `/skill` call inlined as a `## section`. No runtime skill dispatch to vary or re-pay for.
- **Cache-safe ordering.** Every spawn reads that identical payload **before** claiming its varying target from the queue. The target enters as tool output, after the cached prefix — so the prefix stays byte-identical across spawns and cache-reuses across separate `claude -p` processes. A target read ahead of the payload would diverge the prefix and bust the cache.

The payload's per-item instruction must therefore be **target-agnostic**. This skill enforces that: it normalizes the raw instruction so the target is abstracted to a queue-supplied role, or exits naming why it can't (`_normalize-operation.md`).

## Arguments

- `--skills <a,b,...>` — entry skills whose flattened, deduplicated bodies join the shared payload
- `--instruction <path>` — the raw per-item instruction (what to do to a target); normalized before flattening
- `--items <x,y,...>` — the target tokens (paths, ids, anything the operation understands)
- `--isolation <none|worktree>` — output handling (default `none`)
- `[--repo <path>]` — git repo to worktree under `--isolation worktree` (default `~/.claude`)
- `[--cwd <path>]` — working dir for spawns under `--isolation none` (default `--repo`)
- `[--add-dir <path>]` — extra dir the spawns may access (repeatable)
- `[--no-exclude-dynamic]` — keep per-machine sections (cwd, git status) in the system prompt; default moves them out for better cross-call cache reuse

## Workflow

1. If `--skills`, `--instruction`, or `--items` is missing: Exit process: usage (the four core arguments).
2. **Normalize the instruction.** Call: `_normalize-operation.md` ({raw} = `--instruction`, {items} = `--items`, {out} = {normalized}).
    - If it exits (the instruction can't be reshaped into a per-target operation): propagate that reason and stop — the user adjusts the instruction and re-runs.
3. **If `--isolation worktree`:** the worktree branches from the repo's `HEAD`, not its dirty tree. If `git -C {repo} status` shows uncommitted changes to the target paths, commit them first; otherwise stop and report.
4. **Run the driver:**

   bash: `python3 scripts/run.py --skills {skills} --operation-file {normalized} --items {items} --isolation {isolation} [--repo {repo}] [--cwd {cwd}]`

   It flattens the payload, seeds the queue, and spawns one `claude -p` per target sequentially (cache-warm), reporting per-spawn cache stats so the amortization is visible.
5. **Review gate** (apply /confirm-shared-intent — never finalize without explicit approval):
    - `worktree`: present the diff (`git -C {repo} diff --stat HEAD..{branch}` plus key files) and the done/claimed/pending counts. On approval `git -C {repo} merge {branch}`; on rejection remove the worktree and delete the branch (the driver prints both commands). Republish if the targets are published skills.
    - `none`: side effects are already live. Present the done/pending counts and point the user at the operation's output (the fresh dir it wrote, or the records it changed) for review.

## Notes

- **Sequential only.** Parallel spawns race the cold cache; run them back-to-back so each refreshes the 5-min cache TTL. Parallelize only on explicit request.
- **One worktree per run, not per spawn** — a per-spawn worktree changes cwd, which diverges the cached prefix and defeats the savings.
- **Amortize the warmup** — the first 2-3 spawns pay near-full price while the cache fills; worth it only when the shared payload is large and the queue long.
- **`none` has no diff-gate.** Its safe pattern is an *idempotent* operation (re-running a target overwrites cleanly) or one that writes into a *fresh output dir* you review before adopting — design the instruction that way before running unattended.
