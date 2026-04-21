# Per-verb integration test coverage

## Purpose

Exercise every plugin verb that has a CLI surface via at least one integration test that subprocess-invokes `bin/ocd-run <verb>`. Current tests import modules directly and bypass the user-facing entry path, so bin/ocd-run venv resolution, run.py module promotion, and CLI argument marshaling are untested except through a representative probe suite.

## Baseline already in place

`tests/plugins/ocd/integration/test_cli.py` covers dispatch classes — bin executability, no-args error, bare-name promotion, dotted-module passthrough, nested-subparser dispatch, JSON-emitting verb contract, argparse flag marshaling. That closes the mechanical failure-mode gap but does not exhaustively validate every verb.

## Proposed discipline

Per-system integration file — `tests/plugins/ocd/integration/test_<system>_cli.py` — with one test per verb the system exposes. Each test subprocess-invokes `ocd-run <system> <verb> [args]` and asserts on exit code, stdout shape, and any observable side effects.

## Per-system difficulty tiers

**Tier 1 — cheap (start here):**

- `framework` — init/status, scoped with --system, JSON-emitting
- `sandbox` — sibling-path, worktree-list, worktree-status, cleanup inventory (read-only verbs)
- `navigator` — list/get/search verbs against a minimal DB fixture
- `governance` — list/order verbs against existing .claude/conventions
- `log` — list/show verbs

**Tier 2 — needs fixtures:**

- `pdf` — needs a markdown source file and asserts an output artifact
- `refactor` — needs a scratch Python codebase as a temp target
- `patterns` / `conventions` / `rules` — init/status require a synthetic `.claude/` target
- `permissions` — deploys settings to a tmp home-dir

**Tier 3 — side-effect-heavy:**

- `sandbox worktree-add/remove`, `project setup/teardown`, `worktree setup/teardown` — require a disposable git worktree fixture (existing integration tests already use this pattern)
- `cleanup remove` — destructive, needs pre-seeded inventory
- `check dormancy` — exercises every system's dormancy contract, complex state

**Tier 4 — interactive / Claude-subprocess:**

- `sandbox exercise` — dispatches `claude -p`, requires API key and a real subprocess
- Any verb that uses `AskUserQuestion` — can't trivially be integration-tested without harness

## Rollout

Incremental, per-system. Start with Tier 1 (framework, sandbox read verbs, navigator, governance, log) — these cover the majority of the CLI surface with minimal fixture work. Tier 2 and 3 added as each system gets touched by maintenance work. Tier 4 stays manual until a harness exists.

## Shared helper

The baseline test file already has:

```python
PLUGIN_ROOT = Path(__file__).resolve().parents[4] / "plugins" / "ocd"
OCD_RUN = PLUGIN_ROOT / "bin" / "ocd-run"

def _run(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run([str(OCD_RUN), *args], capture_output=True, text=True, cwd=cwd)
```

Factor out into `tests/plugins/ocd/integration/_cli_helpers.py` once a second file needs it. Per-system test files import from that helper.

## Rationale — why this bar matters

Unit tests that `from systems.navigator import scan` skip every piece of mechanism the real user depends on: the bin/ocd-run venv resolution chain (6 fallback steps), run.py's module auto-promotion, argparse at the CLI layer, exit-code propagation. The earlier refactor that moved the test runner out of the plugin surfaced that gap explicitly — the bin wrapper was unexercised because tests all imported directly. Formalizing "every verb has integration coverage" makes the gap vanishingly small without depending on dev discipline.

## Prerequisites

- Plugin venv must be installed (SessionStart hook has run; CI workflows that run integration tests will need this bootstrap).
- Tests that need state (e.g., navigator queries) need a fixture strategy — inline DB setup vs session-scoped worktree fixture.

## Related

- `tests/plugins/ocd/integration/test_cli.py` — baseline dispatch coverage (landed with the tools/bin refactor).
- Broader CI ambition: once per-verb integration coverage exists, CI's "run full test suite" becomes a genuine end-to-end verification rather than module-level-only.
