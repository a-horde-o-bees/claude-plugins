---
name: retrospective
description: Wrap a session by first surfacing open threads — items raised but not yet dispositioned — so the user can act, log, or accept-as-is before retrospective walks for keepers. Then surfaces patterns, friction, ideas, decisions, refinements to existing entries, and user-memory candidates worth persisting before context goes stale. Nothing is written without explicit acceptance.
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

Four passes, in order. The first runs interactively before the others; the rest gather candidates that batch-present at the end.

1. **Open threads pass** — surface items raised in the session that haven't been acted on or explicitly dispositioned. For each, the user picks one of three actions: *act now* (do the work before continuing), *log as <type>* (the thread becomes a candidate for the type-aligned walk), or *accept as-is* (surface only, no log, no further work). Runs first because thread dispositions may generate work that affects later passes — completing an open thread might surface its own decisions, ideas, or patterns that the type-walk will then catch.
2. **Type-aligned walk** — for each log type, read its `_template.md`, then surface session content matching its `What Qualifies` criteria. Same walk asks: does anything from the session sharpen an *existing* entry of this type? Picks up "log as <type>" threads from pass 1 alongside session-discovered candidates.
3. **Memory walk** — separate from logs, surface user-scoped observations (role, preferences, validated approaches, project-level context).
4. **What-else pass** — open-ended; capture observations that didn't fit any type. May signal a new log type, conversational feedback, or just shared context worth flagging.

Passes 2-4 produce draft candidates that batch-present at the end; the user accepts/edits/rejects per item. Pass 1 is interactive throughout — dispositions resolve before later passes start. Nothing is written without explicit acceptance.

## Reflection Prompts

The active prompts that produce non-obvious candidates. The open-threads prompts run first and interactively; the rest run during the type-aligned walk plus the cross-cutting prompts at the end.

### Open threads

These look for **gaps in disposition** — things that were raised in the session but never received a yes/no/defer. Distinct from the type-aligned prompts, which look for content worth keeping. An open thread might or might not produce a log entry; the question is whether it has a disposition at all.

- What got raised in this session that hasn't been acted on or explicitly deferred?
- What scope-broadening question came up but didn't get a yes/no? ("Should we also check X?", "Does this apply to Y too?")
- What observation was noted in passing without a disposition (act, defer, accept-as-out-of-scope)?
- What "we should also..." went unanswered?
- What follow-up was implied by a pivot or reframing but never explicitly committed to?
- What review or audit was started but only partially completed?

For each thread surfaced, the user chooses: *act now* (work happens before continuing), *log as <type>* (becomes a candidate in the type-walk batch), or *accept as-is* (surfaced for awareness, no log, no work).

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

3. Open threads pass (interactive):
    1. Apply the Open threads prompts against the session — produce {open-threads} list, each with a one-sentence description of the unaddressed thread
    2. If {open-threads} is empty: skip to step 4
    3. Present {open-threads} to the user as a lettered list with worded disposition options. Letters identify items for quick reference; dispositions are stated as words because the disposition vocabulary is small and unambiguous on its own. Format:

        ```
        A. <thread description>
        B. <thread description>
        ...

        For each, pick: act / log-<type> / accept-as-is
        Respond like: `A: act, B: log-idea, C: accept-as-is`
        ```

        Lettered items avoid collision with Claude Code's `1/2/3` rating prompt per *Confirm Shared Intent* in the design principles, and let the user reply with shorthand referencing items by letter.
    4. Parse the user's response. For `log`, accept either bare `log` (user picks log type later) or `log-<type>` (user names the type inline). Surface ambiguity rather than guess
    5. Apply dispositions in order:
        1. *act*: do the work the thread implies before continuing — may pull in subsequent tool calls, file edits, etc. The thread is resolved in-session
        2. *log-<type>*: append a draft entry to {new-candidates} for type {type}; the batch presentation in step 8 picks it up alongside session-discovered candidates
        3. *accept-as-is*: surface the thread in the final report's "surfaced-only" section; no log, no work
    6. Once dispositions are applied, proceed to subsequent passes — completed *act* work may itself surface decisions/ideas/patterns the type walk picks up

4. Type-aligned walk:
    1. For each {type} in {decision, friction, idea, pattern, problem, research}:
        1. Apply that type's reflection prompt against the session
        2. {new-candidates} += matching observations as new-entry drafts
        3. For each existing entry of {type}: did the session sharpen it? If yes: {refinement-candidates} += diff draft
5. Apply cross-cutting prompts — surface anything caught at the type-walk level missed
6. Apply memory-candidate prompts — gather user-scoped observations as memory drafts
7. Apply what-else prompt — gather off-axis observations
8. Present all candidates as a single lettered batch — letters continue sequentially across all section boundaries (idea, friction, memory, refinements, what-else); letters do not reset between sections. Every item gets a letter for quick reference. Format:

    ```
    ## New entries

    A. <type> [<target path>] — <one-sentence rationale>
       <draft content or summary>

    B. <type> [<target path>] — <one-sentence rationale>
       <draft content or summary>

    ## Refinements

    C. <type> [<target path>] — <one-sentence rationale>
       <diff preview against existing entry>

    ## Memory

    D. memory [<target memory file>] — <one-sentence rationale>
       <frontmatter + body draft>

    ## What-else

    E. what-else — <observation>
       <proposed disposition>

    For each, pick: accept / edit / reject
    Respond like: `A: accept, B: edit (change X to Y), C: reject` or batch shorthand like `A, B, D: accept; C: reject; E: edit ...`
    ```

    Refinements show diff preview, not just prose. Memory candidates show frontmatter + body. What-else items participate in the lettered sequence — they get the same A/B/C reference shorthand as other types, not a separate free-form section
9. For each lettered candidate, parse the user's disposition: accept / edit / reject
    - For *edit*: user provides the adjustment inline; the agent applies it to the draft before writing
    - Batch shorthand (`A, B, D: accept`) and per-item form (`A: accept, B: edit ...`) are both valid; surface ambiguity rather than guess
10. Apply accepted candidates:
    1. New log entries: read `logs/<type>/_template.md` for structure, then Write `logs/<type>/<title>.md`
    2. Refinements: Edit the existing entry per draft
    3. Memory candidates: Write to user memory at `~/.claude/projects/<project-id>/memory/<name>.md` and update `MEMORY.md` index
    4. What-else: present to user as-is — no auto-write; user decides whether to capture later
11. Return to caller: list of items written, refined, captured-to-memory, or surfaced-only — with their destinations. Include open-threads outcomes (what was acted on, what was logged, what was accepted as-is)
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
