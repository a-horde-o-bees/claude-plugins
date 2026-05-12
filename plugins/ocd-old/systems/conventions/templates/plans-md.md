# plans/ Conventions

Content standards for files under a system's `plans/` subdirectory. A plan is a strategy doc for one active or upcoming workstream — goal, output, sequence of work, locked decisions, open questions. Persists across sessions; rewritten as the workstream evolves.

## Purpose Statement

Opens with an L1 heading naming the workstream and a one-paragraph purpose statement: what this workstream produces and why it matters now. A reader landing on the file understands within those two lines whether the workstream is theirs to engage with.

## Body Structure

Sections by workstream lifecycle. Required sections:

| Section | Description |
|---------|-------------|
| `# <workstream>` | L1 heading naming the workstream |
| Purpose paragraph | What this workstream produces and why it matters |
| `## Goal` | One paragraph stating the desired end state |
| `## Output` | What deliverable lands when the workstream completes |
| `## Sequence` | Ordered phases or steps; checked off as they land |
| `## Decisions` | Locked decisions with one-line rationale each |
| `## Open questions` | Unresolved questions blocking forward motion (move to Decisions when answered) |

## Sequence Format

Each phase or step is a numbered entry with a brief outcome statement. Crossed-off entries (~~strikethrough~~) or `[x]`-prefixed entries indicate completion. The sequence rewrites as the workstream evolves — a plan reflects the latest understanding, not the historical journey.

```markdown
1. ~~Phase A — outcome that landed~~
2. Phase B — current focus
3. Phase C — upcoming
```

## Decisions Format

One bullet per decision. Each captures the choice made plus a one-line rationale. Decisions that exit the plan (e.g., implemented and stable) move to `logs/decision/<title>.md` for permanent record.

## Open Questions Format

One bullet per question. Each captures the question, optional context, and what blocks an answer. Resolved questions move to Decisions with rationale.

## Filename and Location

Plan files live at `<system>/plans/<workstream>.md`. Filename matches the workstream name (e.g., `setup-refactor.md`, `transcripts-user-scope.md`). Lowercase, kebab-case for multi-word names.

A plan listed by `<system>/CLAUDE.md`'s navigation index uses the same name in its purpose-statement entry.

## Lifecycle

Plans are mutable working documents. They rewrite freely as understanding evolves. When the workstream completes, the plan either:

- Stays in `plans/` archived (renamed with `_archived` suffix) if its content remains useful for future similar work
- Moves to `logs/decision/<title>.md` if its key choices warrant permanent decision-record status
- Deletes if the workstream's outcome is captured elsewhere (commits, decision logs, the system's regular docs)

A `plans/` directory should reflect active or imminent work, not historical workstreams.
