---
name: transcripts
description: Query Claude Code session transcripts as structured data — projects, sessions, exchanges (user_msg + agent response groups), with time accounting, full chat content, and persistent per-exchange purpose summaries. Backed by a SQLite DB ingested from ~/.claude/projects/. Default-lean output; opt into detail (messages, metrics, timeframes) via --show. Auto-syncs new lines on every query. Same operations are available agent-side as MCP tools (transcripts.* — projects_list, sessions_query, exchanges_query, purposes_set/clear, schema_describe, sql_query).
argument-hint: "<projects | sessions [--project X | --all-projects] [--from D --to D] [--show timeframes bytes] | exchanges [--project X | --session Y [--range R] | --all-projects] [--from D --to D] [--show messages active breakdown metrics timeframes] | purposes-set <session> <json> | purposes-clear <session> <exchange ...> | settings [<key> [<value>]] | reset>"
allowed-tools:
  - Bash(ocd-run transcripts:*)
---

# /transcripts

Query Claude Code session transcripts. The skill is a thin wrapper over `ocd-run transcripts`; output is JSON throughout for direct agent consumption. The same operations are exposed agent-side via the `transcripts` MCP server — reach for MCP tools when the agent needs the data inline; reach for this skill when the user wants to drive from chat.

## Process Model

The DB is initialized on `/ocd:setup init` (or on-demand via `transcripts reset`). Every verb other than `reset` auto-syncs new transcript lines from `~/.claude/projects/` before querying — there is no separate ingest step.

Seven verbs:

| Verb | Effect |
|------|--------|
| `projects` | List all projects in the DB with the current-project marker |
| `sessions` | Session metadata; default-lean ({project, session, n_exchanges, n_purposed}); `--show` opts into timeframes/bytes |
| `exchanges` | Per-exchange rows; default-lean ({project, session, exchange, purpose}); `--show` opts into messages/active/breakdown/metrics/timeframes |
| `purposes-set` | Batch upsert per-exchange purpose summaries from a JSON map |
| `purposes-clear` | Batch clear per-exchange purpose summaries |
| `settings` | Show or update persistent config; lists derived stats |
| `reset` | Backup the DB and recreate empty schema |

Output is always JSON. Errors emit `{"error": "..."}` on stderr with exit code 1.

`exchanges` returns an array. Default row is lean — opt into detail via `--show`:

```json
[
  {
    "project": "-home-dev-projects-...",
    "session": "1e010e82-...",
    "exchange": 5,
    "purpose": null
  }
]
```

With `--show metrics timeframes messages`:

```json
[
  {
    "project": "-home-dev-projects-...",
    "session": "1e010e82-...",
    "exchange": 5,
    "purpose": null,
    "exchange_start": "2026-04-27T12:05:52Z",
    "exchange_end": "2026-04-27T12:17:17Z",
    "active_s": 660,
    "user_s": 360,
    "agent_s": 300,
    "total_s": 660,
    "idle_s": 0,
    "messages": [
      {"type": "user",      "message": "..."},
      {"type": "assistant", "message": "..."}
    ]
  }
]
```

`projects` returns `{current, projects[]}`. `sessions` returns `{filter, n_sessions, sessions[]}`. `settings` returns `{config, derived}`. See ARCHITECTURE.md for the full schema, time-accounting model, and event catalog.

## Scope

The unit hierarchy: **project → session → exchange**.

- **Project** — Claude Code's encoded directory under `~/.claude/projects/`, e.g., `-home-dev-projects-monaco`. The current project resolves from `CLAUDE_PROJECT_DIR` or git root.
- **Session** — top-level JSONL transcript (one per `claude` invocation). Identified by UUID; queries accept unique prefix.
- **Exchange** — the unit of conversation: one user_msg + the agent's response (including tool use, thinking, queued user input absorbed during the response) until the next user_msg. Numbered 1+ within each session.

Time accounting per exchange (opt in via `--show metrics`):

- `total_s = user_s + agent_s + idle_s` (conservation)
- `active_s = user_s + agent_s` (engaged time; NULL user_s treated as 0)
- `user_s` is the compose pause (NULL when above threshold or unobservable)
- `agent_s` is below-threshold within-exchange agent activity
- `idle_s` is above-threshold gaps

Threshold (default 15 min) is configurable via `settings`.

`--show` buckets on `exchanges`: `messages` (chat content), `active` (active_s only), `breakdown` (active_s + user_s/agent_s), `metrics` (full hierarchy), `timeframes` (start/end). `--show` buckets on `sessions`: `timeframes` (first_ts/last_ts), `bytes`.

Default scope on `sessions` and `exchanges` is the current project. `--all-projects` widens. `--project X` filters by name substring. `--session Y` (on `exchanges`) takes precedence over project filters. Date filters `--from D --to D` apply on top of any scope filter.

**Purposes** are persistent per-exchange summaries stored in the `exchanges` annotations table. Each is a Purpose Statement-style line — scope + role, no mechanics, no history. They survive sync; only `reset` wipes them. `sessions` reports `n_purposed` per session; `exchanges` includes the `purpose` field per row (null when unset). When an agent reads an exchange's content and would benefit from re-finding it later, generate a one-line purpose and persist via `purposes-set`. Both write verbs are batch-shaped — single-key maps and one-element lists handle the singular case naturally.

## Rules

- Output is always JSON — no text formatting toggle.
- `--range` is only meaningful with `--session`; ignored otherwise.
- `--show` accepts space-separated bucket names; unknown values raise a validation error.
- `purposes-set` JSON map keys must coerce to integer exchange numbers (e.g. `'{"5": "...", "12": "..."}'`).
- `reset` backs up to a timestamped sibling file before wiping. Use when schema migrations land or to start fresh.
- Agents that need cross-project rollups iterate via `projects` → `sessions --project X` → `exchanges --session Y`. The CLI does not aggregate across projects in a single call by design.

## Workflow

1. If not $ARGUMENTS: Exit to user: skill description and argument-hint
2. {verb} = first token of $ARGUMENTS
3. {verb-args} = remainder of $ARGUMENTS after {verb}

> Each verb maps 1:1 to an `ocd-run transcripts` subcommand. Output is JSON; pass through stdout for downstream consumption.

4. If {verb} is `projects`:
    1. bash: `ocd-run transcripts projects`
5. Else if {verb} is `sessions`:
    1. bash: `ocd-run transcripts sessions {verb-args}`
6. Else if {verb} is `exchanges`:
    1. bash: `ocd-run transcripts exchanges {verb-args}`
7. Else if {verb} is `purposes-set`:
    1. bash: `ocd-run transcripts purposes-set {verb-args}`
8. Else if {verb} is `purposes-clear`:
    1. bash: `ocd-run transcripts purposes-clear {verb-args}`
9. Else if {verb} is `settings`:
    1. bash: `ocd-run transcripts settings {verb-args}`
10. Else if {verb} is `reset`:
    1. bash: `ocd-run transcripts reset`
11. Else: Exit to user: unrecognized verb {verb} — expected projects, sessions, exchanges, purposes-set, purposes-clear, settings, or reset

### Report

Pass through the CLI's stdout. JSON in all cases. Errors arrive on stderr with `{"error": "..."}` and exit code 1.
