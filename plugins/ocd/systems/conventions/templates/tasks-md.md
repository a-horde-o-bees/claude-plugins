---
includes: "**/TASKS.md"
---

# TASKS.md Conventions

Content standards for `TASKS.md` — the persistent task tracker at a system's root. Each entry tracks one piece of work; sections group entries by status. Distinct from session-scoped tracking (TaskCreate manages the current session's checklist; `TASKS.md` survives session clears).

## Purpose Statement

Opens with an L1 heading `# Tasks` (or system-qualified, e.g., `# Tasks — <system>`) and a brief paragraph: what this tracker covers and how to read it. A reader landing on the file understands the section model and where to look for active work.

## Section Model

Sections organize entries by status, in the order a reader scans:

| Section | Contents |
|---------|----------|
| `## In progress` | Tasks currently being worked. Should be 1–3 entries; more signals fragmented attention. |
| `## Pending` | Tasks ready to start when capacity opens — preconditions met, scope clear. |
| `## Upcoming` | Tasks that will be ready soon — preconditions not yet met, or scope still being clarified. |
| `## Done` | Recently completed tasks. Migrate older entries to commit history or decision logs. |

Empty sections may be omitted; a section with no entries adds noise without information.

## Entry Format

Each entry is one bullet with these fields:

- **Title** — short imperative phrase naming the task
- **Pointer** (optional) — link to a `plans/` file, decision document, or relevant log entry when context is non-trivial
- **One-line summary** — what the task does and why it matters

```markdown
- **Migrate transcripts to user scope** — [plan](plans/transcripts-user-scope.md). Move DB to `~/.claude/ocd/transcripts/`; update setup handler scope matrix.
- **Add operational CLI gating to navigator** — block `ocd-run navigator scan` when not installed; pattern from `plugin-system.md`.
```

Entries longer than two lines indicate the task carries enough context to warrant a `plans/` doc; extract and reference.

## Cross-References

`TASKS.md` is the entry point for active work; details live in `plans/<workstream>.md` or decision documents. The `TASKS.md` line is the index; it should not duplicate plan content.

When a task closes:

- Migrate the entry from `## In progress` or `## Pending` to `## Done`
- The plan moves per the `plans-md.md` lifecycle (archive, decision log, or delete)
- Older `## Done` entries periodically migrate to `logs/decision/` or get pruned — `TASKS.md` reflects recent completions, not full history

## Lifecycle

`TASKS.md` is a mutable working document. It updates freely as work progresses. The persistent value is in the *current* state of work, not its history; commit history captures the journey.
