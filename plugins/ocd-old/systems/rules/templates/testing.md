# Testing

Testing discipline across four phases: authoring, driving changes, maintaining the system, deciding when to test.

## Test Authoring

### What Qualifies

Deterministic operations (same input → same output) get traditional tests. Non-deterministic behavior (agent judgment, NL interpretation, workflow execution quality) gets evaluation protocols that accept variance.

### Durability

Verification of new code goes in the test structure — including smoke tests, round-trip checks, parse-and-render checks, any one-shot validation. Not ad-hoc bash, inline Python heredocs, or `python -c "..."` snippets.

- Exploration and learning differ from verification; explore freely, but verifying new code requires a test
- Test fixtures handle environment setup; ad-hoc commands need inline env vars requiring manual approval

### Techniques by Risk Class

#### Strong-case techniques

> Always earn the investment.

**Output format contracts.** Agents parse output mechanically — any change to structure, field names, or format is breaking.

- Structured output matches explicit schema or snapshot
- Error responses include machine-parseable identifiers
- Tool descriptions and parameter schemas are complete and accurate

Snapshot/approval testing — capture golden output, diff on every change, review diffs before approving.

**Roundtrip and invertibility.** Parse → serialize → parse must yield same structure.

- Format roundtrips (frontmatter, manifests, configuration)
- Pattern matching symmetry (if pattern matches file, listing files under pattern includes it)
- Path resolution determinism (same input always resolves to same absolute path)

Property-based testing — generate random valid inputs, run through pipeline, assert roundtrip holds.

**Idempotency.** Agent workflows retry frequently; operations that change behavior on second invocation cascade.

- Database operations produce same state run once or twice
- Init/deploy operations detect existing state and skip
- File operations overwrite cleanly without side effects

Run operation, capture state, run again, assert state identical.

**Invariant preservation.** Define properties that must hold regardless of input; test with generated data.

- Dependency ordering produces valid topological sort
- Cycle detection raises on cycles, never silently degrades
- Wildcard patterns match everything
- Deny overrides allow in permission systems
- Path traversal sequences never escape allowed boundaries

Define invariant as predicate, generate random inputs, assert universally.

**Deterministic skeleton.** Highest regression prevention per line of test code.

- Resolution priority ordering (which source wins when multiple match)
- Pattern matching (which rules apply to which inputs)
- Command routing (approved, denied, blocked)
- Settings evaluation
- Dependency ordering (topological sort correctness)

Traditional unit tests — isolate each function, verify with explicit inputs and expected outputs.

**Security boundaries.** Permission enforcement has zero tolerance for false negatives.

- Path traversal resistance
- Injection in quoted vs unquoted contexts
- Deny list precedence over allow list
- Empty settings default to restrictive

Explicit boundary enumeration plus property-based fuzzing.

#### Situational techniques

> Earn the investment when the failure mode applies.

**Structured document validation.** Documentation agents parse is code. Validate schema and referential integrity, not prose.

Applies when — fields agents parse programmatically (names, patterns, dependencies); referential integrity (manifest entries reference existing files); format consistency across same-type files.

Skip when — linting prose agents interpret with NL understanding; style rules on descriptions that don't affect parsing.

**Integration tests across boundaries.** Unit tests with mocked dependencies can pass while real integration breaks. Use at boundaries where failure is silent.

Applies when — CLI end-to-end (invoke script, verify stdout/stderr/exit code); database operations against real databases (temp databases in fixtures); file system operations in temp directories.

Skip when — duplicating unit coverage with mocked boundaries; testing library behavior the authors document.

**Value filter:** what failure does this catch that unit tests don't? If "nothing specific," it's a retread. Content assertions validate structure (shape, required fields, exit codes), not semantic behavior unit tests already cover.

**Git worktree isolation.** Integration tests that create, modify, or stage files in the project repository must run in a disposable git worktree — own working tree and index, shared object store. Without isolation, cleanup via `git checkout --`, `git restore`, or `git reset` silently destroys uncommitted changes in the main working tree.

Canonical fixture — `sandbox_worktree` in `tests/plugins/ocd/conftest.py` wraps the ocd sandbox system's worktree primitives:

```python
@pytest.fixture
def sandbox_worktree(request):
    """Disposable sandbox worktree for integration tests that modify project files."""
    from systems.sandbox import worktree_setup, worktree_teardown
    topic = f"pytest-{request.node.name.replace(':', '-')}"
    path = worktree_setup(topic)
    try:
        yield path
    finally:
        worktree_teardown(topic)
```

`systems.sandbox.worktree_setup(topic)` / `worktree_teardown(topic)` create a sibling worktree at `<parent>/<project>--tmp-<topic>/` with a `sandbox/tmp/<topic>` branch and clear it on exit. Topic derives from the pytest node name so concurrent tests don't collide. Orphaned worktrees are swept by `ocd-run sandbox cleanup`.

Tests under `tests/plugins/ocd/` import `systems.sandbox` directly (plugin venv puts it on sys.path). Project-level tests under `tests/integration/` shell out to `ocd-run sandbox worktree setup <topic>` / `teardown <topic>`.

Applies when — tests stage or unstage files (`git add`, `git reset`), run git hooks, create or delete files in the project tree, or modify tracked files and restore them.

Skip when — tests only read project files, operate entirely in `tmp_path` or external temp directories, or mock git operations.

**Agent-spawning tests.** Some behaviors require a real Claude subprocess — hook behavior under real Edit/Write calls, plugin wiring during a fresh `claude -p` session, MCP servers binding under a fresh `CLAUDE_PROJECT_DIR`. Deterministic tests and mocks can't substitute.

Real agent tests cost tokens, take seconds to minutes, and carry model-variance flakiness. Opt-in: mark `pytestmark = pytest.mark.agent` at module level; pytest skips them unless `--run-agent` is passed.

Verify — plugin wiring (PATH resolution, venv binding, `CLAUDE_PROJECT_DIR` propagation, hook registration); hook invocation and corrective output under real tool calls; substrate setup and teardown when a real agent runs in the sandbox.

Don't verify — exact strings the agent produces (model variance is brittle; test side effects); specific tool-call sequences (agents reorder; assert end state, not path); model quality or reasoning (belongs in evaluation protocols).

Cost discipline — fail fast before the subprocess call (assert preconditions before spending tokens); keep tests narrow (one behavior, minimal prompt); share setup (session-scoped fixture beats per-test).

### Isolation

Tests own their state. Never rely on ambient user settings, global environment, or developer's home directory.

- Tests reading `~/.claude/settings.json` set `HOME` to a scratch path and write the exact settings needed
- Tests reading `CLAUDE_PROJECT_DIR` set it to `tmp_path` and populate only what the test requires
- Tests shelling out to tools that read ambient state (git, `uv`) scope state via env vars or `cwd`

A test passing locally but failing in CI with "JSONDecodeError: Expecting value" is almost always a fixture gap, not a flake.

### Placement

| What it tests | Home |
|---|---|
| Feature behavior of one skill or system | That skill or system's own `tests/` folder |
| Cross-system integration within a plugin | Plugin's `tests/` at plugin root |
| Universal discipline conformance across every system | Centralized check system any plugin can invoke |

Feature tests move with the skill or system they belong to. Integration tests stay at plugin root because they outlive any single system. Conformance tests apply universally and run against synthetic fixtures, not real systems that drift.

A behavior never lives in two homes. If a test fits feature or integration, it's a feature test. If a check fits integration or conformance, it's conformance only when it applies to every system uniformly.

## Driving Changes Through Tests

Locate or write the test first, confirm RED against current code, make the change, confirm GREEN. Applies when verification was going to happen anyway.

- **Verification runs through an allowlisted path.** The test suite (`bin/project-run tests`, `pytest`, `ocd-run check`) matches existing permission patterns. Ad-hoc verification (`python -c "..."`, bash pipelines, `VAR=$(...)` chains) often halts for manual approval.
- **The implementation can't ratify itself.** A test written after tends to assert what code does, not what spec demands — bugs get encoded as "correct."

### When Driving Applies

- Adding a new callable (function, method, CLI verb, MCP tool, hook handler)
- Modifying behavior of an existing callable — return values, error paths, side effects
- Fixing a bug where you'd want a regression guard
- Changing a round-trip-able format — parse ↔ serialize, schema, protocol

### Exemptions

- **Verified existing coverage.** Articulate what the post-change test would assert, grep test files, confirm coverage exists with the same inputs and expectation. Active check, not "probably covered somewhere."
- **Configuration restating.** The only possible test would echo data back. Don't write it.
- **No verification intended.** Docs, comments, docstrings, log entries, ROADMAP edits, memory updates.
- **Mechanical changes already covered.** Pure renames or format refactors where existing tests exercise the new shape.

### Running the Test

**Narrow batch.** Run only tests directly affected — the file or class owning the assertion. Broader scope is overhead during a red-green cycle.

**RED first.** Run the narrow batch against current code before implementing. If it passes unchanged, stop:

- The change is unnecessary (behavior is already correct)
- The test doesn't discriminate the behavior (false-positive coverage)
- Your model of current state is wrong

**Implement the change.**

**GREEN after.** Re-run the narrow batch. Confirm pass.

**Full suite.** Run only when structural changes cascade (moves, renames, refactors) or at checkpoint boundaries.

## Maintaining the Test System

### Callable Surface Coverage

Every callable a consumer invokes — CLI verb, subcommand, hook handler, skill entry point, MCP tool, script — has at least one test. Kind (unit, integration, end-to-end) depends on what it does.

- Zero test references is a missing test, not a "simple enough" exemption
- Untested callables rot — the next change breaks them silently
- Required flags need at least one test path
- Boolean flags that change behavior meaningfully (destructive `--force`, mode-switching) need their own path; ceremony flags (`--quiet`, `--no-color`) are covered transitively

**Crawlable inventory.**

1. List every callable — CLI verbs (argparse in `__main__.py`), hook handlers (`hooks.json`), skill slash commands (`SKILL.md`), MCP tools (registrations), project scripts (`bin/`, `scripts/`)
2. Grep test files for invocations
3. Callables with zero invocations are gaps

`/ocd:check` runs this crawl as part of universal conformance.

**Exempt.**

- Private helpers (underscore-prefixed, no public dispatch path) — covered transitively
- Deprecated callables — delete rather than test

### Anti-patterns

**Configuration restating.** If manifest says `pattern: "*.py"` and test asserts `pattern == "*.py"`, the test verifies parsing, not system behavior. Test that pattern matching behaves correctly (file X matches pattern Y).

**Coverage metrics disconnected from risk.** 100% on a formatter has less value than 60% on permission enforcement with adversarial cases. Allocate effort proportional to failure impact.

**Unit-testing non-deterministic behavior.** Agent judgment, NL interpretation, and workflow execution quality can't be caught by unit tests. Don't assert specific strings, tool-call sequences, or prompt interpretations. Test deterministic infrastructure; evaluate agent behavior through protocols.

## Decision Framework

For any callable or deterministic component:

1. Does it have at least one test? If no, write one — untested callables are the first gap.
2. If deterministic:
    1. Contract agents depend on (output format, exit codes, help text): snapshot
    2. Invariants exist: property test
    3. Idempotent by design: test idempotency
    4. Security boundary: exhaustive adversarial cases
    5. Silent failure causes downstream malfunction: test regardless of simplicity
    6. Integration test duplicates unit coverage with no new failure mode: skip
    7. Test merely restates configuration: skip
3. Else: evaluate through protocols, don't unit test
