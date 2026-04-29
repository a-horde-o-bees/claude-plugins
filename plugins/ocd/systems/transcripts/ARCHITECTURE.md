# transcripts — Architecture

Internal structure of the transcripts system: ingests Claude Code JSONL session transcripts into SQLite, partitions per-exchange time into user / agent / idle, exposes projects/sessions/exchanges navigation with persistent per-exchange purpose annotations, and serves the same operations through both a CLI (`__main__.py`) and an MCP server (`server.py`). This document covers the schema, time-accounting model, event catalog, surface layer, and module layout.

## Components

```
systems/transcripts/
  SKILL.md           — Slash-command workflow definition (user-facing CLI wrapper)
  README.md          — User-facing install/use/config docs
  ARCHITECTURE.md    — This file
  __init__.py        — Facade re-exporting internal modules
  __main__.py        — CLI dispatch (7 verbs, JSON output) — agent-debug surface mirroring the MCP server
  server.py          — FastMCP adapter exposing the same operations as MCP tools (transcripts.*)
  _server_helpers.py — Shared MCP _ok/_err + CLAUDE_PROJECT_DIR bootstrap
  _db.py             — SCHEMA + connection + project-name encoding
  _init.py           — Plugin contract: ready / ensure_ready / init / reset / status
  _ingest.py         — JSONL event collection + auto-sync
  _purposes.py       — Per-exchange purpose summary CRUD + batch wrappers (writes the purpose column on `exchanges`)
  _scope.py          — projects() / sessions() / exchanges() data layer with `show` opt-in detail buckets
  _settings.py       — Single-row settings table with typed columns + metadata schema
  _stats.py          — Derived statistics (avg_user_time) computed on demand
```

JSON output throughout — agent-consumable. Every verb other than `reset` calls `sync()` before querying so the DB is current at every read.

## Pipeline

| Stage | Module | Notes |
|---|---|---|
| Init / status / reset | `_init.py` | Uses `tools.db.rectify` for schema-aware deploy and `tools.db.reset_db` for the destructive verb |
| Ingest | `_ingest.py:sync` | Walks `~/.claude/projects/`, processes parent + nested JSONLs, INSERT OR IGNORE on `(file, line)` |
| Query | `_scope.py` | `projects()` / `sessions()` / `exchanges()` over the events table and views; default-lean output, opt into detail via `show` buckets |
| Config | `_settings.py` | Single-row `settings` table; one typed column per setting |
| Stats | `_stats.py` | On-demand callables (no caching) |
| Surface | `__main__.py`, `server.py` | CLI and MCP both delegate to the library functions above; same JSON shape from either surface |

## Database

### `events` table

Flat event log. Idempotent on `(file, line)` — JSONL lines are append-only in Claude Code transcripts, so `INSERT OR IGNORE` makes re-ingestion safe and cheap.

| Column | Source | Purpose |
|---|---|---|
| `file`, `line` | source JSONL path + line number | composite primary key |
| `project_name` | basename of source JSONL's parent dir | multi-project disambiguation |
| `parent_session` | top-level session ID (basename of session JSONL) | session grouping |
| `ts` | ISO timestamp from event | chronological ordering |
| `label` | derived event kind (see catalog below) | type-based filtering |
| `text` | message content (user_msg / assistant text only) | chat replay |
| `tool_use_label` | matched tool name on tool_result rows | analysis convenience |
| `ref` | tool_use_id | tool_use ↔ tool_result linkage |
| `parent_message` | spawning assistant UUID for nested events; NULL for top-level | subagent linkage |
| `uuid` | this event's own UUID | join target |

### `events_with_gaps` view

Adds two derived columns:

- **`exchange`** — running count of *distinct* user_msg timestamps per session. Slash command sequences (the typed slash + the expanded body) fire two user_msg events at the same instant; counting distinct timestamps folds them into a single exchange boundary. Same intent in spirit as queue-operation events being absorbed into the running exchange.
- **`gap_s`** — seconds since the prior event in the same `parent_session`, using `LAG(ts) OVER (PARTITION BY parent_session ORDER BY ts, file, line)` for deterministic tiebreak when timestamps tie.

### `chat_messages` view

Filtered view exposing user_msg + assistant text events for chat replay. Columns: `project_name, parent_session, file, line, ts, role, text` (where `role` is `user`, `subagent_user`, or `assistant`).

### `exchanges` table

Per-exchange annotations table. PK is `(parent_session, exchange)`. Holds stored metadata about exchanges — distinct from the view-derived `exchange` column on `events_with_gaps`, which is the running count used to compute metrics. Annotations persist across ingest; only `reset` wipes them.

| Column | Type | Notes |
|---|---|---|
| `parent_session` | TEXT NOT NULL | FK-equivalent to `events.parent_session` |
| `exchange` | INTEGER NOT NULL | Matches `events_with_gaps.exchange` |
| `purpose` | TEXT | Purpose Statement-style summary; null when unset |
| `purpose_updated_at` | TEXT | Timestamp of last purpose update; null when unset |

Adding more annotations (tags, notes, classifications) becomes adding a column. Each annotation has a setter module — `_purposes.py` is the first; `_tags.py` etc. would follow the same pattern. Clear operations set the relevant column(s) to NULL while preserving the row so other annotations survive.

### `settings` table

Single-row table with one typed column per setting. The metadata schema (in `_settings.SETTINGS_SCHEMA`) declares each setting's SQL type, default, and description. Adding a setting = appending to the schema dict; `init_settings` runs `ALTER TABLE ADD COLUMN` on next call.

Current settings:

| Key | Type | Default | Description |
|---|---|---|---|
| `threshold_min` | INTEGER | 15 | Idle-gap threshold in minutes |

## Event Catalog

Labels recognized by `_ingest.event_label`, derived from the JSONL `type` and sub-fields.

### User input

| Label | Source | Notes |
|---|---|---|
| `user_msg` | `type: user`, no `toolUseResult`, not sidechain | Top-level user input. Increments exchange. |
| `sidechain_user_msg` | `type: user`, sidechain | Subagent prompt. Inside parent exchange, doesn't increment. |
| `tool_result` | `type: user`, has `toolUseResult`, not interrupted | Result returning from a tool. `ref` = matching tool_use_id. |
| `tool_result_interrupted` | `type: user`, has `toolUseResult` with `interrupted: true` | User canceled the tool call. |
| `queue-operation` | `type: queue-operation` | User typed while the agent was busy; queued for later. |

### Assistant output

| Label | Source | Notes |
|---|---|---|
| `assistant[text]` | `type: assistant`, content has text block | Plain response text. |
| `assistant[thinking]` | `type: assistant`, content has thinking block | Agent reasoning trace. |
| `assistant[text,tool_use:X]` | mixed-content assistant message | Multi-block response. |
| `tool_use:<NAME>` | `type: assistant`, content has `tool_use` block | The agent invoked a tool. `ref` = tool_use_id. |

### System events

| Label | Source | Notes |
|---|---|---|
| `system:turn_duration` | `subtype: turn_duration` | Harness-emitted per-exchange compute duration. |
| `system:away_summary` | `subtype: away_summary` | Pre-built recap content the harness will display when the user returns. |
| `system:scheduled_task_fire` | `subtype: scheduled_task_fire` | Background scheduled task fired. |
| `system:api_error` | `subtype: api_error` | Server error with retry metadata. |

### Attachments

| Label | Notes |
|---|---|
| `attachment:hook_success` | A `PreToolUse` hook approved a tool. |
| `attachment:hook_blocking_error` | A hook denied a tool before it ran. |
| `attachment:command_permissions` | "Yes, and don't ask again" — user added an allowlist rule. |
| `attachment:hook_additional_context` | Extra context injected by a hook. |
| `attachment:task_reminder` | The reminder banner the harness injects periodically. |
| `attachment:date_change` | Day-boundary marker. Frequently produces idle gaps. |
| `attachment:queued_command` | Marker for a queued user command. |
| `attachment:edited_text_file` | An edit preview attachment. |
| `attachment:diagnostics` | LSP/type-check diagnostics injected post-edit. |
| `attachment:deferred_tools_delta` | Deferred tools list delta. |
| `attachment:mcp_instructions_delta` | MCP server instructions delta. |
| `attachment:skill_listing` | Skill listing attachment. |

## Exchange Model

An exchange N is the set of events from user_msg N (start) through the last event before user_msg N+1 (or session end for the last exchange).

Tied-timestamp user_msg events fold into a single exchange boundary (slash-command pattern). Queue-operation events and sidechain user_msg events do not increment exchange — they are absorbed into the running exchange.

## Time Accounting

Each `gap_s` is owned by exactly one exchange — the exchange it belongs to in the merged chronological timeline. The user_msg event's gap is the **compose pause** that produced this exchange (the user's lead-in time); other gaps in the exchange are agent activity (or above-threshold idle).

For each exchange, the threshold (default 15 min, set via `settings`) partitions accounted time:

| Quantity | Definition |
|---|---|
| `total_s` | SUM of all gap_s in this exchange — wall-clock duration |
| `user_s` | Compose pause when observable and ≤ threshold; NULL when first session event was user_msg or gap exceeds threshold |
| `agent_s` | SUM(gap_s WHERE gap_s ≤ threshold) on non-user_msg events |
| `idle_s` | SUM(gap_s WHERE gap_s > threshold) — walked-away time |
| `active_s` | `(user_s or 0) + agent_s` — the engaged time (always defined; NULL user_s treated as 0) |

The metrics form a hierarchy:

- `total_s = active_s + idle_s`
- `active_s = user_s + agent_s`

**Conservation.** For any exchange, `total_s = user_s + agent_s + idle_s` exactly (NULL user_s treated as 0; the corresponding gap, if any, is in idle or absent). For any session, SUM(total_s) over all exchanges equals `MAX(ts) − MIN(ts)`.

**User vs agent interpretation.** `user_s` is the only direct signal of the user being at the keyboard — the gap from the agent finishing the prior exchange to the next user_msg arriving. `agent_s` is everything else within active time: tool execution, streaming responses, intermediate thinking blocks, sub-threshold gaps between agent operations.

**Filling NULL user_s slots.** When agents compute aggregates that include exchanges with NULL `user_s`, they can read `_stats.avg_user_time(conn, threshold_s)` (also exposed in the `derived` block of `settings` output) as a fill estimate. Above-threshold compose pauses can be classified as ~3 min of engaged composition + the rest as idle, or left as pure idle depending on the agent's framing. The package surfaces the estimate; the renderer decides whether to apply it.

**Sub-second precision caveat.** Timestamps have millisecond precision, but `julianday()` arithmetic uses double precision (effective ~10ms resolution). Sub-10ms gaps are rounded; not material for analytics.

**Pre-first-user-msg events.** Events that fire before the session's first user_msg get `exchange = 0` and are excluded from accounting (session setup, not engagement). The first event of each session has `gap_s = NULL` and contributes 0 to any aggregate.

## Subagent Linkage

Nested `<session>/subagents/agent-<id>.jsonl` files are spawned-agent transcripts. Their events share the parent's `parent_session` (set at ingest to the top-level session's stem) but carry `parent_message = <spawning assistant UUID>`.

The spawning UUID resolves at ingest by temporal containment: the most recent parent assistant `tool_use:Task` or `tool_use:Agent` event before the nested file's first event is the spawning message.

Subagent runtime is fully contained within the parent exchange's window. Their events contribute their own `gap_s` to active/idle as if they were parent-level events — the merged chronological timeline absorbs them.

## Idempotency

Three properties combine:

1. JSONL files are append-only in Claude Code (lines never rewritten).
2. `(file, line)` is the events table primary key.
3. Ingest uses `INSERT OR IGNORE`.

So re-runs of `sync()`:

- Skip every previously-ingested line.
- Insert only newly appended lines.
- Pick up newly created subagent files.

## Surface Layer

The same library functions back two presentation surfaces — agents and users reach for whichever fits the context:

| Surface | Module | Use |
|---|---|---|
| MCP server | `server.py` | Agent-facing — tools registered with `transcripts.*` prefix, JSON in/out, default-lean responses. Reach for these when the agent needs transcript data inline during reasoning. |
| CLI | `__main__.py` | Agent-debug surface mirroring the MCP tools 1:1 (`sessions` ↔ `sessions_query`, `purposes-set` ↔ `purposes_set`, etc.). Reach for the CLI from `/transcripts` skill invocations or interactive shell debug. |

### MCP Tool Surface

`server.py` registers tools that delegate to library functions. Tool naming follows the input-shape distinction (see problem log `Verb naming convention not formally captured.md`): `_list` for unfiltered enumeration, `_query` for filtered structural retrieval, `_get`/`_set` for single-keyed operations, `_describe` for introspection.

| Tool | Library | Notes |
|---|---|---|
| `projects_list` | `_scope.projects` | Full enumeration, no filter |
| `sessions_query` | `_scope.sessions` | Project / date / `show` filters |
| `exchanges_query` | `_scope.exchanges` | Project / session / range / date / `show` filters |
| `purposes_set` | `_purposes.set_many` | Batch upsert: `{exchange: text}` map |
| `purposes_clear` | `_purposes.clear_many` | Batch null: `[exchange, ...]` list |
| `settings_get`, `settings_set` | `_settings.*` | Single-row config |
| `schema_describe` | `sqlite_master` + curated semantics | Read once before authoring `sql_query` statements |
| `sql_query` | `sqlite3` (read-only) | Ad-hoc analyses not covered by curated tools |

**Read-only enforcement on `sql_query`** — the connection opens in SQLite read-only mode (`file:...?mode=ro` URI). Writes are rejected at the engine level regardless of the SQL passed; no parsing, no authorizer, no bypass. The other tools open read-write connections so they can run `_ingest.sync()` before queries.

**Dormancy** — module-level `_READY = _init.ready(_DB_PATH)` is checked at import; tool registration is gated behind `if _READY:`. When the DB is absent or its schema is divergent, the server registers zero tools and its instructions reduce to a one-line pointer at `/ocd:setup`. Re-registering tools after init requires a Claude Code restart.

**MCP subprocess bootstrap** — `_server_helpers.py` sets `CLAUDE_PROJECT_DIR` from `Path.cwd().resolve()` at import time when the variable is missing. Claude Code launches MCP servers with cwd at the project root but does not propagate the env var; the bootstrap is the per-server bridge described in the project's `mcp-server.md` convention.

## Plugin Contract

`_init.py` implements the standard system-init contract:

- `_db_path()` — `<project>/.claude/<plugin>/transcripts/transcripts.db`
- `_build_schema(target_path)` — runs `_db.init_db` then `_settings.init_settings` so the schema fingerprint reflects both events and settings tables
- `ready(db_path)` — returns True when schema matches expected via `tools.db.matches_expected`
- `ensure_ready(db_path)` — raises `NotReadyError` when not operational
- `init(force)` — uses `tools.db.rectify` to deploy or repair
- `reset()` — uses `tools.db.reset_db` to back up + wipe + rebuild
- `status()` — returns `{files: [...], extra: [...]}` for `/ocd:setup status`
