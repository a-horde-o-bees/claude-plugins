# ingest

Load Claude Code transcripts into the raw scratch DB that every other verb reads. One row per physical JSONL line, the full payload in `json` alongside promoted identity and relationship columns for joins. Nothing is interpreted and nothing is dropped: until we know what's load-bearing, everything comes in, including untimestamped UI-state records that a timed model would discard.

## Signature

```
uv run ${CLAUDE_SKILL_DIR}/raw_db.py init   [--root PATH] [--work PATH]
uv run ${CLAUDE_SKILL_DIR}/raw_db.py ingest [--file F | --dir D] [--db ~/.claude/engaged-time/raw.db]
uv run ${CLAUDE_SKILL_DIR}/raw_db.py reset  [--db ~/.claude/engaged-time/raw.db] [--yes]
```

- `init [--root PATH] [--work PATH]` — store both path anchors. `--root` is the transcripts corpus this skill reads (default `~/.claude/projects`); `--work` is where every artifact lands — the DBs plus `logs/`, `diagrams/`, `scratch/` (default `~/.claude/engaged-time`). Run once before anything else; it reports what it found and warns about retention. Re-runnable to confirm or change either. Repointing `--work` does not move existing artifacts — it warns that they remain at the old location, and moving them is a manual `cp`/`mv`.
- `ingest` (no target) — the whole corpus under the stored root. **Blocks when the root is unset or gone** rather than falling back: a guessed root yields an empty timeline that reads as "no work happened", and a root that vanished usually means retention pruned the corpus.
- `ingest --file F` — one main transcript `.jsonl`; its sibling sub-agent dir (`<stem>/**/*.jsonl`) is pulled in automatically.
- `ingest --dir D` — a project dir: every main transcript in it, each with its sub-agents. An explicit target bypasses the stored root.
- `--db` — the DB shared by every verb (default `~/.claude/engaged-time/raw.db`). One cache, not per-project: ingesting a different `--dir` swaps its contents in, and files no longer on disk drop out. For separate project caches, pass a distinct `--db <work>/raw-<proj>.db` to **every** verb.
- `reset` — drop the cache so the next `ingest` rebuilds from scratch. **Gated:** prompts for confirmation (or `--yes`), and refuses to run non-interactively without `--yes`. A from-scratch rebuild is a deliberate, rare act for a corrupt cache, not a flag on the `ingest` hot path.

## Incremental UPSERT

The walk visits every file in session-start order and **skips any file whose `(size, mtime)` matches the `file_state` ledger**, re-parsing only new or changed files (delete + insert that file) and updating the ledger. Files removed from disk drop out. So a rerun after transcripts grow is near-instant (≈0.1s, 0 files parsed), while the first run on an empty ledger parses everything.

`is_replay` stays correct across the skip: the walk maintains the canonical-uuid `seen` set in file order — for a skipped file it loads that file's uuids from the DB; for a changed or new file it marks against `seen`, then adds its own. Output is verified identical to a clean rebuild (rows, replays, no duplicate `(file, line)`).

Each row records:

- `is_replay` and `is_compact_summary` — kept distinct: a replay is never a forest node, while a compact-summary is a single-child pass-through the post-compact chain links back through.
- `has_parent_field` — distinguishes a real root from a stateless record that carries no parent field.

## Retention

Claude Code prunes session transcripts on the `cleanupPeriodDays` timer in `settings.json`, and this skill reads those files as its **only** source. Pruned sessions are unrecoverable — they do not fail loudly, they silently shorten every rollup's history. `init` reports the live value; keep it at or above the window you intend to analyze.

## Notes

- The raw DB is a **cache**, not a source — rerun freely as transcripts grow. `serve`, `render`, and `report` read it and never write it, and a running `serve` re-reads the whole DB whenever its mtime changes.
- Sub-agent transcripts are ingested and retained for analysis even though the time-spent lens doesn't draw them — they're superseded by their main-chain Agent tool dots.
