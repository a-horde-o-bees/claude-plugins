---
name: retrospective
description: Wrap a session by surfacing patterns, friction, ideas, decisions, and other observations worth persisting before context goes stale. Walks the session, classifies candidates against each log type's `_template.md`, flags refinements to existing entries, surfaces user-memory candidates, and presents drafts for explicit user review. Nothing is written without acceptance.
argument-hint: ""
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
---

# /retrospective

Active reflection at session end — surface patterns, friction, ideas, decisions, problems, research seeds, refinements to existing logs, and user-memory updates that the agent's normal flow would miss. The session's existing log taxonomy (`logs/<type>/_template.md`) defines what qualifies; the skill's value is the *prompts* that produce candidates the user then accepts, edits, or rejects.

## Process Model

Three passes, in order:

1. **Type-aligned walk** — for each log type, read its `_template.md`, then surface session content matching its `What Qualifies` criteria. Same walk asks: does anything from the session sharpen an *existing* entry of this type?
2. **Memory walk** — separate from logs, surface user-scoped observations (role, preferences, validated approaches, project-level context).
3. **What-else pass** — open-ended; capture observations that didn't fit any type. May signal a new log type, conversational feedback, or just shared context worth flagging.

Each pass produces draft candidates. All drafts batch-present at the end; the user accepts/edits/rejects per item. Nothing is written without explicit acceptance.

## Reflection Prompts

The active prompts that produce non-obvious candidates. Apply during the type-aligned walk, plus the cross-cutting prompts at the end.

### Per log type

- **decision** — what choices were made with rejected alternatives that future sessions need? What's not derivable from code or git history alone?
- **friction** — what fought us? Where did the system force a workaround that's queued for fixing? Logged or no?
- **idea** — what got mentioned but deferred? What "we should…" went unwritten?
- **pattern** — what reusable workflow shape emerged or got refined? What approach worked that could apply beyond this session?
- **problem** — what defect or gap was observed but not yet fixed?
- **research** — what subject accumulated enough sample evidence to warrant systematic investigation?

### Cross-cutting (apply once at the end of the type walk)

- What did we build with reuse potential beyond this work?
- What pattern emerged by elimination — what we did NOT do that turned out to matter?
- What pivots happened — what did the original framing miss?
- What existing log entry got sharpened by this session and should be *updated*, not added to?

### Memory candidates

- What about the user's role, preferences, or responsibilities did we learn?
- What corrections did the user make that should not need to be made again?
- What approaches did the user validate (sometimes quietly, by acceptance) that should be repeated?
- What project-level context will future sessions need that isn't in the code?

### What-else

- What from this session was notable but didn't fit any of the above? Where should it live — a new log type? user feedback? just shared context?

## Workflow

```
1. Read each `logs/<type>/_template.md` in the project — these are the qualifying criteria for classification
2. List existing entries per type (Glob `logs/<type>/*.md` excluding `_template.md`) — so refinement candidates can be checked against actual content
3. Apply the type-aligned walk:
    1. For each {type} in {decision, friction, idea, pattern, problem, research}:
        1. Apply that type's reflection prompt against the session
        2. {new-candidates} += matching observations as new-entry drafts
        3. For each existing entry of {type}: did the session sharpen it? If yes: {refinement-candidates} += diff draft
4. Apply cross-cutting prompts — surface anything caught at the type-walk level missed
5. Apply memory-candidate prompts — gather user-scoped observations as memory drafts
6. Apply what-else prompt — gather off-axis observations
7. Present all candidates as a single batch:
    - For each: type / target path / rationale (one sentence) / draft content
    - Refinements show diff preview, not just prose
    - Memory candidates show frontmatter + body
    - What-else items show observation + proposed disposition
8. For each candidate, ask user: accept / edit / reject
9. Apply accepted candidates:
    1. New log entries: read `logs/<type>/_template.md` for structure, then Write `logs/<type>/<title>.md`
    2. Refinements: Edit the existing entry per draft
    3. Memory candidates: Write to user memory at `~/.claude/projects/<project-id>/memory/<name>.md` and update `MEMORY.md` index
    4. What-else: present to user as-is — no auto-write; user decides whether to capture later
10. Return to caller: list of items written, refined, captured-to-memory, or surfaced-only — with their destinations
```

## Rules

- Never auto-write — every persisted candidate requires explicit user acceptance
- Read `_template.md` for each log type before classifying — don't reinvent What Qualifies; the templates are the source of truth
- For refinement candidates, present a diff preview against the existing entry — the user reviews the actual change, not a prose summary of intent
- Memory candidates use user-memory infrastructure (project-scoped under `~/.claude/projects/<project-id>/memory/`), not project logs
- What-else observations are surfaced for awareness — if recurring across sessions, they may warrant a new log type, but the retrospective does not create one
- Run at natural session breakpoints (end of feature work, end of design conversation, before context compaction) — not mid-session

## When to use

- End of a substantive session before context degrades
- After a session that produced non-obvious decisions, friction, or generalizable insights
- After a series of recent sessions where observations have accumulated unwritten

## When NOT to use

- Mid-session — wait for a natural breakpoint
- Sessions that produced no novel content — running the skill produces noise
- Sessions where the user has already manually captured the worth-keeping observations
