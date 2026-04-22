## Purpose

Future dimension for `/ocd:check`: detect module-level state that depends on import-time environment (cwd, env vars, filesystem state). This class of bug silently passes local test runs where the dependent state happens to exist but fails on fresh clones / CI / subprocess contexts.

## Triggering incident

Navigator `server.py` gated `@mcp.tool()` decorator firing on `_READY = _nav.ready(Path(DB_PATH))` at module import. `DB_PATH` defaulted to a relative path, resolved against cwd at import. Local dev cwd had a seeded navigator DB → tools registered → tests passed. Fresh clone did not → tools skipped → 16 test failures with `AttributeError: module 'systems.navigator.server' has no attribute 'paths_*'`. Fixed with a conftest stub, but the underlying pattern (module-level conditional registration based on import-time environment) is the real smell.

## Proposed check shape

Static AST analysis of each system's public modules, flagging:

- Module-level reads of `os.environ`, `Path.cwd()`, or relative filesystem probes that gate module-level side effects (decorator application, attribute assignment, class definition)
- Module-level conditionals whose truth depends on filesystem or environment state observable at import time, when the branch contains `@<something>.tool()` or similar registration patterns
- Any `if` / `for` wrapping decorator applications at module top level

Reporting should distinguish:

- **Hard failure** — decorator inside a condition that evaluates differently across import contexts (the navigator case)
- **Soft warning** — module-level reads of env vars used to configure constants (common and usually fine)

## How it would fit the check family

Slot as `_import_state_dependency.py` in `plugins/ocd/systems/check/`. Skill dispatch: `/ocd:check import-state` or `/ocd:check all` picks it up alongside dormancy. Fixtures under `tests/integration/fixtures/` exercise the detector — compliant module, module with cwd-dependent registration, module with env-var-dependent registration.

## Prerequisite

Navigator's dormancy design already has import-time gating (preserved by the conftest fix). Before shipping this check as enforcing, decide whether that pattern is accepted (test via conftest — current) or should be refactored (call-time gating instead). The check should enforce the chosen discipline, not catch existing compliant patterns.
