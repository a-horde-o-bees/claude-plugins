# Verify doc claims against authoring timeline and code state

When persistent docs and code/state disagree, review the authoring timeline and git history of both with the assumption that more recent is more accurate; flag the doc drift back to the user.

Persistent docs (decision logs, plans, READMEs, ARCHITECTURE.md) can drift from code in two directions: docs ahead of code (aspirational — describes intent that isn't built yet), or code ahead of docs (refactors / additions that bypassed the doc-update step). Both happen.

When an agent encounters a claim in a doc that implies a tool / behavior exists, the failure mode is to build on the assumption without verifying. This wastes context when the assumption is wrong and produces guesses framed as facts.

## Trigger shape

Doc references a named utility / tool / module / feature with implementation-implying language ("we built", "uses", "via", "produced by"), and the agent can't immediately confirm the implementation in the codebase by name-matching.

## Proposed mechanism

A skill or in-skill check that, given a doc reference + a search target:

1. Greps the codebase for the named target
2. If absent: pulls the authoring date of the referencing doc + any code files in the relevant directory; identifies what's more recent
3. Surfaces the drift to the user with a "doc says X exists, didn't find it in code; doc authored {date}, no matching code added since" framing

Could live as a verb under `/ocd:navigator` or as a generic check the agent invokes when planning work that depends on a doc-named artifact.

## Why this matters

Surfaced 2026-05-12 in Monaco migration work. The decision log at `logs/decision/per-row-diff-vs-source-hash.md` chose a column-projection diff approach over per-row hashing and described a `diff_rows(...)` utility as the chosen mechanism. An agent regenerating the load-normalization plan assumed the utility existed because the decision log said it was "chosen." The user redirected the agent to check git history; the implementation didn't exist, only the decision to build it. Plan would have inherited a "follow the implemented utility" direction that was actually "build this utility from scratch."

Pattern likely generalizes: any decision log that names a future-tense mechanism, any plan whose "Sequence" section describes scaffolding that may or may not have landed since drafting.
