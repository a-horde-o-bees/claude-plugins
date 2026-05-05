# transcripts

Query Claude Code session transcripts as structured data — projects, sessions, exchanges (user_msg + agent response groups), with time accounting and full chat content. Backed by a SQLite database ingested from `~/.claude/projects/`.

## When to use

- Inspect a prior session's exchanges, metrics, or full chat content
- Generate a per-day time-block report scoped to a project (`report time-blocks`) for client time-charging or per-project rollups
- Annotate exchanges with persistent Purpose Statement-style summaries (`purposes-set`) so future sessions can re-find work by purpose
- Extract a chat slice for further analysis (topic classification, retro write-ups, decision archaeology)
- Verify how time-accounting (user/agent/idle) lands on a real session

## Install

The system is part of the `ocd` plugin. After plugin install:

```bash
/ocd:setup init      # initializes the DB at <project>/.claude/ocd/transcripts/transcripts.db
```

The DB is project-local; each project has its own. Re-running `init` is idempotent.

## Usage

Three surfaces back the same operations — pick whichever fits the context:

- **Slash command** — `/ocd:transcripts <verb> [...]` from chat. Drives the skill executor; markdown output for `report`, JSON for everything else.
- **CLI** — `ocd-run transcripts <verb> [...]` from any shell Claude Code spawns. Same JSON output as the skill's passthrough verbs.
- **MCP tools** — `transcripts.*` (`projects_list`, `sessions_query`, `exchanges_query`, `purposes_set/clear`, `settings_get/set`, `schema_describe`, `sql_query`) for inline agent use during reasoning. Skill-orchestrated `report` is not exposed via MCP.

Common invocations:

```
/ocd:transcripts projects
/ocd:transcripts sessions
/ocd:transcripts sessions --all-projects --from 2026-04-01
/ocd:transcripts exchanges --session 7bb2b7b0 --range 5
/ocd:transcripts exchanges --session 7bb2b7b0 --range 5-10
/ocd:transcripts exchanges --from 2026-04-27T18:00 --to 2026-04-27T19:00
/ocd:transcripts purposes-set 7bb2b7b0 '{"5": "purpose text", "12": "purpose text"}'
/ocd:transcripts purposes-clear 7bb2b7b0 5 12
/ocd:transcripts report time-blocks
/ocd:transcripts settings
/ocd:transcripts settings threshold_min 20
/ocd:transcripts reset
```

CLI form (passthrough verbs):

```bash
ocd-run transcripts projects
ocd-run transcripts sessions
ocd-run transcripts exchanges --session 7bb2b7b0 --range 5
```

Passthrough verbs emit JSON — pipe to `jq`, `python -m json.tool`, or consume directly. The `report` verb is skill-orchestrated (not on the CLI passthrough surface) and emits markdown rendered per its format component file.

## Verbs

| Verb | Args | Use |
|---|---|---|
| `projects` | — | All projects in the DB with the current-project marker |
| `sessions` | `[--project X \| --all-projects] [--from D --to D] [--show timeframes bytes]` | Session metadata; default-lean (counts), opt into timeframes/bytes via `--show` |
| `exchanges` | `[--project X \| --session Y [--range R] \| --all-projects] [--from D --to D] [--show messages active breakdown metrics timeframes]` | Per-exchange rows; default-lean, opt into detail via `--show` |
| `purposes-set` | `<session> <json>` | Batch upsert per-exchange Purpose Statement-style summaries from a JSON map keyed by exchange number |
| `purposes-clear` | `<session> <exchange ...>` | Batch clear per-exchange purpose summaries |
| `report` | `[<format> [--project X \| --all-projects] [--from D --to D]]` | List available report formats (no args); generate the named format. Currently: `time-blocks`. Skill-orchestrated, markdown output |
| `settings` | `[<key> [<value>]]` | Persistent config + on-demand derived stats (e.g., `avg_user_time_s`) |
| `reset` | — | Backup the DB and recreate empty schema |

Default scope on `sessions` and `exchanges` is the current project. `--all-projects` widens. `--project X` filters by name substring. Date filters apply on top of any scope filter. Scope precedence on `exchanges`: `--session` > `--all-projects` > `--project` > current project.

## Concepts

- **Project** — Claude Code's encoded directory under `~/.claude/projects/`. Current project resolves from `CLAUDE_PROJECT_DIR` or git root.
- **Session** — top-level JSONL transcript, one per `claude` invocation.
- **Exchange** — the unit of conversation: one user message + the agent's full response (text, tool use, thinking, queued user input absorbed during the response) until the next user message.
- **Purpose** — a persistent Purpose Statement-style annotation per exchange (scope + role, no mechanics, no history). Stored on the `exchanges` table; survives ingest, only `reset` wipes. Set via `purposes-set`; read on every `exchanges` row.

Per-exchange time accounting: `total_s = user_s + agent_s + idle_s`.

- `user_s` — observable compose pause before this exchange (NULL when first event of session was the user_msg, or when the gap exceeded the threshold)
- `agent_s` — sum of below-threshold gaps on non-user_msg events (agent execution + reasoning + streaming)
- `idle_s` — sum of above-threshold gaps (walked-away time)
- `active_s` = `(user_s or 0) + agent_s` — engaged time

The threshold (default 15 min) is configurable via `settings threshold_min <value>`. The `avg_user_time_s` derived stat (from `settings`) is the mean of observable compose pauses; agents fill it in for NULL `user_s` when computing aggregates so unmeasurable lead times don't drop to zero.

## Configuration

Persistent config lives in the DB. View and update via the `settings` verb:

```
ocd-run transcripts settings                    # show all config + derived stats
ocd-run transcripts settings threshold_min      # show one
ocd-run transcripts settings threshold_min 20   # set
```

## Reset

`transcripts reset` backs up the DB to a timestamped sibling and recreates the empty schema. Use when:

- Schema has changed and you want a clean rebuild (the next sync will repopulate from `~/.claude/projects/`)
- You want to start fresh

The backup file is preserved at `<project>/.claude/ocd/transcripts/transcripts.db.backup-<timestamp>`.

## See also

- `ARCHITECTURE.md` — schema, event catalog, time-accounting model, internal module layout
- `SKILL.md` — slash-command workflow definition
