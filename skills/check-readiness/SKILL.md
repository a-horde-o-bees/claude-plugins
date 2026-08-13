---
name: check-readiness
description: Use when asked whether something is ready, current, correct, or safe to act on — is the spec up to date, did that land, are we clear to ship, would a cold session get this right — and before reporting any work verified. Checks what the work actually consumes rather than the artifact the question named, and reports the gap along the axis that is uncovered.
---

# check-readiness

Use when asked whether something is ready, current, correct, or safe to act on — is the spec up to date, did that land, are we clear to ship, would a cold session get this right — and before reporting any work verified. Checks what the work actually consumes rather than the artifact the question named, and reports the gap along the axis that is uncovered.

Worked example: asked whether some specs were current, the obvious check compares delta specs against accreted specs. It passes. The stale instructions were in the proposal — not a spec, read by every implementer, and the thing that would have made a cold session build a design that had been retired.

## Procedure

1. **Restate the question as its outcome.** "Is X up to date" becomes "if someone acts on this cold, does the work come out right?" Do this in writing before choosing what to check — an artifact frame lets a literal answer pass, an outcome frame forces the search.
2. **Enumerate what the actor reads or executes.** List it before checking anything. The named artifact is one member, rarely the whole. For a plan that means every artifact an implementer opens, not the one kind the question mentioned.
3. **Check that closure.** Include siblings no dependency edge connects — a file that disagrees with itself is invisible to every cross-file check, and cannot be caught by comparing files to each other.
4. **Report the gap along the uncovered axis.** Name what you did not check, in the same dimension as the risk. "Proposal, design and tasks are unchecked" bounds a spec-only check. "This doesn't confirm the code matches" is a different dimension, and a caveat aimed away from the gap reads as thoroughness while providing none.

## Rules

- **Answering the narrow reading and reporting it clean is the failure**, even when the narrow check was correct. The question's phrasing is not the specification of the check.
- **Prefer the domain's own closure check** where one exists, and run it rather than re-deriving it by hand; a check re-invented per session leaves with the session. Where a domain has no such check and the gap recurs, writing one is cheaper than repeating the judgment.
- **Absence of a finding is not readiness.** Report what was examined and what was not, so a clean answer carries its own scope.
