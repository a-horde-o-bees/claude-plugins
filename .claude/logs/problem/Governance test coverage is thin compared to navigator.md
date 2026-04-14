# Governance test coverage is thin compared to navigator

## Purpose

`lib/governance/` has 435 lines of tests in a single file (`tests/unit/test_governance.py`) covering 8 facade function groups: order, list, match (incl. excludes), pattern normalization, frontmatter reading, block-style patterns, list patterns. Navigator by comparison has 16 per-function test files totalling several thousand lines. The disparity means governance regressions are likelier to slip through — especially anything that only surfaces through the CLI dispatch, which currently has zero direct tests.

## Specific gaps

- **CLI dispatch untested.** `cli.py` has `_dispatch_list`, `_dispatch_for`, `_dispatch_order` (argument-parsing and output formatting). Tests exercise the facade directly, never through the argparse path. Output format changes can't regress an existing test.
- **Error path coverage.** Dangling governance references (missing governor files), malformed frontmatter, invalid includes patterns — partially covered but not exhaustively. The `order` command's dangling-refs branch and non-zero exit code aren't verified end-to-end.
- **No per-function split.** Navigator's pattern of one test file per public facade function makes it easy to see what's covered and where to add tests. Governance's monolith makes gaps less visible.

## When this came up

Surfaced during Phase 1 architectural refactor (lib/governance + lib/navigator reorganization). User noticed the lib sketch implicitly showed governance lacking tests parity with navigator; verification showed tests exist but the structural and coverage gap is real.

## Fix direction

Not a v1 blocker unless governance behavior is about to be changed. Follow-up during or after Phase 2 `testing.md` convention lockdown — at that point the test-file conventions (one file per facade function, split by domain) will be explicit and governance can be brought into line. CLI dispatch tests should land alongside the cli.py → `__main__.py` rename since the dispatch code moves anyway.
