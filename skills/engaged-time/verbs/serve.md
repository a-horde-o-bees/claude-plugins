# serve

Launch and run the interactive timeline server that renders transcript sessions for browser exploration.

Each session draws as a flat rail of segments (root, resume, compaction, rewind, in ts order) over the raw DB, under one global column header. The Python model owns all geometry and time-accounting; the client only places columns and draws. Encodings and interactions are documented in full at `../swimlane_server_ui.md`.

## Signature

```
uv run ${CLAUDE_SKILL_DIR}/swimlane_server.py [--db ~/.claude/engaged-time/raw.db] [--port 8765]
```

Open `http://localhost:<port>/`.

## First run

From nothing to a rendered page in three commands — every flag defaults, so none are needed:

```
uv run ${CLAUDE_SKILL_DIR}/raw_db.py init      # store the transcripts root; create logs/, diagrams/, scratch/
uv run ${CLAUDE_SKILL_DIR}/raw_db.py ingest    # build the raw DB from the whole corpus
uv run ${CLAUDE_SKILL_DIR}/swimlane_server.py  # serve on :8765, foreground
```

Then open `http://localhost:8765/`.

`init` is required first: `ingest` blocks without a stored root, and `init` is what creates the `logs/` directory the backgrounded launch below redirects into. Expect the first `ingest` over a large corpus to take minutes; reruns are near-instant (incremental by size+mtime).

## Process

1. Ensure the raw DB exists and is current (`verbs/ingest.md`).
2. Start the server in the background, redirecting to a log — it runs minutes-plus. `mkdir -p` guards the case where `init` was skipped, since the shell redirect fails before Python can create anything:

   ```
   mkdir -p ~/.claude/engaged-time/logs
   uv run ${CLAUDE_SKILL_DIR}/swimlane_server.py --db ~/.claude/engaged-time/raw.db --port 8765 > ~/.claude/engaged-time/logs/serve.log 2>&1 &
   ```

3. Note the launch **PID** — stopping the server needs it.
4. Open the page; expand segment rows to load them (`/api/segment/<uuid>`, lazy, client-cached).

## Lifecycle — stopping and restarting

- **Kill by PID number** (`kill <PID>`). Never `pkill -f swimlane_server` — the pattern self-matches the launcher's own command line and kills the calling shell (exit 144).
- **A code edit needs a restart.** After editing any `*.py`, kill the PID, relaunch, and hard-reload the page — all geometry and time-accounting is server-side, so the client renders stale output until the server restarts.
