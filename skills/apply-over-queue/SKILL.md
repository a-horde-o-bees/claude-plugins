---
name: apply-over-queue
description: Use to run one expensive, uniform operation across many targets while paying for its large shared instruction only once — a sequential `claude -p` fan-out where every spawn serves that instruction from prompt cache (~0.1×) regardless of queue length. Worth it when the per-item instruction is large and shared and the queue is long enough to amortize a brief cache warmup — e.g. authoring descriptions across many sessions, or reauthoring many skills under one discipline set. File and directory targets are edited in a staged workspace and land as one reviewed diff; targets that are not files (e.g. DB writes) side-effect directly.
---

# apply-over-queue

Use to run one expensive, uniform operation across many targets while paying for its large shared instruction only once — a sequential `claude -p` fan-out where every spawn serves that instruction from prompt cache (~0.1×) regardless of queue length. Worth it when the per-item instruction is large and shared and the queue is long enough to amortize a brief cache warmup — e.g. authoring descriptions across many sessions, or reauthoring many skills under one discipline set. File and directory targets are edited in a staged workspace and land as one reviewed diff; targets that are not files (e.g. DB writes) side-effect directly.

The queue is **static** (`--items`, a fixed list, each target yielded once) or **dynamic** (`--feeder`, a command yielding the next target until it returns `DONE`). The static list is the degenerate feeder; a feeder that re-yields one target until a pass leaves it unchanged converges it. Either way the operation is invariant and only the target varies — the exact property the cache relies on.

## The cache contract

The saving holds only if **everything in the prompt before the target is byte-identical across spawns**. Three mechanisms guarantee that:

- **Payload assembly** (`flatten.py`) joins the normalized operation with the `--skills` it names, normalized to the **deduplicated union closure**: each named skill's materialized region is stripped, its declaration read, and every unit — named skill or transitive dependency — is emitted exactly once as a `## <name>` section. One self-contained instruction, no runtime skill dispatch to vary or re-pay for, and no duplicate copies when named skills overlap. There is no reference discovery: the operation cites an inlined skill by bare name or its `## <name>` anchor (which resolves to the single copy), and the orchestrator passes the names via `--skills`.
- **Cache-safe ordering.** Every spawn reads that identical payload **before** claiming its varying target from the queue. The target enters as tool output, after the cached prefix — so the prefix stays byte-identical and cache-reuses across separate `claude -p` processes. A target read ahead of the payload would diverge the prefix and bust the cache.
- **Fixed location.** cwd and the `--add-dir` set are part of the prefix, so they too must not vary per target. Under `staged` (default) the driver **copies every file/dir target into one run-local workspace** and runs every spawn with cwd fixed to that workspace — targets from different repos no longer diverge the prefix. Under `none` the cwd is the operation's own fixed home, not the target's.

The payload's per-item instruction must therefore be **target-agnostic**. Normalization enforces that: it reshapes the raw instruction so the target is abstracted to a queue-supplied role — or exits naming why it can't — and resolves its variables to literals.

## Keeping the prefix hot

The prompt cache has a ~5-minute TTL, so a single per-item spawn slower than that would let the shared prefix age out before the next spawn reads it. Empty-target spawns prevent that — both kinds run the **identical stub** with `AOQ_EMPTY=1`, so `queue.py next` returns `NONE` and they re-read the exact cached prefix without claiming work:

- **Warmup** — one upfront, establishing the cache so the first real spawn is already warm: no cold-start race, no special-casing of spawn 1. A failed warmup is fatal — there is no shared cache to build on.
- **Keepalive** — fired every `--warm-interval` seconds (default 240, twice per TTL so a single missed ping is survived) *while a work-spawn runs*, refreshing the cache for the next spawn. A failed keepalive retries once if transient (a server hiccup) and is skipped if decisive (auth, permission); either way it is non-fatal — the next spawn's reading catches any real divergence.

## The cache assertion

The saving is **asserted, not trusted**. The warmup establishes the cached prefix, the first real spawn sets the baseline, and `run.py` requires every later spawn to re-read at least `--cache-floor` of it, aborting the run when the prefix diverges. The measurement is taken at the **prefix boundary** — the one model call right after the spawn reads the shared instruction and *before* the target's body enters context — so the ratio reflects shared-prefix reuse alone, never the per-target payload (which would otherwise inflate the baseline and the per-spawn total alike, and scale with each spawn's tool-call count). The whole-turn cumulative usage is reported as cost but never asserted on.

A silently diverged prefix re-bills the full payload on every spawn; the gate turns that into a loud abort. A spawn whose `usage` can't be read warns that it could not be verified, but does not abort.

**Read an abort by pattern, not by the single reading — ~100% is the healthy norm.** The measurement excludes the per-target payload, so a working chain reads 99–100% every spawn; the 0.95 floor is headroom, not a target. Readings jitter a few points around 100%, including slightly **over** it — the measurement call's `cache_read` includes the assistant's own generated turn, which varies by a few hundred tokens spawn to spawn — and a genuine divergence reads as a multi-thousand-token drop, not a jitter.

- **A one-off sub-floor spawn** is almost always transient: a cache-TTL break on the prefix tail, or an instruction-read turn that generated differently and re-keyed the blocks after it. **Resume the pending queue at the same floor** (the queue is resumable, and a well-formed operation is idempotent) and judge the next spawns — back at ~100% ⇒ transient, move on.
- **Consistently low reads** mean the prefix genuinely varies per spawn — fix the operation, the cwd, or the `--add-dir` set.
- **Never lower `--cache-floor` to make the abort pass** — that converts the loud abort back into the silent re-billing the gate exists to catch.

## Normalization

Turn the raw instruction into a **target-normalized, fully-literal** operation file the queue can drive — or exit naming why it can't. Runs once, before payload assembly; the output is the per-item instruction baked into the cache-warm payload, so a target left un-abstracted here busts the prefix on every spawn, and a variable left unresolved reaches spawns with no dispatcher to bind it.

## The operation contract

A normalized operation operates on **exactly one TARGET per spawn**, supplied at runtime by `queue.py next`. The file opens with the contract, then states the procedure against the abstract target:

```
# Operation

You will be given exactly one TARGET — {target-kind} — emitted by the queue.
Operate only on that TARGET; do not reference, read, or depend on any other item.

{the procedure, phrased against TARGET}

Output: {where output lands, expressed purely as a function of TARGET}
```

## Reshapeability gate

The instruction qualifies only if all four hold. Judge each against the raw instruction and the queue's target tokens; if one fails irreducibly (can't be rewritten to satisfy it), **Exit process** naming the failed criterion and what to change.

1. **Single target axis** — exactly one thing varies per item; the procedure and disciplines are invariant. (Fails: two independent things vary per run and can't collapse to one token.)
2. **Opaque-token-expressible** — the target is one token a queue can yield (path, id, string). (Fails: the "target" is a structured bundle of unrelated inputs.)
3. **Independence** — processing one target needs nothing from another target's output or ordering. (Fails: item N consumes item N−1's result — sequential spawns are independent by design.)
4. **Self-contained output** — where output lands is a function of the target alone. (Fails: output location depends on aggregate or cross-item state.)

The gate protects the cache contract, not correctness of the operation itself — a normalized file can still describe a bad operation. Normalization only guarantees the operation is *shaped* for independent, per-target, cache-warm fan-out.

## Variable resolution

The raw instruction may carry `${CLAUDE_SKILL_DIR}` — the skill-dir binding a normal skill invocation provides and a cold spawn lacks. Normalization is the last point where that binding exists, because the orchestrator knows where it read the instruction from:

- Replace every `${CLAUDE_SKILL_DIR}` with the directory the raw instruction was read from.
- Any other `${VAR}` with no binding in the invocation context: **Exit process** naming it.

`flatten.py` backstops this mechanically: it substitutes `${CLAUDE_SKILL_DIR}` in every skill body it inlines (resolving each skill's own folder), so dispatcher-convention commands stay runnable in the cold spawns, and it refuses to emit a payload where the variable survives — a missed resolution aborts loudly instead of letting a spawn guess a path.

## Output models

- **`staged`** (default) — for file/dir targets. The driver stages each origin into the workspace (`stage.py add`), the spawns edit the copies, and review is a formal `git diff --no-index` of every copy against its origin, applied back to the live origins only on approval. Origins are untouched until apply, the diff stays reliable after repeated modification (a convergence feeder), and a target may be a single file or a whole directory — staging copies whatever the operation reads at runtime.
- **`none`** — for side-effecting operations whose token is not a file to stage (DB writes, external state). No staging, no diff; the operation side-effects directly under its fixed `--cwd`. Its safe pattern is an *idempotent* write, or one into a *fresh output dir* reviewed before adopting.

## Arguments

- `--instruction <path>` — the raw per-item instruction (what to do to a target); normalized before payload assembly.
- `--items <x,y,...>` — **static queue:** the target tokens, each yielded once. Under `staged` these are file/dir paths; under `none`, any token the operation understands.
- `--feeder <cmd>` — **dynamic queue** (instead of `--items`): a command printing the next target token or `DONE[:reason]`; `--dir <rundir>` is appended on each call. The queue feeds until the feeder stops.
- `[--max <n>]` — feeder-mode iteration backstop (default 20); the feeder decides real termination.
- `[--skills <a,b,...>]` — the skills to inline into the payload; the operation cites each by bare name or its `## <name>` anchor. Pass the disciplines the operation applies as named — overlap needs no pruning: the payload is normalized to the union closure, so a skill already inside another named skill's closure, or a dependency two named skills share, is emitted once.
- `[--isolation <staged|none>]` — output model (default `staged`).
- `[--repo <path>]` — where the inlined skills live (skills-root = `repo/<disciplines-subdir>`; default `~/.claude`). Independent of where the targets live.
- `[--cwd <path>]` — `none` only: the operation's fixed home cwd (default `--repo`). Ignored under `staged`, where cwd is forced to the workspace.
- `[--add-dir <path>]` — extra dir every spawn may access (repeatable); the same set on each spawn.
- `[--cache-floor <frac>]` — minimum fraction of the instruction prefix each later spawn must re-read, measured at the prefix boundary (default `0.95`); below it the run aborts.
- `[--warm-interval <secs>]` — seconds between cache-keepalive pings while a work-spawn runs (default `240`; fires twice per ~300s TTL, so one missed ping is survived). Tighten toward `TTL/(misses_to_survive + 2)` for more headroom; keepalives are cheap (~one prefix read each).
- `[--max-spawn-minutes <n>]` — wall-clock ceiling per work-spawn (default `20`); one that outlives it is killed as hung or malformed and counted as a failure.
- `[--continue-on-failure]` — on a work-spawn failure (hung or errored), skip it and continue. Default (off) **halts the chain** so a malformed operation can't spawn N more doomed calls; completed targets are still reported and the pending queue is resumable.
- `[--model <name>]` — model for the `claude -p` spawns (default: the CLI's default).
- `[--no-exclude-dynamic]` — keep per-machine sections (cwd, git status) in the system prompt; default moves them out for better cross-call cache reuse.

## Process

1. If `--instruction` is missing, or neither `--items` nor `--feeder` is given: **Exit process**: usage.
2. **Normalize the instruction** — `{raw}`: the `--instruction` file:
    1. Read `{raw}` and inspect the queue's target tokens to identify the **varying target** and its kind.
    2. Judge each reshapeability criterion pass / reshapeable / irreducible-fail. On any irreducible fail: **Exit process** — `cannot normalize: {criterion} — {what about {raw} violates it} — {how to adjust}`.
    3. Apply [procedure-authoring](#procedure-authoring), [concise-prose](#concise-prose) to:
        1. Rewrite `{raw}` into the operation contract, abstracting every concrete target reference to the TARGET role.
        2. Preserve the procedure and any disciplines or criteria verbatim in intent.
        3. State the output as a function of TARGET: a path derived from it, DB rows keyed by it, a file in a named output dir.
        4. Leave no target literal and no cross-item language ("for each", "all of them", "the rest") in the result.
    4. Resolve variables: `${CLAUDE_SKILL_DIR}` → the directory `{raw}` was read from; any other unbound `${VAR}`: **Exit process** naming it.
    5. `{normalized}`: write the result to a scratch file.
3. Run the driver — bash: `python3 scripts/run.py --operation-file {normalized} <--items {items} | --feeder "{feeder}" [--max {max}]> [--skills {skills}] [--isolation {isolation}] [--repo {repo}] [--cwd {cwd}]`:
    - It assembles the payload (union-closure normalized), stages the targets (under `staged`), warms the cache with one empty-target spawn, then drives the queue sequentially — a static list to exhaustion, or a feeder until it returns `DONE` — spawning one `claude -p` per target with a concurrent keepalive holding the cache hot.
    - It prints each spawn's prefix re-read fraction, and halts the chain on a spawn that falls below `--cache-floor`, hangs past `--max-spawn-minutes`, or errors (unless `--continue-on-failure` is set).
    - On completion it prints a **per-target cache breakdown** — each target's input / cache_create / cache_read / prefix-reread, by origin path under `staged` — so the realized saving is auditable at a glance.
4. **Review gate** — never finalize without explicit approval (confirm-shared-intent):
    - `staged`: the driver prints the per-target diff summary and writes the full patch to `{rundir}/diff.patch`. Present it with the done/claimed/pending counts. On approval run the driver's printed `apply` command (`stage.py … apply` — copies each changed copy back over its origin); on rejection run its `discard` command. Republish if the targets are published skills.
    - `none`: side effects are already live. Present the done/pending counts and point the user at the operation's output — the fresh dir it wrote, or the records it changed — for review.

## Notes

- **Overlapping skill sets are expected, not an error.** A request may name disciplines that contain one another — a host skill and one of its own dependencies, or two hosts sharing a dependency. Pass them to `--skills` as named and prune nothing by hand: normalization emits each unit once, and every bare-name or anchor reference resolves to that single copy.
- **Sequential work, not parallel work.** Work-spawns run one at a time — parallel *work*-spawns would race the cold cache and each cold-write the payload. The only thing running alongside a work-spawn is the keepalive, a cheap empty-target read. Parallelize work-spawns only on explicit request.
- **Amortize the warmup.** The warmup spawn pays near-full price to fill the cache; it is worth it only when the shared payload is large and the queue long enough that the warmup plus the per-spawn reads beat paying cold each time.
- **Pool by home repo only as a fallback.** For an operation that genuinely needs in-repo execution context (e.g. running tests against the live tree) and so can't be staged, group the targets by repo and run one queue per repo, paying a cold cache per pool. The staged workspace is the default and is location-independent.

<!-- flatten-skills START {"deps": ["procedure-authoring", "concise-prose"]} -->

## Dependencies

### procedure-authoring

Apply when authoring an agent procedure with control flow beyond a linear sequence (e.g. conditionals, loops, variable binding, sub-routine calls, error handling) to keep non-trivial procedures readable and unambiguously executable. Not needed for simple sequential steps or lists.

**procedure-authoring sets expectations, not meanings.** This guide is never in the executing agent's context — only the authored procedure is. So a construct cannot *define* a meaning the executor is bound to honor; it can only pick wording whose plain reading **reliably evokes the intended behavior in an agent that has never read this guide.**

The bar is therefore empirical. Each construct below names a behavior and the wording meant to evoke it cold; when wording fails to evoke its behavior, the *phrasing* is the defect to strengthen — never the executor faulted for "misreading" a meaning it was never given. `tests/` measures each construct this way (cold `claude -p`, no guide loaded), so a weak-evoking construct shows as a low hit-rate rather than a surprise in production.

#### Steps

- **`1.`** — a numbered step: one ordered action or construct.
- **`-`** — a bullet: an unordered list or sub-item of a step.
- **Indentation** — scope, 4 spaces per level: a construct ending in `:` opens a block, indented lines are its children, and outdenting to the parent ends it.
- **Grouping subheading** — a label between contiguous steps; numbering continues across them.

A load-bearing step must have a consumer — a step nothing consumes is advisory and often silently skipped under load; bind its finding, write its artifact, or gate a future step or conditional on it.

#### Annotations

- **`—`** (em-dash) — an inline note on a step.
- **`>`** (blockquote) — a standalone note between steps.

An annotation describes, never instructs — keep executable actions out, since an agent runs any instruction it reads wherever it sits.

#### Variables

A variable is written `` `{curly-dashes}` `` — braces inside backticks, a code span, so it sits in standard markdown without renderer or linter collisions — and is visible at any later depth; bind it before referencing it. Inside a larger code span or fence the braces stay bare (`--branch {branch}`).

**`{name}: <block>`** — binds the name to the block's value:

- inline value — `{x}: 42`
- bash stdout — `` {x}: Bash: `cmd` ``
- a call's return — `{x}: Call: [label](#anchor)`
- an applied block's result — `{x}: Apply [lens](#anchor) to: <block>`
- a conditional — `{x}: <a> if <cond> else <b>`
- an indented sub-block — its final assignment or return
- a loop accumulator — `{acc}:` then a `For each:` block that builds it

#### Conditionals

- **`If X:`** — run the block when X is true.
- **`Else if X:`** / **`Else:`** — exclusive chain after an `If`; one branch fires.
- **`If`** / **`If`** (consecutive) — independent; each will fire.

#### Loops

- **`For each {item} in {collection}:`** / **`While X:`** — iterate.
- **`Continue next`** — skip to the next iteration.
- **`Break loop`** — exit the loop.
- **`Go to step N`** / **`Go to step X.Y.Z`** — jump to a step.

#### Invocations

A step delegates only to text already in context. The document is loaded whole, so its own `##` sections are reliable targets; text outside it is not — an un-opened file is invisible, its steps get improvised from the call site instead of run, and the miss appears under real orchestration load even though cold single-task tests pass every wording. No verb choice fixes an absent target.

- **`Call: [label](#anchor)`** — *procedural*: follow the section as steps within the current context.
- **`Apply [label](#anchor) to:`** — *behavioral*: run the indented block **through** the section as a lens — a discipline that shapes *how* the steps execute, not steps themselves. Opens a block; binds when assigned (`{x}: Apply [lens](#anchor) to: <block>`). Listed targets combine into a single lens over the block, interpreted together rather than as successive passes: `Apply [a](#a), [b](#b) to:`.

Text a procedure depends on but does not own is materialized or mechanized, never fetched by the executor:

- **A sibling skill's discipline** — declare it as a flatten dependency; the build inlines it under `## Dependencies`, an ordinary in-document target.
- **Deterministic work** — a script the step runs with `Bash:`. Token relief comes from mechanization, never from making the executor navigate to text stored elsewhere.
- **Steps meant for a fresh context** — a spawn whose directive names the file; the spawned agent starts empty, so reading the file is its first act, not a hop it may skip (see Spawn).
- **Provenance or background** — cite by bare name; a citation is not an invocation, and its miss costs nothing.

Return:

- **`Return to caller`** — hands control back from a called section.
- **`Return to caller:`** — hands a returned result back to the caller (e.g. from a spawned agent).

Never gate an invocation on a judgment the target owns. A condition restating the target's own trigger — *if the entry needs composing fresh*, over a lens whose whole job is deciding that — makes the discipline contingent on the decision it exists to make; the executor skips it and never meets the text that would have flipped its judgment. Invoke unconditionally — the target self-limits.

#### Tools

- **`Bash:`** — runs a shell command: `` `cmd` ``.
- **`Read:`** — loads content without executing it; the read-only counterpart to `Call:`.
- **`Grep:`** — searches file contents.
- **`Glob:`** — matches file paths.
- **`Tool: args`** — any other MCP tool, invoked by name.

#### Spawn

- **`Spawn agent to:`** — delegates to a new agent with its own context. A directive that names a file (`Spawn agent to: read and follow _plan.md`) keeps the caller's context clean; only the agent reads it.
- **`Spawn async agent to:`** — runs agents concurrently; the next outdented step runs after they complete.
- **`Spawn background agent to:`** — runs the agent in the background.
- **Route data around the caller** — a step whose output only a spawned agent consumes runs inside the spawn: the caller passes the directive and bare variables (paths, ids), never content it doesn't itself consume. Content relayed through the caller is read, written, and re-read — paid in the costliest context — and anchors the spawn to the caller's framing besides.

#### Exit

- **`Exit process`** — terminate the whole flow from any depth, unwinding all nested calls.
- **`Exit process:`** — terminate while emitting content.

#### Error handling

- **`If Error:`** — catches failures from its sibling steps above and their descendants; depth determines scope.

#### Arguments

A process declares its input surface CLI-style so an invoker knows what to pass.

| Format | Interpretation |
| --- | --- |
| `<value>` / `[value]` | required / optional value |
| `<x \| y>` / `[x \| y]` | choice — one alternative |
| `[--flag]` | boolean flag |
| `--flag <value>` / `[--flag <value>]` | flag with a value |
| `[--flag <v> ...]` | repeatable flag |

- **`{flag}`** — references a flag's value.

Pair flags with their verb inline — `<verb1 | verb2 --flag <v>>` — rather than at top level. Prefer a positional value for a single required subject; a flag for optional, named, or convention-bound inputs (`--branch`).

#### What belongs in a procedure — the gate on every line

The executor sees only the authored procedure, cold, and runs any instruction it reads wherever it sits — so descriptive prose mixed into the steps both dilutes the actionable signal and risks being executed as a step. Classify every line by the **actionability test**: *would an executor need this to perform the task?*

- **Procedure** (keep) — reasoning, judgment, and contextual sequencing the agent steers; orchestration whose composition depends on intermediate results (section calls, tool invocations, agent spawns); and the user-facing surface (review gates, clarifying questions, error-recovery dialogue).
- **Script** (→ a `Bash:` call or invoked module) — deterministic operations with no agent context: parsing, filtering, aggregation, format conversion, fixed-rule classification. The tell: *could a deterministic function with no agent context produce this result?* Yes → script. Prefer one wherever it suffices; it preserves the agent's focus for the judgment only an agent can supply.
- **Durable structure** (→ the architecture doc) — the shape, boundaries, and external facts a reader needs *before* the steps make sense and that survive a rewrite. Not a step; state it there and link.
- **Why this and not that** (→ the decision record) — a choice made over rejected alternatives. The procedure *runs* the choice; the reasoning belongs there. Link.
- **Derivable** (cut) — anything the executor reconstructs from the steps themselves or the artifacts they touch.

Two misclassifications to catch, each corrected in one direction:

- **Mechanical work stranded in a procedure** — a step doing parsing, filtering, or formatting the agent performs by hand. Tell: a deterministic function could replace it with nothing lost. Push it into a script.
- **Judgment buried in a script** — code branching on context, resolving ambiguity, or deciding what the agent should steer. Tell: a comment hedges ("if ambiguous…", a heuristic, a guessed default). Lift that decision into the calling procedure; leave the script the deterministic part.

### concise-prose

Use to shape prose for any reader (e.g. chat replies, docs, code comments, commit messages, error strings) to minimize overhead without losing meaning — the foundation for all prose output, which other instructions build on or modify.

- **Input contract** — treat all input as intent to recompose, not text to transplant; preserve exact wording only when explicitly directed.
- **Edit license** — rephrase only to cut or correct: a reduction that preserves meaning is improvement; a swap that trades one adequate phrasing for another is churn.
- **Output contract** — length follows information, not prompt length: prose runs as long as the content requires once every directive below is applied.

#### Voice

- Write in active imperative voice, never passive.
- Report facts — no speculation, no hedging.
- Cut ceremonial and narrative overhead (e.g. preambles, cheerleading, self-congratulation).

#### Structure

- Reshape to move meaning into structure — give content the shape that carries it most efficiently, not the shape it arrived in; grouping, ordering, and form express relationships that connective wording spells out, and often cut more than trimming does.
- Trim to shed wording the meaning doesn't need (e.g. modifiers, restatement, filler).
- Keep parallel or comparative content aligned in bullet lists or tables, never collapsed into prose.
- Mark the load-bearing claim and let the rest visibly support it — the reader should find the one thing that matters without weighing every sentence equally.

#### Restraint

- Drop examples or counter-examples unless the content is incomprehensible without them.
- Signal non-exhaustiveness with `(e.g. …)`, in exactly that form — an unqualified list implicitly claims completeness; the qualifier is signal, not filler.
- Quantify only when the number is load-bearing (e.g. a threshold, a tracked discrepancy, a result whose value a decision turns on). A decorative count rots and demands upkeep; state the qualitative fact instead.
- Cross-reference only when the reader must consult the source to understand the current surface.
- Never enumerate content from a linked source — parenthetical summaries are redundant, cherry-picked, and prone to drift.

#### Context leverage

- Assume a capable reader — lean on the vocabulary and general knowledge they hold (e.g. concepts established upstream in this surface, anything a generalist would recognize), and spend words only on non-obvious, domain- or project-specific facts.
- Compact sibling items against each other — in a complementary set (e.g. failure modes, axes, angles), each item describes only what it covers; the surrounding siblings clarify what it excludes. A gap that persists across all siblings is a legitimate hole to address.
- Eliminate duplication within a surface (e.g. a point stated twice, examples making the same point, parallel sections that hedge each other), not across surfaces (e.g. frontmatter, body, metadata, docstring, error codes, error messages) — each surface has distinct readers and triggers; the same content appearing in two is not duplication.

#### Anti-staleness

- Cut commentary on prior states the artifact no longer reflects — the artifact represents current reality only.
- Cut dependence on context that may be absent when the artifact is read (e.g. temporary phases, position labels, pointers to removed siblings) — state each fact directly rather than by reference.

#### Correction

Correct by reduction, not accretion. When a passage reads wrong, sharpen or cut the offending line rather than layer a clarifying sentence over it. A passage that passed review is not proven minimal: the sharper, shorter form is often still unarticulated.

#### Safety checks

These bound the cut decision itself, not a separate review pass.

- **Slim test** — would removing this leave meaning intact for a reader who lacks your context? If yes, it is a candidate for removal pending the remaining checks.
- **Lossless preservation** — carry safety boundaries, corrective guidance, and disambiguation through any cut; a phrase bearing one of these loads stays.
- **Curse of knowledge** — content that feels redundant to the author often carries the only "why" the reader has (e.g. rationale, scope-setting, anti-pattern framing that reads as preamble but makes the rule stick). If content fits a companion surface better, migrate it rather than delete and assume the other surface will catch up.
- **Chesterton's Fence** — do not remove a fence until you know why it was built. Raise to the user when a candidate for removal has no recoverable purpose.

<!-- flatten-skills STOP -->
