---
name: engaged-time
description: "Reconstruct and inspect engaged time from raw Claude Code transcripts via the timeline model — events → time-blocks → exchanges → topics, rendered as an interactive swimlane-timeline. Use to explore session anatomy (segments, time-blocks, coverage, the prompt queue) or to derive engaged-time rollups (which a consumer may bill on). Verbs: ingest, serve, render, exchanges, report."
argument-hint: "<init [--root PATH] [--work PATH] | ingest [--file F | --dir D] [--db DB] | reset [--db DB] [--yes] | serve [--db DB] [--port N] | render [--db DB] [--lines N] [--out HTML] | exchanges (list | describe | topics | roots | threads | thread-list | thread-assign) | report <scope> [--topics …] | export --session ID --out FILE.md [--db DB]>"
allowed-tools:
  - Bash(uv run *)
---

# /engaged-time

The engaged-time model. Reconstruct and inspect engaged time from raw Claude Code transcripts via the timeline model (events → time-blocks → exchanges → topics), rendered as a swimlane-timeline visualization. The model and its terms are defined in `ARCHITECTURE.md` — read it before changing any verb; this file is the verb index only.

## Invocation

The scripts are a self-contained stdlib package. Run any verb with `uv run` against the skill dir — no `cd` needed (`${CLAUDE_SKILL_DIR}` resolves it, and data paths are absolute, so cwd is irrelevant):

```
uv run ${CLAUDE_SKILL_DIR}/<script>.py <args>
```

Two path anchors. The **transcripts root** is the corpus this skill reads — stored once by `init`, with no default, and every reading verb blocks without it. The **raw DB** (default `~/.claude/engaged-time/raw.db`, override `ENGAGED_TIME_WORK`) is the shared substrate: `ingest` builds it; every other verb reads it. Rebuild after transcripts change — the raw DB is a cache, not a source; the corpus is.

Claude Code prunes the corpus on the `cleanupPeriodDays` timer, so raise it to cover the window you analyze — pruned sessions are unrecoverable and shorten every rollup silently. `init` reports the live value.

## Verbs

Each verb's process lives in its own file under `verbs/`. Signatures here; open the file for the step-by-step.

| Verb | Signature | Does | Process |
| --- | --- | --- | --- |
| **init** | `init [--root PATH] [--work PATH]` | Set or confirm both path anchors: the transcripts root to read (default `~/.claude/projects`) and the working dir every artifact lands in (default `~/.claude/engaged-time`). Run once first. Re-runnable — repointing `--work` warns about artifacts left at the old location. Reports the corpus found and the live retention setting. | `verbs/ingest.md` |
| **ingest** | `ingest [--file F \| --dir D] [--db DB]` · `reset [--db DB] [--yes]` | JSONL → raw scratch DB; every line, nothing interpreted, sub-agent dir pulled in, idempotent per file. Bare, it takes the whole stored root and blocks if unset. `reset` (gated) drops the cache for a clean rebuild. | `verbs/ingest.md` |
| **serve** | `serve [--db DB] [--port 8765]` | Launch the interactive flat-rail timeline UI (sessions as segments, time-blocks, coverage). The exploration surface. | `verbs/serve.md` |
| **render** | `render [--db DB] [--lines N] [--out HTML]` | Static single-session timeline HTML + its entity-key companion `.md`. For a fixed artifact, no server. | `verbs/render.md` |
| **exchanges** | `exchanges (list \| describe \| topics \| roots \| threads \| thread-list \| thread-assign) [--db DB] [--anno A]` | The persistent annotation store + the thread-first lineage (exchange → thread → topic → billable): derive prompt-anchored exchanges from the raw DB (UUID-keyed, consumed interjections folded in), author their `description`, coalesce each ROOT's exchanges into focus-`threads`, and assign each thread one `topic`. Two `/apply-over-queue` fan-outs hang off it — descriptions (`_annotate-corpus.md`) and per-root focus-synthesis (`_synthesize-focus.md`); topic assignment is a single global pass (`thread-assign`). | `verbs/exchanges.md` |
| **report** | `report [--topics …] [--from D --to D] [--format md\|csv]` | Roll up time-block coverage → engaged-time per day/month, filtered through the thread lineage (time follows threads). The "Engaged Time Report" verb. | `verbs/report.md` |
| **export** | `export --session ID --out FILE.md [--db DB]` | One session's dialogue as readable markdown — user/agent messages only (no tool calls or thinking), horizontal rules between messages. Content-level reader; no timeline model involved. | `verbs/export.md` |

The segment builder (`branch_tree.py`) and the geometry/accounting library (`swimlane_timeline.py`) are internal to `serve`/`render`/`report`, not user verbs — `ARCHITECTURE.md` documents them.

## Pipeline order

```
ingest ──> raw DB ──┬──> serve   (interactive)
                    ├──> render  (static HTML)
                    └──> report  (engaged-time rollup)
```

## Diagrams

Sources live in `docs/`; generated HTML lands in the working dir's `diagrams/` (`~/.claude/engaged-time/diagrams/`).

- **`archmap.py` → `diagrams/archmap.html`** — the detailed architecture map: a clickable flow diagram plus a card per component showing its **file path** and the **functions/signatures it owns**, each with a hover tooltip = the symbol's docstring. Signatures are introspected live via `ast`, so they can't drift — **re-run after code changes**.
- **`docs/architecture.mmd` → `diagrams/architecture.html`** — the high-level systems/interfaces/ownership sketch (Mermaid; GitHub renders the `.mmd` inline). `mmd2html.py <file.mmd>` wraps any Mermaid source into a self-contained, browser-openable HTML (source inlined → works over `file://`, no server) with SVG/PNG export.
- CLI raster/vector export needs `npx @mermaid-js/mermaid-cli` (pulls a headless Chromium — not installed by default).

## Server lifecycle

`serve` is a long-running process. **Never `pkill -f swimlane_server`** — the pattern self-matches the launcher's own command line and kills the calling shell (exit 144). Kill by PID number. A code edit needs a restart to take effect (the geometry model is server-side). Full cycle in `verbs/serve.md`.
