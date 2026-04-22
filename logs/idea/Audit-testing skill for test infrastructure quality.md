# Audit-testing skill for test infrastructure quality

## Purpose

A new evaluate-testing skill that audits test infrastructure against the testing convention and codebase structure.

## Context

Current evaluation skills cover governance files and skill files. Test infrastructure has its own quality concerns that neither skill catches:

- **Coverage** — are submodules and key code paths exercised? Where are the gaps?
- **File decomposition and grouping** — do test files mirror the structure of the modules they test? Are tests for unrelated subsystems bundled into catch-all files?
- **Unit vs integration classification** — tests living as unit tests that hit real databases, networks, or filesystem should be integration tests; pure logic tests under integration/ waste CI time. Check actual implementation details against the boundary
- **Convention conformity** — does the test structure follow the testing convention (fixture patterns, decision framework for deterministic vs agent-level, worktree isolation, naming)?
- **Convention gaps** — implementation patterns in existing tests that work well but aren't captured in the testing convention yet. The evaluation discovers what the convention should prescribe, not just what it already does

The bidirectional nature matters: evaluate-testing checks tests against conventions AND checks conventions against test reality. Tests that consistently deviate from convention in the same way suggest the convention is wrong, not the tests.

Follows the same evaluation-skill-md pattern: report-only agent with domain-specific `_evaluation-criteria.md`, orchestrator-owned triage. Scope would be project-wide or per-plugin test directories.
