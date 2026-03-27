# Testing Conventions

Testing guidance for projects where code is consumed by both humans and AI agents. Language-agnostic principles organized by when tests add value versus when they are overhead.

## Fundamental Boundary

Deterministic operations get traditional tests. Non-deterministic behavior (agent judgment, NL interpretation, workflow execution quality) gets evaluation protocols, not unit tests. If identical inputs reliably produce identical outputs, test it. If not, evaluate it through protocols that accept variance and assess outcomes.

## When Tests Prevent Real Regressions

### Output Format Contracts

Stdout is an API contract. Agents parse CLI output mechanically — any change to output structure, field names, ordering, or delimiters is a breaking change even if the data is the same.

Test:
- Structured output matches explicit schema or snapshot
- Exit codes are semantic and stable (0 = success, nonzero = categorized failure)
- Error messages include machine-parseable identifiers, not just prose
- Help text includes all flags, marks required vs optional, enumerates valid values

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

Separate deterministic skeleton from non-deterministic behavior. Test skeleton with traditional unit tests — highest regression prevention per line of test code.

Test:
- Resolution priority ordering (which source wins when multiple match)
- Pattern matching (which rules apply to which inputs)
- Command routing (which operations get approved, denied, or blocked)
- Settings evaluation (how configuration is interpreted)
- Dependency ordering (topological sort correctness)

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

## What to Avoid

### Configuration Restating

If manifest says `pattern: "*.py"` and test asserts `pattern == "*.py"`, test asserts that parsing works, not that system works. Test that pattern matching behaves correctly (file X matches pattern Y), not that configuration reads back as written.

### Coverage Metrics Disconnected from Risk

100% coverage on a formatting function has less value than 60% coverage on permission enforcement with adversarial edge cases. Allocate testing effort proportionally to failure impact.

### Unit Testing Non-Deterministic Behavior

Agent judgment, NL interpretation, and workflow execution quality cannot be caught by unit tests. Do not assert agents produce specific strings, make specific tool call sequences, or interpret prompts specific ways. Test deterministic infrastructure agents depend on; evaluate agent behavior through protocols that assess outcomes.

## Decision Framework

For any component, ask:

1. If deterministic: test traditionally
2. Else: evaluate through protocols, do not unit test
3. If contract agents depend on (output format, exit codes, help text): snapshot test
4. If invariants exist (properties that must hold for all inputs): property test
5. If idempotent by design: test idempotency explicitly
6. If security boundary: test exhaustively with adversarial cases
7. If silent failure would cause downstream agent malfunction: test regardless of code simplicity
8. If test merely restates configuration: skip — testing theater
