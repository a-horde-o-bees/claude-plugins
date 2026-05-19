"""Exception types raised by the transcripts CLI.

`NotReadyError` signals the DB is absent or has a divergent schema.
`InitError` signals init refused a destructive action without `--force`.
The CLI entry catches both, prints `{"error": "..."}` on stderr, and
exits 1.
"""


class NotReadyError(RuntimeError):
    """Raised when the transcripts DB is absent or has a divergent schema."""


class InitError(RuntimeError):
    """Raised when init() refuses a destructive action without explicit force."""
