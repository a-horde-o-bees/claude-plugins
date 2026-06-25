# Timeline model — DECISIONS

Load-bearing choices and the alternatives they beat — the rationale that keeps settled questions settled. `ARCHITECTURE.md` describes the mechanism as it *is*; this file records *why*, so a later change can't quietly reintroduce a discarded approach. Build status and remaining work live in the plan, not here.

## Engaged time derives from record signatures, never hand-labeled

Time-blocks are found by event *signature* (class plus closure property), never by reading content or any manual annotation — so the result is reproducible from the raw transcript and carries no hand-judgement. **Rejected:** content-based or hand-tuned interval labeling — unreproducible and unauditable.

## START is a typed prompt only; an interrupt is a STOP

An exchange opens only on a *typed* `prompt` (`is_typed_prompt`: real user text, or a typed `<command-name>`), excluding harness-authored `user-meta`, compact summaries, delivered `<task-notification>`s, and `[Request interrupted` markers. An interrupt is a STOP, not a START. **Rejected:** the legacy `user_msg`-to-`user_msg` boundary — it counts harness-meta and interrupts as `user_msg`, so they read as exchange starts (446 delivered notifications alone polluted the START set).

## Sub-second ms: truncate for display, keep full for duration math

The harness writes same-second bursts with ms often inverted versus write/parent order, so ms is unreliable sub-second. Display lays out one row per wall-clock second (`ymap_compact`); the duration math keeps full ms. **Rejected:** truncating ms in the math too — measured to undercount coverage 0.07% (8.8 min / 196 h, a systematic round-down at every block edge) for no gain.

## A resume after a STOP is a BREAK; the trigger is thinking, tool_use, OR text

The first agent re-engagement after a STOP with no interceding START continues the same exchange — a break that overrides the stop — rather than opening a new one. The trigger set is `thinking` / `tool_use` / `text`. **`text` is required:** a combined thinking+text assistant record classes as `text` (not `thinking`), so without it a think-and-reply resume is missed (measured +892.9s / +24 blocks corpus-wide). **Rejected:** `thinking`-only (misses text-first and combined resumes); `tool_result` as a trigger (that is the background task *returning*, not the agent re-engaging — its run time is excluded by design).

## The dequeue fold is decided by fate, not by inspecting the enqueue

A prompt enqueued mid-run folds by what *happened* to it: consumed (`enqueue`→`remove`, never delivered) has no `prompt`-START, so it folds into the running exchange and its text joins that exchange's content; delivered (`enqueue`→`dequeue`→`prompt`) opens its own exchange. **Rejected:** a heuristic on the enqueue itself — fate is mechanical and exact.

## Queue pairing is eager-FIFO plus content-gated; timestamp position is never used

Anonymous consuming ops (dequeue/remove/popAll) pair to the oldest pending enqueue (eager FIFO); a delivery is re-confirmed by content (whitespace-normalized, full length). **Rejected:** ts / next-op adjacency — ts desyncs under a backlog and can't say which queued item an op touched. Eager-FIFO chain order is reliable, and content gating means a wrong pairing can never invent a bridge. (Queue depth-1 at ~97% and zero FIFO underflow over 1999 ops corroborate but are not load-bearing.)

## Delivered notifications are reclassified out of the prompt set

A delivered `<task-notification>` is a `user` record but is classified `system`, removing it from the START set, rewind detection, and prompt counts. **Rejected:** treating it as a prompt — it read as an exchange start (446 corpus-wide).

## raw.db and annotations.db are separate files

The raw cache (regenerable, hundreds of MB) and the authored annotation store (irreplaceable, KB) live as two files in one working dir. **Rejected:** one fused DB — it entangles irreplaceable authored state inside a disposable cache, so a `reset`, schema bump, or backup can't treat them by their true lifecycles.

## Annotations key on the prompt UUID, not position

An exchange's description/topic key is its opening prompt's canonical UUID — stable across ceiling changes, turn boundaries, and cache rebuilds. **Rejected:** the positional `(session, exchange#)` key — fragile; any re-derivation shifts it.

## The interactive view is a flat rail of segments, not a deep branch tree

The one live thread splits into segments at re-emission boundaries (resume/compaction) and rewinds, all on a single ts-ordered rail. **Rejected:** walking every alternative history as a deep tree — too deep to diagnose active work.

## Sub-agent records carry no time role

A sub-agent run is superseded by its main-chain Agent tool dots, whose returning `tool_result` carries the run's duration. **Rejected:** pairing time inside the sub-agent transcript — double-counts against the main-chain tool call.

## Operator compose time is not counted as active

Operator reading/thinking/composing is real human time but not machine-evidenced — it can't be distinguished from idle by signature, so it isn't counted as active. **Rejected:** estimating it — a truncated-mean typed-prompt gap climbs monotonically with any ceiling (72s@5m → 376s@4h, no plateau), so any compose estimate is a chosen number, not a measurement.

## Background machine runtime is a distinct category, not foreground-active

Work completing outside the foreground turn (backgrounded deploys/audits) is separately identifiable via task-notification ↔ tool_use pairing, but is **not** foreground-active time, so it doesn't enter coverage. **Rejected:** folding it into the active measure — backgrounded kickoffs touch only their ~0.1h of foreground wall-clock, foreground Bash is harness-capped, and the wall-clock is stall-inflated; counting it would need an evidence-derived runtime pass, not the foreground signal.

## The active measure is machine-evidenced and wait-free

Among recorded alternatives, marker-windows (prompt → last turn) include operator waits/suspends, and recorded per-turn `durationMs` is blind to work completing outside turns; the chosen measure is the one that is both machine-evidenced *and* wait-free. Smoothing (the gap adjustments) is a continuity device only — never widened to absorb operator think-time.

## Membership lanes overlay the event view; they never re-spine it

The live view stays a per-record event stream; the coarser annotation streams (exchange, focus-thread) ride it as two thin **membership lane** columns (left of the class columns), one filled cell per row colored by the record's exchange (alternating shade) and focus-thread (topic hue), with the descriptions surfaced on selection. Per-record exchange membership is the `materialize_exchanges` owner bisect (ts interval → opening anchor uuid); thread + description join on that **anchor uuid globally**, so no file→root resolution is needed even though threads are per-root. **Rejected:** re-spining the rail to root and rendering exchange/thread *contents* in parallel panels — costs horizontal space and a tree re-org for correlation that two aligned bars + an on-select detail already give; a broken thread bar (non-contiguous membership) is accepted, not engineered away.

## The lane render is policy-neutral — every topic a spread-palette colour, none privileged

The viz reads the topic *names* the consumer assigned (annotation data) and colors each from a maximally-distinct, evenly-spaced hue palette sized to the next multiple of 3 ≥ the topic count (spare slots unused); a multi-topic thread shows one stripe per topic. The **Stats** tab filters topics one by one, and the filter **drives the engaged-time totals** — the per-exchange measures sum only over threads with a shown topic (ANY-match), so toggling off all but the billable topics simply *shows the bill*. It embeds no vocabulary and **draws no billable/non-billable line** — every topic is just a colour, equally filterable. **Rejected:** hardcoding the project's vocabulary, graying "non-billable" topics, or a billable highlight even as a launch arg — that imports the consumer's billing policy into the neutral measurement layer; per-topic filtering gives the same isolation (and generalizes `report.py`'s billable measure into the live view) without the policy. **Rejected:** a name-hash hue — collisions land near-identical colours by chance; the spread palette guarantees separation.

## Only one model is the live engaged-time source at a time

The timeline model supersedes the legacy primary-DB `exchange_s` model; they never both claim to be the live source. On graduation the legacy path quarantines. (The graduation steps live in the consuming project's plan.)
