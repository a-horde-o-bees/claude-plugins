# Move check to project root tooling

`plugins/ocd/systems/check/` runs the System Dormancy conformance check against plugin systems. Its domain — verifying every plugin's systems follow the dormancy contract, plus markdown and python discipline checks across the tree — is cross-plugin and inherently project-level, not something a consumer of the ocd plugin would care about or toggle per-system. It currently ships bundled with ocd because the implementation depends on the plugin framework (`framework.NotReadyError`, `framework.get_plugin_root`, `framework.get_plugin_name`).

Markdown and python check dimensions added since this idea was first written further reinforce the project-level positioning — neither is plugin-specific; both apply uniformly across the whole working tree.

## Proposed home

- New path: `tools/check/` alongside `tools/testing/` and `tools/setup/`
- Invoked via `bin/project-run check dormancy [--plugin <name>]`
- Defaults to iterating every `plugins/*/` when `--plugin` is omitted
- Tests move to project-level `tests/integration/test_check_dormancy.py` with fixtures still synthetic

## Framework dependency handling

Check currently relies on the plugin's `framework` module for:

- `framework.NotReadyError` — catching exceptions raised by target systems. Class identity matters, so check cannot define its own — it must import the target plugin's framework to reference the same class object the target raises.
- `framework.get_plugin_root()` / `framework.get_plugin_name(root)` — plugin location and name.

Approach: inject the target plugin's `systems/` onto `sys.path` at invocation time and `importlib.import_module("framework")` from there. Module cache must be cleared between plugins when iterating multiple targets, same pattern `scripts/auto_init.py` uses.

Alternative: catch by `type(e).__name__ == "NotReadyError"` and skip the framework import. Looser typing; works without sys.path manipulation; loses isinstance check specificity.

## Why not in v0.1.0

The opt-in work split explicitly deferred this. Check's current location does not affect user experience — it is already excluded from the opt-in surface because it has no `_init.py`. Moving it is structural hygiene and can land without user-visible change.

## Prerequisites

- Opt-in feature committed and stable (so check's location does not interact with opt-in semantics)
- Decision on whether `bin/project-run check` should iterate every plugin by default or require explicit `--plugin`

## Naming

Once `check` is project-level rather than plugin-system, consider renaming to `lint` if the bulk of the dimensions (markdown, python, future shellcheck/ruff/PyMarkdownLnt) are linting-style checks rather than conformance checks. Dormancy is the only dimension that strictly verifies a contract; the rest are linters in the conventional sense. Either pick the name that matches the dominant dimension type at promotion time, or land both verbs and let invocation patterns disambiguate.

## Run scheduling

`/ocd:check` (or `/ocd:lint`) belongs run with tests — they share the same "verify before merging" lifecycle. Concrete integration points:

- `bin/project-run tests` runs the lint pass alongside (or before) pytest, so contributors who run tests automatically get lint feedback. Failure of either gates the run.
- `.github/workflows/ci.yml` calls the same project-run target — single source of truth for what "checked" means.
- Pre-commit hook is optional follow-on: once the project-level invocation exists and is fast enough, wire it into `.githooks/pre-commit` for staged-file scoped runs.

## Adoption discipline

When a new dimension turns on (or an existing dimension's scope expands), rectify the existing tree to conform before the gate fires — do not introduce a transitional allowlist. Allowlists for genuinely-blessed exceptions (anchor files for the parent-walking rule, fixture inputs for the markdown rule) stay; allowlists for "we'll fix this later" do not. The discipline only works when contributors trust that a green run means clean tree, not "clean tree minus the historical backlog."

This means: dimension turn-on is a coordinated rectification PR — fix every existing violation in the same change that wires the dimension into `bin/project-run tests` and CI. The size of that PR is the size of the existing violation count; tolerable if rectification is mechanical (autofix) and reviewable if not.
