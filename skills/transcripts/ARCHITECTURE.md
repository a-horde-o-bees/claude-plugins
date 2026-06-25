# Timeline model — ARCHITECTURE

The mechanical reconstruction of **engaged time** from raw Claude Code transcripts — the source of truth for splitting machine time into **active** and **idle**, per-session and per-project. It reads the raw transcript DB (every JSONL line, nothing interpreted away) and derives active-processing intervals from record *signatures* alone. What a consumer does with the active/idle signal (billing, capacity, focus metrics) is the consumer's concern. The shaping rationale behind each mechanism, and the alternatives rejected, lives in `DECISIONS.md`.

## The four tiers

A strict containment hierarchy: each tier groups the one below; time is measured on time-blocks and rolls up.

| Tier | Definition |
| --- | --- |
| **event** | One JSONL row — one record. The atom. |
| **time-block** | A contiguous span of active processing, bounded by a START and the next END. The unit time is *measured* on. |
| **exchange** | A run of consecutive time-blocks anchored by one typed prompt — the work that prompt set in motion, across any mid-exchange idle. The unit time is *attributed* to. |
| **topic** | A set of related exchanges sharing a focus — the report filter key. |

## Engaged time — active vs idle

Engaged time is the model's quantity: the intervals the machine is provably **active**, separated from **idle** by record signature alone — machine-evidenced, reproducible, deliberately conservative. Active is a time-block (a START→END pairing); idle is everything else. Three kinds of idle are excluded *because they are not foreground-active machine time*, not by any downstream policy:

- **wait / suspend** — gaps where nothing runs (between turns, parked on a prompt).
- **operator reading / thinking / composing** — real human time, but not machine-evidenced; indistinguishable from idle by signature, so uncounted.
- **background machine runtime** — work completing outside the foreground turn (backgrounded deploys/audits) — a distinct, separately-identifiable category, not foreground-active.

The measure is **machine-evidenced and wait-free**, every active/idle call **evidence-derived per instance**, never guessed. How a consuming project *leverages* the signal — billing engaged time at a rate, capacity planning, focus metrics — is the consumer's policy, not the model's. Rejected alternatives (estimating operator compose time; the measure choice): `DECISIONS.md`.

## Line detection — the mechanism under time-blocks

A time-block is found not by content but by **lines**: a line is a horizontal marker at one event's row whose *role* is fixed by that event's signature. Three roles:

- **START** (blue) — the beginning of a time-block.
- **STOP** (red) — the end of an exchange. May appear mid-exchange, but is then *consumed by a break* (below).
- **BREAK** (yellow) — a **pair** of lines marking idle in the *middle* of an exchange: the prior block's END half + the next block's START half. The exchange continues across it.

### Class → role

The pairing role (`_role_of`, `swimlane_timeline.py`) — a **signature→role** map, not a list of `classify()` outputs: two rows key off something other than a class (`turn_duration` is a record *property*; `user-response` is a `tool_result` reclassified in `build()`). The distinguishing signature is given per row. (Internal class names; UI display names are in `swimlane_server_ui.md`.)

| Signature | Role | Distinguishing test |
| --- | --- | --- |
| class `prompt` | START | `type=user` with real text, OR a typed `<command-name>`; excludes isMeta / empty / `<task-notification>` / `[Request interrupted`. Opens a block, anchors an exchange. |
| property `closure="turn"` | STOP | `type=system AND subtype=turn_duration` — **not a class**; the record's closure property. The machine halted (turn end, AskUserQuestion wait, notification park). |
| class `user-interrupt` | STOP | `type=user`, text starts `[Request interrupted` (Escape). A hard stop of machine contiguity. |
| reclass `user-response` | BREAK | a `tool_result` whose originating `tool_use.name ∈ {AskUserQuestion, ExitPlanMode, EnterPlanMode}` — human-authored, reclassed in `build()` (not `classify()`). The pre-gap is human decision time, so it splits the block without ending the exchange. |
| class `thinking` / `tool_use` / `text`, resuming after a STOP | BREAK (override) | the FIRST agent re-engagement with no interceding START (role `activity`; **inert mid-block**). The trigger set, and why `text` is in it, are in `DECISIONS.md`. |
| class `queue-operation` | *none* | enqueue/dequeue/remove/popAll — an attribution border (a prompt typed mid-run), never an activity break. The dequeued prompt delivers as an ordinary `prompt` and carries the START. |
| everything else | *none* | mid-block `thinking`/`tool_use`/`text`, non-interactive `tool_result`, `attachment`, `system`, `other` — fall inside a block, never bound one. |

Sidechain (sub-agent) records carry no role — their time rides on the main-chain Agent tool's returning `tool_result` (`DECISIONS.md`).

### The override rule — STOP consumed by BREAK

When agent activity (a `thinking`, `tool_use`, or `text` record) resumes after a STOP with **no interceding START**, the agent continued the same exchange without a new prompt. Rather than open a fresh START (which would split one exchange into two), this is a BREAK that **overrides the stop** (`_sweep_points`): the resuming dot gets a yellow break line (a START for pairing), and the preceding stop dot gets an *additional* yellow line while keeping its red. A single dot can thus own multiple lines.

## Time-blocks and coverage

Pairing (`_pair_points`): walk the role points in time order; pair each START with the next END that has no START between → one **time-block** of `end_t − start_t` seconds. A START with no following END, or an END with no open START, is **stranded** — ignored for time but counted (a non-zero stranded count is a signature the line rules don't yet cover, never noise to wave off).

**Coverage** = Σ time-block durations over a record set. **Span** = last event ts − first. **Gap** = span − coverage (the idle the breaks and unpaired stretches carved out). These three are the per-set accounting readout. Coverage is the engaged-time measure; it is invariant to how blocks are later grouped into exchanges (exchanges only partition the same blocks), so the exchange tier changes *attribution*, never the total.

**Sub-second ms.** Display lays out one row per wall-clock second (`ymap_compact`, so bursts collapse and relationship arcs stay flat); the duration math keeps full ms. Rationale and the rejected truncate-the-math measurement: `DECISIONS.md`.

## Exchange

An **exchange** is the run of consecutive time-blocks from one `prompt`-START up to the next *non-overridden* STOP. Its boundary is a **`prompt`-START that follows a non-overridden stop** — not just any START, because the START set is broader than prompts (break-starts and resume-starts continue an exchange rather than opening one). Every exchange is anchored by exactly one typed prompt; the blocks after its first are opened by breaks/resumes within it.

- **Time** attributed per exchange = Σ its member time-blocks' coverage, landing on the exchange's own day.
- **Coverage invariance**: Σ exchange times = total coverage (exchanges partition the blocks). Verified across the corpus (`materialize_exchanges` vs `segment_coverage`, 0 mismatches).

**The dequeue fold.** A prompt typed *while the agent is running* is enqueued mid-run, and its fate is mechanically one of two:

- **Consumed interjection** (`enqueue`→`remove`, never delivered): the running turn answered it *inline*. It has **no `prompt`-START at all**, so it never opened an exchange — it **folds into the running exchange**, and its *text* (the enqueue content) belongs to that exchange's content and authored description. Rendered as the `△`/`▲` triangle pair.
- **Delivered queued prompt** (`enqueue`→`dequeue`→delivered as a `prompt`-START): it became a real prompt event and **opens its own exchange**, like any prompt. Rendered as the `○`/`●` circle pair.

(Detector: `Corpus._mark_interjections` — the `_consumed` enqueue + its `_consumed_remove`. The fold is decided by fate, not by inspecting the enqueue: `DECISIONS.md`.)

## Descriptions and topics

Each exchange carries a persistent **description** — a per-exchange line (scope + role, no mechanics) authored via `/description-authoring`, keyed by its opening typed prompt's canonical UUID (stable across ceiling changes, turn boundaries, and rebuilds). Its input is the opening prompt + every consumed-interjection text the exchange folds in + the agent's response; it regenerates when those inputs change.

A **topic** groups related exchanges by shared focus (many exchanges → one topic), assigned in one global pass over the descriptions from a fixed vocabulary. It is the report filter key and the cross-session rollup unit, carrying what a consuming project bills on; the model stores no topic policy.

Storage is a separate persistent annotation store (`annotations.db`), keyed by UUID and joined at read/report time. The raw DB is a regenerable cache, so the two are distinct files (`DECISIONS.md`).

## Prompt-queue resolution

The prompt queue holds messages waiting to reach the agent — user prompts typed mid-run (interjections) and harness-injected background-task completion notifications. Its records (`queue-operation`, `operation` ∈ enqueue/dequeue/remove/popAll) carry **no `uuid`**, so the canonical-uuid forest never places them; they attach to a segment by line locality (`Corpus._attach_orphan_lines`). Their relationships are *not* readable from adjacency alone, hence the mechanical resolution here.

**Only `enqueue` carries identity** — the queued `content`, plus the embedded `<task-id>` / `<tool-use-id>` for a notification. The consuming ops carry nothing (`popAll` carries one `content` snapshot, its own submitted message), so every reconstructed relationship anchors on the enqueue.

| op | carries | meaning |
| --- | --- | --- |
| enqueue | `content` (+ ids for notifications) | a message entered the queue |
| dequeue | — | the head was **delivered** to the agent |
| remove | — | the head was **discarded** (never delivered) |
| popAll | one `content` snapshot | the queue was **flushed** — its own message delivered, the rest discarded |

Enqueue content splits three ways and `classify` labels the dot accordingly (`enqueue:notification` / `enqueue:prompt` / `enqueue:loop`): a `<task-notification>` (with task/tool ids), a typed user prompt (a mid-run interjection), or a `<<…>>` autonomous-loop sentinel. There is no type flag — content *is* the discriminator. Pairing is eager-FIFO and delivery is content-gated; timestamp position is never used (`DECISIONS.md`).

**The resolution — dissolve to direct bridges** (`Corpus._queue_relationships`, thick amber arcs). Once each chain is reconstructed (spawn → consume → deliver), the queue ops are **dissolved**: the kept dots are the **fate-coded prompt markers** in the prompt lane — an emitted prompt's enqueue (`○`→`●`) and a consumed interjection's enqueue + remove (`△`→`▲`); notification enqueues and the remaining ops are dropped (the queue column disappears). One `qbridge` edge connects the two ends a chain actually bridged:

| chain | bridge drawn | when |
| --- | --- | --- |
| queued prompt **emitted** | `○` enqueue → `●` delivered prompt | dequeued (consume + deliver collapse; the enqueue re-attaches to the real prompt) |
| **consumed interjection** | `△` enqueue → `▲` at the `remove` | removed AND content delivered nowhere — the running turn answered it inline (`_mark_interjections`) |
| background **notification** | tool_use → delivered notification | spawn id matched **and** delivered |
| slash-command / Monitor (no `tool_use`) / cross-boundary | **nothing** | a chain that doesn't fully bridge draws no edge |

**Delivered notifications are not prompts.** A delivered task-notification is a `user` record whose content starts `<task-notification>`; `classify` routes it to `system`/`task-notification`, *out of* the prompt START set, rewind detection, and prompt counts (`DECISIONS.md`).

## Segments — the flat rail

The interactive view organizes each session as a **flat rail of segments** (`branch_tree.py`). The one live thread is split into segments at **re-emission boundaries** (resume/compaction) and at **rewinds** (a same-file fork: the earliest path stays inline as the original continuation, the later paths split off as `rewind` segments). Everything rides one rail in ts order; there are no nested branches. A **segment** is a *structural* unit (an era of the thread), orthogonal to the *temporal* tiers — its duration column is just its coverage (Σ its time-blocks), and a segment may hold several exchanges. Per-segment geometry the UI renders is `segment_geometry`; a cross-segment relationship arc drops (its endpoint lives in another segment — the re-attach point is recorded in the segment's `from`). Why a flat rail and not a deep tree: `DECISIONS.md`.

## Where the model lives (code)

The model is the single source of truth; the renderers (static HTML, live server) are dumb consumers of its geometry. Read the module docstrings for the authoritative detail.

- `raw_db.py` — ingest: JSONL → the raw scratch DB (every line, `is_replay`/`is_compact_summary` marked, nothing dropped).
- `swimlane_timeline.py` — the model + geometry: `classify` (event → class), the line/role functions (`_role_of`, `_role_items`, `_sweep_points`), pairing + coverage (`_pair_points`, `segment_coverage`), exchange materialization (`materialize_exchanges`), and the ordinal segment geometry (`segment_geometry`). Also the standalone static render.
- `branch_tree.py` — the session segments / flat rail (`session_trees`, `_node`).
- `swimlane_server.py` — the interactive shared-column tree server; `swimlane_server_ui.md` documents its UI.
- `exchanges.py` — the annotation store CLI over `annotations.db`.
