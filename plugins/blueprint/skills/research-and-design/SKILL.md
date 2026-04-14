---
name: research-and-design
description: Research an open question and produce a validated design, driving convergence via a persistent question list rather than fixed-wave dispatch. Spawns focused research agents with skeptical briefs, validates assumptions in worktree-isolated prototypes, and surfaces architectural decisions as discrete user acknowledgments. Delivers a design document with open questions explicitly tracked for follow-up.
argument-hint: "<research-prompt>"
allowed-tools:
  - Read
  - Edit
  - Write
  - Bash
  - Glob
  - Grep
  - WebSearch
  - WebFetch
---

# /research-and-design

Research an open question and produce a validated design, driving convergence via a persistent question list rather than fixed-wave dispatch. Spawns focused research agents with skeptical briefs, validates assumptions in worktree-isolated prototypes, and surfaces architectural decisions as discrete user acknowledgments. Delivers a design document with open questions explicitly tracked for follow-up.

## Process Model

Research is an open-ended investigation whose shape cannot be preplanned. A fixed number of waves forces either premature convergence (stopped before answers are real) or wasted effort (still dispatching when convergence would be natural). Convergence-driven dispatch avoids both: each wave dispatches the current top unanswered questions, and the loop terminates when the question list is empty or the user acknowledges the remaining gaps as acceptable.

Research outputs persist to disk at `${CLAUDE_PLUGIN_DATA}/research-and-design/{session-id}/` so the main conversation carries pointers, not content. Each wave's agent returns a summary; details stay on disk for audit and follow-up waves.

Assumptions that drive design decisions are validated empirically when possible. A worktree-isolated probe runs a minimal prototype against real project artifacts — the same infrastructure already used for isolated testing in `evaluate-skill`. This replaces the "mental dry-run" failure mode where theoretical designs survive review only because no one executed them.

Design writing is a separate phase. The skill does not draft SKILL.md, component files, or architecture notes until research has converged. Early design writing commits to architectures that later findings invalidate, producing rework. When research converges, architectural choices are enumerated and each is surfaced to the user for acknowledgment before the design phase proceeds.

Findings that accumulate during the run (defects surfaced, unmet needs, misalignments with existing conventions) are staged for routing at the end. Before logging or filing anything, the skill presents the proposed routing to the user — a user's "capture everything in one place" intent overrides the default log-routing split.

## Scope

One research-and-design session addresses one problem. Problem is given as a free-text argument — a question, a feature request, a gap to close, an audit target. The skill owns everything between problem statement and validated design proposal; implementation happens in a separate session after design is accepted.

Accepted arguments:

- `<research-prompt>` — required; the problem or question to investigate

## Rules

- Research converges when the question list is empty or user acknowledges remaining questions as acceptable — never dispatch a preset wave count
- Agent briefs include counter-evidence framing — "find where this would be wrong" is a required section in every brief
- Persist wave outputs to disk; main context holds pointers only
- Validate assumptions empirically when possible — worktree probe for anything that can be executed rather than reasoned about
- Block design writing until research converges; each architectural choice surfaces for explicit user acknowledgment before writing starts
- Surface routing before logging findings — confirm with user when default log-routing would split what the user wants consolidated
- Clean up spawned work at end — continued agents terminated or explicitly handed off; worktrees removed

## Route

1. If no research prompt: Exit to caller — respond with skill description and argument-hint
2. {session-id} = `${CLAUDE_SESSION_ID}-$(date +%s)`
3. Create scratch dir: bash: `mkdir -p ${CLAUDE_PLUGIN_DATA}/research-and-design/{session-id}`
4. {state-path} = `${CLAUDE_PLUGIN_DATA}/research-and-design/{session-id}/state.md`
5. Seed the question list:
    1. Given the research prompt, generate an initial set of questions whose answers are needed to design a solution
    2. Write to {state-path} per `_research-state.md` schema
6. Present the initial question list to user and request confirmation, additions, or scope changes
7. Dispatch Workflow

## Workflow

### Research Loop

> Research converges when the question list has no open items or the user acknowledges remaining items as acceptable. Each iteration dispatches focused agents to the top open questions and reintegrates their findings into the question list.

1. {wave} = 0
2. Read {state-path} — collect open questions
3. If no open questions: Break loop — converged
4. Select a batch of open questions for this wave:
    1. Prefer questions whose answers unblock the most downstream work
    2. Group questions a single agent can answer together (shared domain) into one brief
    3. Prefer parallel dispatch across distinct domains
5. Present wave plan to user — what questions will be asked, what agents will be spawned, expected token cost — confirm
6. For each {brief} in wave:
    1. async Spawn: Call: `_agent-brief.md` ({brief} = {brief}, {session-id} = {session-id})
    2. Return: findings-pointer + short status
7. Collect wave results
8. For each {finding} in collected results:
    1. Mark originating question(s) as answered or partial per the finding
    2. Add new questions surfaced during research to the open list
    3. Identify assumptions that need empirical validation
9. Save updated {state-path}
10. If empirical validation needed:
    1. For each {assumption} to validate: Call: `_worktree-probe.md` ({assumption} = {assumption}, {session-id} = {session-id})
    2. Incorporate probe results into findings
11. Present wave summary to user — what was learned, what remains open, any surprises
12. Ask user: continue loop, or acknowledge remaining questions as acceptable?
13. If continue: {wave} = {wave} + 1; Go to step 2. Research Loop
14. Else: Break loop — user-acknowledged convergence

### Architectural Decision Surfacing

> Before writing any design file, enumerate the architectural choices that research has made clear and surface each for user acknowledgment. Silent incorporation produces surprise later; explicit acknowledgment catches disagreement while the choice is still cheap to revise.

15. From research state, identify architectural decision points — each is a choice where the design has alternatives that research findings inform but do not fully determine
16. For each {decision}:
    1. Present: the choice, the alternatives considered, the research finding that shapes the recommendation
    2. Ask user: acknowledge recommendation, select alternative, or defer
17. Record acknowledged decisions in {state-path}

### Design Writing

> Only after research convergence and decision acknowledgment does design writing begin. Design artifacts persist alongside research state.

18. Draft design document at `${CLAUDE_PLUGIN_DATA}/research-and-design/{session-id}/DESIGN.md`
    1. Include: problem statement, research summary with citations, architectural decisions with rationale, design specification, open questions remaining
19. If design proposes new skill, component, or code: draft skeleton files alongside DESIGN.md — `SKILL.md`, component files, etc.
20. Optional dry-run: Call: `_worktree-probe.md` with a realistic usage scenario to stress-test the design before delivery

### Findings Triage and Routing

> Findings accumulated during research may warrant log entries, backlog items, or immediate action. Present routing to user before filing.

21. Enumerate accumulated findings:
    - Defects in existing artifacts observed during research
    - Unmet needs surfaced by the research topic
    - Gaps in existing conventions or rules
    - Ideas for future work that emerged
22. Propose routing for each: log type (problem / friction / idea / decision), backlog item in project state, or one consolidated entry per user preference
23. Confirm routing with user before writing
24. Apply approved routings

### Cleanup

> Spawned work and worktrees outlive the Workflow unless the skill releases them. Preserved state is kept for user reference; transient resources go.

25. Terminate any background agents still running
26. Remove any worktrees still open
27. Preserve `{state-path}` and `DESIGN.md` under scratch for user reference until next explicit cleanup
28. Present Report

### Report

- **Problem statement** — what was asked
- **Research summary** — waves completed, questions answered, questions deferred
- **Assumptions validated** — list of worktree probes with pass/fail outcomes
- **Architectural decisions** — each with rationale and user acknowledgment status
- **Design document location** — pointer to `DESIGN.md`
- **Skeleton files** — list of scaffolded files if design involves new artifacts
- **Findings routed** — log entries created, backlog items added, action items surfaced
- **Residual open questions** — list with scope-needed-to-resolve; parked for follow-up

## Error Handling

1. If a spawned agent returns malformed output or fails: retry once with tightened brief; if still fails, mark the brief's questions as "agent could not answer" and continue loop
2. If worktree probe fails to setup or execute: surface failure to user; skip the probe; note in findings that the assumption is unverified
3. If user declines to acknowledge a required architectural decision: park the design phase; save state; exit to caller for re-invocation when decision is ready
4. Scratch dir preservation on failure: never auto-wipe on error; user explicitly directs cleanup
