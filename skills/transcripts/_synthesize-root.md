# Synthesize root focus-threads

Coalesce ONE root's per-exchange descriptions into **focus-threads** — each a coherent objective the work pursued, owning a one-line `summary` and the member exchange UUIDs it spans. A ROOT is the visualization's connected work-tree: usually one session file, but a cross-file resume continues the thread into a later file, and both files are ONE root — so a thread may span them. The apply-over-queue fan-out runs this across many roots; it also runs standalone for one. Each spawn reads and writes only its own root, so parallel runs never contend.

Threads only — never assign topics. Topics come from a separate global pass over every thread at once (`exchanges.py thread-assign`); a coherent vocabulary can't be set one root at a time, and the vocabulary is refined against the full thread set. Narrative + billing lineage — a thread's member exchanges are what its topic bills, so membership must be faithful: every substantive exchange belongs to exactly one thread; genuinely incidental turns belong to none.

## Target contract

You are given exactly one TARGET — a root id (a queue item, or a root id for a standalone run). Operate only on TARGET. Never read, reference, or depend on another root.

## Path

The commands hard-code the absolute path `/home/dev/.claude/skills/transcripts/exchanges.py`. apply-over-queue consumes this file raw, outside the dispatcher that resolves `${CLAUDE_SKILL_DIR}`. `exchanges.py` is a standalone stdlib script — `uv run <path>` runs it from any directory.

## Process

1. {exchanges}: Bash: `uv run /home/dev/.claude/skills/transcripts/exchanges.py list --root TARGET` — each row is a described exchange of TARGET (across all the root's files): its `uuid`, `ts`, and authored `description`, in time order. A leading keyless `(continuation)` pseudo-exchange (uuid=null) carries no description — ignore it; it is never a thread member.
2. {threads}: Apply: /description-authoring, /concise-prose — they own the structure (voice, concision, outcome over narration, no decorative facts). This step adds only the **coalescing**: read {exchanges} in full as one root's arc, and partition it into focus-threads.
    - **One objective → one thread.** A run of exchanges driving at a single goal — a feature built, a bug traced and fixed, a doc reconciled, a deploy run — collapses to ONE thread, whose `summary` states that objective and its outcome (what it achieved, decided, or fixed). Keep genuinely distinct objectives apart.
    - **Consolidate hard** — far fewer threads than exchanges. The count is the distinct objectives that actually occurred, never padded; most roots are one to three threads.
    - **Faithful membership.** Each thread's `uuids` are exactly the exchanges that served that objective, in time order. Assign every substantive exchange to its thread. Leave genuinely incidental turns (a bare clear, an ack, an interrupted/unanswered turn) out of every thread — unthreaded exchanges do not bill, which is correct for incidental work.
    - **Past tense** summaries; threads in the order each objective first appears.
3. Persist: Bash: `uv run /home/dev/.claude/skills/transcripts/exchanges.py threads --root TARGET --set '{threads}'` — `{threads}` a JSON array `[{"summary": "<one line>", "uuids": ["<uuid>", ...]}, ...]`. The store recomputes TARGET's content hash from the live descriptions and validates every uuid belongs to TARGET; an out-of-root uuid is rejected (re-check your membership).

> Writes land in `annotations.db` `root_thread`, keyed by the root's content hash — content-
> addressed, so a later description edit re-keys the root and this re-runs; the stale entry is
> orphaned (harmless). Each thread's stable identity (for the topic pass) is the hash of its sorted
> member UUIDs, so re-running with the same grouping preserves any topic already assigned.
