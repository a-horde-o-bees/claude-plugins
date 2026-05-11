"""Shared primitives propagated to every plugin.

Canonical home for cross-cutting modules that every plugin imports —
path resolution (`environment`), shared exception types (`errors`).
Each file here is a single source of truth: `.githooks/pre-commit`
vendors a byte-equal copy into every plugin's `dependencies/` directory, and
`tests/integration/test_shared_file_sync.py` enforces drift-freedom.

Consumers import the modules explicitly — `from dependencies.environment
import get_project_dir`, `from dependencies.errors import NotReadyError`.
This facade intentionally re-exports nothing so callers cannot
accidentally import a stale name after a canonical source evolves.
"""
