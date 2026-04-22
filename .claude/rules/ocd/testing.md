---
includes: "*"
governed_by:
  - .claude/rules/ocd/design-principles.md
---

# Testing

Testing discipline — when to test, how to test, where tests live, and the minimum coverage bar every callable must meet. Always-on because the decision "do I test this" precedes the act of editing a test file.

## Test Durability

Verification of new code belongs in the test structure. Not in ad-hoc bash commands. Not in inline Python heredocs. Not in `python -c "..."` snippets. Not in any one-shot execution outside the test files.

- All verification of new code — including smoke tests, "just to check" runs, round-trip confirmations, parse-and-render checks, and any other one-shot validation — goes through the test structure as a test in the relevant test file
- The discipline is absolute. If the verification is worth doing, the test is worth writing first. There is no "I'll just quickly check before writing the test" path
- Exploration and learning (reading code, querying state, understanding existing behavior) are different from verifying new code; explore freely, but verification of new code that you wrote requires a test
- Test fixtures handle environment setup automatically while ad-hoc commands require inline env vars that need manual approval — and the durability cost matters more than the friction cost

## Callable Surface Coverage

Every callable surface a consumer invokes — CLI verb, subcommand, hook handler, skill entry point, MCP tool, script — has at least one test exercising it. The test may be unit, integration, or end-to-end; the choice depends on what the callable does. What matters is that no callable goes untested.

- A callable with zero test references is a missing test, not a "simple enough" exemption
- Untested callables accumulate rot — the next change breaks them silently because nothing fails
- Required flags must have at least one test path exercising them
- Boolean flags that change behavior meaningfully (destructive `--force`, mode-switching flags) require their own test path; boolean flags that only affect output ceremony (`--quiet`, `--no-color`) are covered transitively by flagless invocations

### Crawlable inventory

Coverage is decidable from the repository:

1. List every callable — CLI verbs (argparse in `__main__.py`), hook handlers (entries in `hooks.json`), skill slash commands (`SKILL.md` files), MCP tools (tool registrations), project-level scripts (`bin/`, `scripts/`)
2. For each callable, grep test files for an invocation
3. Callables with zero invocations are coverage gaps

A discipline check under `/ocd:check` runs this crawl as part of universal conformance.

### Exempt

- Private helpers (underscore-prefixed, not reachable through a public dispatch path) — covered transitively by public callers' tests
- Deprecated callables slated for removal — delete rather than continue testing

## Test Scope Selection

Run tests at the scope that matches the change.

- Run only tests directly affected by current changes, scoped to narrowest relevant test file
- Run broader suites only when explicitly requested
- Exception: run full suite after structural changes (moves, renames, refactors) and before checkpoints — broken imports and cascading failures won't surface in narrow tests

## Fundamental Boundary

Deterministic operations get traditional tests. Non-deterministic behavior (agent judgment, NL interpretation, workflow execution quality) gets evaluation protocols, not unit tests. If identical inputs reliably produce identical outputs, test it. If not, evaluate it through protocols that accept variance and assess outcomes.

## When Tests Prevent Real Regressions

### Output Format Contracts

Tool responses are API contracts. Agents parse output mechanically — any change to structure, field names, or response format is a breaking change even if the data is the same.

Test:

- Structured output matches explicit schema or snapshot
- Error responses include machine-parseable identifiers, not just prose
- Tool descriptions and parameter schemas are complete and accurate

Technique: snapshot/approval testing — capture golden output for representative inputs, diff on every change, review diffs deliberately before approving new snapshots.

### Roundtrip and Invertibility

If a system reads a format and writes it back, the roundtrip property is the highest-value test. Parse then serialize then parse again must yield same structure.

Test:

- Format parse-serialize roundtrips (frontmatter, manifests, configuration)
- Pattern matching symmetry (if pattern matches file, listing files under pattern includes that file)
- Path resolution determinism (same input always resolves to same absolute path)

Technique: property-based testing — generate random valid inputs, run through pipeline, assert roundtrip holds.

### Idempotency

Agent workflows retry frequently. Any operation that changes behavior on second identical invocation causes cascading failures.

Test:

- Database operations produce same state whether run once or twice
- Init/deploy operations detect existing state and skip gracefully
- File operations overwrite cleanly without side effects

Technique: run operation, capture state, run again, assert state identical.

### Invariant Preservation

Define properties that must hold regardless of input, then test with generated data. Invariants catch classes of bugs, not individual cases.

Test:

- Dependency ordering always produces valid topological sort
- Cycle detection always raises on cycles, never silently degrades
- Wildcard patterns always match everything
- Deny always overrides allow in permission systems
- Path traversal sequences never escape allowed boundaries

Technique: define invariant as predicate, generate random valid inputs, assert predicate holds universally.

### Deterministic Skeleton

Separate deterministic skeleton from non-deterministic behavior. Test skeleton — highest regression prevention per line of test code.

Test:

- Resolution priority ordering (which source wins when multiple match)
- Pattern matching (which rules apply to which inputs)
- Command routing (which operations get approved, denied, or blocked)
- Settings evaluation (how configuration is interpreted)
- Dependency ordering (topological sort correctness)

Technique: traditional unit tests — isolate each deterministic function, verify with explicit inputs and expected outputs.

### Security Boundaries

Permission enforcement has zero tolerance for false negatives. A bug that permits an operation that should be denied has immediate consequences.

Test:

- Path traversal resistance
- Injection in quoted vs unquoted contexts
- Deny list precedence over allow list
- Empty settings default to restrictive, not permissive

Technique: explicit boundary case enumeration plus property-based fuzzing of inputs.

## When Tests Add Value Situationally

### Structured Document Validation

Structured documentation consumed by agents is code. Validate schema and referential integrity, not prose content.

When it adds value:

- Fields that agents parse programmatically (names, patterns, dependencies)
- Referential integrity (manifest entries reference files that exist)
- Format consistency across files of same type

When it is overhead:

- Linting prose content that agents interpret with natural language understanding
- Enforcing style rules on descriptions that do not affect machine parsing

### Integration Tests Across Boundaries

Unit tests with mocked dependencies can pass while real integration is broken. Use integration tests strategically at boundaries where failure is silent.

When it adds value:

- CLI end-to-end: invoke actual script, verify stdout/stderr/exit code
- Database operations against real databases (temp databases in test fixtures)
- File system operations in temp directories

When it is overhead:

- Duplicating what unit tests already cover with mocked boundaries — the same behavior covered by both kinds is testing-for-its-own-sake
- Testing library behavior documented by library authors

**Value filter for an integration test:** what dispatch-class or real-world failure does this catch that unit tests don't? If the answer is "nothing specific," it's a retread of unit coverage. Content assertions should validate structure (shape, required fields, exit codes) — not semantic behavior that unit tests already cover.

### Git Worktree Isolation

Integration tests that create, modify, or stage files within the project repository must run in a disposable git worktree. A worktree shares the object store with the main repo — tests operate on real project files in real git context — but has its own working tree and index. Changes in the worktree cannot affect the main working tree.

Without isolation, tests that use `git checkout --`, `git restore`, or `git reset` to clean up after themselves silently destroy uncommitted changes in the main working tree.

**Mechanism.** Create a detached worktree from HEAD via `git worktree add <path> HEAD --detach`; tear it down with `git worktree remove --force`. Tests receive the worktree path and reference all project files relative to it.

**Fixture patterns live in the language convention.** Worktree isolation is language-agnostic — the fixture machinery that implements it (pytest session-scoped fixtures, Jest setup hooks, etc.) is language-specific and documented alongside the language's other testing patterns, not here.

When worktree isolation is required:

- Tests that stage or unstage files (`git add`, `git reset`)
- Tests that run git hooks (pre-commit, commit-msg)
- Tests that create or delete files in the project tree
- Tests that modify tracked files and restore them afterward

When worktree isolation is unnecessary:

- Tests that only read project files without modification
- Tests that operate entirely in `tmp_path` or other external temp directories
- Unit tests that mock git operations

### Agent-Spawning Tests

Some behaviors can only be verified end-to-end by spawning a real Claude subprocess — hook behavior during real Edit or Write calls, plugin wiring during a fresh `claude -p` session, MCP servers binding under a fresh `CLAUDE_PROJECT_DIR`. These tests exercise the integration between the plugin and a running agent, which deterministic tests and mocks cannot substitute for.

Real agent tests cost tokens, take seconds to minutes per test, and carry model-variance and API-reliability flakiness. They are opt-in by default: mark them `pytestmark = pytest.mark.agent` at the module level, and the pytest configuration skips them unless `--run-agent` is passed on the command line.

What agent tests should verify:

- Plugin wiring around the subprocess — PATH resolution, venv binding, `CLAUDE_PROJECT_DIR` propagation, hook registration
- Hook invocation and corrective output under real tool calls the agent makes
- Substrate setup and teardown correctness when a real agent runs inside the sandbox

What agent tests should *not* verify:

- Exact strings the agent produces — model variance makes these brittle; test the observable side effects (file contents, hook output, exit codes) instead
- Specific tool-call sequences — agents reorder work; assert the required state at the end, not the path taken
- Model quality or reasoning — that belongs in evaluation protocols, not pytest

Discipline for cost:

- Fail fast before the subprocess call — assert preconditions (fixture files exist, `claude` binary on PATH, venv present) before spending tokens
- Keep agent tests narrow — one behavior per test, minimal prompt, minimal expected work
- Share setup where possible — a session-scoped fixture that spins up a sandbox once costs far less than per-test setup

## Ambient-State Isolation

Tests must own their state. Never rely on ambient user settings, global environment, or the developer's home directory happening to contain what the test needs.

- Tests that read `~/.claude/settings.json` (or similar) set `HOME` to a scratch path in the fixture and write the exact settings they need
- Tests that read `CLAUDE_PROJECT_DIR` content set it to a `tmp_path` and populate only what the test requires
- Tests that shell out to tools that may read ambient state (git, `uv`, etc.) scope that state via env vars or `cwd`

CI's clean environment surfaces ambient-state dependencies loudly — a test that passes locally but fails in CI with "JSONDecodeError: Expecting value" or similar is almost always a fixture gap, not a flake.

## Where Tests Live

Test files go in one of three homes depending on what they verify:

| What it tests | Home | Example |
|---------------|------|---------|
| Feature behavior of one skill or system | That skill or system's own `tests/` folder | Does `paths_get` return the right shape for a directory |
| Cross-system integration within a plugin | The plugin's `tests/` at plugin root | Does setup init → navigator scan → governance match compose correctly |
| Universal discipline conformance across every system | A centralized check system that any plugin can invoke | Does every system follow the dormancy contract |

Feature tests are bounded by the skill or system they belong to and move with it. Integration tests exercise cross-system workflows and stay at plugin root because they outlive any single system. Discipline conformance tests encode rules that apply universally — they belong to a dedicated check system and are tested against synthetic fixtures, not against real systems that drift.

A single behavior never belongs in two homes. If a test would fit either feature or integration, it is a feature test — the skill owns it. If a check would fit either integration or discipline conformance, it is a conformance check only when it applies to every system uniformly.

## What to Avoid

### Configuration Restating

If manifest says `pattern: "*.py"` and test asserts `pattern == "*.py"`, test asserts that parsing works, not that system works. Test that pattern matching behaves correctly (file X matches pattern Y), not that configuration reads back as written.

### Coverage Metrics Disconnected from Risk

100% coverage on a formatting function has less value than 60% coverage on permission enforcement with adversarial edge cases. Allocate testing effort proportionally to failure impact — the Callable Surface Coverage bar sets the floor, Decision Framework allocates effort above it.

### Unit Testing Non-Deterministic Behavior

Agent judgment, NL interpretation, and workflow execution quality cannot be caught by unit tests. Do not assert agents produce specific strings, make specific tool call sequences, or interpret prompts specific ways. Test deterministic infrastructure agents depend on; evaluate agent behavior through protocols that assess outcomes.

## Decision Framework

For any callable or deterministic component, ask:

1. Does the callable have at least one test? If no: write one — the test kind is your choice per the rules below, but untested callables are the first gap to close.
2. If deterministic:
    1. If contract agents depend on (output format, exit codes, help text): snapshot test
    2. If invariants exist (properties that must hold for all inputs): property test
    3. If idempotent by design: test idempotency explicitly
    4. If security boundary: test exhaustively with adversarial cases
    5. If silent failure would cause downstream agent malfunction: test regardless of code simplicity
    6. If a proposed integration test duplicates existing unit coverage with no new failure mode: skip — overhead
    7. If a proposed test merely restates configuration: skip — testing theater
3. Else: evaluate through protocols, do not unit test
