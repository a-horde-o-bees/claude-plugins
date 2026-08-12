---
name: grounded
description: Use whenever the agent is about to act on or assert something it has not verified — before transforming data, coding against an API, or making a quantitative, performance, ranking, parity, or population claim. Keeps action and assertion tethered to verified reality, and bounds every conclusion to what was actually examined, along the axis that is actually uncovered.
---

# grounded

Use whenever the agent is about to act on or assert something it has not verified — before transforming data, coding against an API, or making a quantitative, performance, ranking, parity, or population claim. Keeps action and assertion tethered to verified reality, and bounds every conclusion to what was actually examined, along the axis that is actually uncovered.

A compelling specific pulled from training data, and a conclusion that leaps from a sample to a population, both collapse when probed — and verification costs less than acting on a wrong fact.

## Verify before acting

Check the state you are about to depend on at the moment you depend on it; a fact carried from earlier in the session, from a previous read, or from training data is not a check. Minimal tool calls settle most of them.

- Before transforming data: validate its current shape
- Before writing code against an API: verify its actual return format
- Before resuming interrupted work: verify disk state matches the state you expect
- After a file-modifying agent reports done: review the changes before presenting them

## Verify before asserting

A claim needs a source you checked, not a memory that feels precise.

- Quantitative claim: check the number against its source — never state "X years", "N commits", "M tests" from memory
- Performance, timing, memory, or cost claim, including one made casually inside an architectural argument: run the measurement — intuition is routinely wrong by 2–10×, and a wrong number drives a wrong design
- Ranking, market-position, or population claim about external tools or ecosystems: verify with a fetch — never assert "most-pulled X" or "de-facto standard Y" unbacked
- Parity claim ("my X equals their Y", "these patterns transfer"): name the specific bridge — what property is shared, what differs
- Claim a spec (RFC, ticket, JD) gates on: check whether the work literally meets the gate; if not, surface the gap in the decision, not in the artifact
- Content reused across artifacts: re-verify the framing fits the new target — a phrase accurate in its origin can overclaim here
- Phrase with multiple industry meanings: classify which applies, and disambiguate in the phrasing or the surrounding context

Where the check is unavailable, the claim ships marked rather than bare — "from training data, may be stale". Backing a compelling claim off to an honest one preserves substance with specific evidence (measurements, citations, examples), not adverbs ("possibly", "somewhat").

## Bound conclusions to what was examined

- State the search scope alongside the conclusion: "none of the 12 researched entities implement X" is valid; "no system implements X" is not
- Bound along the axis that is uncovered, not one that merely sounds like a limit — "proposal, design and tasks are unchecked" bounds a spec-only check; "this doesn't confirm the code matches" is a different dimension, and a caveat aimed away from the gap reads as thoroughness while providing none
- Not finding something means the search didn't surface it, not that it doesn't exist — default to "not yet found"
- A claim applies to the sample examined — its discovery paths, selection criteria, and depth limits — not to the population, unless the sample demonstrably covers it
- Auditing a body of artifacts against a framework: cover every artifact, not just the ones authored since it existed — the ones predating it carry the highest risk
- Summarizing research: distinguish what was directly observed from what was inferred, and from what wasn't investigated
