"""Local tooling specific to the ocd plugin.

DB-backed helpers (`db`) live here when they are scoped to this plugin's
implementation rather than propagated to every plugin. Cross-cutting
primitives (path resolution, shared error types) live under `dependencies/`
instead, propagated from the project root by `.githooks/pre-commit`.
"""
