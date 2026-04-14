---
includes:
  - "test_*.*"
  - "conftest.*"
governed_by:
  - .claude/rules/ocd/design-principles.md
---

# Testing Conventions

Testing guidance for projects where code is consumed by both humans and AI agents. Language-agnostic principles organized by when tests add value versus when they are overhead.

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

- Duplicating what unit tests already cover with mocked boundaries
- Testing library behavior documented by library authors

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

## What to Avoid

### Configuration Restating

If manifest says `pattern: "*.py"` and test asserts `pattern == "*.py"`, test asserts that parsing works, not that system works. Test that pattern matching behaves correctly (file X matches pattern Y), not that configuration reads back as written.

### Coverage Metrics Disconnected from Risk

100% coverage on a formatting function has less value than 60% coverage on permission enforcement with adversarial edge cases. Allocate testing effort proportionally to failure impact.

### Unit Testing Non-Deterministic Behavior

Agent judgment, NL interpretation, and workflow execution quality cannot be caught by unit tests. Do not assert agents produce specific strings, make specific tool call sequences, or interpret prompts specific ways. Test deterministic infrastructure agents depend on; evaluate agent behavior through protocols that assess outcomes.

## Decision Framework

For any component, ask:

1. If deterministic:
    1. If contract agents depend on (output format, exit codes, help text): snapshot test
    2. If invariants exist (properties that must hold for all inputs): property test
    3. If idempotent by design: test idempotency explicitly
    4. If security boundary: test exhaustively with adversarial cases
    5. If silent failure would cause downstream agent malfunction: test regardless of code simplicity
    6. If test merely restates configuration: skip — testing theater
2. Else: evaluate through protocols, do not unit test
