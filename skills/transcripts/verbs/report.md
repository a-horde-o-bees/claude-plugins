# report

Roll up time-block coverage into engaged time per day and month — the "Engaged Time Report" — the
live engaged-time source (supersedes the legacy `exchange_s` path). Built on the START/STOP/BREAK
line model, filtered through the thread-first lineage.

## Signature

```
uv run ${CLAUDE_SKILL_DIR}/report.py [--topics a,b,c] [--from D --to D] [--format md|csv] [--out FILE]
```

- `--topics` — the billable topic set the consuming project bills on (the model stores no topic
  policy). An exchange counts iff it is a member of a thread whose topic is in this set. Omit for an
  unfiltered diagnostic view (every exchange, threaded or not).
- `--from` / `--to` — inclusive attributed-day range (`YYYY-MM-DD`).
- `--format` — `md` (default; header + by-month/by-day tables + daily breakdown) or `csv` (by-day).
- `--out` — write to FILE (default stdout). Reports belong in the **consuming project's**
  `build/reports/`, never the skill dir.

## How it bills

- **Time follows threads.** Focus-threads are synthesized per ROOT (`exchanges.py threads`) and each
  assigned one topic. The billable record set is every exchange that is a member of a billable-topic
  thread; unthreaded exchanges (incidental turns) and non-billable-thread exchanges drop out of both
  the time and the narrative. This reproduces the block model — work that never coalesced into a
  billable objective was never billed.
- **Filter-then-adjust, by day only.** The gap ceilings (`gap_adjust`) are recomputed per day over
  the *kept* records, so a bridge into an excluded neighbour reopens. A multi-topic/multi-day thread
  can't honestly split its time by narrative, so time appears ONLY in the by-day / by-month / total
  tables; the daily breakdown is work narrative (one bullet per billable thread), no per-row time.
- **Daily breakdown** — a flat chronological list of billable focus-thread bullets per day. A thread
  is listed once, on its first day; a thread that ran past midnight still bills both days (time
  splits) but its narrative appears only where it began — no cross-day duplication.

## Process

1. Ensure the raw DB is current (`verbs/ingest.md`), descriptions + threads + topics are current
   (`_synthesize-focus.md`).
2. Run `report.py --topics <billable set> [--from … --to …] --out <project>/build/reports/<name>.md`.
3. Render to PDF via the `export-pdf` skill if a prepared deliverable is needed.

The legacy `exchange_s` path (`transcripts-legacy`) is superseded; this is the live source.
