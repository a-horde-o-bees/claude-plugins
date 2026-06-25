# exchanges

The persistent **annotation store** for the timeline model and its **thread-first lineage** —
`exchange → thread → topic → billable`. Exchanges are *derived* on demand from the raw DB
(`materialize_exchanges`), never stored; the store persists the authored per-exchange
`description`, the per-root focus-thread synthesis, the topic vocabulary, and the per-thread topic
assignment, at `~/.claude/a-horde-o-bees/transcripts/annotations.db`. See `../ARCHITECTURE.md`
§ Exchange / Topic / Population.

## Signature

```
uv run ${CLAUDE_SKILL_DIR}/exchanges.py <cmd> [--db ~/.claude/a-horde-o-bees/transcripts/raw.db] [--anno ~/.claude/a-horde-o-bees/transcripts/annotations.db]
```

| cmd | args | does |
|---|---|---|
| `list` | `[--session SID \| --root RID] [--from ISO] [--to ISO] [--undescribed] [--bodies]` | derive exchanges, join descriptions → JSON (uuid, ts, `text`, description). `--session` = one file; `--root` = a whole work-tree (all the root's files, in time order — the synthesis input). `--from`/`--to` time-box by inclusive ISO-ts prefix — a partial bound covers its whole span (`--to …T16:35` keeps all of 16:35; `--from 2026-06-23` keeps the whole day). `text` is the exchange's narration in time order; `--bodies` adds the `agent` turns. |
| `describe` | `--set '{"<uuid>": "<description>"}'` | upsert per-exchange descriptions (batch) |
| `topics` | `[--set '{"<name>": "<description>"}']` | set the topic vocabulary; bare lists it |
| `roots` | `[--pending]` | list root ids, oldest first — the synthesis worklist. `--pending` = only roots whose threads aren't cached (or whose descriptions changed, re-keying the root) |
| `threads` | `--root RID --set '[{summary, uuids:[...]}]'` | store one root's focus-threads (topic-free), keyed by the root's content hash; bare prints the cached root count |
| `thread-list` | `[--unassigned]` | every synthesized thread (key, root, summary, uuids, topic) — the global topic-pass input; `--unassigned` = threads with no topic yet |
| `thread-assign` | `--set '{"<thread_key>": "<topic>"}'` | assign one topic per thread (rejects an unknown topic) |

## Concepts

- **Exchange** — one typed-prompt START to the next; spans ≥1 turn (joined by breaks) and **folds in
  its consumed interjections** (they appear as `user` turns in the `text` array at their real
  position, so one description covers both). Anchored by the prompt UUID. A leading
  `anchor_uuid=null` `(continuation)` exchange holds work carried across a segment boundary and is
  **not** describable or threadable (no stable key). Time metrics ride the `materialize_exchanges`
  object the `report` verb reads, not the `list` JSON.
- **Root** — the visualization's connected work-tree (`branch_tree.session_trees`): usually one
  session file, but a cross-file resume continues the thread into a later file and both are ONE root
  (`_root_components`). The synthesis unit, so a single objective is never fragmented across a
  resume boundary.
- **Thread** — a coherent objective spanning a run of a root's exchanges; owns a one-line `summary`
  and its member exchange UUIDs. Topic-free at synthesis; its stable identity is the hash of its
  sorted member UUIDs (`thread_key`), so a topic assignment survives a re-synthesis that preserves
  the grouping.
- **Topic** — the broad focus, **a property of the thread** (one per thread), and the report's
  billability filter key. Assigned in one global pass over every thread, from a fixed vocabulary set
  via `topics --set` — and refined against the real threads in that same pass.

## Process

1. **Describe** every exchange (per-session fan-out): `../_annotate-corpus.md` runs the per-session
   unit `../_annotate-session.md` over `/apply-over-queue`. Descriptions are per-exchange, so the
   file grain is fine here.
2. **Synthesize threads** per root (per-root fan-out): `../_synthesize-focus.md` runs the per-root
   unit `../_synthesize-root.md` over `/apply-over-queue`. Worklist: `roots --pending`.
3. **Seed + refine the vocabulary** and **assign topics** in one global pass (steps in
   `../_synthesize-focus.md` § 3): review `thread-list`, tune `topics --set`, then `thread-assign`.

## Notes

- The annotation store survives raw-DB rebuilds — it joins by stable UUID / uuid-derived hashes.
  Re-deriving exchanges after a re-ingest re-attaches every existing annotation with no remap.
- **Content-addressed, self-invalidating.** A description edit re-keys its root → `roots --pending`
  surfaces it → re-synthesis; the stale `root_thread` entry is orphaned (harmless). Threads whose
  grouping is unchanged keep their `thread_key` and topic.
- `report` reads the thread lineage to bill: an exchange counts iff it is a member of a thread whose
  topic is in the report's filter set (`report.py` § time follows threads).
