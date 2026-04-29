---
includes: "*"
governed_by:
  - .claude/rules/ocd/design-principles.md
---

# Testing

Testing discipline organized by phase of interaction: authoring tests, driving changes through tests, maintaining the test system, and deciding when to test. Always-on because the decision "do I test this" precedes the act of editing a test file.

## Test Authoring

### What Qualifies

Deterministic operations get traditional tests. Non-deterministic behavior (e.g., agent judgment, NL interpretation, workflow execution quality) gets evaluation protocols, not unit tests. If identical inputs reliably produce identical outputs, test it. If not, evaluate it through protocols that accept variance and assess outcomes.

### Durability

Verification of new code belongs in the test structure. Not in ad-hoc bash commands. Not in inline Python heredocs. Not in `python -c "..."` snippets. Not in any one-shot execution outside the test files.

- All verification of new code — including smoke tests, "just to check" runs, round-trip confirmations, parse-and-render checks, and any other one-shot validation — goes through the test structure as a test in the relevant test file
- Exploration and learning (e.g., reading code, querying state, understanding existing behavior) are different from verifying new code; explore freely, but verification of new code that you wrote requires a test
- Test fixtures handle environment setup automatically while ad-hoc commands require inline env vars that need manual approval — the durability cost matters more than the friction cost

### Techniques by Risk Class

Each risk class has a test technique that produces the highest regression-prevention value for that class. The first group — strong cases — always earns the investment. The second — situational — earns it when the specific failure mode applies.

#### Strong-case techniques

**Output format contracts.** Tool responses are API contracts. Agents parse output mechanically — any change to structure, field names, or response format is a breaking change even if the data is the same.

- Structured output matches explicit schema or snapshot
- Error responses include machine-parseable identifiers, not just prose
- Tool descriptions and parameter schemas are complete and accurate

Technique: snapshot/approval testing — capture golden output for representative inputs, diff on every change, review diffs deliberately before approving new snapshots.

**Roundtrip and invertibility.** If a system reads a format and writes it back, the roundtrip property is the highest-value test. Parse then serialize then parse again must yield same structure.

- Format parse-serialize roundtrips (e.g., frontmatter, manifests, configuration)
- Pattern matching symmetry (if pattern matches file, listing files under pattern includes that file)
- Path resolution determinism (same input always resolves to same absolute path)

Technique: property-based testing — generate random valid inputs, run through pipeline, assert roundtrip holds.

**Idempotency.** Agent workflows retry frequently. Any operation that changes behavior on second identical invocation causes cascading failures.

- Database operations produce same state whether run once or twice
- Init/deploy operations detect existing state and skip gracefully
- File operations overwrite cleanly without side effects

Technique: run operation, capture state, run again, assert state identical.

**Invariant preservation.** Define properties that must hold regardless of input, then test with generated data. Invariants catch classes of bugs, not individual cases.

- Dependency ordering always produces valid topological sort
- Cycle detection always raises on cycles, never silently degrades
- Wildcard patterns always match everything
- Deny always overrides allow in permission systems
- Path traversal sequences never escape allowed boundaries

Technique: define invariant as predicate, generate random valid inputs, assert predicate holds universally.

**Deterministic skeleton.** Separate deterministic skeleton from non-deterministic behavior. Test skeleton — highest regression prevention per line of test code.

- Resolution priority ordering (which source wins when multiple match)
- Pattern matching (which rules apply to which inputs)
- Command routing (which operations get approved, denied, or blocked)
- Settings evaluation (how configuration is interpreted)
- Dependency ordering (topological sort correctness)

Technique: traditional unit tests — isolate each deterministic function, verify with explicit inputs and expected outputs.

**Security boundaries.** Permission enforcement has zero tolerance for false negatives. A bug that permits an operation that should be denied has immediate consequences.

- Path traversal resistance
- Injection in quoted vs unquoted contexts
- Deny list precedence over allow list
- Empty settings default to restrictive, not permissive

Technique: explicit boundary case enumeration plus property-based fuzzing of inputs.

#### Situational techniques

**Structured document validation.** Structured documentation consumed by agents is code. Validate schema and referential integrity, not prose content.

Applies when — fields that agents parse programmatically (e.g., names, patterns, dependencies); referential integrity (manifest entries reference files that exist); format consistency across files of same type.

Skip when — linting prose content that agents interpret with natural language understanding; enforcing style rules on descriptions that do not affect machine parsing.

**Integration tests across boundaries.** Unit tests with mocked dependencies can pass while real integration is broken. Use integration tests strategically at boundaries where failure is silent.

Applies when — CLI end-to-end (invoke actual script, verify stdout/stderr/exit code); database operations against real databases (temp databases in test fixtures); file system operations in temp directories.

Skip when — duplicating what unit tests already cover with mocked boundaries; testing library behavior documented by library authors.

**Value filter for an integration test:** what dispatch-class or real-world failure does this catch that unit tests don't? If the answer is "nothing specific," it's a retread of unit coverage. Content assertions should validate structure (e.g., shape, required fields, exit codes) — not semantic behavior that unit tests already cover.

**Git worktree isolation.** Integration tests that create, modify, or stage files within the project repository must run in a disposable git worktree. A worktree shares the object store with the main repo — tests operate on real project files in real git context — but has its own working tree and index. Changes in the worktree cannot affect the main working tree.

Without isolation, tests that use `git checkout --`, `git restore`, or `git reset` to clean up after themselves silently destroy uncommitted changes in the main working tree.

Canonical fixture — the `sandbox_worktree` pytest fixture in `tests/plugins/ocd/conftest.py` wraps the ocd sandbox system's ephemeral worktree primitives:

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

The fixture is a thin wrapper over `systems.sandbox.worktree_setup(topic)` / `worktree_teardown(topic)`, which create a sibling worktree at `<parent>/<project>--tmp-<topic>/` with a `sandbox/tmp/<topic>` branch and clear it on exit. Topic derives from the pytest node name so concurrent tests never collide. Orphaned worktrees left by crashed tests are swept by `ocd-run sandbox cleanup`.

Why sandbox, not a bespoke fixture — the sandbox system is this project's canonical disposable-workspace mechanism — used by `/ocd:sandbox exercise`, by future `/ocd:sandbox run <test.md>` markdown-driven tests, and by pytest integration tests. One set of primitives, one set of orphan-sweep semantics, one permission glob covering every substrate.

Cross-suite reuse — tests under `tests/plugins/ocd/` import `systems.sandbox` directly because the plugin's venv puts it on sys.path. Project-level tests (under `tests/integration/`) run in the project venv without that import path; they shell out to `ocd-run sandbox worktree setup <topic>` / `teardown <topic>` instead. Same primitives, different invocation.

Applies when — tests stage or unstage files (`git add`, `git reset`), run git hooks, create or delete files in the project tree, or modify tracked files and restore them afterward.

Skip when — tests only read project files without modification, operate entirely in `tmp_path` or other external temp directories, or mock git operations.

**Agent-spawning tests.** Some behaviors can only be verified end-to-end by spawning a real Claude subprocess — hook behavior during real Edit or Write calls, plugin wiring during a fresh `claude -p` session, MCP servers binding under a fresh `CLAUDE_PROJECT_DIR`. These tests exercise integration between the plugin and a running agent, which deterministic tests and mocks cannot substitute for.

Real agent tests cost tokens, take seconds to minutes per test, and carry model-variance and API-reliability flakiness. They are opt-in by default: mark them `pytestmark = pytest.mark.agent` at the module level, and the pytest configuration skips them unless `--run-agent` is passed on the command line.

Agent tests should verify — plugin wiring around the subprocess (e.g., PATH resolution, venv binding, `CLAUDE_PROJECT_DIR` propagation, hook registration); hook invocation and corrective output under real tool calls the agent makes; substrate setup and teardown correctness when a real agent runs inside the sandbox.

Agent tests should not verify — exact strings the agent produces (model variance makes these brittle; test observable side effects instead); specific tool-call sequences (agents reorder work; assert the required state at the end, not the path taken); model quality or reasoning (that belongs in evaluation protocols).

Discipline for cost — fail fast before the subprocess call (assert preconditions before spending tokens); keep agent tests narrow (e.g., one behavior per test, minimal prompt); share setup where possible (a session-scoped fixture costs far less than per-test setup).

### Isolation

Tests must own their state. Never rely on ambient user settings, global environment, or the developer's home directory happening to contain what the test needs.

- Tests that read `~/.claude/settings.json` (or similar) set `HOME` to a scratch path in the fixture and write the exact settings they need
- Tests that read `CLAUDE_PROJECT_DIR` content set it to a `tmp_path` and populate only what the test requires
- Tests that shell out to tools that may read ambient state (e.g., git, `uv`) scope that state via env vars or `cwd`

CI's clean environment surfaces ambient-state dependencies loudly — a test that passes locally but fails in CI with "JSONDecodeError: Expecting value" or similar is almost always a fixture gap, not a flake.

### Placement

Test files go in one of three homes depending on what they verify:

| What it tests | Home | Example |
|---------------|------|---------|
| Feature behavior of one skill or system | That skill or system's own `tests/` folder | Does `paths_get` return the right shape for a directory |
| Cross-system integration within a plugin | The plugin's `tests/` at plugin root | Does setup init → navigator scan → governance match compose correctly |
| Universal discipline conformance across every system | A centralized check system that any plugin can invoke | Does every system follow the dormancy contract |

Feature tests are bounded by the skill or system they belong to and move with it. Integration tests exercise cross-system workflows and stay at plugin root because they outlive any single system. Discipline conformance tests encode rules that apply universally — they belong to a dedicated check system and are tested against synthetic fixtures, not against real systems that drift.

A single behavior never belongs in two homes. If a test would fit either feature or integration, it is a feature test — the skill owns it. If a check would fit either integration or discipline conformance, it is a conformance check only when it applies to every system uniformly.

## Driving Changes Through Tests

A change is driven through its test: locate or write the test first, confirm it fails against current code, make the change, confirm it passes. Not universal TDD ritual — the discipline applies when verification was going to happen anyway.

Two concrete benefits specific to this workflow:

- **Verification runs through an already-allowlisted path.** The test suite (e.g., `bin/project-run tests`, `pytest`, `ocd-run check`) is covered by existing permission patterns. Ad-hoc verification (e.g., `python -c "..."`, one-off bash pipelines, `VAR=$(...)` chains) frequently doesn't match allowlist patterns cleanly and halts for manual approval. Test-first converts unapproved verification into approved verification.
- **The implementation can't ratify itself.** A test written after implementation tends to assert what the code happens to do rather than what the spec demands — if the implementation has a subtle bug, the after-the-fact test often encodes the bug as "correct."

### When Driving Applies

- Adding a new callable (e.g., function, method, CLI verb, MCP tool, hook handler)
- Modifying behavior of an existing callable — return values, error paths, side effects
- Fixing a bug where you'd want a regression guard
- Changing a round-trip-able format — parse ↔ serialize, schema, protocol

### Exemptions

Skip the test-first step when any of the following hold:

- **Verified existing coverage.** Articulate what your hypothetical post-change test would assert, grep test files for that assertion, and confirm the coverage actually exists with the same inputs and expectation. The check is active, not presumed — "probably covered somewhere" is not an exemption.
- **Configuration restating.** The only possible test would echo data back (`assert config == config`). Handled by *Maintaining — Anti-patterns* below; not a new exemption, but noted so Driving doesn't force a testing-theater workaround.
- **No verification intended.** Docs, comments, docstrings, log entries, ROADMAP edits, memory updates — you weren't going to verify anything, so there's nothing to frontload.
- **Mechanical changes already covered.** Pure renames or format refactors where existing tests exercise the new shape as-is.

### Running the Test

**Narrow batch.** Run only the tests directly affected by the current change — the file or class owning the assertion, not the full suite. Broader scope is overhead during a red-green cycle.

**RED first.** Run the narrow batch against current code before implementing. If it passes unchanged, stop and surface the uncertainty — three things could be wrong and none are resolved by proceeding blindly:

- The change is unnecessary (the behavior you meant to fix is already correct)
- The test doesn't discriminate the behavior you're changing (false-positive coverage)
- Your model of the current state is wrong

**Implement the change.**

**GREEN after.** Re-run the same narrow batch. Confirm pass.

**Full suite.** Run the full suite only when structural changes cascade (moves, renames, refactors) or at checkpoint boundaries — broken imports and cascading failures do not surface in narrow tests.

The RED-first requirement applies to both paths opened by *When Driving Applies*:

- **New test** — write, run, confirm RED for the right reason (the assertion fails, not an import error or typo), implement, run, confirm GREEN
- **Existing coverage** — locate, run, confirm RED against current code, implement, run, confirm GREEN

A new test that passes on first run is the same red flag as an existing test that passes pre-change: something is off, stop.

## Maintaining the Test System

### Callable Surface Coverage

Every callable surface a consumer invokes — CLI verb, subcommand, hook handler, skill entry point, MCP tool, script — has at least one test exercising it. The test may be unit, integration, or end-to-end; the choice depends on what the callable does. What matters is that no callable goes untested.

- A callable with zero test references is a missing test, not a "simple enough" exemption
- Untested callables accumulate rot — the next change breaks them silently because nothing fails
- Required flags must have at least one test path exercising them
- Boolean flags that change behavior meaningfully (e.g., destructive `--force`, mode-switching flags) require their own test path; boolean flags that only affect output ceremony (e.g., `--quiet`, `--no-color`) are covered transitively by flagless invocations

**Crawlable inventory.** Coverage is decidable from the repository:

1. List every callable — CLI verbs (argparse in `__main__.py`), hook handlers (entries in `hooks.json`), skill slash commands (`SKILL.md` files), MCP tools (tool registrations), project-level scripts (e.g., `bin/`, `scripts/`)
2. For each callable, grep test files for an invocation
3. Callables with zero invocations are coverage gaps

A discipline check under `/ocd:check` runs this crawl as part of universal conformance.

**Exempt.**

- Private helpers (underscore-prefixed, not reachable through a public dispatch path) — covered transitively by public callers' tests
- Deprecated callables slated for removal — delete rather than continue testing

### Anti-patterns

**Configuration restating.** If manifest says `pattern: "*.py"` and test asserts `pattern == "*.py"`, test asserts that parsing works, not that system works. Test that pattern matching behaves correctly (file X matches pattern Y), not that configuration reads back as written.

**Coverage metrics disconnected from risk.** 100% coverage on a formatting function has less value than 60% coverage on permission enforcement with adversarial edge cases. Allocate testing effort proportionally to failure impact — Callable Surface Coverage sets the floor, Decision Framework allocates effort above it.

**Unit-testing non-deterministic behavior.** Agent judgment, NL interpretation, and workflow execution quality cannot be caught by unit tests. Do not assert agents produce specific strings, make specific tool call sequences, or interpret prompts specific ways. Test deterministic infrastructure agents depend on; evaluate agent behavior through protocols that assess outcomes.

## Decision Framework

For any callable or deterministic component, ask:

1. Does the callable have at least one test? If no: write one — the test kind is your choice per the rules below, but untested callables are the first gap to close.
2. If deterministic:
    1. If contract agents depend on (e.g., output format, exit codes, help text): snapshot test
    2. If invariants exist (properties that must hold for all inputs): property test
    3. If idempotent by design: test idempotency explicitly
    4. If security boundary: test exhaustively with adversarial cases
    5. If silent failure would cause downstream agent malfunction: test regardless of code simplicity
    6. If a proposed integration test duplicates existing unit coverage with no new failure mode: skip — overhead
    7. If a proposed test merely restates configuration: skip — testing theater
3. Else: evaluate through protocols, do not unit test
