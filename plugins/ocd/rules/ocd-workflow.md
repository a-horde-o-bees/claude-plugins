---
matches: "*"
governed_by:
  - .claude/rules/ocd-design-principles.md
---

# Workflow

Project-specific operational patterns governing how agents work day-to-day in this project.

## Working Directory

Working directory must remain project root for the entire session. Use absolute paths or tool flags instead of changing directories.

- No `cd`, `pushd`, `popd` — use `git -C <path>` for submodule operations
- Use relative paths from project root for `.claude/` scripts

## Agents

Minimize agent count — each sub-agent independently loads context and rediscovers the project, multiplying token cost. Default to a single agent processing tasks sequentially within one context.

## Test Durability

Verification of new code belongs in the test structure. Not in ad-hoc bash commands. Not in inline Python heredocs. Not in `python -c "..."` snippets. Not in any one-shot execution outside the test files.

- All verification of new code — including smoke tests, "just to check" runs, round-trip confirmations, parse-and-render checks, and any other one-shot validation — goes through the test structure as a test in the relevant test file
- The format of the inline verification doesn't matter: bash command, Python heredoc (`python <<EOF ... EOF`), `python3 -c "..."`, REPL session — they're all ad-hoc verification and they all violate this rule
- The discipline is absolute. If the verification is worth doing, the test is worth writing first. There is no "I'll just quickly check before writing the test" path
- Exploration and learning (reading code, querying state, understanding existing behavior) are different from verifying new code; explore freely, but verification of new code that you wrote requires a test
- Test fixtures handle environment setup automatically while ad-hoc commands require inline env vars that need manual approval — and the durability cost matters more than the friction cost

## Test Scope Selection

Run tests at the scope that matches the change.

- Run only tests directly affected by current changes, scoped to narrowest relevant test file
- Run broader suites only when explicitly requested
- Exception: run full suite after structural changes (moves, renames, refactors) and before checkpoints — broken imports and cascading failures won't surface in narrow tests

