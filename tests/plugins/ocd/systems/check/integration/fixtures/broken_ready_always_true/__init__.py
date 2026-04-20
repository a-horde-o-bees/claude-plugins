"""Broken fixture — ready() always returns True.

Used as a negative fixture: the dormancy checker should flag this
system because its readiness predicate does not reflect actual state.
"""

from ._init import ready, ensure_ready  # noqa: F401
