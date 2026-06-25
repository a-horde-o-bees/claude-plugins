# Synthesize focus-threads (the daily-breakdown + billing lineage)

Coalesce each **root's** per-exchange descriptions into focus-threads, by fanning the per-root unit `_synthesize-root.md` out over `/apply-over-queue`. This file is the parent orchestration; `_synthesize-root.md` is the per-item unit it runs. One agent per whole ROOT — the visualization's connected work-tree (one session, or several files linked by a cross-file resume) — so the root's full context informs the threads and a single objective is never fragmented across a resume boundary. Cached content-addressed in `annotations.db` `root_thread`.

Threads are the report's unit of BOTH narrative (the daily breakdown lists one bullet per thread) and billing (an exchange bills iff it is a member of a thread whose topic is billable). So this pass is not narrative-only — get the membership right.

## When to run

After descriptions are current, before the topic pass and before rendering. Re-run any time descriptions change — the cache is content-addressed, so only changed roots re-synthesize.

## Why apply-over-queue

The shared instruction — the coalescing rule plus `/description-authoring` + `/concise-prose` — is large and identical on every spawn, so `/apply-over-queue` pays for it once and serves it from prompt cache on every later root. The per-root unit reads and writes only its own root, so spawns never contend. The same pattern as the per-exchange description fan-out (`_annotate-corpus.md`).

## Process

1. **Build the queue** — the roots needing (re)synthesis:

    ```
    uv run exchanges.py roots --pending
    ```

    Each line is a full root id whose threads are not yet cached (or whose descriptions changed, re-keying the root). Empty → nothing to do. `--items` wants full ids, which this emits.

2. **Fan out** — invoke `/apply-over-queue` with the per-root unit as instruction:

    ```
    /apply-over-queue \
      --instruction /home/dev/.claude/skills/transcripts/_synthesize-root.md \
      --items <full root ids, comma-separated> \
      --isolation none \
      --cwd /home/dev/.claude/skills/transcripts \
      --add-dir /home/dev/.claude/a-horde-o-bees/transcripts
    ```

    - `--isolation none` — the side effect is a SQLite write to `annotations.db`, outside any repo.
    - **Sequential only** — `annotations.db` is one SQLite writer, and sequential spawns keep the cache warm. The unit self-declares its disciplines, so no `--skills` flag is needed.

3. **Assign topics (the global pass — NOT fanned out).** Once every root is synthesized, review all threads at once and assign each one topic. This is also where the vocabulary is tuned to the real threads:
    - `uv run exchanges.py thread-list` → every thread (key, root, summary, current topic).
    - Refine the vocabulary if the threads warrant it: `uv run exchanges.py topics --set '{…}'`.
    - `uv run exchanges.py thread-assign --set '{"<thread_key>": "<topic>", …}'` — one topic each.
    - `uv run exchanges.py thread-list --unassigned` → expect `[]` (every thread classified).

4. **Verify** — `uv run exchanges.py threads` prints the cached root count; `roots --pending` emits nothing (all synthesized).

## Notes

- **Content-addressed, self-invalidating.** A description edit re-keys its root → cache miss → reappears in `roots --pending` → re-synthesized next run; the stale `root_thread` entry is orphaned (GC-able). A thread whose grouping is unchanged keeps its `thread_key`, so its topic assignment survives the re-synthesis.
- **Affects the bill.** Unlike the old narrative-only synthesis, thread membership IS the billing lineage — time follows threads. Faithful membership is the bar, not just readable bullets.
