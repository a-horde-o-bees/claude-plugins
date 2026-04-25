"""Shared exception types for plugin systems.

NotReadyError is raised by a system's `ensure_ready()` when the system's
infrastructure is absent or divergent. The message should name the
corrective action (the setup skill or CLI command that installs the
missing pieces). CLI entry points catch this type, print the message to
stderr, and exit with a non-zero status — see the System Dormancy
discipline in the marketplace-level architecture.
"""


class NotReadyError(RuntimeError):
    """Raised when a system is called before its infrastructure is deployed."""
