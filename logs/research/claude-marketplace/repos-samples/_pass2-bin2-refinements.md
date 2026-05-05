# Pass 2 Refinements — Bin 2

Proposed refinements to `_CONSOLIDATED_breadth-then-depth.md` from rewriting samples in this bin. The reconciler integrates accepted refinements into the next consolidated revision.

## Proposed new paths

> Format: `<role> > <new-path>` — supporting samples — qualitative description draft

- `State persistence > Identity-transition compat layer for env vars and data dirs` — Arcanon-hub/arcanon — Every runtime surface honors both new (`ARCANON_*`) and legacy (`LIGAMEN_*`) env-var spellings, and data-dir/config-file resolvers fall back from `~/.arcanon/` to `~/.ligamen/` when the new dir does not exist. Pattern applies any time a plugin renames itself: covers env vars (`ARCANON_API_KEY`/`LIGAMEN_API_KEY`, `ARCANON_WORKER_PORT`/`LIGAMEN_WORKER_PORT`, `ARCANON_DATA_DIR`/`LIGAMEN_DATA_DIR`, `ARCANON_DISABLE_GUARD`, `ARCANON_DISABLE_SESSION_START`, `ARCANON_EXTRA_BLOCKED`, etc.), data-dir resolver in `lib/data-dir.sh`, and config files (`arcanon.config.json` preferred, `ligamen.config.json` honored). Distinct from `Channel distribution > Single channel with version-reset across rebrand` (which describes the marketplace-side identity break) — this is the runtime-side bridge for users mid-transition.

- `Install change detection > Dual-manifest sentinel-vs-real-dep-source split` — Arcanon-hub/arcanon — A separate sentinel manifest (`runtime-deps.json`) coexists with the manifest npm actually reads (`package.json`); the sentinel is the diff source for idempotency, the package.json is the install source. They can drift; the convention is undocumented in the repo-root README and only surfaces in internal planning docs. Distinct hazard from a hash-based detection: a byte-identical sentinel gives false-OK when package.json has drifted away from it.

- `State persistence > Cross-session correction-learning SQLite` — BULDEE/ai-craftsman-superpowers — `metrics.db` (SQLite) plus `session-state.json` track violation fixes across sessions; SessionStart injects a `Learning: PHP001 fix rate 78%` clause into the rendered `systemMessage` derived from cross-session correction trends. Persistence is local per-machine — no cloud sync. Distinct from generic SQLite state because the data drives a self-modifying agent prompt at session boundaries, not just observability. Cross-references the existing `SQLite for behavioral metrics` path but adds the specific feedback-into-prompt loop.

- `Long-running scheduled behavior > Cron shepherd with durable tracking issue + InstructionsLoaded nudge` — BaseInfinity/sdlc-wizard — Three composing pieces: cron workflow polls an external source (release feed, API changelog, community forum), opens or updates a single tracking GitHub issue with a structured JSON body (`relevance`, `summary`, `impact`), and `InstructionsLoaded` hook surfaces the open issue at next session start. Replaces `monitors.json` for external-change watching while extending it into durable issue tracking — the "where did I leave off" cursor lives in committed state files (`.github/last-checked-*.txt`) and the user-visible artifact lives in GitHub Issues. Distinct from existing `Outsourced to GitHub Actions cron` because the differentiator is the cron→issue→hook chain, not the cron alone.

## Proposed description sharpenings

> Format: `<role> > <existing-path>` — what the existing description misses; supporting samples; sharpening suggestion

## Proposed new roles

> Format: `<new-role>` — what role this is, why it doesn't fit any existing role, supporting samples

## Proposed bucket splits

> Format: `<role> > <existing-path>` — why it should split, into what, supporting samples

## Structural concerns

> Anything that's hard to fit cleanly under any role/path; questions for the reconciler
