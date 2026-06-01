# Transcripts — modernization plan

Active workstream to bring the `transcripts` skill up to its intended architecture. Two coupled gaps to close: where the DB lives, and how repeated content is stored. Authored 2026-05-21 against the current `plugins/transcripts/skills/transcripts/` skill (post-Phase-G compartmentalization, post-CLI-from-MCP migration). Unblocked + promoted to In progress 2026-05-31 (gating questions resolved; state-location framework retired).

This plan is the canonical "what's being done and why" for transcripts. Read it cold without conversation context. Cross-references at the bottom point at the design decisions and historical artifacts that fed into it.

---

## Background

The transcripts skill queries Claude Code session transcripts as structured data. JSONL transcripts at `~/.claude/projects/*.jsonl` are ingested into a SQLite DB; the skill exposes nine verbs over that DB (`projects`, `sessions`, `exchanges`, `descriptions-set`, `descriptions-clear`, `report`, `settings`, `init`, `reset`). Every read verb auto-syncs new JSONL lines before querying.

Two problems surface in the current implementation:

### Problem 1 — DB lives in the calling project's tree

The DB is resolved at `<CLAUDE_PROJECT_DIR>/.claude/transcripts/transcripts.db`, where `CLAUDE_PROJECT_DIR` falls back to `git rev-parse --show-toplevel` from cwd. The auto-sync ingests **all** sessions from `~/.claude/projects/` regardless of which project invoked the skill — so the DB in any given project's tree contains transcript content from every project the user has worked in.

Consequences:

- **Cross-project sensitive-content exposure.** If a user invokes transcripts from a project whose `.gitignore` doesn't cover `.claude/transcripts/*.db`, transcript content from unrelated projects can land in that repo's git history. The current claude-plugins repo gitignores it, but no other project automatically will.
- **DB sprawl.** Each project the user invokes transcripts from grows its own copy of the full corpus. At ~213 MB observed in this repo, that's substantial duplication.
- **No cross-project queries by default.** Each per-project DB has the full corpus, but per-project descriptions diverge.

### Problem 2 — Repeated content inflates storage and read context

Claude Code injects skill bodies, available-skills lists, hook outputs, and similar deterministic-marker content into the conversation stream. These appear in `events.text` for `user_msg` rows verbatim each time the same skill or hook fires. Empirical observation from the original transcripts friction log: skill-template injections inflate session text by 30–50%.

Consequences:

- **Storage bloat in the DB.** The same skill body is stored once per invocation across sessions.
- **Read-time context burn.** Any analytical consumer reading transcripts (agent or human) re-reads identical content repeatedly. With `exchanges --show messages` over a 60-exchange session this already exceeded the historical MCP response cap.

Both problems compound: a bigger DB in a wrong location is more damaging than a smaller DB in a wrong location, and a wrong location for a contaminated DB is worse than for a clean one.

---

## Decisions captured

### A. Storage location

**DB moves to `~/.claude/transcripts.db`** — a single top-level file under `~/.claude/`, no enclosing directory.

- Cross-project by design — one DB serves all projects the user works in.
- Project filtering remains at query time via existing `--project X` / `--all-projects` flags.
- **Default scope is current-project** (via `get_project_dir()`); `--all-projects` opts out. Preserves today's mental model — global default would surprise users used to per-project data.
- Top-level path under `~/.claude/` is the chosen convention for plugin state going forward. The earlier `~/.claude/plugins/data/<plugin>-<author>/` framework was retired 2026-05-31 — it assumed bin-mediated state (the ocd-run helper pattern) which the project no longer uses. New plugins choose their own top-level path; transcripts.db is the precedent.

**Mechanics:**

- `_environment.py` resolves DB path. Change the DB-path branch (currently `<project>/.claude/transcripts/transcripts.db`) to `~/.claude/transcripts.db`. The project-dir resolver itself (`get_project_dir`) stays — still needed for the current-project marker on `projects` and as the default filter for `sessions`/`exchanges` queries.
- `init` / `reset` target the new location.
- Auto-sync source unchanged (`~/.claude/projects/*.jsonl`).
- One-time migration: deletion is acceptable. Existing DBs at `<project>/.claude/transcripts/transcripts.db` should be wiped after confirming zero user-authored descriptions (the only non-derivable state). This repo's DB had zero; sweep other projects before deleting.
- Drop the `.gitignore` block at `claude-plugins/.gitignore:20-22` once the move ships.

### B. Content hash-reference table

**Repeated content is extracted into a hash-keyed reference table; the canonical `events.text` stores text with `[[ref:hash]]` substitutions.**

#### B.1 — Both storage-time and read-time dedup

- **Storage-time:** ingest extracts patterns into the references table; `events.text` is rewritten to carry refs in place of the matched body.
- **Read-time:** `exchanges --show messages` returns the ref-substituted text by default; opt-in expansion via flag (e.g. `--expand-refs all` or `--expand-refs <hash1>,<hash2>`).
- These are independent — storage-time delivers DB-size + future-read-cost wins automatically; read-time delivers per-read context-saving conditional on agent dereference discipline.

#### B.2 — References table scope: user-global

- Skill bodies repeat across **projects**, not just sessions in one project. Same skill invoked in 10 projects = 10 copies of the same body in a project-scoped references table.
- One references table at the user level amortizes maximally.
- Schema: same DB (`~/.claude/transcripts.db`) with a `references` table — simpler JOINs, atomic migrations, no cross-DB coordination.

#### B.3 — Reference format: opaque hash only

- Form: `[[ref:<hash>]]` — no embedded skill name, no version metadata, no display name.
- **Leading marker line stays in the text verbatim.** For skill-body injections, the line `Base directory for this skill: /path/to/skill` is per-message identifying context and is not part of the hashed payload. Only the body that follows becomes the ref. Result reads as:

  ```
  Base directory for this skill: /home/dev/.claude/skills/foo

  [[ref:a3f9d2bc8e1f…]]
  ```

- Rationale for opaque-hash-only:
    - A name embedded in the ref implies identity. Two skill versions with the same name have different content → different hash → must not be conflated.
    - Skills carry too much information to encapsulate meaningfully in a short name+version stub.
    - The leading marker already self-reads — the agent can identify content kind from the marker, then decide whether to dereference based on what it already knows in-session.
- Failure mode is safe: a `[[ref:nonexistent]]` ref renders as literal text. A broken or hand-edited ref doesn't corrupt downstream consumption — at worst, the message is slightly noisier than intended.

#### B.4 — Empirical validation before scale-up

The hinge question: when agents read transcripts containing refs, do they reflexively dereference everything (wiping the read-time win), or do they dereference surgically based on what they already know?

- Storage-time savings are mechanical and uncontested — they land regardless.
- Read-time savings depend on agent dereference behavior.

**Validation protocol** (Workstream B3 below): build the smallest viable extraction (skill bodies only, no other patterns), run an analytical agent task over a real corpus, measure dereference rate per skill body. If agents inflate every ref reflexively, ship storage-only and rethink the read-side. If they inflate surgically, ship both.

#### B.5 — Audit-doc-first extraction

Each extraction pattern is documented before deployment in `plugins/transcripts/skills/transcripts/extraction-patterns.md`. Each row captures:

- **Marker** — the regex or structural feature that identifies a candidate
- **Extraction range** — what gets hashed (which lines/bytes around the marker)
- **Hash strategy** — algorithm + canonicalization rules (e.g. trim trailing whitespace, normalize line endings)
- **Sample input** — a real example from the corpus
- **Sample output** — the rewritten text + the reference row payload
- **Status** — proposed / shipped / deprecated

This is governance, not implementation overhead. Patterns ship one at a time; each addition requires its row before the code change.

**Hard non-goal: fuzzy similarity.** No statistical text-repeat detection, no n-gram clustering, no "hash-map maze of reconstruction calls." Every pattern has a deterministic mechanical marker, or it doesn't ship.

#### B.6 — Initial extraction patterns

In priority order, smallest mechanical leverage first:

1. **Skill body injections** — marker: `Base directory for this skill:` at the start of the injection. Body: everything from the line after the marker through the end of the injection.
2. **Available-skills system reminders** — marker: `The following skills are available for use with the Skill tool:` inside `<system-reminder>` tags. Body: the bulleted skill list.
3. **CLAUDE.md system-prompt content** — marker structure TBD; CLAUDE.md content appears repeatedly per project. Lower priority because the marker isn't yet pinned.
4. **Hook output blocks** — `<user-prompt-submit-hook>` and similar wrapped sections. Repetition rate per session varies; investigate after 1 and 2.

Anything beyond this list waits for empirical evidence that the marker is reliable.

---

## Workstream A — Storage-location move (ship first)

Lower-risk refactor with immediate security win. Land before Workstream B so the content-dedup work happens in the right home.

### A1 — Path resolution

- `_environment.py`: add `get_db_path()` returning `~/.claude/transcripts.db`; replace project-derived DB-path callers with this.
- `_init.py`: `init` and `reset` target the new path.
- `get_project_dir()` updated to use the verified resolver chain (validated 2026-05-21 in interactive + headless `claude -p`):
    1. `CLAUDE_PROJECT_DIR` env var (honors explicit override / hook setups).
    2. `CLAUDE_CODE_SESSION_ID` → tail-scan `~/.claude/projects/*/<sid>.jsonl` for latest line with `cwd` field. Authoritative; handles non-git projects and mid-session cwd switches; inherited into sub-agents.
    3. `git rev-parse --show-toplevel` from cwd (tail safety net for early-session probes before first user-turn JSONL line).
    4. `_reject_if_inside_home` guard stays — plugin-cache git-checkout trap protection.
- Assertion landed 2026-05-21 at `plugins/skill-authoring/skills/skill-architecture/assertions/platform-discovery/project-dir-resolution.md` (status: confirmed, last-verified: 2026-05-21). A1 references it as the canonical source of truth for the resolver mechanism.

### A2 — Default-scope behavior (resolved)

- `sessions` / `exchanges` default to **current-project** filter (via `get_project_dir()`); `--all-projects` opts out.
- Preserves today's per-project mental model; global default would surprise users used to project-scoped data.
- Existing `--project <substring>` continues to work; `--all-projects` continues to bypass the filter.

### A3 — Migration handling

- Wipe-on-init: when the new path's DB is absent on first run, build fresh from `~/.claude/projects/`.
- Existing project-tree DBs become orphaned. Document in the SKILL that they can be deleted manually; descriptions in them are lost (consistent with "no user state in DB" being the design assumption — sweep before deleting).

### A4 — Gitignore cleanup

- Remove `.claude/transcripts/*.db` and `.claude/transcripts/*.db.backup-*` lines from `claude-plugins/.gitignore`.
- Add a note to the SKILL.md and the project's README if they reference the old path.

### A5 — SKILL.md updates

- Description (frontmatter) updated to reflect cross-project DB + current-project default scope.
- Argument-hint reviewed — no flag changes from A2 (defaults shift, flags unchanged).
- Process Model section: replace "The DB lives at `<project>/.claude/transcripts/transcripts.db`" with `~/.claude/transcripts.db`.

### A6 — Test pass

- Existing test suite (`plugins/transcripts/skills/transcripts/scripts/` — verify whether there's a tests/ dir, add if missing).
- New tests cover: path resolution returns `~/.claude/transcripts.db`; init creates the DB at that path; queries work against the new path; current-project marker still resolves correctly.

---

## Workstream B — Content hash-reference table

### B1 — Schema + extraction infrastructure

- New `references` table inside `~/.claude/transcripts.db`: `(hash TEXT PRIMARY KEY, payload TEXT NOT NULL, byte_size INTEGER, first_seen TIMESTAMP, hit_count INTEGER)`.
- Ingest pipeline gains an extraction stage between JSONL read and `events.text` write. The stage runs each registered pattern; on match, computes hash, upserts the references row (incrementing `hit_count`), and substitutes `[[ref:<hash>]]` in the text.
- `events.text` becomes "rewritten text" — original JSONL content is *not* stored in `events.text` for matched patterns. The references table is the truth for matched payloads; the JSONL is the original source of truth for everything.
- First pattern shipped: skill body injections.
- `extraction-patterns.md` row for skill bodies added before the code change.

### B2 — Read-side support

- New verb or flag for ref expansion. Tentative: `--expand-refs <all|none|hash,hash,...>` on `exchanges --show messages`.
- A SQL view materializes full-text messages (LEFT JOIN events to references, COALESCE the substitution back). The view is what `--expand-refs all` returns.
- Default behavior: refs in, no expansion. The agent or human consumer chooses to inflate.

### B3 — Empirical validation

- Test corpus: pick N=5–10 real sessions from `~/.claude/projects/` that contain multiple skill invocations and substantial agent analysis.
- Test query: spawn a sub-agent over a transcript-with-refs and ask a real analytical question (e.g. "what was the decision path on X").
- Measure: how many refs did the agent dereference vs total refs in the transcript; output quality vs un-extracted control.
- Decide based on results:
    - Surgical dereferencing → ship read-side as designed.
    - Reflexive full dereferencing → ship storage-only; rethink read-side presentation (different ref form? expansion-on-prompt? cache hint in the ref itself?).
- Document validation results in `extraction-patterns.md` skill-body row as evidence.

### B4 — Audit doc rollout

- `plugins/transcripts/skills/transcripts/extraction-patterns.md` ships as part of B1 with the skill-body row.
- Subsequent patterns (available-skills, CLAUDE.md, hooks) add rows before deployment.
- The doc is referenced from SKILL.md so consumers know how to read refs.

### B5 — Backfill

- One-shot pass over existing rows: apply all currently-deployed patterns to `events.text`, write refs.
- Idempotent — re-running over already-extracted rows is a no-op (extraction is deterministic; the marker won't match the substituted form).
- Run after B1 ships, before any analytical consumer is told to expect refs.

---

## Sequencing

```
A (storage location)
├── A1 path resolution
├── A2 default scope ✓ resolved (current-project default)
├── A3 migration
├── A4 gitignore cleanup
├── A5 SKILL.md updates
└── A6 tests
        ↓
B (hash-reference table)
├── B1 schema + skill-body extraction
├── B2 read-side expansion
├── B3 empirical validation  ← gate before scaling
├── B4 audit doc + further patterns (gated by B3 result)
└── B5 backfill
```

A is short; B has the empirical gate at B3. Don't ship B4 patterns until B3 results land.

---

## Open questions

1. **Hash algorithm + display.** sha256 (64 chars) vs sha1 (40 chars). Non-cryptographic dedup — sha1 is fine. Truncation in `[[ref:...]]` rendering: full hash, first 12, first 16? Affects readability vs collision-safety (collision prob is astronomically small at any reasonable truncation for dedup). Defer until B3.

2. **What does the navigator state-location migration look like once transcripts ships?** Same top-level-path pattern; target shape is `~/.claude/navigator.db` (or whatever the navigator's primary store is). Cross-reference once this plan completes.

(Closed questions — moved into Decisions captured above: default scope → A2 current-project; references table location → same DB; marker-in-hash → no, marker stays verbatim; state-location framework → retired 2026-05-31.)

---

## Cross-references

- **Original friction:** Pre-modernization, surfaced during 2026-05-01 consolidated-profile refresh. The skill-template injection observation drove Workstream B. The friction log itself (`logs/problem/transcripts.md`) was deleted on 2026-05-21; the substantive item is captured in B above.
- **Architecture context:** `plans/architecture-refactor.md` Phase D (transcripts CLI-from-MCP migration, completed 2026-05-19) and Phase G (plugin compartmentalization). This plan resumes where Phase D left off — the storage-location move was implicitly deferred during Phase D and never tracked.
- **MCP retirement:** `logs/decision/mcp-benching.md` — historical decision to bench MCP servers; transcripts portion executed in Phase D.

---

## Out of scope

- Verb-naming-rectification — broader project-wide naming plan (`logs/idea/verb-naming-rectification.md`); separate decision pending whether to revive or retire it.
- Navigator storage-location move — same top-level-path pattern as Workstream A; separate workstream once this plan ships.
- ocd-old Phase E migration — orthogonal.
- Performance work on the SQL queries themselves — only if validation surfaces query-side bottlenecks.
- Adding new report formats — `time-blocks` is the only one today; new formats are independent feature work.
