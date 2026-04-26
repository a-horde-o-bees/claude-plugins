# Sandbox: ocd/transcripts

Generalize the transcript-extraction work scattered across personal projects into a single ocd skill that mines past Claude Code session transcripts for content worth persisting (decisions, friction, patterns, etc.).

Scope settled mid-sandbox: this sandbox ships only the **extraction substrate** (chat extraction + path gate). The mining layer that resolves the originating idea is left as future work, captured in the updated `Backfill decision rationale from transcripts` idea log.

## Pointers

- `logs/idea/Backfill decision rationale from transcripts.md` — updated to reflect substrate landed; mining layer remains unbuilt
- `logs/idea/Approval and permission signals export.md` — taxonomy preserved from the source `architecture.md` for a future `approvals_export` companion verb
- `/home/dev/projects/job-search/transcripts/` — canonical source variant (chosen over four older variants on recency and smallest surface)
- `plugins/ocd/systems/transcripts/` — ported destination
- `tests/plugins/ocd/systems/transcripts/` — 53 ported tests, all passing

## Tasks

- [x] Read and compare the five extant variants; decide which is the canonical starting point — picked job-search/transcripts/
- [x] Identify the public surface — extraction primitive only; no mining in this sandbox
- [x] Decide skill shape — multi-verb: `project_list | project_path | chat_export | chat_clean`
- [x] Port the chosen variant into `plugins/ocd/systems/transcripts/` — `_path_encode` and `project_current` both replaced by `project_path()` (uses `tools.environment.get_project_dir()`)
- [x] Wire `ocd-run transcripts` CLI surface — automatic via `run.py` auto-promotion of bare names to `systems.<name>`
- [x] Write `SKILL.md` for the user-facing entry — thin skill describing the four verbs
- [x] Add tests against fixture transcript files — 53 tests, full plugin suite (676 tests) green
- [x] Update the `Backfill decision rationale from transcripts` idea log to point at the new skill
- [x] Update ROADMAP to reflect the merge — Backfill entry rewritten; new Approval-signals entry added

## Resolved Open Questions

- **Does this skill consume from the global `~/.claude/projects/<project-id>/` location, or accept a path argument?** — Global only. `_user_dir()` derives from `tools.environment.get_claude_home() / "projects"`; there's no path-argument override. Tests redirect via `CLAUDE_HOME`.
- **Should the skill emit candidates for `/retrospective` or own the full mine-and-format loop?** — Neither. This skill is purely extraction. Mining is the unbuilt layer captured in the updated Backfill idea log.

## Ready to Unpack

All sandbox tasks complete. Next step: `/ocd:sandbox unpack ocd/transcripts` opens a PR to main.
