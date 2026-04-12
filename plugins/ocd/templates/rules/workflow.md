---
includes: "*"
governed_by:
  - .claude/rules/ocd/design-principles.md
---

# Workflow

Project-specific operational patterns governing how agents work day-to-day in this project.

## Working Directory

Working directory must remain project root for the entire session. Use absolute paths or tool flags instead of changing directories.

- No `cd`, `pushd`, `popd` — use `git -C <path>` for submodule operations

## Agents

Minimize agent count — each sub-agent independently loads context and rediscovers the project, multiplying token cost. Default to a single agent processing tasks sequentially within one context.

## Test Durability

Verification of new code belongs in the test structure. Not in ad-hoc bash commands. Not in inline Python heredocs. Not in `python -c "..."` snippets. Not in any one-shot execution outside the test files.

- All verification of new code — including smoke tests, "just to check" runs, round-trip confirmations, parse-and-render checks, and any other one-shot validation — goes through the test structure as a test in the relevant test file
- The discipline is absolute. If the verification is worth doing, the test is worth writing first. There is no "I'll just quickly check before writing the test" path
- Exploration and learning (reading code, querying state, understanding existing behavior) are different from verifying new code; explore freely, but verification of new code that you wrote requires a test
- Test fixtures handle environment setup automatically while ad-hoc commands require inline env vars that need manual approval — and the durability cost matters more than the friction cost

## Push Blocking

Git push can be temporarily blocked for safe non-destructive testing or worktree-isolated evaluation. The block sets an invalid pushurl on `origin` — any push attempt fails loudly with `fatal: '/dev/null' does not appear to be a git repository`.

- Block: `git config remote.origin.pushurl "file:///dev/null"`
- Unblock: `git config --unset remote.origin.pushurl`
- Check: `git config --get remote.origin.pushurl` — no output means unblocked

When push fails unexpectedly with "does not appear to be a git repository": check whether pushurl is set. A left-over block from a crashed evaluation or interrupted test is the likely cause — unblock with the command above.

## Test Scope Selection

Run tests at the scope that matches the change.

- Run only tests directly affected by current changes, scoped to narrowest relevant test file
- Run broader suites only when explicitly requested
- Exception: run full suite after structural changes (moves, renames, refactors) and before checkpoints — broken imports and cascading failures won't surface in narrow tests

