# Transcripts — modernization plan

Remaining work on the `transcripts` skill, in two independent workstreams: **B — content hash-reference table** (shrink the DB and read-time context by deduping repeated injected content) and **C — blocks & topics** (persist blocks as DB entities, add a topic axis, enable per-project billable-time reporting). Either may proceed first; they share only the additive-migration discipline (§C.5).

Read this cold, no conversation context. This is the canonical "what's being done and why" for transcripts. The workstream lettering starts at B because **Workstream A — the storage-location move (DB → `~/.claude/transcripts.db`, explicit `--project` for all per-project verbs) — shipped 2026-05-31** and is out of this plan; its letter is preserved only because external docs reference "Workstream B" by name.

Open questions a picker-up faces are surfaced first; design detail follows.

---

## Open questions

**Workstream B**

1. **Hash algorithm + display.** sha256 (64 chars) vs sha1 (40). Non-cryptographic dedup — sha1 is fine. Truncation in `[[ref:...]]` rendering: full hash, first 12, first 16? Readability vs collision-safety (collision prob is astronomically small at any reasonable truncation for dedup). Defer until B3.

**Workstream C**

2. **Billable-topic interface.** `--billable-topics a,b,c` (explicit, stateless) vs `--topics-from <file>` (project keeps a list) vs a project-config convention the report auto-reads. Stateless arg is simplest; a project file is more ergonomic for a recurring bill. Pick one before C-4.
3. **Topic vocabulary governance.** Free-text invites drift ("qbo-oauth" vs "oauth"). Worth a `block-list --topics` summary (distinct topics + counts) so a curator can spot and merge near-duplicates. Lightweight; no topics table.
4. **Auto vs manual block membership at coalescing.** The topic/summary judgment is LLM work; should the skill offer a "suggest blocks for unblocked exchanges" helper, or stay purely a store the report workflow writes to? Lean: store only; the workflow (LLM) decides grouping.

---

## Background

### Workstream B — Repeated content inflates storage and read context

Claude Code injects skill bodies, available-skills lists, hook outputs, and similar deterministic-marker content into the conversation stream. These appear in `events.text` for `user_msg` rows verbatim each time the same skill or hook fires. Empirical observation from the original transcripts friction log: skill-template injections inflate session text by 30–50%.

Consequences:

- **Storage bloat in the DB.** The same skill body is stored once per invocation across sessions.
- **Read-time context burn.** Any analytical consumer reading transcripts (agent or human) re-reads identical content repeatedly. With `exchanges --show messages` over a 60-exchange session this already exceeded the historical MCP response cap.

### Workstream C — Blocks are ephemeral, so scope and grouping have nowhere to live

The skill stores one **description** per exchange (`exchanges.description`, verb `descriptions-set`) and generates a `time-blocks` report (skill-orchestrated, see `_report-time-blocks.md`). A **block** groups exchanges that share a topic/focus; the report sums engaged time per block. But blocks exist only as text in rendered report files, recomputed by an LLM pass each run — the DB has only `events`, `exchanges`, `settings` (confirm: `sqlite3 ~/.claude/transcripts.db .tables`).

Two consequences the first real consumer (the Monaco ERP-migration project, which bills client time from these reports) hit:

- **Scope leaks into hard-coded exclusions.** With no persisted scope, billable-vs-not classification was redone each run and degraded into hard-coded session/exchange exclusion sets — unmaintainable, and they silently mis-fire as the corpus grows.
- **No grouping above the single block.** Related work recurs across many sessions (e.g. an OAuth thread spanning four sessions); the report can't express "these twelve blocks are all one concern."

The fix: persist blocks, let them span sessions, and add a broad **topic** label. Scope becomes a property of the topic, and billability becomes a small per-project **topic→billable** policy — reviewable, auditable ("why was this excluded?" → "its topic isn't billable"), and free of hard-coded refs.

---

## Decisions captured

### B — Content hash-reference table

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

### C — Blocks & topics

#### C.1 — Blocks are persisted in `~/.claude/transcripts.db`

Two new tables (not a project-local sidecar — blocks are a generic skill capability). The skill owns the mechanism; projects own the billable policy (C.4).

#### C.2 — Blocks may span session boundaries

A block's membership is a set of `(parent_session, exchange)` pairs that can reference **different** sessions. A block is the right grouping whenever its summary description holds across the member exchanges, regardless of which session they came from. One exchange belongs to **at most one** block (enforced by a unique index). This supersedes the current within-session-only coalescing in `_report-time-blocks.md` step 6.

#### C.3 — `topic` is a broad column on the block

A very short phrase naming the block's focus — deliberately **broader** than the per-block `summary`, so multiple blocks (and their summaries) sharing a concern collapse to one topic (e.g. summaries "OAuth writeback patch", "stale-token re-auth", "ngrok callback tunnel" → topic `qbo-oauth`). Free-text column on `blocks` (not a separate `topics` table) — dedup by string convention. Topics are assigned during coalescing by the same LLM pass that writes the summary, per `/writing:description-authoring`.

#### C.4 — Billability is a per-project policy over topics

The skill stays project-agnostic: it stores topics and offers **topic-filtered** querying/reporting (e.g. "include only blocks whose topic is in this set"). The *project* declares which topics bill. The skill never hard-codes billability. Interface options for the implementer are Open question 2. The consumer keeps its billable/non-billable topic list in its own repo.

#### C.5 — Migration MUST be additive (no wipe) — shared by B.1 and C.1

**Hard requirement for any new table (the `references` table in B and both block tables in C).** `_schema.py` enforces a strict rectify contract: a live DB either *matches* the canonical schema signature or is *divergent*, and the only built-in remediation for divergent is `--force`/`reset`, which **backs up and wipes**. Adding tables naively marks every existing `~/.claude/transcripts.db` divergent → the built-in fix would **destroy all user-authored `descriptions`**, which are the sole non-derivable state (re-sync re-ingests events from `~/.claude/projects/` but cannot restore descriptions).

`_settings.py` already establishes the codebase's non-destructive pattern: it `CREATE TABLE IF NOT EXISTS` + `ALTER TABLE ADD COLUMN` on the next init call, upgrading in place. Extend that: the init flow must **additively create new tables on existing DBs** rather than treating their absence as wipe-worthy divergence. New tables via `CREATE TABLE IF NOT EXISTS` never touch existing tables' data; the work is teaching `rectify`/init to treat "missing new table" as an additive upgrade. Verify against a *copy* of a real populated DB that descriptions survive.

---

## Workstream B — Content hash-reference table

### B1 — Schema + extraction infrastructure

- New `references` table inside `~/.claude/transcripts.db`: `(hash TEXT PRIMARY KEY, payload TEXT NOT NULL, byte_size INTEGER, first_seen TIMESTAMP, hit_count INTEGER)`. Add it additively per §C.5 (no wipe).
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

- `extraction-patterns.md` ships as part of B1 with the skill-body row.
- Subsequent patterns (available-skills, CLAUDE.md, hooks) add rows before deployment.
- The doc is referenced from SKILL.md so consumers know how to read refs.

### B5 — Backfill

- One-shot pass over existing rows: apply all currently-deployed patterns to `events.text`, write refs.
- Idempotent — re-running over already-extracted rows is a no-op (extraction is deterministic; the marker won't match the substituted form).
- Run after B1 ships, before any analytical consumer is told to expect refs.

---

## Workstream C — Blocks & topics

### C-1 — Schema + additive migration

DDL home: `plugins/transcripts/skills/transcripts/scripts/_db.py` (currently holds `events` + `exchanges`).

```sql
CREATE TABLE IF NOT EXISTS blocks (
    block_id    INTEGER PRIMARY KEY,
    topic       TEXT,              -- broad focus; shared across blocks (C.3)
    summary     TEXT,              -- the specific block description
    created_at  TEXT,
    updated_at  TEXT
);

CREATE TABLE IF NOT EXISTS block_exchanges (   -- membership; spans sessions (C.2)
    block_id        INTEGER NOT NULL,
    parent_session  TEXT    NOT NULL,
    exchange        INTEGER NOT NULL,
    PRIMARY KEY (block_id, parent_session, exchange)
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_block_exch_one_block
    ON block_exchanges(parent_session, exchange);   -- one block per exchange
CREATE INDEX IF NOT EXISTS idx_blocks_topic ON blocks(topic);
```

`(parent_session, exchange)` is the existing exchange identity (see the `exchanges` PK). Membership rows referencing a pruned/absent session are tolerated (a consumer may have lost a source transcript); readers must not assume every member exchange still resolves in `exchanges`/`events`. Add the tables additively per §C.5; test on a copy of a populated DB that descriptions survive.

### C-2 — Block verbs (`__main__.py`)

- `block-create --topic <t> --summary <s> --exchanges <session:exch,...>` → returns `block_id`. Accepts cross-session member lists.
- `block-set --block <id> [--topic ..] [--summary ..]`, `block-add-exchanges`, `block-remove-exchanges`, `block-delete`.
- `block-list [--project X | --all-projects] [--topic T]` → blocks with members + computed time.
- Batch-shaped where natural (mirror `descriptions-set`). Emit JSON like the other passthrough verbs.

### C-3 — Coalescing produces persisted blocks

- Revise `_report-time-blocks.md`: the coalescing step now (a) may group across sessions, (b) writes each block via the verbs with a `topic`, (c) persists once and is reused on later runs (don't re-coalesce already-blocked exchanges).
- The report step reads persisted blocks instead of recomputing them.

### C-4 — Topic-filtered time-blocks report

Fold the first consumer's hard-won report requirements into `report time-blocks`:

- **Billable filter:** include only blocks whose `topic` is in the project's billable set (interface = Open question 2).
- **Billing basis = Combined** (User+Agent engaged seconds); default output shows Combined only.
- **`--fill off|on` toggle (default off):** credit each *unobserved* compose pause one `avg_user_time_s`. Unobserved = `user_s` is NULL **or** 0. Rationale: `user_s` measures the compose gap only when ≤ the idle threshold; a real prompt typed after a long think, or typed-ahead during agent work, registers 0 (the wait is bucketed as `idle_s` on the prior exchange), so 0 ≠ zero effort. OFF bills only measured compose time (conservative); ON estimates true human engagement. Measured magnitude on the first consumer: fill moved User time ~47.5h→66.7h (≈12.6% of Combined).
- **Column header is "Summary Description"** (the stored field is `description`; "Purpose" was stale wording).
- **In-scope/billable only in output; a day with no billable blocks produces no file.**
- **Two-tier layout (consumer convention, keep generic):** top-level per-day = Combined (the bill); `detail/` per-day = User/Agent split (honours `--fill`); plus summaries and a span roll-up.

### C-5 — Docs + version + reinstall

- Update `SKILL.md`: new verbs; blocks can span sessions; topic concept; report's billable-topic filter + `--fill`.
- Update `_report-time-blocks.md` per C-3/C-4.
- Bump the plugin version; reinstall so the cache copy at `~/.claude/plugins/cache/a-horde-o-bees/transcripts/<version>/` and the marketplace mirror at `~/.claude/plugins/marketplaces/a-horde-o-bees/` pick up the change. **Never edit the cache copy directly — it is the build artifact.**

### First consumer / reference dataset

The Monaco ERP-migration project (`~/projects/monaco-lock-company--erp-migration`) drove Workstream C and is the test bed:

- **~1,534 exchanges across 18 sessions are already described** in the live DB (`--project monaco...`). Good real corpus for C-3/C-4.
- Consumer quirk to tolerate, not solve in the skill: one of Monaco's early sessions (2026-04-21..04-26) was pruned from `~/.claude/projects/`, so some blocks' member exchanges won't resolve — the skill needs only C.2's "tolerate absent members" guarantee. The recovered User/Agent split for those pruned days exists only in Monaco's git history (pre-deletion `logs/time-blocks/detail/2026-04-2x.md` in HEAD) — the durable source if those days ever need re-seeding.

The consumer's report requirements are captured forward in C-4 (Combined basis, `--fill` default off, billable-by-topic, "Summary Description"). No project-local prototype is retained on the Monaco side — the design here supersedes it entirely.

---

## Sequencing

```
B (hash-reference table)              C (blocks & topics)   ── independent of B
├── B1 schema + skill-body extraction ├── C-1 schema + additive migration
├── B2 read-side expansion            ├── C-2 block verbs
├── B3 empirical validation ← gate    ├── C-3 coalescing → persisted blocks
├── B4 audit doc + further patterns   ├── C-4 topic-filtered report (+ --fill)
└── B5 backfill                       └── C-5 docs + version + reinstall
```

B and C are independent — either order, or in parallel. Within B, don't ship B4's further patterns until the B3 empirical gate lands. Both B1 and C-1 add tables and so share the §C.5 additive-migration requirement; do that work once and reuse.

---

## Cross-references

- **Original friction (B):** Pre-modernization, surfaced during 2026-05-01 consolidated-profile refresh. The skill-template injection observation drove Workstream B. The friction log (`logs/problem/transcripts.md`) was deleted on 2026-05-21; the substantive item is captured in B above.
- **Architecture context:** the transcripts CLI-from-MCP migration (completed 2026-05-19) and plugin compartmentalization both shipped; see `logs/decision/mcp-benching.md` and `logs/decision/plugin-compartmentalization.md` (the former `architecture-refactor.md` plan was retired 2026-06-01).
- **Schema mechanics:** `scripts/_schema.py` (rectify-or-wipe contract), `scripts/_db.py` (events/exchanges DDL), `scripts/_settings.py` (the additive ALTER precedent to follow for §C.5).
- **Report workflow:** `skills/transcripts/_report-time-blocks.md`.

---

## Out of scope

- Navigator storage-location move — same top-level-path pattern as the shipped transcripts storage move; separate workstream, lands at `plugins/navigator/`.
- Verb-naming-rectification — broader project-wide naming plan (`logs/idea/verb-naming-rectification.md`); separate decision pending whether to revive or retire it.
- ocd-old Phase E migration — orthogonal.
- Performance work on the SQL queries themselves — only if validation surfaces query-side bottlenecks.
- Adding new report formats — `time-blocks` is the only one; C-4 enhances it, but new formats are independent feature work.
- The consumer's project-local report layout and billable-topic list — those stay in the consuming repo.
- Time-attribution model changes (the `user_s`/`agent_s`/idle bucketing) — the `--fill` toggle works within the existing model; reworking it is separate.
