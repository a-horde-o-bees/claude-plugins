# export

Pretty-print one session's conversation as a markdown file — the readable dialogue, nothing else. User and agent messages only: tool calls, tool results, thinking, meta/command records, replays, compact summaries, and sidechains are all dropped. A horizontal rule separates messages; consecutive records of one role merge into a single message first, so the rules mark logical turns, not storage records.

## Signature

```
uv run ${CLAUDE_SKILL_DIR}/export_md.py --session ID_OR_PREFIX --out FILE.md \
    [--db ~/.claude/engaged-time/raw.db]
```

- `--session` — the session id; any unique prefix works. Ambiguous prefixes list the candidates and exit.
- `--out` — the markdown path to write (parents created).
- `--db` — the raw DB to read. Point this at a purpose-specific DB when the sessions don't belong in the engaged-time corpus (e.g. game-bot transcripts, which would pollute `report` rollups if ingested into the default `raw.db`).

## Process

1. Ensure the sessions are ingested (`verbs/ingest.md`) — into a separate `--db` if they shouldn't enter the default corpus.
2. Run once per session; each writes one `.md`.

## Output shape

```markdown
# Session <id>

_<n> messages · <first ts> → <last ts>_

**User**

...

---

**Agent**

...
```

This is a content-level reader of the raw DB — it renders dialogue and is orthogonal to the timeline model (no roles, lines, or time-blocks involved).
