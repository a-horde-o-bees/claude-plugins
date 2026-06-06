---
name: transcripts
description: Query Claude Code session transcripts as structured data — projects, sessions, exchanges (user_msg + agent response groups), with time accounting, full chat content, and persistent per-exchange descriptions. Group exchanges into cross-session blocks tagged by topic for per-project billable-time reporting. Backed by a SQLite DB at `~/.claude/transcripts.db` ingested from `~/.claude/projects/`; repeated injected content (skill bodies) is deduped into a hash-reference table. Per-project verbs require explicit `--project X` or `--all-projects`; run `projects` to list available names. Default-lean output; opt into detail (messages, metrics, timeframes) via `--show`. Auto-syncs new lines on every query.
argument-hint: "<projects | sessions (--project X | --all-projects) [--from D --to D] [--show timeframes bytes] | exchanges (--project X | --session Y [--range R] | --all-projects) [--from D --to D] [--show messages active breakdown metrics timeframes] [--expand-refs all|none|hash,...] | descriptions-set <session> <json> | descriptions-clear <session> <exchange ...> | block-create [--topic T --summary S --exchanges S:E,...] | block-set --block ID [--topic T] [--summary S] | block-add-exchanges --block ID --exchanges S:E,... | block-remove-exchanges --block ID --exchanges S:E,... | block-delete --block ID | block-list (--project X | --all-projects | --session Y) [--topic T] [--billable-topics a,b,c] [--topics] [--fill off|on] | refs [--limit N | --expand <hash>] | backfill | report [<format> [--project X | --all-projects] [--from D --to D] [--billable-topics a,b,c] [--fill off|on]] | settings [<key> [<value>]] | init [--force] | reset>"
allowed-tools:
  - Bash(python3 -m scripts:*)
  - Bash(python -m scripts:*)
---

# /transcripts

Query Claude Code session transcripts. Each verb emits JSON; `report` is skill-orchestrated and emits markdown. The Python package lives at `scripts/`; the agent invokes via `python3 -m scripts <verb> [args]` from the skill directory (no external dependencies — sqlite3 stdlib).

## Process Model

The DB lives at `~/.claude/transcripts.db` — a single top-level file under Claude home, shared across every project the user works in. Initialize via `init` (or `reset` to wipe + rebuild). Every verb other than `init`/`reset` auto-syncs new transcript lines from `~/.claude/projects/` (Claude Code's session-log directory — distinct from the skill's DB) before querying.

Verbs:

| Verb | Effect |
|------|--------|
| `projects` | List all projects present in the DB |
| `sessions` | Session metadata; default-lean ({project, session, n_exchanges, n_described}); `--show` opts into timeframes/bytes |
| `exchanges` | Per-exchange rows; default-lean ({project, session, exchange, description}); `--show` opts into messages/active/breakdown/metrics/timeframes; `--expand-refs` expands `[[ref:hash]]` tokens in messages |
| `descriptions-set` | Batch upsert per-exchange descriptions from a JSON map |
| `descriptions-clear` | Batch clear per-exchange descriptions |
| `block-create` / `block-set` / `block-add-exchanges` / `block-remove-exchanges` / `block-delete` | Manage persisted blocks — topic + summary + cross-session members |
| `block-list` | Blocks with members + engaged time; `--topic`/`--billable-topics` filter, `--topics` returns the topic vocabulary, `--fill` toggles compose-pause crediting |
| `refs` | Inspect the content hash-reference table (dedup audit; `--expand <hash>` prints a payload) |
| `backfill` | Apply extraction patterns to existing rows in place (idempotent) |
| `report` | List available report formats (no args); generate the named format with `<format>` (currently: `time-blocks`). Skill-orchestrated, not a passthrough |
| `settings` | Show or update persistent config; lists derived stats |
| `init` | Rectify the DB to the canonical schema — adds new tables (refs/blocks) to an existing DB additively, no wipe. `--force` backs up and rebuilds a genuinely-conflicting schema |
| `reset` | Backup the DB and recreate empty schema |

Passthrough verbs emit JSON; errors arrive on stderr as `{"error": "..."}` with exit code 1. `report` emits markdown per its format component file.

`exchanges` returns an array. Default row is lean — opt into detail via `--show`:

```json
[
  {
    "project": "-home-dev-projects-...",
    "session": "1e010e82-...",
    "exchange": 5,
    "description": null
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
    "description": null,
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

`projects` returns `{projects[]}`. `sessions` returns `{filter, n_sessions, sessions[]}`. `settings` returns `{config, derived}`.

## Scope

The unit hierarchy: **project → session → exchange**.

- **Project** — Claude Code's encoded directory under `~/.claude/projects/`, e.g., `-home-dev-projects-monaco`. Run `projects` to list available names; pass one via `--project X` on the per-project verbs.
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

Scope on `sessions` and `exchanges` is required, not defaulted: pass `--project X` (substring match against project names — run `projects` for the list), `--all-projects` (every project), or for `exchanges` `--session Y` (single session). The CLI rejects invocations missing an explicit scope. Date filters `--from D --to D` apply on top.

**Descriptions** are persistent per-exchange annotations stored in the `exchanges` table. Write each per /author-descriptions — one line, scope + role, no mechanics, no history. They survive sync; only `reset` wipes them. `sessions` reports `n_described` per session; `exchanges` includes the `description` field per row (null when unset). When an agent reads an exchange's content and would benefit from re-finding it later, author a description and persist via `descriptions-set`. Both write verbs are batch-shaped — single-key maps and one-element lists handle the singular case naturally.

**Blocks & topics** group exchanges above the single-exchange level, persisted in the `blocks` / `block_exchanges` tables. A **block** is a set of `(session, exchange)` members — which **may span sessions** — sharing a focus, carrying a `summary` (specific) and a `topic` (broad, shared across blocks). One exchange belongs to at most one block. `block-list` computes engaged time per block from the member exchanges' metrics; the `--fill` toggle decides whether unobserved compose pauses (`user_s` NULL or 0) are credited one `avg_user_time_s` (on) or zero (off, the default, billing only measured time). The skill stores no billability — `--billable-topics a,b,c` filters blocks to a topic set the *consuming project* supplies, and `--topics` returns the topic vocabulary (distinct topics + counts + time) to evaluate against before billing. The `report time-blocks` workflow drives coalescing into persisted blocks and renders the billable, two-tier per-day report.

**Content references.** Repeated injected content (currently skill-body injections) is deduped at ingest into the `refs` table; `events.text` carries a `[[ref:<hash>]]` token in place of the body, with the identifying marker line kept verbatim. Message text reads with refs in place by default; `exchanges --show messages --expand-refs all` (or a comma-separated hash list) substitutes payloads back. An unresolved token renders as literal text — the safe failure mode. `refs` audits the table; `backfill` applies extraction to rows ingested before the feature shipped (idempotent). See `extraction-patterns.md` for the pattern catalog and validation.

## Rules

- Passthrough verbs emit JSON only — no text formatting toggle. `report` emits markdown per its format component file.
- `--range` is only meaningful with `--session`; ignored otherwise.
- `--show` accepts space-separated bucket names; unknown values raise a validation error.
- `descriptions-set` JSON map keys must coerce to integer exchange numbers (e.g. `'{"5": "...", "12": "..."}'`).
- `reset` backs up to a timestamped sibling file before wiping. Use when schema migrations land or to start fresh.
- Agents that need cross-project rollups iterate via `projects` → `sessions --project X` → `exchanges --session Y`. The CLI does not aggregate across projects in a single call by design.
- Older project-tree DBs (`<project>/.claude/transcripts/transcripts.db` or `<project>/.claude/ocd/transcripts/transcripts.db`) become orphaned by the move to `~/.claude/transcripts.db` — `init` will not migrate them. Delete them manually; descriptions in them are lost (sweep before deleting if you authored any).

## Workflow

1. If not $ARGUMENTS: Exit process: skill description and argument-hint
2. {verb} = first token of $ARGUMENTS
3. {verb-args} = remainder of $ARGUMENTS after {verb}

    > Most verbs run the Python CLI in `scripts/`. `report` is skill-orchestrated — it dispatches to a format-specific component file that drives a multi-step workflow.
4. If {verb} is `report` (skill-orchestrated):
    1. {format} = first token of {verb-args}
    2. {format-args} = remainder of {verb-args} after {format}
    3. If not {format}: Exit process: available report formats — `time-blocks`
    4. Else if {format} is `time-blocks`: Call: `_report-time-blocks.md` ({format-args} = {format-args})
    5. Else: Exit process: unrecognized format {format} — expected `time-blocks`
5. Else if {verb} ∈ {projects, sessions, exchanges, descriptions-set, descriptions-clear, block-create, block-set, block-add-exchanges, block-remove-exchanges, block-delete, block-list, refs, backfill, settings, init, reset} (passthrough):
    1. bash: `cd <THIS-FILE-DIR> && python3 -m scripts {verb} {verb-args}`
6. Else: Exit process: unrecognized verb {verb} — run with no args for the verb list

**Important:** the `cd <THIS-FILE-DIR>` is required so Python can find the `scripts` package. The skill no longer resolves a "current project" from cwd, env, or git — the project is always an explicit `--project` argument. `CLAUDE_HOME` overrides `~/.claude` if set; otherwise the DB lives at `~/.claude/transcripts.db` regardless of where the verb is invoked from.

### Report

Every verb except `report` is a passthrough: it emits JSON on stdout, and errors arrive on stderr as `{"error": "..."}` with exit code 1. The `report` verb is skill-orchestrated and emits markdown rendered per the format component file (e.g., `_report-time-blocks.md`), driving block coalescing and the two-tier billable report.
