# Sandbox: ocd/transcripts

Generalize the transcript-extraction work scattered across personal projects into a single ocd skill that mines past Claude Code session transcripts for content worth persisting (decisions, friction, patterns, etc.).

## Pointers

- `logs/idea/Backfill decision rationale from transcripts.md` — the canonical idea this sandbox resolves; references a stale `~/projects/msp-psa-aggregator/.claude/scripts/` pointer that no longer exists
- `/home/dev/projects/job-search/transcripts/_transcripts.py` (2026-04-18, 8 KB) — newest, smallest variant; project-root `transcripts/` module with internal `_` prefix. Likely the latest generalized core
- `/home/dev/projects/claude-shell/.claude/scripts/transcripts/` (2026-03-16, paired `transcripts.py` + `transcripts_cli.py`) — older lib + CLI split, byte-identical to claude-code-workflow's copy
- `/home/dev/projects/claude-code-workflow/.claude/scripts/transcripts/` — same as claude-shell (synced copy)
- `/home/dev/projects/professional-portfolio/.claude/scripts/transcripts_cli.py` (2026-03-09, single file) — older single-file version
- `/home/dev/projects/no-kill-cat-collective/.claude/scripts/transcripts.py` (2026-03-01, single file) — oldest variant

## Tasks

- [ ] Read and compare the five extant variants; decide which is the canonical starting point (default: job-search's, given recency)
- [ ] Identify the public surface — what queries does the script answer (decisions in transcripts? all logged content? specific date ranges?)
- [ ] Decide skill shape — single verb (`/ocd:transcripts`) or multi-verb (`/ocd:transcripts mine | search | summarize | ...`)
- [ ] Port the chosen variant into `plugins/ocd/systems/transcripts/`
- [ ] Wire `ocd-run transcripts` CLI surface
- [ ] Write `SKILL.md` for the user-facing entry
- [ ] Add tests against fixture transcript files
- [ ] Update the `Backfill decision rationale from transcripts` idea log to point at the new skill (or remove it, since the work resolves the idea)
- [ ] Update ROADMAP/TASKS to reflect the merge

## Open Questions

- Does this skill consume transcripts from the global `~/.claude/projects/<project-id>/` location, or does it accept a path argument so it can also read transcripts from arbitrary sources?
- Should the skill emit candidates for the `/retrospective` skill to format, or own the full mine-and-format loop itself?
