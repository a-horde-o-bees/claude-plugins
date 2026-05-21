# Assertions

Durable claims about platform behavior, captured with the tests that verify them. Distinct from plans (work to be done, removed after completion) and from research logs (one-shot investigations).

These exist because Claude Code (and any platform we build on) evolves. An assertion that was true in v2.1 may not hold in v2.5. The test must be reconstitutable so we can re-verify against future versions without re-deriving the methodology.

## File anatomy

Each assertion file declares:

- **Status** — `pending` (not yet tested), `confirmed` (verified), `refuted` (verified false), `needs-recheck` (last verification is stale or the platform changed)
- **Hypothesis** — the specific claim being tested
- **Why it matters** — what design decisions depend on the answer
- **Test design** — full content of any test artifact (skill body, prompt, etc.), the run procedure, and the detection method that discriminates outcomes
- **Expected outcomes** — table mapping observed results to interpretations
- **Historical results** — append-only log of test runs, dated, with platform version when known

## When to update

- After a test run: append a row to historical results with date, result, and any platform version detail
- After a platform update lands: re-run assertions touching the affected subsystem
- When a new edge case is discovered: add a new assertion file
- When an assertion is refuted: change status, document the new behavior

## Subdirectories

- [`skill-runtime/`](./skill-runtime/) — how skills load, persist in context, scope their directives, and compose across invocations
