# Move check to project root tooling

`plugins/ocd/systems/check/` runs the System Dormancy conformance check against plugin systems. Its domain — verifying every plugin's systems follow the dormancy contract — is cross-plugin and inherently project-level, not something a consumer of the ocd plugin would care about or toggle. It currently ships bundled with ocd because the implementation depends on the plugin framework (`framework.NotReadyError`, `framework.get_plugin_root`, `framework.get_plugin_name`).

## Proposed home

- New path: `tools/check/` alongside `tools/testing/` and `tools/setup/`
- Invoked via `bin/plugins-run check dormancy [--plugin <name>]`
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
- Decision on whether `bin/plugins-run check` should iterate every plugin by default or require explicit `--plugin`
