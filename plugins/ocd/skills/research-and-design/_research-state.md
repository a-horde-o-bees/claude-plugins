# Research State Schema

Persistent state for a research-and-design run. Tracks open questions, findings, assumptions requiring empirical validation, architectural decisions, and residual unknowns. Lives at `${CLAUDE_PLUGIN_DATA}/research-and-design/{session-id}/state.md`. Survives session restarts; the skill reads it on entry to resume.

## Structure

```markdown
# Research State: {problem-statement}

## Metadata

- Session: {session-id}
- Started: {timestamp}
- Problem: {one-line restatement of the research prompt}
- Status: {seeding | researching | converged | designing | delivered}

## Questions

### Open

- {id}: {question-text}
  - Scope: {what domain, which artifact(s), where to look}
  - Assigned wave: {wave-number or null}
  - Added: {timestamp or wave-N}

### Answered

- {id}: {question-text}
  - Answer summary: {one-line}
  - Evidence: {pointer to findings file, URL, or artifact path}
  - Answered in wave: {wave-number}

### Deferred

- {id}: {question-text}
  - Reason: {why deferred — out of scope, unanswerable, low-value}
  - Deferred by: {user-acknowledged or skill-judgment}

## Assumptions Requiring Validation

- {id}: {assumption-statement}
  - Validation approach: {worktree probe script, ad-hoc test, manual review}
  - Status: {pending | validated | falsified}
  - Result: {pointer to probe output or one-line outcome}

## Architectural Decisions

- {id}: {decision-name}
  - Choice: {selected alternative}
  - Alternatives: [{other options considered}]
  - Driving findings: [{question ids or evidence pointers}]
  - User acknowledgment: {acknowledged | deferred | awaiting}

## Findings for Triage

- {id}: {finding-type}: {one-line description}
  - Discovered in: {wave-number}
  - Proposed routing: {log type or backlog placement}
  - Routing confirmation: {pending | confirmed | overridden}
```

## Usage

- The Research Loop reads `Questions.Open` to select dispatch batches
- Agent returns update `Questions.Answered` and may add `Questions.Open` entries for newly surfaced sub-questions
- Empirical validation steps move entries through `Assumptions`
- Architectural Decision Surfacing populates `Architectural Decisions` and the user's ack status
- Findings Triage reads `Findings for Triage` and applies routings

## Identifier Scheme

Questions: `q1`, `q2`, ... assigned sequentially as added. Never reused.
Assumptions: `a1`, `a2`, ...
Decisions: `d1`, `d2`, ...
Findings: `f1`, `f2`, ...

Short ids are opaque handles. The description carries meaning; ids are references.

## Convergence Test

The Research Loop terminates when one of:

- `Questions.Open` is empty
- Every entry in `Questions.Open` has been explicitly deferred by user acknowledgment
- User explicitly directs the loop to stop regardless of open questions
