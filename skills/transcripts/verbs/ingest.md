# ingest

Load Claude Code transcripts into the raw scratch DB that every other verb reads. One row per physical JSONL line, the full payload in `json` alongside promoted identity and relationship columns for joins. Nothing is interpreted and nothing is dropped: until we know what's load-bearing, everything comes in — unlike the ratified `transcripts.db`, which models the timed layer and drops untimestamped UI-state records.

## Signature

```
uv run ${CLAUDE_SKILL_DIR}/raw_db.py ingest (--file F | --dir D) [--db ~/.claude/a-horde-o-bees/transcripts/raw.db]
uv run ${CLAUDE_SKILL_DIR}/raw_db.py reset  [--db ~/.claude/a-horde-o-bees/transcripts/raw.db] [--yes]
```

- `ingest --file F` — one main transcript `.jsonl`; its sibling sub-agent dir (`<stem>/**/*.jsonl`) is pulled in automatically.
- `ingest --dir D` — a project dir: every main transcript in it, each with its sub-agents.
- `--db` — the DB shared by every verb (default `~/.claude/a-horde-o-bees/transcripts/raw.db`). One cache, not per-project: ingesting a different `--dir` swaps its contents in, and files no longer on disk drop out. For separate project caches, pass a distinct `--db <work>/raw-<proj>.db` to **every** verb.
- `reset` — drop the cache so the next `ingest` rebuilds from scratch. **Gated:** prompts for confirmation (or `--yes`), and refuses to run non-interactively without `--yes`. A from-scratch rebuild is a deliberate, rare act for a corrupt cache, not a flag on the `ingest` hot path.

## Incremental UPSERT

The walk visits every file in session-start order and **skips any file whose `(size, mtime)` matches the `file_state` ledger**, re-parsing only new or changed files (delete + insert that file) and updating the ledger. Files removed from disk drop out. So a rerun after transcripts grow is near-instant (≈0.1s, 0 files parsed), while the first run on an empty ledger parses everything.

`is_replay` stays correct across the skip: the walk maintains the canonical-uuid `seen` set in file order — for a skipped file it loads that file's uuids from the DB; for a changed or new file it marks against `seen`, then adds its own. Output is verified identical to a clean rebuild (rows, replays, no duplicate `(file, line)`).

Each row records:

- `is_replay` and `is_compact_summary` — kept distinct: a replay is never a forest node, while a compact-summary is a single-child pass-through the post-compact chain links back through.
- `has_parent_field` — distinguishes a real root from a stateless record that carries no parent field.

## Notes

- The raw DB is a **cache**, not a source — but an incremental one: rerun freely as transcripts grow; only changed files re-parse. `serve`, `render`, and `report` read it and never write it. (The `serve` process still re-reads the whole DB on mtime change; incremental serving is a separate, later optimization.)
- Sub-agent transcripts are ingested and retained for analysis even though the time-spent lens doesn't draw them — they're superseded by their main-chain Agent tool dots.
