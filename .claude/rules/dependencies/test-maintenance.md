# Test Maintenance

Auditing the test suite — coverage gaps, anti-patterns, rot in untested callables.

## Callable Surface Coverage

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

## Anti-patterns

**Configuration restating.** If manifest says `pattern: "*.py"` and test asserts `pattern == "*.py"`, the test verifies parsing, not system behavior. Test that pattern matching behaves correctly (file X matches pattern Y).

**Coverage metrics disconnected from risk.** 100% on a formatter has less value than 60% on permission enforcement with adversarial cases. Allocate effort proportional to failure impact.

**Unit-testing non-deterministic behavior.** Agent judgment, NL interpretation, and workflow execution quality can't be caught by unit tests. Don't assert specific strings, tool-call sequences, or prompt interpretations. Test deterministic infrastructure; evaluate agent behavior through protocols.
