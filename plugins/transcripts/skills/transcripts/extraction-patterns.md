# Extraction patterns — references table audit

Canonical record of every pattern the transcripts skill extracts into the hash references table. One row per pattern. A pattern ships only after its row lands here with marker, hash strategy, sample input, and sample output. Status tracks lifecycle.

This doc is referenced from SKILL.md so consumers know how to read `[[ref:<hash>]]` substitutions. Rationale for the design lives in `plans/transcripts.md` Workstream B.

## Governance

- **Marker must be mechanically reliable.** A regex or structural feature that matches one thing unambiguously. Fuzzy similarity (n-gram clustering, statistical repeat detection) is a hard non-goal.
- **Hash strategy must be deterministic.** Canonicalize whitespace and line endings explicitly. Two identical-by-meaning payloads must hash to the same value; two semantically-different payloads must not.
- **Bad refs render as literal text.** Any pattern whose failure mode corrupts message content is rejected — only patterns whose worst case is "ref didn't resolve, message reads as `[[ref:abc]]`" are eligible.
- **Empirical evidence before scale-up.** First pattern (skill bodies) carries its B3-validation results inline. Subsequent patterns reuse the methodology and link to results.

## Patterns

### Skill body injections — proposed

- **Status:** proposed (not yet shipped). Awaiting Workstream B1 implementation per `plans/transcripts.md`.
- **Marker (regex):** `^Base directory for this skill: (?P<path>.+)$`, matched against `events.text` for `label = 'user_msg'` rows with `parent_message IS NULL`.
- **Extraction range:** from the line immediately after the marker line through the end of the message body. The marker line itself stays in `events.text`.
- **Hash strategy:** sha256 over the extracted body after canonicalization: strip trailing whitespace from each line, normalize line endings to `\n`, strip a single trailing newline. Algorithm/truncation may revise after B3.
- **Substitution:** body replaced with `[[ref:<hash>]]` on its own line.

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

TBD — populated after Workstream B3.

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
