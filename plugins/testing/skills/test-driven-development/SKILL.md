---
name: test-driven-development
description:
---

# Test Driven Development

Implementing a code change that needs verification — locate or write the test first, confirm RED against current code, make the change, confirm GREEN.

Applies when verification was going to happen anyway. Two reasons the test-first cycle matters:

- **Verification runs through an allowlisted path.** The test suite (`bin/project-run tests`, `pytest`, `ocd-run check`) matches existing permission patterns. Ad-hoc verification (`python -c "..."`, bash pipelines, `VAR=$(...)` chains) often halts for manual approval.
- **The implementation can't ratify itself.** A test written after tends to assert what code does, not what spec demands — bugs get encoded as "correct."

## When Driving Applies

- Adding a new callable (function, method, CLI verb, MCP tool, hook handler)
- Modifying behavior of an existing callable — return values, error paths, side effects
- Fixing a bug where you'd want a regression guard
- Changing a round-trip-able format — parse ↔ serialize, schema, protocol

## Exemptions

- **Verified existing coverage.** Articulate what the post-change test would assert, grep test files, confirm coverage exists with the same inputs and expectation. Active check, not "probably covered somewhere."
- **Configuration restating.** The only possible test would echo data back. Don't write it.
- **No verification intended.** Docs, comments, docstrings, log entries, ROADMAP edits, memory updates.
- **Mechanical changes already covered.** Pure renames or format refactors where existing tests exercise the new shape.

## Running the Test

**Narrow batch.** Run only tests directly affected — the file or class owning the assertion. Broader scope is overhead during a red-green cycle.

**RED first.** Run the narrow batch against current code before implementing. If it passes unchanged, stop:

- The change is unnecessary (behavior is already correct)
- The test doesn't discriminate the behavior (false-positive coverage)
- Your model of current state is wrong

**Implement the change.**

**GREEN after.** Re-run the narrow batch. Confirm pass.

**Full suite.** Run only when structural changes cascade (moves, renames, refactors) or at checkpoint boundaries.
