---
name: fix-foundations-not-symptoms
description:
---

# Fix Foundations, Not Symptoms

When something is wrong, trace to the root cause and correct it — even if that means rebuilding. Bandaids create two problems: the original defect and the workaround that obscures it.

- Aliases and indirection layers that map short names to real names are symptoms of an incomplete refactor — propagate the real names instead
- Before proposing a workaround that changes what is delivered: name the gap and present alternatives; proceed after user selects direction
- When mid-execution an approach diverges from what was asked: stop and flag the gap; never silently reframe the workaround as equivalent to the original ask
- Before working around unexpected constraints: research the constraint, name what it blocks and the alternatives; proceed after user directs
- Before changing approach due to errors: research the error cause, name what failed and propose a corrected approach; proceed after user directs
- When surfacing a bug or gap mid-task: propose the fix, not just the log — current-session context that surfaced the issue is expensive to reconstruct, and the fix is cheap when the context is already loaded
- Log-without-fix only when the fix would derail the current task — touches unrelated systems, requires design decisions beyond current scope, or depends on work outside the task
- When the fix is in the layer or code path already being edited: act, don't ask
