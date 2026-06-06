# Extraction patterns — references table audit

Canonical record of every pattern the transcripts skill extracts into the hash references table. One row per pattern. A pattern ships only after its row lands here with marker, hash strategy, sample input, and sample output. Status tracks lifecycle.

This doc is referenced from SKILL.md so consumers know how to read `[[ref:<hash>]]` substitutions. Rationale for the design lives in `plans/transcripts.md` Workstream B.

The extracted payloads live in the `refs` table (`hash` PK, `payload`, `byte_size`, `first_seen`, `hit_count`) — named `refs` rather than `references` because the latter is a SQL reserved word. The token form is `[[ref:<hash>]]` with the full sha256 hash. `events.text` stores the rewritten text; expansion is read-side and opt-in (`exchanges --expand-refs`).

## Governance

- **Marker must be mechanically reliable.** A regex or structural feature that matches one thing unambiguously. Fuzzy similarity (n-gram clustering, statistical repeat detection) is a hard non-goal.
- **Hash strategy must be deterministic.** Canonicalize whitespace and line endings explicitly. Two identical-by-meaning payloads must hash to the same value; two semantically-different payloads must not.
- **Bad refs render as literal text.** Any pattern whose failure mode corrupts message content is rejected — only patterns whose worst case is "ref didn't resolve, message reads as `[[ref:abc]]`" are eligible.
- **Empirical evidence before scale-up.** First pattern (skill bodies) carries its B3-validation results inline. Subsequent patterns reuse the methodology and link to results.

## Patterns

### Skill body injections — shipped

- **Status:** shipped (storage-time + read-side). Extraction runs in `_ingest.insert_events` for newly-inserted rows; `backfill` applies it to pre-existing rows; expansion is `exchanges --expand-refs`. Code: `scripts/_references.py`.
- **Marker:** text that *begins with* the line `Base directory for this skill: <path>`. Matched structurally (`text.startswith("Base directory for this skill: ")`), label-agnostic — the injection appears on `user_msg`, `sidechain_user_msg` (subagent skill loads), and occasionally `assistant` rows; all carry the same dedupable body. Only leading-marker text is extracted; the 15 corpus rows where the marker appears mid-text are left untouched.
- **Extraction range:** everything after the first newline (the body), with the marker line kept verbatim in `events.text`. The marker is per-message identifying context (which skill, which path) and is not part of the hashed payload.
- **Hash strategy:** full sha256 over the canonicalized body — normalize line endings to `\n`, strip trailing whitespace per line, strip leading/trailing blank lines. Identical bodies across contexts collapse to one hash; the marker-line path difference does not affect the hash. Truncation in the token (Open question 1) was not adopted — the full hash is used.
- **Substitution:** body replaced with `[[ref:<hash>]]` on its own line after the marker line.
- **Idempotency:** a body that is already a `[[ref:...]]` token is never re-extracted, so ingest re-runs and repeated `backfill` are no-ops.

#### Sample input

```
Base directory for this skill: /home/dev/.claude/skills/concise-prose

# /concise-prose

Use whenever the agent is writing or editing prose...

[full skill body continues]
```

#### Sample output

`events.text`:
```
Base directory for this skill: /home/dev/.claude/skills/concise-prose

[[ref:a3f9d2bc8e1f...]]
```

`references` row:
- `hash`: `a3f9d2bc8e1f...` (full sha256 of canonicalized body)
- `payload`: `# /concise-prose\n\nUse whenever the agent is writing or editing prose...\n[full body]`
- `byte_size`: length of payload
- `first_seen`: timestamp of first ingest
- `hit_count`: incremented on every subsequent match of the same hash

#### Validation results

**Storage-time (mechanical, banked).** Backfill over the reference corpus (139,484 events, 19 projects) extracted 364 skill-body injections into **145 unique refs**, collapsing **855 KB** of duplicated payload (`refs.dedup_bytes_saved`). The most-reused body (`/author-processes`, ~11 KB) recurred 16×. Storage-time wins are uncontested and land regardless of the read-side question.

**Read-time (mechanical).** Across the 43 sessions that contain refs, leaving tokens unexpanded saves **1.24 MB — 7.5%** of total user/assistant message bytes; on the heaviest skill-using session it avoids **25%** inflation. The whole-session figure is below the original 30–50% friction-log estimate because that estimate was per-injection, not per-session — skill bodies are a large fraction of an injection message but a smaller fraction of an entire transcript.

**Read-time (behavioral) — the open gate.** The mechanical read-time saving is realized only if an analytical agent dereferences *surgically* rather than reflexively expanding every ref. That behavioral question is unmeasured here: a realistic probe needs refs deployed to a live DB an agent queries (this build verified only against DB copies, not the user's live DB). Protocol when run: point a sub-agent at a ref-bearing corpus, pose an analytical question, and measure expanded-refs ÷ total-refs. Surgical → keep the read-side default as shipped (refs in, opt-in expand); reflexive → the storage win still stands and the read-side flag remains harmless (default expands nothing). Either outcome leaves the shipped mechanism correct; the gate tunes guidance, not code.

---

## Pending patterns (not yet detailed)

These are queued per `plans/transcripts.md` Workstream B6 priority order. Each gets a full section above before it ships.

- **Available-skills system reminders** — marker: `The following skills are available for use with the Skill tool:` inside `<system-reminder>` tags. Body: the bulleted skill list.
- **CLAUDE.md system-prompt content** — marker structure to identify; deterministic per project.
- **Hook output blocks** — `<user-prompt-submit-hook>` and similar wrapped sections.

---

## Out of scope (explicit non-patterns)

- Statistical text-repeat detection across messages without a fixed marker.
- Per-session "frequent strings" extraction.
- Compression schemes other than reference substitution.
- Lossy summarization of any kind.
