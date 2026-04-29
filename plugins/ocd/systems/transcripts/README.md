# transcripts

Query Claude Code session transcripts as structured data — projects, sessions, exchanges (user_msg + agent response groups), with time accounting and full chat content. Backed by a SQLite database ingested from `~/.claude/projects/`.

## When to use

- Inspect a prior session's exchanges, metrics, or full chat content
- Build a daily / weekly / per-topic time report (composed in agent code; the CLI provides primitives)
- Extract a chat slice for further analysis (topic classification, retro write-ups, decision archaeology)
- Verify how time-accounting (user/agent/idle) lands on a real session

## Install

The system is part of the `ocd` plugin. After plugin install:

```bash
/ocd:setup init      # initializes the DB at <project>/.claude/ocd/transcripts/transcripts.db
```

The DB is project-local; each project has its own. Re-running `init` is idempotent.

## Usage

Invoke as a slash command from any project:

```
/transcripts projects
/transcripts sessions
/transcripts sessions --all-projects --from 2026-04-01
/transcripts exchanges --session 7bb2b7b0 --range 5
/transcripts exchanges --session 7bb2b7b0 --range 5-10
/transcripts exchanges --from 2026-04-27T18:00 --to 2026-04-27T19:00
/transcripts settings
/transcripts settings threshold_min 20
/transcripts reset
```

Or directly via the CLI (any shell Claude Code spawns):

```bash
ocd-run transcripts projects
ocd-run transcripts sessions
ocd-run transcripts exchanges --session 7bb2b7b0 --range 5
```

Output is JSON throughout — pipe to `jq`, `python -m json.tool`, or consume directly from agent code.

## Verbs

| Verb | Args | Use |
|---|---|---|
| `projects` | — | All projects in the DB with the current-project marker |
| `sessions` | `[--project X \| --all-projects] [--from D --to D]` | Session metadata: counts, byte size, datetime range |
| `exchanges` | `[--project X \| --session Y [--range R] \| --all-projects] [--from D --to D]` | Exchanges with metrics + messages |
| `settings` | `[<key> [<value>]]` | Persistent config + on-demand derived stats |
| `reset` | — | Backup the DB and recreate empty schema |

Default scope is the current project. `--all-projects` widens. Date filters apply on top of any scope filter. Scope precedence on `exchanges`: `--session` > `--all-projects` > `--project` > current project.

## Concepts

- **Project** — Claude Code's encoded directory under `~/.claude/projects/`. Current project resolves from `CLAUDE_PROJECT_DIR` or git root.
- **Session** — top-level JSONL transcript, one per `claude` invocation.
- **Exchange** — the unit of conversation: one user message + the agent's full response (text, tool use, thinking, queued user input absorbed during the response) until the next user message.

Per-exchange time accounting: `total_s = user_time_s + agent_time_s + idle_s`.

- `user_time_s` — observable compose pause before this exchange (NULL when first event of session was the user_msg, or when the gap exceeded the threshold)
- `agent_time_s` — sum of below-threshold gaps on non-user_msg events (agent execution + reasoning + streaming)
- `idle_s` — sum of above-threshold gaps (walked-away time)

The threshold (default 15 min) is configurable via `settings threshold_min <value>`.

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
