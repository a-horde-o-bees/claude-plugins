# Callable-surface coverage crawler

## Purpose

Implement the discipline check that enforces `rules/ocd/testing.md`'s Callable Surface Coverage bar — every callable (CLI verb, subcommand, hook, skill, MCP tool, project script) has at least one test exercising it. Runs under `/ocd:check` as universal conformance.

The rule states the bar; this idea tracks building the machinery that mechanically finds gaps.

## Inventory sources to crawl

Callables are discoverable from specific file patterns across the repo:

- **CLI verbs** — argparse `add_subparsers` + `add_parser` calls in every `systems/*/__main__.py` (`framework`, `sandbox`, `navigator`, `log`, `pdf`, etc.). Plus project-level verbs in `tools/__main__.py`.
- **Hook handlers** — entries in every `hooks.json` with `command`, `http`, `prompt`, or `agent` types. Also the `.claude/settings.json` hooks array for project-local hooks.
- **Skill slash commands** — every `SKILL.md` declares its verb via frontmatter `name` + body workflow. Sub-verbs typically in `argument-hint`.
- **MCP tools** — tool registrations in MCP server code (decorators or `server.tool()` calls for Python SDK; varies per server framework).
- **Project-level bins** — `bin/project-run` subcommands, `scripts/*.sh`, `scripts/*.py`.

## Test reference discovery

For each callable name, grep test files:

- Python: `import <module>` or `subprocess.run([<bin>, "<verb>"])` or `run("<module>", ...)` (the `run` helper in `test_invocation.py`)
- Shell: `bash` invocations of hook scripts in fixtures
- Frontmatter: no equivalent needed — skill tests are typically integration tests that invoke via `claude -p` (agent-spawning) or parse the skill's own workflow

A callable is "covered" if at least one test file contains a grep-matching invocation. Zero matches = gap.

## Output shape

```
/ocd:check surface-coverage

CLI verbs (ocd plugin): 12 callables, 11 covered, 1 gap
  - ocd-run framework permissions analyze — no test references

Hook handlers: 2 callables, 2 covered

Project bins: 4 callables, 4 covered

Overall: 1 gap.
```

The output format follows the existing `/ocd:check` shape (structured counts + gap list).

## Edge cases to handle

- **Private helpers** — underscore-prefixed functions are transitive-covered by public callers' tests; exempt from the bar.
- **Deprecated callables** — a frontmatter or docstring marker (`deprecated: <date>`) exempts a callable from the check; list deprecated + planned-removal as a separate report.
- **Dynamic dispatch** — if a callable is registered dynamically (plugin-to-plugin, decorators that shadow argparse), static grep may miss it. Mitigation: allow explicit `# coverage:exempt` markers with a rationale comment. Should be rare.
- **Test helpers invoking callables indirectly** — a test helper that calls `run("framework", "status")` should count for any test that uses it. The crawl needs to trace helper references too, or accept false-positive gaps when tests route through helpers.

## Dependencies

- Existing `/ocd:check` skill infrastructure (dormancy check lives here today — add coverage check alongside)
- argparse introspection for dispatch enumeration (parse the argparse tree from `__main__.py` files without executing them)
- Grep + language-specific parsing for test-file invocation detection

## Related

- Idea superseded: previous "Per-verb integration test coverage" log — the per-verb-per-integration-test framing was wrong; this replaces with the correct coverage bar (any test kind) + crawler implementation.
