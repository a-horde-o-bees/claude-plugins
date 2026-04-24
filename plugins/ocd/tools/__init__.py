"""Always-on primitives vendored into this plugin.

`tools/` ships with the plugin and is importable at any time — before
`/ocd:setup` has run, in projects that may not even be git repos, and
on the critical path of hooks fired by Claude Code on every tool use.
Nothing here depends on lifecycle state; anything requiring activation
lives under `systems/` instead.

Canonical sources are at the project root `tools/`. Every file under
this directory is a propagated copy maintained by `.githooks/pre-commit`
and verified byte-equal by `tests/integration/test_shared_file_sync.py`.

Consumers import the modules explicitly — `from tools.environment
import get_project_dir`, `from tools.errors import NotReadyError`. This
facade intentionally re-exports nothing so callers cannot accidentally
import a stale name after a canonical source evolves.
"""
