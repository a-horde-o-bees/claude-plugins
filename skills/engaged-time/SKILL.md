---
name: engaged-time
description: "Engaged time reconstructed from raw Claude Code transcripts — the machine-evidenced active/idle split per session, project, and day, feeding rollups a consumer may bill on, plus an interactive swimlane timeline for exploring a session's anatomy (exchanges, time-blocks, coverage, the prompt queue)."
argument-hint: "<init [--root PATH] [--work PATH] | ingest [--file F | --dir D] [--db DB] | reset [--db DB] [--yes] | serve [--db DB] [--port N] | render [--db DB] [--lines N] [--out HTML] | exchanges (list | describe | topics | roots | threads | thread-list | thread-assign) | report [--topics …] | export --session ID --out FILE.md [--db DB]>"
allowed-tools:
  - Bash(uv run *)
---

# engaged-time

Engaged time reconstructed from raw Claude Code transcripts — the machine-evidenced active/idle split per session, project, and day, feeding rollups a consumer may bill on, plus an interactive swimlane timeline for exploring a session's anatomy (exchanges, time-blocks, coverage, the prompt queue).

This file is the entry contract: how to invoke, and which verb runs what. `ARCHITECTURE.md` defines the model and every term used here — read it before changing any verb.

## Invocation

The scripts are a self-contained stdlib package. Run any verb with `uv run` against the skill dir — no `cd` needed (`${CLAUDE_SKILL_DIR}` resolves it, and data paths are absolute, so cwd is irrelevant):

```
uv run ${CLAUDE_SKILL_DIR}/<script>.py <args>
```

Two path anchors, both stored by `init`. The **transcripts root** is the corpus this skill reads — it has no default, and every reading verb blocks without it. The **raw DB** (`~/.claude/engaged-time/raw.db`, moved by repointing the working dir via `ENGAGED_TIME_WORK` or `init --work`) is the shared substrate: `ingest` builds it, every other verb reads it. Rebuild after transcripts change — the raw DB is a cache, the corpus is the source.

Claude Code prunes the corpus on the `cleanupPeriodDays` timer, so raise it to cover the window you analyze — pruned sessions are unrecoverable and shorten every rollup silently. `init` reports the live value.

## Verbs

Each verb's process lives in its own file under `verbs/`. Signatures here; open the file for the step-by-step.

| Verb | Signature | Does | Process |
| --- | --- | --- | --- |
| **init** | `init [--root PATH] [--work PATH]` | Set or confirm both path anchors: the transcripts root to read (default `~/.claude/projects`) and the working dir every artifact lands in (default `~/.claude/engaged-time`). Run once first; re-runnable. Reports the corpus found and the live retention setting. | `verbs/ingest.md` |
| **ingest** | `ingest [--file F \| --dir D] [--db DB]` · `reset [--db DB] [--yes]` | JSONL → raw scratch DB; every line, nothing interpreted, sub-agent dir pulled in, idempotent per file. Bare, it takes the whole stored root. `reset` (gated) drops the cache for a clean rebuild. | `verbs/ingest.md` |
| **serve** | `serve [--db DB] [--port 8765]` | Launch the interactive flat-rail timeline UI (sessions as segments, time-blocks, coverage). The exploration surface. | `verbs/serve.md` |
| **render** | `render [--db DB] [--lines N] [--out HTML]` | Static single-session timeline HTML + its entity-key companion `.md`. For a fixed artifact, no server. | `verbs/render.md` |
| **exchanges** | `exchanges (list \| describe \| topics \| roots \| threads \| thread-list \| thread-assign) [--db DB] [--anno A]` | The persistent annotation store and the thread-first lineage `exchange → thread → topic → billable`: derive prompt-anchored exchanges, author each one's description, coalesce them into focus-threads, tag the threads with topics. What `report` bills on. | `verbs/exchanges.md` |
| **report** | `report [--topics …] [--from D --to D] [--format md\|csv]` | Roll up time-block coverage → engaged time per day and month, filtered through the thread lineage (time follows threads). The "Engaged Time Report" verb. | `verbs/report.md` |
| **export** | `export --session ID --out FILE.md [--db DB]` | One session's dialogue as readable markdown — user/agent messages only (no tool calls or thinking), horizontal rules between messages. Content-level reader; no timeline model involved. | `verbs/export.md` |

## Pipeline order

```
ingest ──> raw DB ──┬──> serve      (interactive)
                    ├──> render     (static HTML)
                    ├──> export     (session dialogue)
                    └──> exchanges ──> annotations DB ──> report  (engaged-time rollup)
```

## Diagrams

Sources live in `docs/`; generated HTML lands in the working dir's `diagrams/` (`~/.claude/engaged-time/diagrams/`).

- **`archmap.py` → `diagrams/archmap.html`** — the detailed architecture map: a clickable flow diagram plus a card per component showing its **file path** and the **functions/signatures it owns**, each with a hover tooltip = the symbol's docstring. Signatures are introspected live via `ast`, so they can't drift — **re-run after code changes**.
- **`docs/architecture.mmd` → `diagrams/architecture.html`** — the high-level systems/interfaces/ownership sketch (Mermaid; GitHub renders the `.mmd` inline). `mmd2html.py <file.mmd>` wraps any Mermaid source into a self-contained, browser-openable HTML (source inlined → works over `file://`, no server) with SVG/PNG export.
- CLI raster/vector export needs `npx @mermaid-js/mermaid-cli` (pulls a headless Chromium — not installed by default).

## Server lifecycle

`serve` is a long-running process. **Never `pkill -f swimlane_server`** — the pattern self-matches the launcher's own command line and kills the calling shell (exit 144). Kill by PID number. A code edit needs a restart to take effect (the geometry model is server-side). Full cycle in `verbs/serve.md`.

## Reference

- `DECISIONS.md` — why each mechanism is what it is, and the alternatives it beat.
- `swimlane_server_ui.md` — every element, encoding, and interaction on the live page `serve` renders.
