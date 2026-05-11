"""Compliant runtime-operational fixture system.

Exposes the full readiness interface. Used as a positive fixture for
the dormancy checker — exercises the dormant → init → operational
transition and verifies ready/ensure_ready behave correctly.
"""

from ._init import ready, ensure_ready  # noqa: F401
