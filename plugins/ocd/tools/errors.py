"""Shared exception types for plugin systems.

NotReadyError is raised by a system's `ensure_ready()` when the system's
infrastructure is absent or divergent. InitError is raised during `init()`
when reinitialization would destroy state without explicit consent — the
refusing-path for systems whose data is not regenerable. The message
should name the corrective action (the setup skill or CLI command that
installs the missing pieces, or the `--force` flag that authorizes a
destructive rebuild). CLI entry points catch these types, print the
message to stderr, and exit with a non-zero status — see the System
Dormancy discipline in the marketplace-level architecture.
"""


class NotReadyError(RuntimeError):
    """Raised when a system is called before its infrastructure is deployed."""


class InitError(RuntimeError):
    """Raised when init() refuses a destructive action without explicit force."""
