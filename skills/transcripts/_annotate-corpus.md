# Annotate the corpus (description fan-out)

Populate per-exchange description lines across the whole corpus, or a chosen session set, by fanning the per-session unit `_annotate-session.md` out over `/apply-over-queue`. This file is the parent orchestration; `_annotate-session.md` is the per-item unit it runs. Topic assignment is a separate global pass (`verbs/exchanges.md` § topics), never fanned out — coherent tags need the full set in view.

## Why apply-over-queue

The shared instruction — the writing disciplines plus the per-session unit — is large and identical on every spawn, so `/apply-over-queue` pays for it once and serves it from prompt cache on every later session. The per-session unit is target-shaped, reading and writing only its own session, so spawns never contend.

## Disciplines flatten automatically

`_annotate-session.md` authors each description under two independent disciplines:

- **`/description-authoring`** — what each line must convey.
- **`/concise-prose`** — raise signal, cut filler.

The unit references both as `/skill` calls, and `/apply-over-queue` discovers and flattens every `/skill` reference in the instruction's latest version. No `--skills` flag is needed — a well-formed instruction self-declares its disciplines. (`--skills` remains available to *supplement* a discipline the instruction doesn't name.)

## Process

1. **Build the queue** — the session ids to annotate. Take the whole corpus, or only sessions with undescribed exchanges; the unit self-skips fully-described sessions, so an over-broad queue costs only cheap no-op spawns.
    - bash: `ls <corpus dir>/*.jsonl` → full session ids (`--items` wants full ids, not prefixes).

2. **Fan out** — invoke `/apply-over-queue` with the per-session unit as instruction:
    ```
    /apply-over-queue \
      --instruction /home/dev/.claude/skills/transcripts/_annotate-session.md \
      --items <full session ids, comma-separated> \
      --isolation none \
      --cwd /home/dev/.claude/skills/transcripts \
      --add-dir /home/dev/.claude/a-horde-o-bees/transcripts
    ```
    - `--isolation none` — the side effect is a SQLite write to `annotations.db`, outside any repo; a worktree diff can't capture DB rows.
    - `--add-dir` the working dir so spawns reach `raw.db` (read) and `annotations.db` (write).
    - **Sequential only** — `annotations.db` is one SQLite writer, and sequential spawns keep the prompt cache warm. Run no other annotation command during the fan-out.

3. **Verify coverage** — confirm every uuid-anchored exchange is now described:
    - bash: `uv run /home/dev/.claude/skills/transcripts/exchanges.py list --undescribed` → expect `[]`.

## Notes

- **Idempotent and re-runnable.** The per-session unit writes only missing descriptions, so re-running over a queue that mixes done and new sessions backfills the new ones and no-ops the rest — the way to bring a new billing period current.
- **Descriptions only.** This pass never assigns topics; that is the single global pass after every session is described.
